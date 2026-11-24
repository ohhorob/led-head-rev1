# Pico 2 W carrier

Open `pico-carrier.kicad_pro` through KiCad Project Manager. This is a populated schematic and an **unrouted placement draft**, not a fabrication release. No board outline is assigned yet.

The root schematic links two sheets:

- `control.kicad_sch`: Pico sockets, UART0, SPI0, two I2C buses and probe headers, ADC breakout, SWD header and J-Link connector.
- `string-slots.kicad_sch`: eight vertical Sullins EBC06DCWN sockets.
- `current-monitoring.kicad_sch`: two PAC1934 monitors, bypass capacitors wired directly to VDD/VDD_IO, and source/PG pull-ups.

String data for slots 1–8 uses GP4, GP5, GP6, GP2, GP3, GP11, GP12 and GP13 respectively. GP20 drives U6 (TXU0101DBVR), which translates the head of the eight-pixel status chain to 5 V before J21 A5. The last pixel's output is intentionally unused. The PAC1934 monitor bus uses GP8/GP9 on I2C0, with pull-ups to the external peripheral 3.3 V rail. NeoTrellis uses GP14/GP15 on I2C1, with no added pull-ups. Its connector pin 2 now supplies **5 V VIN**, rather than the Pico's 3.3 V output. Wire the harness to the tile's VIN input and retain 3.3 V I2C pull-ups.

`PICO_3V3` is the Pico regulator output and debugger reference. `PERIPH_3V3` is the separate regulator's output; they are distinct nets. The Pico's VSYS is supplied through the existing SS14 isolation diode from `IN_5V`. `PICO_PG`, `PICO_BATT_SEL_N` and the battery ADC path await the power-manager interface; their protective scaling/voltage behavior is not complete here.

The PCB contains 34 footprints with schematic UUID paths and matching nets. Positions are initial organization only. Existing Pico socket geometry and its original project 3D model were retained; validate that model against the exact Pico hardware before using it for enclosure clearance. No tracks or fill zones were copied from the old combined board.

U4 and U5 are PAC1934T-I/JQ, 4 × 4 mm UQFN with 0.65 mm pitch. U4 ADDRSEL is grounded (0x10); U5 ADDRSEL is tied to VDD (0x1F). Both VDD and VDD_IO have separate 100 nF bypasses, physically grouped near the IC on the draft PCB. SLOW is pulled low through 10k and PWRDN is held high. The standard KiCad land pattern was checked against Microchip C04-2257A: 0.80 × 0.35 mm outer pads, 4.00 mm opposed-pad-centre spacing, 0.65 mm pitch and a 2.7 mm centre pad, without thermal vias.

## Socket footprint

J21–J28 use the vertical **Sullins EBC06DCWN**. The footprint has 12 plated contacts, a 2.54 mm column pitch, 5.08 mm between rows, 1.10 mm finished drills, and 1.70 × 2.20 mm pads. The no-ear housing measures 21.84 × 9.40 mm and sits 15.49 mm above the board. The printed card rails provide retention and must prevent reversed insertion. Test-fit a socket and a daughtercard to confirm contact orientation and clearance.

See the [Sullins C11424 Rev D drawing](../shared/reference/Sullins_C11424_RevD_CW_CT.pdf) and [footprint verification notes](../models/Sullins_EBC06DCWN_model-notes.md).

## Checks and remaining work

KiCad CLI reports zero ERC violations and zero schematic-parity issues. The interface checker passes for all eight sockets and both monitors and the unchanged daughtercard. The draft has 159 unrouted connections and no board outline; DRC correctly reports these unfinished items. No checks were disabled to hide them.

Choose the power interconnect using [power connection options](power-connection-options.md), then establish board size, stack height, card-facing direction and rail locations. Review USB/SWD/cable access before routing. Keep both supply rails and their power-up/down behavior in the electrical review.

## Firmware configuration

Use 0.025 ohm for every daughtercard shunt. PAC1934 unipolar shunt-voltage scaling gives a nominal 4 A full-scale range; the nominal 2 A load produces 50 mV and 0.10 W at the shunt. Keep the 3 A fuse; measurement range does not set a current limit. Apply the low-sample-rate REFRESH workaround from Microchip errata DS80001160A.

Unlike the INA3221 connection previously used, the PAC1934 measures bus voltage at SENSE+, upstream of the shunt. For delivered string voltage use `Vload = Vbus - Vshunt`; for delivered power use `I * Vload`. Its reported input-side power includes shunt dissipation. No firmware driver has been implemented by this hardware change.

For all eight strings at 2 A, provision 16 A plus controller/peripheral overhead. The previously proposed four-contact Mini-Fit harness was discussed for the smaller system; its final circuit count/wire size and the converter budget must be reviewed for this expanded carrier before routing the main feed.

## Power-board input

J19 is a **10-position Molex Mini-Fit Jr**, PCB header **0039281103**, footprint `Connector_Molex:Molex_Mini-Fit_Jr_5566-10A_2x05_P4.20mm_Vertical`. It combines the regulated string rail and peripheral rail in one harness. Mating housing: **0039012100**; female contacts: **0039000039**, selected for 18–24 AWG. The intended main power conductors are 18 AWG; check the complete connector/wire derating and loaded temperature before release.

| Pins | Net |
| --- | --- |
| 1–4 | IN_5V, parallel regulated 5 V conductors |
| 5 | PERIPH_3V3, separate peripheral regulator output |
| 6–10 | GND, parallel returns |

PERIPH_3V3 remains separate from Pico 3V3(OUT). The carrier connector is placed to the right of the present layout and marked POWER IN; the user can position it. Existing parts and routing were preserved. The briefly added two-pin JST input was removed, including its symbol, footprint and labels.

The matching power-manager circuitry/connector still needs implementation. This connector does not carry source-ID, PG or divided battery ADC signals; their inter-board connection remains to be designed. No 16 A harness rating is inferred merely by multiplying the catalogue single-contact rating.

## Dedicated 5 V module — 2026-11-21

The power-manager project is now the simple dedicated-5-V module: one XT60, the WEBENCH TPS62091 3.3 V converter and Mini-Fit output J5. Connect it to carrier J19 with the existing straight-through ten-pin power cable. The carrier pinout is unchanged: 1–4 IN_5V, 5 PERIPH_3V3, 6–10 GND.

Carrier J20 remains a reserved five-pin telemetry connector for a future separate battery module: 1 GND, 2 PICO_3V3, 3 BAT_ADC, 4 PICO_PG, 5 PICO_BATT_SEL_N. It is parked outside the outline at (110,135) mm. It has no matching connector on the dedicated 5 V module and is not needed for that module to supply power. The future battery-module interface is deferred.

The shared power interface checker verifies the implemented main cable and the reserved carrier-side telemetry pinout separately. No carrier layout or routing was changed while replacing the combined power-manager design with the dedicated-supply module.

## Status chain at 5 V — 2026-11-24

U6 sits on front copper near the Pico socket, with C44 on VCCA (PICO_3V3) and C45 on VCCB (IN_5V). OE is tied to PICO_3V3. The 5 V output STATUS_RGB_5V goes to slot 1 (J21 A5). The existing inter-slot status links are unchanged. Use the matching daughterboard revision with D1 powered from fused 5 V before its shunt. A6 and B6 remain reserved.
