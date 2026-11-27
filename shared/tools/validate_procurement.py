#!/usr/bin/env python3
"""Run native KiCad and procurement checks. Exit 1 when release is blocked."""
import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from check_interfaces import ROOT, kid, kids, parse, value

SYSTEM_REVIEWS = {
    "power_and_protection", "six_card_status_chain", "inventory_and_assembly",
    "xt60_authenticity_and_source_cable", "harness_and_peripheral_coverage",
}
BOARDS = ("pico-carrier", "power-manager", "string-daughterboard")
P = ROOT / "procurement"


def fields(node):
    return {value(p[1]): value(p[2]) for p in kids(node, "property")}


def atoms(node, key):
    return [value(token) for token in (kid(node, key) or [])[1:] if isinstance(token, str)]


def unique(records, label, errors):
    result = {}
    for key, record in records:
        if not key or key in result:
            errors.append(f"{label}: missing or duplicate key {key!r}")
        result[key] = record
    return result


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def unc(net):
    return None if not net or net.startswith("unconnected-(") else net


def inspect_board(board, xml, bom, errors):
    tree = ET.parse(xml)
    pcb = parse((ROOT / board / f"{board}.kicad_pcb").read_text())
    footprints = kids(pcb, "footprint")
    extras = []
    placed = []
    for fp in footprints:
        ref = fields(fp).get("Reference")
        if not kid(fp, "path") and not any(atoms(p, "net") for p in kids(fp, "pad")) and (
            "board_only" in atoms(fp, "attr") or not kids(fp, "pad")
        ):
            attrs = atoms(fp, "attr")
            extras.append([ref, value(fp[1]), atoms(fp, "uuid"), attrs])
            if "board_only" not in attrs:
                errors.append(f"{board}/{ref}: unlinked PCB graphic is missing board_only")
        else:
            placed.append((ref, fp))
    physical = unique(placed, board + " PCB", errors)
    symbols = unique(((s.get("ref"), s) for s in tree.findall("./components/comp")), board, errors)
    bom_rows = unique(((r["ref"], r) for r in read_csv(bom)), board + " BOM", errors)
    pins = defaultdict(dict)
    for net in tree.findall("./nets/net"):
        for node in net.findall("node"):
            ref, pin = node.get("ref"), node.get("pin")
            if pin in pins[ref]:
                errors.append(f"{board}/{ref}/{pin}: duplicate netlist node")
            pins[ref][pin] = net.get("name")
    all_refs = {}
    eligible = {}
    for ref in sorted(symbols.keys() | physical.keys() | bom_rows.keys()):
        label = f"{board}/{ref}"
        symbol, fp, row = symbols.get(ref), physical.get(ref), bom_rows.get(ref)
        record = all_refs[ref] = {}
        if symbol is None:
            errors.append(f"{label}: missing from native netlist")
        else:
            properties = {p.get("name") for p in symbol.findall("property")}
            path = symbol.find("sheetpath").get("tstamps", "").rstrip("/")
            uuids = symbol.findtext("tstamps", "").split()
            record.update(value=symbol.findtext("value", ""), footprint=symbol.findtext("footprint", ""),
                          paths=[f"{path}/{uuid}" for uuid in uuids], pins=pins.get(ref, {}),
                          source=f"{board}/" + symbol.find("./property[@name='Sheetfile']").get("value"),
                          dnp="dnp" in properties, in_bom="exclude_from_bom" not in properties,
                          on_board="exclude_from_board" not in properties)
            record["mpn"] = symbol.findtext("./fields/field[@name='MPN']", "")
            record["symbol_pins"] = sorted({p.get("num") for p in symbol.findall("./units/unit/pins/pin")})
            if (row is None and record["in_bom"]) or (row and any(
                row[k] != record[k] for k in ("value", "footprint", "mpn")
            )):
                errors.append(f"{label}: BOM identity differs from netlist")
            if row and bool(row["excluded"]) == record["in_bom"]:
                errors.append(f"{label}: BOM exclusion differs from netlist")
            if row and bool(row["dnp"]) != record["dnp"]:
                errors.append(f"{label}: BOM DNP differs from netlist")
            if record["in_bom"] and not record["dnp"]:
                eligible[ref] = record
            if record["on_board"] != (fp is not None):
                errors.append(f"{label}: schematic on-board flag differs from PCB presence")
        if fp is None:
            continue
        attr = atoms(fp, "attr")
        path = atoms(fp, "path")
        record["pcb"] = {"footprint": value(fp[1]), "path": path, "attributes": attr,
                         "at": atoms(fp, "at"), "layer": atoms(fp, "layer"), "pads": []}
        if symbol is not None:
            if value(fp[1]) != record["footprint"]:
                errors.append(f"{label}: footprint mismatch")
            if len(path) != 1 or path[0] not in record["paths"]:
                errors.append(f"{label}: UUID path mismatch")
            if ("exclude_from_bom" not in attr) != record["in_bom"]:
                errors.append(f"{label}: PCB BOM exclusion mismatch")
            if ("dnp" in attr) != record["dnp"]:
                errors.append(f"{label}: PCB DNP mismatch")
        pad_numbers = set()
        for pad in kids(fp, "pad"):
            number, kind, shape = map(value, pad[1:4])
            net = atoms(pad, "net")
            actual = net[-1] if net else None
            geometry = {value(entry[0]): entry[1:] for entry in pad[4:]
                        if isinstance(entry, list) and entry[0] not in ("uuid", "net")}
            record["pcb"]["pads"].append([number, kind, shape, actual, geometry])
            if kind == "np_thru_hole" or not number:
                if unc(actual):
                    errors.append(f"{label}/{number}: mechanical pad carries {actual}")
                continue
            pad_numbers.add(number)
            if symbol is not None and number not in record["symbol_pins"] and number not in pins[ref]:
                errors.append(f"{label}/{number}: no matching schematic pin")
            if symbol is not None and unc(pins[ref].get(number)) != unc(actual):
                errors.append(f"{label}/{number}: schematic net {pins[ref].get(number)!r}, PCB net {actual!r}")
        expected_pads = set(record.get("symbol_pins", [])) | pins.get(ref, {}).keys()
        for number in sorted(expected_pads - pad_numbers):
            errors.append(f"{label}/{number}: no numbered PCB pad")
    return all_refs, extras, eligible


def category(ref):
    if ref.startswith(("R", "C", "L")):
        return "passive"
    if ref.startswith(("D", "U", "Q")):
        return "semiconductor"
    if ref.startswith("J"):
        return "connector"
    return "other"


def calculate(policy, eligible, rows, errors):
    register = unique((((r["board"], r["ref"]), r) for r in rows), "register", errors)
    for key in sorted(eligible.keys() ^ register.keys()):
        errors.append(f"{'/'.join(key)}: register coverage mismatch")
    if set(policy["builds"]) != set(BOARDS) or any(
        type(n) is not int or n <= 0 for n in policy["builds"].values()
    ):
        raise ValueError("Build policy must contain positive integer quantities for all boards")
    dispositions = {}
    for status in ("omit", "owned"):
        for board, refs in policy[status].items():
            for ref in refs:
                key = board, ref
                if key not in eligible or key in dispositions:
                    errors.append(f"{board}/{ref}: invalid or repeated {status} policy entry")
                dispositions[key] = status
    slots = {ref for (board, ref), item in eligible.items()
             if board == "pico-carrier" and item["footprint"] == "Interfaces:Sullins_EBC06DCWN_Socket_2x06_P2.54mm_Vertical"
             and dispositions.get((board, ref), "buy") != "omit"}
    if len(slots) != policy["carrier_slots"]:
        errors.append("Carrier socket population differs from policy")
    if policy["builds"]["string-daughterboard"] > len(slots) * policy["builds"]["pico-carrier"] and slots:
        errors.append("Daughtercard count exceeds fitted sockets")
    quantities = {}
    for board, ref in sorted(eligible.keys() & register.keys()):
        item, row = eligible[board, ref], register[board, ref]
        disposition = dispositions.get((board, ref), "buy")
        for field in ("value", "footprint", "source"):
            if item[field] != row[field]:
                errors.append(f"{board}/{ref}: register {field} mismatch")
        if item["mpn"] and item["mpn"] != row["mpn"]:
            errors.append(f"{board}/{ref}: register MPN mismatch")
        if disposition != row["disposition"]:
            errors.append(f"{board}/{ref}: register disposition mismatch")
        if disposition != "buy":
            continue
        mpn = row["mpn"].strip()
        if not mpn:
            errors.append(f"{board}/{ref}: missing candidate MPN")
            continue
        part = quantities.setdefault(mpn, {"fitted": 0, "category": category(ref), "references": {}})
        if part["category"] != category(ref):
            errors.append(f"{mpn}: conflicting spare categories")
        count = policy["builds"][board]
        part["references"][f"{board}/{ref}"] = count
        part["fitted"] += count
    for part in quantities.values():
        spare = policy["spares"][part["category"]]
        if type(spare) is not int or spare < 0:
            raise ValueError("Spare quantities must be nonnegative integers")
        part["spares"] = spare
        part["required"] = part["fitted"] + spare
    return quantities, sorted(slots)


def manufacturer_blockers(required, rows, design_commit):
    blockers = []
    evidence = unique(((r["mpn"], r) for r in rows), "evidence register", blockers)
    for mpn in sorted(required):
        row = evidence.get(mpn, {})
        missing = [field for field in ("electrical", "mechanical", "mating")
                   if row.get(field) not in ("verified", "n/a")
                   or (row.get(field) == "n/a" and not row.get(field + "_rationale", "").strip())]
        if (missing or row.get("design_commit") != design_commit
                or not all(row.get(k, "").strip() for k in (
                    "manufacturer", "primary_evidence", "revision", "locator", "reviewer", "notes"
                ))):
            blockers.append(f"{mpn}: manufacturer evidence incomplete" +
                            (f" ({', '.join(missing)})" if missing else ""))
    return blockers


def supplier_plan(required, rows, design_commit):
    blockers = []
    orders = {}
    evidence = unique(((r["mpn"], r) for r in rows), "supplier evidence", blockers)
    seen_skus = set()
    for mpn, quantity in sorted(required.items()):
        row = evidence.get(mpn, {})
        if (row.get("distributor") != "verified" or row.get("design_commit") != design_commit
                or not all(row.get(k, "").strip() for k in (
                    "supplier", "sku", "packaging", "price", "supplier_evidence", "reviewer",
                    "supplier_checked_on"
                ))):
            blockers.append(f"{mpn}: supplier evidence incomplete")
            continue
        sku = row["supplier"].strip().casefold(), row["sku"].strip().casefold()
        if sku in seen_skus:
            blockers.append(f"{mpn}: duplicate supplier SKU")
        seen_skus.add(sku)
        try:
            date.fromisoformat(row["supplier_checked_on"])
            pack, stock = int(row["pack_size"]), int(row["stock_units"])
            if pack <= 0 or stock < 0:
                raise ValueError
        except (KeyError, ValueError):
            blockers.append(f"{mpn}: invalid supplier check date, pack size or stock")
            continue
        units = ((quantity + pack - 1) // pack) * pack
        if stock < units:
            blockers.append(f"{mpn}: stock below rounded demand")
            continue
        orders[mpn] = {"supplier": row["supplier"], "sku": row["sku"],
                       "packs": units // pack, "units": units}
    return orders, blockers


def harness_quantities(policy, errors):
    harness = policy["power_harness"]
    candidates = harness["lead_candidates"]
    lengths = harness["lengths_mm"]
    if len(candidates) != 2 * len(lengths) or len(set(candidates)) != len(candidates):
        errors.append("Harness policy requires distinct red and black candidates per length")
    demand = {harness["housing_mpn"]: harness["housing_quantity"],
              **policy["peripheral_harness_candidates"]}
    leads = []
    for index, mpn in enumerate(candidates[:2 * len(lengths)]):
        color = ("red", "black")[index % 2]
        count = harness[f"{color}_per_length"]
        if mpn in demand:
            errors.append(f"{mpn}: repeated harness candidate")
        demand[mpn] = count
        leads.append({"mpn": mpn, "color": color, "length_mm": lengths[index // 2], "quantity": count})
    return demand, leads


def run(args):
    try:
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    except FileNotFoundError as exc:
        return {"exit": 127, "output": str(exc)}
    message = "\n".join(s.strip() for s in (result.stdout, result.stderr) if s.strip())
    # KiCad DRC console output can contain progress sequences.
    return {"exit": result.returncode, "output": message}


def rules_summary(result, output):
    if output.exists():
        report = json.loads(output.read_text())
        result["findings"] = {}
        for section in ("violations", "unconnected_items", "schematic_parity", "sheets"):
            entries = report.get(section, [])
            if section == "sheets":
                entries = [v for sheet in entries for v in sheet["violations"]]
            if entries:
                result.setdefault("details", {})[section] = [
                    [v["type"], v["description"], v.get("excluded", False),
                     [[i["description"], i.get("uuid"), i.get("pos")] for i in v.get("items", [])]]
                    for v in entries
                ]
                result["findings"][section] = dict(sorted(Counter(
                    f"{v.get('severity', '')}/{v.get('type', '')}" +
                    ("/excluded" if v.get("excluded") else "") for v in entries
                ).items()))
    return result


def input_manifest():
    candidates = git("ls-files", "--", *BOARDS, "shared", "HeadUnit.pretty", "HeadUnit.kicad_sym").splitlines()
    design = [name for name in candidates if "/manufacturing/" not in name and (
        Path(name).suffix in {".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_dru",
                              ".kicad_sym", ".kicad_mod"} or name.endswith("-lib-table")
        or name.startswith("shared/interfaces/")
    )]
    design_commit = git("log", "-1", "--format=%H", "--", *design)
    files = design + [
        "procurement/policy.json", "procurement/component-register.csv",
        "procurement/verification-register.csv", "procurement/validation/environment.json",
        "shared/tools/validate_procurement.py", "shared/tools/test_validate_procurement.py",
        "shared/tools/check_interfaces.py", "shared/tools/check_power_interface.py",
    ]
    clean = not git("status", "--porcelain", "--", *design)
    return design_commit, clean, {name: digest(ROOT / name) for name in sorted(files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--exports", type=Path, help="Directory for full native exports and rule reports")
    args = parser.parse_args()
    policy = json.loads((P / "policy.json").read_text())
    design_commit, clean, manifest = input_manifest()
    errors = []
    if not clean or design_commit != policy["baseline"]:
        errors.append("Design differs from the committed policy baseline")
    checks, inventory, eligible = {}, {}, {}
    cli = "kicad-cli"
    version = run([cli, "version"])
    if version["exit"] or not version["output"].startswith("10."):
        errors.append("KiCad 10 CLI is required for this design and the native audit")
    with tempfile.TemporaryDirectory(prefix="procurement-") as temp:
        output = (args.exports or Path(temp)).resolve()
        output.mkdir(parents=True, exist_ok=True)
        for board in BOARDS:
            base = f"{board}/{board}"
            xml = output / f"{board}.xml"
            bom = output / f"{board}.csv"
            erc = output / f"{board}-erc.json"
            drc = output / f"{board}-drc.json"
            for artifact in (xml, bom, erc, drc):
                artifact.unlink(missing_ok=True)
            commands = {
                "netlist": [cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(xml), base + ".kicad_sch"],
                "bom": [cli, "sch", "export", "bom", "--fields",
                        "Reference,Value,Footprint,MPN,${DNP},${EXCLUDE_FROM_BOM}",
                        "--labels", "ref,value,footprint,mpn,dnp,excluded", "-o", str(bom), base + ".kicad_sch"],
                "erc": [cli, "sch", "erc", "--format", "json", "--severity-all",
                        "--exit-code-violations", "-o", str(erc), base + ".kicad_sch"],
                "drc": [cli, "pcb", "drc", "--format", "json", "--severity-all",
                        "--schematic-parity", "--exit-code-violations", "-o", str(drc), base + ".kicad_pcb"],
            }
            board_checks = checks[board] = {name: run(cmd) for name, cmd in commands.items()}
            for name, result in board_checks.items():
                result["output"] = result["output"].replace(str(output), "<exports>")
                if result["exit"]:
                    errors.append(f"{board}: {name} exited {result['exit']}")
            for name, artifact in (("erc", erc), ("drc", drc)):
                rules_summary(board_checks[name], artifact)
                if not artifact.exists():
                    errors.append(f"{board}: {name} report missing")
            if xml.exists() and bom.exists() and not any(board_checks[k]["exit"] for k in ("netlist", "bom")):
                refs, extras, parts = inspect_board(board, xml, bom, errors)
                inventory[board] = {"references": refs, "board_only": extras}
                eligible.update({(board, ref): part for ref, part in parts.items()})
            else:
                errors.append(f"{board}: native inventory unavailable")
    for checker in ("check_interfaces.py", "check_power_interface.py"):
        checks[checker] = run([sys.executable, f"shared/tools/{checker}"])
        if checks[checker]["exit"]:
            errors.append(f"{checker}: exited {checks[checker]['exit']}")
    quantities, slots = calculate(policy, eligible, read_csv(P / "component-register.csv"), errors)
    harness, leads = harness_quantities(policy, errors)
    required = Counter({mpn: part["required"] for mpn, part in quantities.items()})
    required.update(harness)
    evidence = read_csv(P / "verification-register.csv")
    orders, supplier_blockers = supplier_plan(required, evidence, design_commit)
    blockers = manufacturer_blockers(required, evidence, design_commit) + supplier_blockers
    for review in sorted(SYSTEM_REVIEWS):
        evidence = policy["system_reviews"].get(review, {})
        if (evidence.get("design_commit") != design_commit or
                not all(evidence.get(k) for k in ("source", "reviewer", "conclusion")) or
                evidence.get("status") != "verified"):
            blockers.append(f"{review}: system evidence incomplete")
    report = {
        "schema": 1, "design_commit": design_commit, "sha256": manifest,
        "tools": {"kicad": version, "python": platform.python_version(),
                  "git": git("--version"), "architecture": platform.machine()},
        "checks": checks, "discrepancies": sorted(errors), "evidence_blockers": sorted(blockers),
        "builds": policy["builds"], "carrier_sockets": slots,
        "unoccupied_card_positions": (len(slots) * policy["builds"]["pico-carrier"]
                                      - policy["builds"]["string-daughterboard"]),
        "pcb_demand": quantities, "harness_demand": harness, "lead_candidates": leads,
        "amazon_candidate": policy["amazon"],
        "release": "blocked" if errors or blockers else "ready_for_review",
        "inventory": inventory,
    }
    if not errors and not blockers:
        report["supplier_plan"] = orders
    if args.report:
        args.report.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n")
    for issue in sorted(errors + blockers):
        print(issue)
    print(f"{report['release']}: {len(errors)} discrepancies, {len(blockers)} evidence blockers")
    return int(bool(errors or blockers))


if __name__ == "__main__":
    raise SystemExit(main())
