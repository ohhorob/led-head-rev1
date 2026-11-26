#!/usr/bin/env python3
"""Read-only procurement audit. Never emits approved orders.
Run from repository: python3 shared/tools/validate_procurement.py
"""
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path
from check_interfaces import parse, kids, kid, value

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "procurement"

def props(node):
    return {value(p[1]): value(p[2]) for p in kids(node, "property")}

def flag(node, name, default):
    x = kid(node, name)
    return value(x[1]) if x else default

def unique(items, label, errors):
    result = {}
    for ref, record in items:
        if ref in result:
            errors.append(f"{label}: duplicate {ref}")
        result[ref] = record
    return result

def audit():
    policy = json.loads((P / "policy.json").read_text())
    with (P / "component-register.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    errors = []
    register = unique([((r["board"], r["ref"]), r) for r in rows], "register", errors)
    counts = Counter()
    for board, quantity in policy["builds"].items():
        folder = ROOT / board
        sch_items = []
        pcb_items = []
        for path in sorted(folder.glob("*.kicad_sch")):
            for symbol in kids(parse(path.read_text()), "symbol"):
                p = props(symbol)
                ref = p.get("Reference", "")
                if not ref or ref.startswith("#") or not p.get("Footprint"):
                    continue
                sch_items.append((ref, (p, flag(symbol, "in_bom", "yes"), flag(symbol, "dnp", "no"))))
        for fp in kids(parse((folder / (board + ".kicad_pcb")).read_text()), "footprint"):
            p = props(fp)
            ref = p.get("Reference", "")
            if not ref:
                errors.append(f"{board}: PCB footprint missing reference")
            pcb_items.append((ref, value(fp[1])))
        sch = unique(sch_items, board + " schematic", errors)
        pcb = unique(pcb_items, board + " PCB", errors)
        for ref in sorted(set(sch) ^ set(pcb)):
            errors.append(f"{board}/{ref}: reference only in one design document")
        for ref in sorted(set(sch) & set(pcb)):
            if sch[ref][0]["Footprint"] != pcb[ref]:
                errors.append(f"{board}/{ref}: footprint mismatch")
        eligible = {ref for ref, (p, bom, dnp) in sch.items() if bom != "no" and dnp != "yes"}
        expected = {ref for b, ref in register if b == board}
        for ref in sorted(eligible ^ expected):
            errors.append(f"{board}/{ref}: register coverage mismatch")
        for ref in sorted(eligible & expected):
            r = register[board, ref]
            p = sch[ref][0]
            for field, key in [("value", "Value"), ("footprint", "Footprint")]:
                if r[field] != p.get(key):
                    errors.append(f"{board}/{ref}: changed {key}")
            if p.get("MPN") and r["mpn"] != p["MPN"]:
                errors.append(f"{board}/{ref}: changed MPN")
            disposition = ("omit" if ref in policy["omit"].get(board, []) else
                           "owned" if ref in policy["owned"].get(board, []) else "buy")
            if r["disposition"] != disposition:
                errors.append(f"{board}/{ref}: policy disposition mismatch")
            if disposition == "buy":
                if not r["mpn"]:
                    errors.append(f"{board}/{ref}: missing candidate MPN")
                else:
                    counts[r["mpn"]] += quantity
        print(f"{board}: {len(eligible)} BOM references, {len(pcb)} PCB footprints")
    print("Candidate PCB quantities (before spares, not order approval):")
    for mpn, count in sorted(counts.items()):
        print(f"{mpn}: {count}")
    print("BLOCKED: independent electrical, mechanical, harness and supplier evidence and native KiCad parity not yet approved.")
    if errors:
        print("\n".join(errors))
    return 1

if __name__ == "__main__":
    raise SystemExit(audit())
