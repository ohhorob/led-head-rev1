# Procurement verification (draft, not order authorization)

Baseline: 265531fab44996e0d69467f4a7c851bf6b56fe77.

Use policy.json and component-register.csv. The latter is an independently parsed snapshot of top-level symbols across the six committed schematic files, not proof of PCB parity or electrical suitability. Candidate MPNs absent from schematic fields were carried from the historical sourcing list or proposed explicitly (C0603C104K5RACTU). All require independent confirmation.

Run locally:
`python3 shared/tools/validate_procurement.py`
This initial validator checks reference coverage, duplicate references, footprint IDs, schematic values, explicit MPN fields and policy dispositions. It always exits nonzero: it does NOT yet implement a release gate or supplier exports. Native KiCad hierarchy/netlist, UUID parity, ERC/DRC and actual footprint pad geometry require separate verification. No orders are authorized. Do not use historical 2026-11-23 imports as current.

## Evidence requirements
For every exact MPN record manufacturer, revision/date, source URL, relevant page/table, measured/required specification, conclusion and reviewer. Check electrical ratings, tolerances, pin mapping, pad geometry, orientation and assembly requirements as applicable. Record N/A with reason. Distributor SKU, stock, packaging, quantity and price must be checked separately. Repeat when design files or part selection change.

## Initial evidence (partial)
- Molex 215340: https://www.molex.com/en-us/products/series-chart/215340 — series includes female-female tin 16 AWG leads, 75 mm example 2153401121. Verify all six exact suffixes, housing compatibility, loaded current/temperature and stock before ordering.
- JST XH: https://www.jst-mfg.com/product/index.php?lang=2&series=277 — genuine XH rated 3 A using 22 AWG. Existing Adafruit 4423 kit is not independently proven equivalent; check markings, quantity, crimp wire and insulation range, fit and heating under load.
- Wurth LED: https://www.we-online.com/components/products/datasheet/1312020030000.pdf — source identified, full review pending.
- AMASS Amazon ASIN B09XTN9N9S: user-selected candidate; seller authenticity, exact male PCB geometry and rating pending.
- Harness additions: 5 Mini-Fit housing candidates 0039012100, 6 red and 6 black leads per length (75/150/300 mm), PHR-4 and PHR-6 two each, SPH-002T-P0.5S 20 candidate contacts; verify exact mating and application wire size. XH kit owned, no loose Molex contacts/crimper required. External source XT60 mating cable, wire stock, protection and peripheral cable needs remain to be checked.

## Open release blockers
1. Run local audit and native KiCad parity on current checkout, including any uncommitted changes. Remote PCB retrieval was limited.
2. Independently verify all PCB and harness candidate MPNs from primary sources; verification-register.csv intentionally remains pending.
3. Resolve real current capacity of 10-position power harness, PCB feed, source protection and string connectors; do not multiply single-contact ratings. Check 6-string load and future 8-string load separately.
4. Verify card edge mating and status chain continuity with six installed cards.
5. Confirm actual inventory and appropriate soldering/reflow capability.
6. Implement/test evidence-driven release gate and supplier CSV generator with spares, pack rounding, duplicate-order checks and design revision binding. Refresh exact supplier SKUs and availability.
7. Review and approve any substitutions explicitly. Do not modify PCB design in procurement branch.

Historical documentation has stale sections; current committed schematic/PCB and primary evidence take precedence. No PCB files modified.
