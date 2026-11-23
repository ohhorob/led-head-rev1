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
