# LED Head Unit · Rev 1

## Modular redesign — 2026-11-20

The new modular design lives in separate projects in this same repository:

- [Pico carrier](pico-carrier/README.md): populated control/monitoring schematic and unrouted PCB draft.
- [Power manager](power-manager/README.md): empty KiCad starter project.
- [String daughtercard](string-daughterboard/README.md): existing routed card, preserved.
- [Shared interfaces](shared/README.md): connector pinout, mechanical contract and verification tool.

Open the relevant `.kicad_pro`, rather than opening its PCB on its own. The combined board described below is retained as the earlier design; its control/monitoring circuits have started migrating into the carrier; the power manager remains a starter project.

Open `led-head-rev1.kicad_pro` in KiCad 10. The project contains the schematic, PCB and draft SMT assembly data. The nominal outline is 100 × 73 mm with a notch under the socketed Pico 2 W antenna. The enclosure must leave the antenna end clear of wiring, battery and metal hardware. Check USB and SWD reach, socket height and harness opening clearance against the physical parts.

## Board and harness

| Ref | Connection |
| --- | --- |
| J1 | Shared board-mounted XT60PW-M. Pin 1 is ground and pin 2 is positive. Connect a regulated 5 V supply, a fused 3S LiPo, or a fused 12 V LiFePO₄ camper circuit with BMS protection. Keep the 5 A fuse in the battery harness and size the 5 V source-side fuse for its wiring and load. |
| J3 | High-current panel toggle connections. Board pin 1 (EXT_5V) to S333 lug 3, pin 2 (LED_5V) to lug 2, pin 3 (BUCK_5V) to lug 1. |
| J5 | Toggle auxiliary pole. Board pin 1 to S333 lug 6, pin 2 to lug 5, pin 3 to lug 4. |
| MOD1 | Plug-in Pololu D36V50F5 (4091). Solder two 1×6 female sockets to the carrier and two matching male strips to the module. The pin pitch is 2.54 mm. Use every VIN, VOUT and GND pad. See the mounting details below. |
| J10/J11 | Female 1×20 sockets, on the standard 17.78 mm row spacing. J10 pin 1 is Pico pin 1. J11 pin 1 is Pico pin 21. |
| J12 | NeoTrellis JST-PH. Pins 1–4 on this board are GND, 3.3 V, SDA, SCL. Map the harness wire by wire to the actual keypad; a generic straight-through JST-PH cable is provisional. Check the keypad power budget. |
| J21–J23 | Right-angle JST-XH S3B-XH-A(LF)(SN) string outputs. Pin 1 = GND, pin 2 = DATA, pin 3 = fused and sensed +5 V. Use an XHP-3 housing with SXH-001T-P0.6 contacts and 22 AWG leads to the matching string-side JST-SM connector. Verify the string pin order before crimping. |
| J16 | UART0 for Adafruit 4331. Pin 1 (square, black cable wire) = GND, pin 4 = Pico RX (GP1), pin 5 = Pico TX (GP0). Pins 2, 3 and 6 are unconnected. |
| J17 | SPI0, six-pin JST-PH. Pins 1–6 are GND, switched LED_5V, MISO/GP16, CSn/GP17, SCK/GP18, MOSI/GP19. SPI signals use 3.3 V logic. |
| TP2–TP5 | Standard 2.54 mm 1×2 headers for Logic Pro probes. Pin 1 (square) is signal and pin 2 is ground. TP2 = INA3221 bus SDA, TP3 = INA3221 bus SCL, TP4 = Trellis bus SDA, TP5 = Trellis bus SCL. |

The NKK S333 pole 1 selects the Pololu output or the protected 5 V bypass with OFF between. Label the switch BAT / OFF / 5 V. The second pole grounds buck EN in 5 V mode and grounds the source ID input on the battery setting. Verify switch terminal numbering and lever positions with continuity before marking the enclosure. The switch mounts to the enclosure and connects using a harness. Keep the switch power loop short, use suitably rated wire and strain relief, and ventilate the carrier-mounted Pololu module. The unit and all outputs share DC ground.

The 13.7 kΩ EN pull-down works with the Pololu's nominal internal 100 kΩ pull-up. Nominal loaded cutoff is 9.96 V and restart is 11.20 V from the 1.2/1.35 V EN thresholds. Confirm both with the actual module. The firmware should blank the LEDs before the hardware cutoff. A pack-level threshold cannot identify an imbalanced cell. The camper source uses its own BMS/low-voltage protection. ADC reporting should show volts without inferring chemistry.

Pico GP4/GP5/GP6 remain LED lanes 1–3. GP8/GP9 are hardware I²C0 SDA/SCL for the INA3221, with R7/R8 pull-ups and TP2/TP3 probe headers. NeoTrellis is on hardware I²C1: physical pin 19 (GP14) is SDA and physical pin 20 (GP15) is SCL. The carrier adds no pull-ups to this bus. Use the pull-ups on the connected keypad. GP7 reads the active-low battery-select signal, GP10 reads buck PG, and GP26 is battery ADC. Firmware must add current monitoring, keypad, source sensing and current limiting on top of the existing output paths. The nominal budgets are 1.8 A per string and 4.5 A aggregate LED load on battery. The board power distribution target is 6 A of LEDs plus controller and keypad overhead on external 5 V.

Three TXU0101 buffers replace the originally planned AHCT125. Each output-side supply is taken after its own fuse and shunt, so the data driver isolates when that rail or Pico 3.3 V is absent. Each shunt is 50 mΩ, dropping 100 mV and dissipating 0.20 W at 2 A. Check fuse trip coordination, inrush through the switch and actual connector voltage at full load. Fuse removal and harness changes are performed with power off.

## Four layers, 1 oz copper on both outside layers

Fabrication intent is 1.6 mm FR-4, four layers, **1 oz finished outer copper on both layers**. The 4.8 mm switched trunk, 4.2 mm bypass trunk downstream of the eFuse fan-out, 4.0 mm buck feed, and 1.9 mm per-string top routes are present as copper. String rail fan-outs use 2.3 mm copper and four 0.4 mm drilled vias per string. Positive power routing stays on the outer layers. The dedicated In1 ground plane complements the backside ground pour, with solid connections to high-current through-hole pads. In2 provides room for signal crossovers. Specify 1 oz for the In1 return plane if the fabricator offers it, and verify the chosen stackup on the quote.

IPC-2221 external-trace screening at nominal 35 µm copper gives approximately 3.97 mm for 6.5 A, 2.77 mm for 5 A and 0.78 mm for 2 A at 10 °C rise. Treat these as screening values for straight, uniform traces. Connector annuli, fuse pads, shunt pads, via plating and the minimum width of the actual filled return paths need review as individual bottlenecks. Validate populated electrical and thermal performance with a current-limited bench supply, then at 6 A external and the intended battery load inside the enclosure.

## SMT quote

Request top-side SMT only. Load the supplied BOM and centroid files as quote drafts and review the pin-one and diode orientation on the vendor placement preview. The Pico sockets, screw terminals, XT60 and XH headers, NeoTrellis PH header and bulk electrolytic are through-hole and installed separately. Install the Pololu module and its two headers by hand. The panel switch and mating battery harness are off-board. If using JLCPCB, match the exact manufacturer parts to its catalog before placing the order. In particular, confirm sourcing for the TPS25970ARPWR, the three TXU0101DBVRs, the INA3221, 3 A fuse and shunts. Verify the RPW0010A land pattern, stencil openings, and pin 1 against the assembly preview. PCBWay can quote these by manufacturer part number. Release Gerbers and the placement files together from the same verified PCB revision.

## Review status

KiCad 10 electrical-rule and design-rule reports are included, including board/schematic parity. Both design-rule checks and a vendor placement preview are separate from an electrical prototype test. First articles should verify the physical socket orientation, harness polarity, NeoTrellis pin mapping, S333 auxiliary-contact operation, source-change inrush, 3S cutoff/restart, and voltage drop/temperature in the populated enclosure. Use correctly polarized XT60 leads. The eFuse bypass and input-side status electronics depend on correct polarity.

The firmware is unchanged in its original project. The preserved outputs can drive the existing strings. New sensing, keypad and current-budget behavior require firmware work before relying on the stated limits.

References: [IPC-2221 screening calculator](https://www.digikey.com/en/resources/conversion-calculators/conversion-calculator-pcb-trace-width), [Pico 2 W datasheet](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf), [Pololu D36V50F5](https://www.pololu.com/product/4091), [NKK S-series](https://www.nkk.com/pdf/toggle_S.pdf), [TI TXU0101](https://www.ti.com/product/TXU0101), [TI INA3221](https://www.ti.com/product/INA3221), [JLCPCB assembly files](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad), [PCBWay assembly files](https://www.pcbway.com/assembly-file-requirements.html).

This revision includes Gerbers and separate plated/non-plated drill files for quote review. The KiCad 10.0.7 checks on the archived revision returned zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues. The SMT BOM and placement file contain 71 positions. The fabrication and placement files in this package supersede the earlier Rev 1 exports.

## VSYS update

F4 was removed. The switched LED_5V rail now feeds D1 directly via a 0.65 mm branch with a 0.40 mm drill through via. D1 remains in series for USB isolation. Its cathode reaches J11 pad 19 on 0.65 mm front copper. The LED string fuses F1–F3 are retained.

## Connector silkscreen

J12 NEOTRELLIS marks the rotated four-pin JST-PH on the left. The combined string outlets are marked STR 1–3. The D, + and − markings identify data, fused +5 V and ground. J5 identifies the switch logic harness. MOD1 identifies the direct-mount regulator. The shared XT60 input has + and − markings.

## Connector access

The shared J1 XT60 inlet exits the right edge. The three JST-XH string outlets exit the top edge and overhang it for plug access. The J1 mating face projects approximately 5.4 mm beyond the PCB edge. The installed KiCad library has no STEP model for XT60PW-M; use the footprint fabrication outline to review the projection. Verify enclosure openings and wire bend radius with the actual harnesses.

## Pololu mounting

MOD1 uses the Pololu STEP model and generic KiCad models for two 1×6 female sockets and two downward-facing male strips. The modeled stack puts the module PCB underside 11.04 mm above the carrier surface (8.50 mm socket height plus a 2.54 mm male-header spacer). Measure the fully seated hardware before sizing the nylon standoff. The three module mounting-hole centers are indicated on the KiCad Drawings layer for support design. H5 is a 2.2 mm non-plated M2 clearance hole centered at (76.159, 30.759) mm, aligned with the upper-left MOD1 hole in PCB top view.

Viewed from the carrier top with the connector row toward the lower edge of the module, pads 1–6 are on the outer row and pads 7–12 on the inner row. Both rows run left to right.

| Row | Left to right |
| --- | --- |
| Outer (1–6) | VRP, EN, VOUT, VOUT, GND, VIN |
| Inner (7–12) | VRP, PG, VOUT, VOUT, GND, VIN |

Compare the physical module labels to the carrier pin mapping before soldering. Keep airflow around the converter and the existing battery-mode power budget pending a loaded thermal test.

## Shared inlet and status LEDs

| Toggle | Power path | Status |
| --- | --- | --- |
| BAT | J1 through the Pololu | POWER follows the switched rail. FAULT lights if Pololu PG is low after the BAT delay. |
| OFF | Neither throw connects to the switched rail | POWER goes dark as the rail discharges. FAULT is gated off. |
| 5 V | J1 through the TPS25970A eFuse | POWER follows the switched rail. FAULT is gated off. If J1 sees battery voltage, the bypass is blocked. |

The eFuse nominal rising thresholds are 4.33 V for enable and 5.38 V for overvoltage cutoff. With a 768 Ω ILIM resistor the nominal current-limit setpoint is 7.48 A, distinct from the device's 7 A continuous rating. The 6.8 nF DVDT capacitor slows startup when the eFuse enables. Switching to an already energized bypass can still cause inrush into C2. The output uses six plated vias into its 4.2 mm trunk. Inspect the short fan-outs from the RPW power contacts during the loaded test. Validate voltage drop and temperature at the 6 A LED load plus controller overhead before fabrication sign-off.

The red LED uses an input-side 3.3 V LDO independent of Pico power. D2 and D3 isolate the Pico inputs from that supply when the Pico is off. The BAT delay uses a 100 kΩ and 4.7 µF network with a Schmitt input, so timing depends on component and input-threshold tolerances. A depleted battery may be indicated as a fault while input power is sufficient to light the LED. If J1 is unplugged, the indicator has no supply.

With a current-limited bench source and the strings disconnected, test each switch mode, verify the overvoltage cutoff with battery-level input in 5 V mode, and scope the switched rail during hot-plug and source changes. Verify the fault LED with PG low while the Pico supply is absent. Follow with the loaded thermal and enclosure tests.

[TI TPS2597 datasheet](https://www.ti.com/lit/ds/symlink/tps2597.pdf) · [TI SN74LVC1G57 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g57.pdf)

## Pre-fabrication board review

Use Panasonic EEU-FR1C102 for C2 (1,000 µF, 16 V, 10 mm body and 5 mm lead pitch). The suffixed EEU-FR1C102L uses 3.5 mm lead pitch. The U4 INA3221 and R11–R13 shunt land patterns are in the project footprint library and follow the TI and Vishay reference dimensions. The SMT placement file was exported from the manually routed board. The native KiCad PCB is the source for subsequent edits.

The current layout passed KiCad ERC, DRC and schematic parity. The documented design-rule exclusions remain in the reports. Review the silkscreen and regenerate all final fabrication outputs from the resulting PCB. Verify assembly sourcing and rotation against the vendor preview before ordering.
