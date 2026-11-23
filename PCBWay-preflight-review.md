# PCBWay pre-production review

Reviewed against the saved PCB and the actual PCBWay order W369080AS1C2 / T-1C3W369080A.
No board edits, quote changes, uploads or messages were made in this review.

## Selected specification

100 x 73 mm, 4 layers, 1.6 mm FR-4 S1000H TG150, 1 oz finished outer copper and 1 oz inner copper, green mask, white silk, ENIG 1 microinch, tented vias, 0.3 mm minimum drill, declared 4/4 mil minimum track/space. Five boards manufactured, two top-side SMT assembled. Single-piece fabrication is selected. Removal of PCBWay product number is NOT selected.

## Checks completed on saved PCB

- Refilled zones in memory and ran KiCad DRC with schematic parity and all severities, without saving board changes: 0 violations, 0 unconnected items, 0 parity issues.
- Minimum routed track width: 0.20 mm.
- Via drills: 0.30 and 0.40 mm. Via diameters: 0.55 to 0.85 mm.
- All 104 vias marked tented on front and back.
- Visible silkscreen text: minimum 0.80 mm height and 0.15 mm stroke. This is at PCBWay's published lower limit for some text, not a readability guarantee.
- Six fiducials, each 1.0 mm diameter with 2.0 mm mask opening.

## Items still requiring resolution or written manufacturer acceptance

1. Via-to-pad ring clearance: hole clearance alone is insufficient. PCBWay's BGA layout guidance recommends 0.075-0.10 mm between via copper-ring edge and SMT pad edge. Conservative target for this review is at least 0.10 mm. Nine pads are below it:

| Pad | Copper-edge clearance (mm) |
|---|---:|
| C40.2 | 0.0580 |
| C54.2 | 0.0205 |
| F1.1, two vias | 0.0049 each |
| F2.1, two vias | 0.0097 each |
| F3.1, two vias | 0.0413 / 0.0491 |
| R1.2 | -0.0250 (copper overlap) |
| R44.2 | approximately 0.0000 (tangent) |
| U6.4 | 0.0570 |

This is manufacturer guidance applied conservatively to this non-BGA design, not a newly established binding order requirement. Confirm actual solder-mask separation and assembly acceptance with PCBWay. Tenting does not guarantee a separation where a component mask aperture exposes the via region.

2. U5 eFuse mask and stencil: several copper-pad gaps are nominally 0.20 mm, at PCBWay's published green-mask IC-pad-spacing threshold. U5 mask expansion currently resolves to zero. Have CAM/assembly review the exact RPW footprint and stencil apertures, including the two long power pads and corner contacts. Do not blindly apply a global mask expansion or change the manufacturer's land pattern to create mask bridges.

3. Rails/panel/tooling: selected Single pieces, with a notched outline and SMT close to the perimeter. PCBWay guidance calls for process rails when components approach edges and for odd-shaped boards. Ask them to propose temporary rails/tooling and a removal method that preserves final outline and connector overhang. Existing 1 mm fiducials are useful, but FID1, FID2 and FID4 are closer to the board edge than their 5 mm fiducial-edge guidance. Rail fiducials may resolve this without moving board components.

4. Confirm final 1 oz stackup, copper order, and CAM trace/spacing acceptance rather than relying only on the quote's general 4/4 mil selection. Published detailed process tables depend on copper thickness and process category.

5. Before release, regenerate Gerbers, drills, paste, placement data and assembly drawing from ONE final saved board. Current uploaded files predate the via moves and remain stale. Verify all 71 SMT designators are present exactly once in the placement file and expanded grouped BOM. Confirm PCBWay uses the revised grouped BOM rather than the old cart attachment.

6. Review placement/polarity preview for U4, U5, U1-U3/U8, D1-D9, Q1/Q2 and J13. Confirm exact LED part/pinout and any proposed substitutions before procurement. Confirm top-only SMT; all through-hole parts and modules remain customer-installed.

7. Confirm solder alloy/reflow and QFN inspection with assembly. No functional test or firmware programming was ordered. Bare-board electrical test checks opens/shorts, not the design's power-source selection, fault indication, current sensing or loaded thermal performance.

8. Final mechanical and power review: connector pin order and access, Pico USB and antenna clearance, Pololu standoff/socket heights, mounting-hole tolerances, and power-path/via/return bottlenecks. These remain design checks and later prototype tests; a clean DRC does not establish functional or thermal performance.

## References

- PCBWay capabilities: https://www.pcbway.com/capabilities.html
- Assembly guide: https://www.pcbway.com/smt_ordering_guide.html
- Assembly file requirements: https://www.pcbway.com/assembly-file-requirements.html
- Solder-mask bridges: https://www.pcbway.com/helpcenter/soldermask_issues/Soldermask_bridge.html
- Via-to-pad guidance: https://www.pcbway.com/blog/14/BGA_PCB_Layout_Guidelines_Placement_Fanout_and_Routing_b8eeabdd.html
- Panel/rail/fiducial guidance: https://www.pcbway.com/helpcenter/design_instruction/PCB_Panelization__Breakaway_Rails__Fiducial_Marks__Tooling_Holes.html
- Assembly capabilities and testing: https://www.pcbway.com/assembly-capabilities.html
- Independent pre-manufacture checklist: https://labcit.ligo.caltech.edu/~abbott/files/E060231-05.pdf (search-index text available; direct retrieval failed during review)
