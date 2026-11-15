# LED Head Unit · Rev 1

Open `led-head-rev1.kicad_pro` in KiCad 10. The project contains the schematic, PCB and draft SMT assembly data. The nominal outline is 100 × 73 mm with a notch under the socketed Pico 2 W antenna. The enclosure must leave the antenna end clear of wiring, battery and metal hardware. Check USB and SWD reach, socket height and harness opening clearance against the physical parts.

## Board and harness

| Ref | Connection |
| --- | --- |
| J1 | 1 battery +, 2 ground. Connect to a keyed XT60 panel pigtail with a 5 A battery-side fuse. Input is 3S LiPo or a fused, BMS-protected LiFePO₄ camper circuit. |
| J2 | 1 regulated external +5 V, 2 ground. Use a keyed or clearly segregated panel harness and source-side fuse sized for the feed wiring. External source polarity is mandatory. |
| J3 | High-current panel toggle connections. Board pin 1 to S333 lug 1, pin 2 to lug 2, pin 3 to lug 3. |
| J5 | Toggle auxiliary pole. Board pin 1 to S333 lug 6, pin 2 to lug 5, pin 3 to lug 4. |
| J4 | Wired Pololu D36V50F5 module. Board pins 1–4 to VIN, GND, VOUT, GND respectively. |
| J6 | Pololu logic harness. Pins 1–3 to EN, VRP, PG respectively. |
| J10/J11 | Female 1×20 sockets, on the standard 17.78 mm row spacing. J10 pin 1 is Pico pin 1. J11 pin 1 is Pico pin 21. |
| J12 | NeoTrellis JST-PH. Pins 1–4 on this board are GND, 3.3 V, SDA, SCL. Map the harness wire by wire to the actual keypad; a generic straight-through JST-PH cable is provisional. Check the keypad power budget. |
| J21–J23 | XT30PW-F outputs. Pad 1 ground, pad 2 fused and sensed +5 V. |
| J31–J33 | JST-XH data outputs. Pad 1 DIN, pad 2 signal reference. Pair each data lead with its ground and connect to the matching string. |
| TP1 | GP1 mirror of string 1 for scope probing. |

The NKK S333 pole 1 selects buck output or external 5 V with OFF between. The second pole grounds buck EN on the external setting and grounds the source ID input on the battery setting. Verify switch terminal numbering and lever positions with continuity before marking the enclosure. The module and switch mount to the enclosure and connect using harnesses. Keep the module power and switch power loops short, use suitably rated wire and strain relief, and ventilate the module. The unit and all outputs share DC ground.

The 13.7 kΩ EN pull-down works with the Pololu's nominal internal 100 kΩ pull-up. Nominal loaded cutoff is 9.96 V and restart is 11.20 V from the 1.2/1.35 V EN thresholds. Confirm both with the actual module. The firmware should blank the LEDs before the hardware cutoff. A pack-level threshold cannot identify an imbalanced cell. The camper source uses its own BMS/low-voltage protection. ADC reporting should show volts without inferring chemistry.

Pico GP4/GP5/GP6 remain LED lanes 1–3. GP8/GP9 are I²C0 SDA/SCL respectively. GP7 reads the active-low battery-select signal, GP10 reads buck PG, and GP26 is battery ADC. Firmware must add current monitoring, keypad, source sensing and current limiting on top of the existing output paths. The nominal budgets are 1.8 A per string and 4.5 A aggregate LED load on battery. The board power distribution target is 6 A of LEDs plus controller and keypad overhead on external 5 V.

Three TXU0101 buffers replace the originally planned AHCT125. Each output-side supply is taken after its own fuse and shunt, so the data driver isolates when that rail or Pico 3.3 V is absent. Each shunt is 50 mΩ, dropping 100 mV and dissipating 0.20 W at 2 A. Check fuse trip coordination, inrush through the switch and actual connector voltage at full load. Fuse removal and harness changes are performed with power off.

## Four layers, 1 oz copper on both outside layers

Fabrication intent is 1.6 mm FR-4, four layers, **1 oz finished outer copper on both layers**. The 4.8 mm switched trunk, 4.2–4.5 mm external feed, 4.0 mm buck feed, and 1.9 mm per-string top routes are present as copper. String rail fan-outs use 2.3 mm copper and four 0.4 mm drilled vias per string. Positive power routing stays on the outer layers. The dedicated In1 ground plane complements the backside ground pour, with solid connections to high-current through-hole pads. In2 provides room for signal crossovers. Specify 1 oz for the In1 return plane if the fabricator offers it, and verify the chosen stackup on the quote.

IPC-2221 external-trace screening at nominal 35 µm copper gives approximately 3.97 mm for 6.5 A, 2.77 mm for 5 A and 0.78 mm for 2 A at 10 °C rise. Treat these as screening values for straight, uniform traces. Connector annuli, fuse pads, shunt pads, via plating and the minimum width of the actual filled return paths need review as individual bottlenecks. Validate populated electrical and thermal performance with a current-limited bench supply, then at 6 A external and the intended battery load inside the enclosure.

## SMT quote

Request top-side SMT only. Load the supplied BOM and centroid files as quote drafts and review the pin-one and diode orientation on the vendor placement preview. The Pico sockets, screw terminals, XT30s, XH headers, NeoTrellis PH header and bulk electrolytic are through-hole and installed separately. The panel switch, XT60 harness and Pololu module are off-board. If using JLCPCB, match the exact manufacturer parts to its catalog before placing the order. In particular, confirm sourcing for the three TXU0101DBVRs, the INA3221, 3 A fuse and shunts. PCBWay can quote these by manufacturer part number. Release Gerbers and the placement files together from the same verified PCB revision.

## Review status

KiCad 10 electrical-rule and design-rule reports are included, including board/schematic parity. Both design-rule checks and a vendor placement preview are separate from an electrical prototype test. First articles should verify the physical socket orientation, harness polarity, NeoTrellis pin mapping, S333 auxiliary-contact operation, source-change inrush, 3S cutoff/restart, and voltage drop/temperature in the populated enclosure. The polarity-controlled external 5 V input has no board-level reverse-polarity circuit.

The firmware is unchanged in its original project. The preserved outputs can drive the existing strings. New sensing, keypad and current-budget behavior require firmware work before relying on the stated limits.

References: [IPC-2221 screening calculator](https://www.digikey.com/en/resources/conversion-calculators/conversion-calculator-pcb-trace-width), [Pico 2 W datasheet](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf), [Pololu D36V50F5](https://www.pololu.com/product/4091), [NKK S-series](https://www.nkk.com/pdf/toggle_S.pdf), [TI TXU0101](https://www.ti.com/product/TXU0101), [TI INA3221](https://www.ti.com/product/INA3221), [JLCPCB assembly files](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad), [PCBWay assembly files](https://www.pcbway.com/assembly-file-requirements.html).

This revision includes Gerbers and separate plated/non-plated drill files for quote review. The KiCad 10.0.7 checks on the archived revision returned zero ERC violations, zero DRC violations, zero unconnected items and zero schematic-parity issues. The SMT BOM and placement file contain 35 positions. The fabrication and placement files in this package supersede the earlier Rev 1 exports.

## VSYS update

F4 was removed. The switched LED_5V rail now feeds D1 directly via a 0.65 mm branch with a 0.40 mm drill through via. D1 remains in series for USB isolation. Its cathode reaches J11 pad 19 on 0.65 mm front copper. The LED string fuses F1–F3 are retained.
