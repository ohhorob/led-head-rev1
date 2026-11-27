# Procurement verification (draft, not order authorization)

Baseline: 265531fab44996e0d69467f4a7c851bf6b56fe77.

The current audit covers one Pico carrier, one power manager and six daughtercards. Fit all eight sockets (J21–J28), leaving two unoccupied card positions. The November 23 sourcing and imports remain historical.

Run with KiCad 10 on PATH and its standard symbol and footprint library tables initialized.

```sh
python3 -m unittest discover -s shared/tools -p 'test_validate_procurement.py' -v
python3 shared/tools/validate_procurement.py \
  --report procurement/validation/audit.json --exports /tmp/led-head-kicad-exports
```

The audit exits 1 when checks or evidence block release. The report captures input SHA-256 hashes, tool versions, each rule command's exit and findings, the native component and pin inventory, PCB land patterns, candidate quantities and evidence blockers. The optional exports directory contains the native XML netlist, BOM CSV and JSON ERC/DRC for each board. The KiCad BOM includes DNP rows if present, and KiCad 10 omits BOM-excluded rows. The full component inventory uses native XML to account for the excluded references.

## Results

| Board | Native BOM rows | Schematic components | PCB footprints | ERC | DRC with schematic parity |
| --- | ---: | ---: | ---: | --- | --- |
| Pico carrier | 39 | 47 | 49 | 0 findings | 1 parity warning |
| Power manager | 11 | 15 | 18 | 0 findings | 2 parity warnings, 5 silkscreen warnings, 1 excluded footprint warning |
| String daughterboard | 9 | 10 | 11 | 0 findings | 0 findings |

All linked footprints match native schematic references, UUID paths, footprint IDs, pin nets, BOM exclusions and DNP flags. Carrier H1–H8, power manager TP1–TP4 and daughtercard J1 are schematic BOM exclusions. No DNP flags are set. Two carrier PCB graphics, three power-manager graphics and daughtercard QR1 are unlinked. The carrier and power manager each have an unlinked KiCad logo missing the board-only flag. Native DRC also flags duplicate `REF**` footprints on the power manager. The excluded library mismatch concerns power-manager J5 (Molex 0039300100). The basic pad numbers, local XY, sizes and drills match its current library footprint after accounting for the 180° placement. Review the full footprint difference and independently verify the manufacturer drawing.

The power interface checker passed, including the reserved J20 telemetry pinout. The string interface checker failed. All eight carrier B3 GPIO assignments and six PAC1934 sense pins per monitor differ from the contract in both schematic and PCB. Carrier A5/B5 nets form a series chain from J21 through J28, so an empty upstream socket interrupts the path to downstream cards. Keep the six-card installation and status continuity as an explicit review item.

An independent count from the three native BOM CSVs gives 30 candidate purchases on the carrier (after 8 owned and 1 omitted), 11 on the power manager, and 9 per daughtercard × 6 = 54. This is 95 fitted candidate units across 28 MPNs, plus 47 policy spares for 142 PCB candidate units. The eight carrier sockets contribute 8 fitted units plus 1 spare. The harness plan separately includes 5 housings, 36 leads, 4 peripheral housings and 20 peripheral contacts. The Amazon XT60 listing is a source candidate for the same PCB MPN.

## Environment

Ubuntu 26.04.1 arm64 supplied KiCad 9.0.8, which failed to open the KiCad 10 native files. The audit used KiCad 10.0.8 and its matching symbol and footprint libraries from the KiCad release PPA. The downloaded arm64 runtime dependencies and package hashes are recorded in [environment.json](validation/environment.json).

For a temporary install, extract the recorded packages with `dpkg-deb -x PACKAGE PREFIX`. Add `PREFIX/usr/lib/aarch64-linux-gnu` and `PREFIX/usr/lib` to `LD_LIBRARY_PATH`. Set `KICAD10_FOOTPRINT_DIR`, `KICAD10_SYMBOL_DIR` and `KICAD10_TEMPLATE_DIR` to the corresponding directories under `PREFIX/usr/share/kicad`. Use writable XDG config, cache and data directories, and copy the package's default `fp-lib-table` and `sym-lib-table` from the template directory into `$XDG_CONFIG_HOME/kicad/10.0`. Put `PREFIX/usr/bin` on PATH or use a wrapper with those exports. Python uses only the standard library.

The original validator exited 1. It detected repeated `REF**` entries and treated unlinked graphics as reference mismatches. The native report records graphics individually by UUID and retains KiCad's own parity findings.

## Evidence requirements
For every exact MPN record manufacturer, revision/date, source URL, relevant page/table, measured/required specification, conclusion and reviewer. Check electrical ratings, tolerances, pin mapping, pad geometry, orientation and assembly requirements as applicable. Record N/A with reason. Distributor SKU, stock, packaging, quantity and price must be checked separately. Repeat when design files or part selection change.

## Initial evidence (partial)
- Molex 215340: https://www.molex.com/en-us/products/series-chart/215340 — series includes female-female tin 16 AWG leads, 75 mm example 2153401121. Verify all six exact suffixes, housing compatibility, loaded current/temperature and stock before ordering.
- JST XH: https://www.jst-mfg.com/product/index.php?lang=2&series=277 — genuine XH rated 3 A using 22 AWG. Existing Adafruit 4423 kit is not independently proven equivalent; check markings, quantity, crimp wire and insulation range, fit and heating under load.
- Wurth LED: https://www.we-online.com/components/products/datasheet/1312020030000.pdf — source identified, full review pending.
- AMASS Amazon ASIN B09XTN9N9S: user-selected candidate; seller authenticity, exact male PCB geometry and rating pending.
- Harness additions: 5 Mini-Fit housing candidates 0039012100, 6 red and 6 black leads per length (75/150/300 mm), PHR-4 and PHR-6 two each, SPH-002T-P0.5S 20 candidate contacts; verify exact mating and application wire size. XH kit owned, no loose Molex contacts/crimper required. External source XT60 mating cable, wire stock, protection and peripheral cable needs remain to be checked.

## Release gate

For each required MPN, record manufacturer, drawing revision, location in the source, reviewer, measured and required specifications, conclusion and the matching design commit. Set each manufacturer check to `verified` or `n/a` with its own rationale. Record supplier, exact SKU, packaging, price with currency, source, verification date, pack size and available stock in units before setting `distributor` to `verified`.

The quantity plan aggregates fitted references by exact MPN, applies one spare allowance per PCB MPN, adds separately specified harness candidates and rounds verified supplier demand up to whole packs. Supplier SKU collisions and stock below rounded demand block release. Individual harness lead colors are policy candidates in alternating red/black order for the listed lengths and still need primary-source confirmation.

Independent system reviews in policy.json cover power and protection, six-card status continuity, inventory and assembly, XT60 authenticity and source cable, and harness and peripheral coverage. Each requires a reviewer, evidence source, conclusion and matching design commit. The report only includes a supplier plan when all checks and evidence pass. The resulting status is `ready_for_review`. The current report is `blocked`.
