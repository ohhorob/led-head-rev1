# LED Head Rev 1 handoff

Updated 2026-11-24. The three active KiCad designs are the Pico carrier, power manager, and string daughterboard. The top-level combined LED head design is an earlier design. This handoff records the source revisions and fabrication exports prepared in this session.

## Resume on another computer

Clone the whole [led-head-rev1 repository](https://github.com/ohhorob/led-head-rev1), since projects share symbols, footprints, and STEP models. Use KiCad 10. The checks and plots in this session used KiCad 10.0.7.

- [Pico carrier project](pico-carrier/pico-carrier.kicad_pro)
- [Power-manager project](power-manager/power-manager.kicad_pro)
- [String daughterboard project](string-daughterboard/string-daughterboard.kicad_pro)

For Codex, open the cloned folder as the workspace. For live inspection, open the target board in KiCad PCB Editor first, then ask Codex to use KiCad MCP for that board. Confirm that the live PCB and saved file agree before a fabrication export. Keep the project-relative library paths intact.

## OSH Park fabrication files

Use standard **2-layer, 1 oz, nominal 1.6 mm** prototype service. These ZIPs are ready for upload review.

| Board | Upload ZIP | Features to check in the OSH Park preview |
| --- | --- | --- |
| Pico carrier | [Carrier ZIP](pico-carrier/manufacturing/pico-carrier-oshpark-2layer-2026-11-24.zip) | 69 × 97 mm outline, antenna notch with 1 mm inside radii, 96 socket drills, eight non-plated mounting holes, back QR |
| Power manager | [Power-manager ZIP](power-manager/output/power-manager-oshpark-2layer-2026-11-24.zip) | Four edge notches, two plated XT60 slots, two non-plated J5 retention holes, four plated test holes, back QR |
| String daughterboard | [Daughterboard ZIP with QR](string-daughterboard/manufacturing/string-daughterboard-oshpark-2layer-2026-11-24-qr.zip) | 17.4 × 8 mm tongue, six exposed fingers on each side, three J2 plated holes, back QR |

The exported back-silkscreen QR codes were decoded to the GitHub URL above. Use the QR version of the daughterboard ZIP. The Nov 20 daughterboard export predates the current status-pixel footprint and wiring. The current source PCBs match the snapshots used to make the listed ZIPs. Order placement and physical prototype testing were outside this session's verification.

## Electrical changes and bring-up

- **Power manager.** Keep the fixed 3.3 V TPS62091 for the peripheral rail. J5 is the right-angle Molex 0039300100. Pins 1–4 are IN_5V, pin 5 is PERIPH_3V3, and pins 6–10 are GND. The four plated test holes are 5V, 3V3, PG, and GND. Standalone H1–H4 were removed. The export preserves the connector retention holes. The preflight noted back-silkscreen clearance warnings and an intentional J5 silkscreen mismatch exclusion. Check the KiCad logo by the XT60 in the fab preview.
- **Carrier.** U6 (TXU0101DBVR) converts GP20 to 5 V logic before J21 A5. All later slots use the existing daisy-chain links. Use the vertical Sullins EBC06DCWN sockets. The final 2.4 mm main bridge feeds J21/J23/J25/J27. At 8 A its estimated room-temperature drop is about 39 mV and dissipation about 0.31 W, excluding the rest of the path. Step up the load before using all eight 2 A strings and measure the farthest slot voltage, bridge temperature, and connector temperature. Dry-fit adjacent cards and verify that the guides prevent reversed insertion.
- **Daughterboard.** The Würth 1312020030000 status pixel runs on fused 5 V upstream of R1, with a local 100 nF C3 bypass. The status pixel's current bypasses the 25 mΩ shunt. A6 and B6 remain spare. Use this daughtercard revision throughout the 5 V status chain. An empty slot or unpowered pixel interrupts the chain to later slots.
- **Firmware.** The actual routed GPIO order for slots 1–8 is GP13, GP2, GP12, GP3, GP11, GP4, GP6, GP5. PAC1934 channels 1–4 on U4 map to slots 2, 4, 3, 1. U5 maps to 6, 8, 7, 5. Use 0.025 Ω for shunt conversion. The older string-interface contract has different GPIO and PAC channel assignments, so its checker still flags those differences.

Fabrication preflight used fresh zone fills on temporary copies, applied OSH Park minimums, and checked Gerbers and drills. The final carrier had zero DRC errors, ERC issues, and unconnected items. Its padless KiCad logo may appear as an extra footprint in schematic parity. The daughterboard export passed DRC and parity. Re-export from the relevant native project after any new PCB changes.
