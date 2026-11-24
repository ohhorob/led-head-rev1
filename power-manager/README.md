# Dedicated 5 V power module

Open **power-manager.kicad_pro** through KiCad Project Manager. This project now contains the simple dedicated-supply board: one regulated-5-V XT60 input, a 3.3 V buck converter and the carrier's ten-pin Mini-Fit output. The single-page schematic is complete, and the PCB contains **14 linked footprints in a staging grid**. Place the parts, draw the outline and route the board manually.

[View the schematic](preview/power-manager-schematic.pdf). Component selections are in [parts.csv](parts.csv).

The abandoned combined battery/external-input design is archived at `../.history/power-manager-combined-before-dedicated-5v-20261121.zip`. It is not an active alternative project. The battery power module is deferred and will be a separate interchangeable module.

## Circuit and connectors

J1 is the existing right-angle **AMASS XT60PW-M**. Footprint pin 1 is GND and pin 2 is positive. It accepts a correctly polarized, externally regulated **5 V supply only**. IN_5V goes directly to the carrier power output and to the buck input. Use source-side wiring protection appropriate to the harness and load.

J5 is **Molex 0039281103**, matching carrier J19. A straight-through harness uses 0039012100 housings and 0039000039 female contacts. The exact 3D model remains attached to the local footprint. Main conductors were previously selected as 18 AWG across parallel contacts; verify current sharing, complete connector derating and loaded temperature before fabrication.

| J5 pin | Net |
| --- | --- |
| 1–4 | IN_5V, parallel 5 V contacts |
| 5 | PERIPH_3V3, independent peripheral regulator output |
| 6–10 | GND, parallel returns |

PERIPH_3V3 must remain separate from the Pico's 3V3(OUT). This module needs only the ten-pin cable to the carrier; it has no battery telemetry connector. Carrier J20 remains reserved for a future battery module and is not connected to this board.

D1/R2 provide a simple green 5 V power indicator. TP1, TP2 and TP3 are standard 2.54 mm signal/GND pairs for 5 V, peripheral 3.3 V and converter power-good respectively. PG is an open-drain signal with the WEBENCH 499k pull-up; use a high-impedance probe.

## WEBENCH circuit

Source: `reference/webench/WBDesign2_AltiumDesigner.zip`, WEBENCH design 2, ID 18973430, exported 2026-11-21. Its circuit is 5 V input to 3.3 V at a **2 A design target**. TPS62091 itself belongs to a 3 A family; this board has not been thermally qualified at 3 A.

| Original WEBENCH reference | KiCad reference | Value / function |
| --- | --- | --- |
| U1 | U1 | TPS62091RGTR, fixed 3.3 V |
| L1 | L1 | 1 µH, Würth 74439346010 |
| Cin | C1 | 22 µF, input |
| Cout | C2 | 22 µF, output |
| Ccp | C3 | 10 nF, flying capacitor between CP and CN |
| Css | C4 | 3.9 nF, soft-start |
| Rpg | R1 | 499 kΩ, PG pull-up to the 3.3 V output |

EN and FREQ are tied to IN_5V, reproducing always-enabled **1.4 MHz** operation. VOS senses the output after L1. FB is grounded, as permitted for the fixed-output TPS62091. Pins 14/15 connect to power ground; pin 6 and exposed pad 17 connect to analog ground, with all grounds common on this schematic.

The export contains misleading generic library fields: U1's package reference and simulation title identify TPS62091, but its manufacturer-number field says TPS62090. TI's device comparison table confirms that **TPS62091 is the fixed 3.3 V part**, while TPS62090 is adjustable. The KiCad circuit/BOM use TPS62091RGTR. Likewise, the export labels L1 GENERIC_INDUCTOR in some fields, but its package reference identifies 74439346010; that is the selected real part.

## Packages and footprints

- **U1:** 3 × 3 mm QFN16, 0.5 mm pitch. Local footprint follows TI **RGT0016C**: perimeter copper 0.60 × 0.24 mm, opposing pad-centre spacing 2.80 mm, exposed pad 1.68 × 1.68 mm. The centre paste aperture is 1.55 × 1.55 mm. There are no vias in the pad. The exposed pad must be soldered; hot-air/reflow assembly is appropriate.
- **L1:** stock `Inductor_SMD:L_Wuerth_XHMI-6060`, checked against the Würth land pattern. Pads are 1.45 × 5.50 mm, centred 4.00 mm apart (2.55 mm inner gap). The Altium export's generic inductor pad pattern is not used: it does not fit the real selected part.
- **C1/C2:** 1206 Samsung CL31A226KAHNNNE, 22 µF, 25 V, X5R. They replace the export's 0603/6.3 V parts while retaining nominal capacitance. Confirm effective capacitance over bias, tolerance and temperature before release; TI's capacitor guidance includes DC-bias derating.
- **C3/C4 and R1/R2:** 0805, replacing the export's smaller 0402/0201 packages where applicable. Values are unchanged. C3 is 10 nF KEMET C0805C103K5RACTU; C4 is 3.9 nF C0G KEMET C0805C392J5GACTU.
- **Connectors/probes:** through-hole. The green indicator is 0805.

The nominal electrical design is preserved, but changing physical parts/packages is not a reproduction of WEBENCH's simulated parasitics or a new simulation. Validate startup, output ripple, load transients and temperature on the assembled board.

## Placement and routing priorities

The capacitors are drawn directly at the pins they serve and contain Placement fields.

1. Put **C1 immediately beside PVIN pins 11/12 and PGND pins 14/15**. Minimize the input switching-current loop.
2. Put **L1 close to SW pins 1/2**. Keep SW copper compact. Würth specifies no vias or sensitive traces underneath the inductor.
3. Put **C2 at the output side of L1**. Route VOS pin 16 as a quiet sense trace to this output node, away from SW and the inductor.
4. Put **C3 directly between CP pin 7 and CN pin 8**. Neither end goes to ground. Put C4 next to SS pin 9 and quiet AGND.
5. Solder EP17 to an adequate ground heat-spreading region. Join analog and power returns near the IC; keep the LED-string return trunk from sharing the sensitive regulator ground path.
6. Use broad 5 V and return copper between XT60 and Mini-Fit. The 16 A string path bypasses the buck converter. Copper bottlenecks, connector fan-outs and return paths still require review after routing.

Main5V defaults to 8 mm tracks, Peripheral3V3 to 1 mm and ordinary signals to 0.25 mm. These are routing presets, not current-capacity guarantees. The project retains its standard two-layer / 1.6 mm baseline and existing fabrication clearances.

Account for the 3.3 V converter's input consumption in the 5 V budget. At 2 A output and an illustrative 90% efficiency it draws approximately 1.47 A from 5 V, in addition to strings, Pico and other 5 V loads. An 18 A source does not automatically cover every load running at its individual maximum.

## Validation and remaining work

ERC reports zero errors/warnings, PCB/schematic parity reports zero mismatches, and the shared interface checker verifies J5 against carrier J19. DRC intentionally reports a missing outline and 42 unrouted connections. No new exclusions were added to suppress faults. The circuit and footprint checks are recorded in `validation/`.

Before fabrication, complete layout, refill zones and run DRC; review current/thermal paths and harness ratings. Before connecting the carrier, verify 3.3 V regulation and power-good with a current-limited supply, then test startup and load steps. The supplied WEBENCH board remains a reference export, not the PCB being manufactured.

## Primary references

- [TI TPS6209x datasheet](https://www.ti.com/lit/ds/symlink/tps62090.pdf): part variants, pins, 1.4 MHz configuration, layout and RGT0016C package drawing.
- [Würth 74439346010 datasheet](https://www.we-online.com/components/products/datasheet/74439346010.pdf): real inductor dimensions and land pattern.
- [Samsung CL31A226KAHNNN family](https://product.samsungsem.com/mlcc/CL31A226KAHNNN.do): selected 22 µF / 25 V / 1206 capacitor, currently mass production.

## Right-angle connector trial — 2026-11-23

Restore point: `faf932c`. Current J5 selection is now Molex **0039291107** (DigiKey WM9157-ND), the flanged right-angle Mini-Fit Jr. version. Schematic, board and parts.csv now use KiCad `Connector_Molex:Molex_Mini-Fit_Jr_5569-10A1_2x05_P4.20mm_Horizontal`. This supersedes the vertical J5 selection above for the active trial. Carrier J19 is unchanged.

This footprint includes two 3.2 mm non-plated mounting holes. J5's anchor and orientation are retained for comparison, with UUID and schematic link preserved. All existing tracks, vias, board edges and other footprint placements are unchanged. Copper zones were refilled. At this trial placement the larger body/flange overlaps regulator components, probes and mounting-hole areas; one flange hole intersects TP2. Place/rotate J5 and adjust layout before fabrication. This is not a released fabrication revision. The referenced stock 3D model is absent in the local KiCad installation, so the right-angle connector will not yet appear in the 3D viewer.

Prior sourcing snapshots and DigiKey lists still reflect the vertical part; revise them after accepting the connector change. Primary part page: https://www.molex.com/en-us/products/part-detail/0039291107 .

## Selected right-angle connector: 0039300100

The flanged 0039291107 trial above is superseded. Active J5 is now **Molex 0039300100**, DigiKey **WM21355-ND**, with KiCad footprint `Connector_Molex:Molex_Mini-Fit_Jr_5569-10A2_2x05_P4.20mm_Horizontal`. This uses two snap-in retention pegs instead of screw flanges. The stock footprint includes the two peg holes. Schematic and parts.csv match the board. The current placement and all existing routing are retained; inspect and adjust connector placement before manufacture. Carrier J19 is unchanged. Existing procurement snapshots/My Lists still need updating to the selected part before purchase.

## J5 manufacturer 3D model — 2026-11-23

The exact Molex 0039300100 STEP model is now installed. User downloaded `039300100_stp.zip` from Molex; the unmodified source is `../models/Molex_0039300100_source.stp`. The normalized `../models/Molex_0039300100.step` retains manufacturer geometry and colours and is attached through project footprint `PowerManager:Molex_0039300100`. This supersedes the earlier missing-model note. The footprint's copper, holes and drawings are identical to stock KiCad 5569-10A2; only the local identifier and model path differ. Schematic and parts.csv use the local footprint so F8/footprint refresh retain the model.

Model normalization: x=-source_x+8.4, y=source_z+13.9, z=source_y (millimetres). Ten tail centres align at x=0,4.2,8.4,12.6,16.8 and model y=0,-5.5; model peg centres x=0,16.8, y=7.3 align with PCB holes y=-7.3. PCB seating plane is z=0. Normalized complete-model bounds: x=-3.1..19.5, y=-6.035..13.9, z=-3.6..11.4 mm. Solid validity checked after reimport. Only J5's model and footprint-library identifier changed on the PCB; layout/routing are untouched.

## Larger passives and power indicator — 2026-11-23

C3, C4, R1, R2 and D1 now use standard reflow 1206 footprints (nominal 3.2 × 1.6 mm bodies), replacing 0805 for easier manual placement/hot-air work. Values and pin-to-net mappings are unchanged. Selected MPNs: C3 KEMET C1206C103K5RACTU (10 nF, 50 V, X7R); C4 KEMET C1206C392J5GACTU (3.9 nF, 50 V, C0G); R1 Yageo RC1206FR-07499KL (499 kOhm, 1%); R2 Yageo RC1206FR-071KL (1 kOhm, 1%); D1 Lite-On LTST-C150KGKT (green). Schematic, PCB and parts.csv agree. These selections supersede earlier 0805 notes.

Centres, orientations and schematic links are retained. All 37 track segments, 23 vias, and board-edge graphics are unchanged (verified by UUID and geometry). The user will handle layout and routing changes required by the larger pads; local shorts, clearances, overlaps and dangling ends remain. The pre-existing missing H4 footprint warning also remains. ERC passes with zero violations; the replacements have no footprint-library mismatch warnings. Dated procurement snapshots and online DigiKey lists still contain previous package selections and need updating before purchase.

## J5 row swap reverted

J5 is restored to the original straight-through interface: pins 1–4 IN_5V, pin 5 PERIPH_3V3, pins 6–10 GND. Carrier J19 remains unchanged. Use a pin-number-to-same-pin-number cable; the proposed crossed cable is no longer applicable. Right-angle 0039300100 connector/model, larger 1206 components and all current placement/routing edits are retained. Only the row-swap pin assignments were reversed.

## Plated test holes

TP1–TP3's two-pin headers are replaced by bare plated test holes: TP1 IN_5V, TP2 PERIPH_3V3, TP3 PERIPH_PG. New TP4 is the shared GND hole, initially at the former TP3 ground-pin position. Each uses `TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm`: 1.5 mm copper diameter, 0.7 mm plated drill, exposed on both sides. No component or connector is required; a temporary wire/loop can be soldered into a hole. These four features are excluded from the component BOM/placement outputs, and former header rows were removed from parts.csv. This supersedes earlier signal/GND header-pair descriptions.

Signal-hole centres are unchanged from the former header pin-1 positions; traces and all other components are unchanged. Removed ground pads can leave old trace stubs for layout cleanup. Netlist verification confirms all four single-pin net assignments, ERC passes, and footprint-library agreement is clean. The existing missing-H4 parity warning remains. Historical manufacturing exports and procurement lists have not been regenerated.

## Named probe holes; mounting holes removed

Mounting-hole symbols H1–H4 are removed to match the PCB. The four probe holes now use meaningful references consistently in schematic, PCB and instance paths: **5V**, **3V3**, **PG**, **GND**. Their references are visible on bottom silkscreen, matching the side used in the manual layout, with 0.8 mm text and 0.15 mm stroke. The prior TP1–TP4 naming is superseded; electrical nets remain IN_5V, PERIPH_3V3, PERIPH_PG and GND respectively. Pad geometry, drill sizes, locations and routing are unchanged. Connector retention-peg holes are retained as part of J5's footprint.
