# String daughterboard

Open `string-daughterboard.kicad_pro` in KiCad Project Manager. This is the existing manually routed daughtercard in the same repository as the carrier and power-manager projects.

One string channel has:

- F1: Littelfuse 0451003.MRL, 3 A fuse.
- **R1: Vishay WSL2512R0250FEA, 25 mOhm, 1%, 1 W, 2512.**
- U1: TXU0101 data translator, followed by R2, 220 ohm.
- J2: right-angle JST-XH output; pin 1 GND, pin 2 DATA, pin 3 string +5 V.
- D1: Würth 1312020030000 (2 × 2 mm) status pixel on fused 5 V before the shunt (SHUNT_HI).
- C1/C2: 100 nF bypass capacitors for the TXU0101 supplies. C3 is a dedicated 100 nF bypass for D1 on the back of the card.

The new shunt value replaces 50 mOhm. At 2 A it drops 50 mV and dissipates 0.10 W. The carrier uses two PAC1934 monitors; the 100 mV sense range corresponds to nominal 4 A full scale with this resistor. Firmware must use 0.025 ohm. The 3 A fuse is not a precise 2 A current limiter.

The R1 footprint now has the value-neutral name `StringCard:Vishay_WSL2512`. Its pad geometry is unchanged. The older `_50mR` library item is retained only as a legacy definition; the current schematic and board use the value-neutral item. No track, via, zone, outline, component position or pad geometry changed during the shunt update.

## Card interface and mechanics

J1 is the PCB edge itself, mating with a carrier-mounted Sullins EBC06DRAS. Do not fit a socket on this daughtercard. Nominal board thickness is 1.6 mm, with six contacts per face at 2.54 mm pitch. The present board is 22 × 26.5 mm overall, including its 17.4 mm wide × 8 mm tongue. Printed rails provide retention; there are no mounting holes on this daughtercard. Check physical mating and card-facing direction with the socket before fabrication.

| Finger | Net | Purpose |
| --- | --- | --- |
| A1, B1 | GND | Parallel power returns |
| A2, B2 | IN_5V | Parallel regulated 5 V input contacts, 2 A nominal total |
| A3 | PERIPH_3V3 | String translator input-side supply |
| B3 | STRING_DATA_IN | 3.3 V string data |
| A4 | SHUNT_HI | Kelvin sense upstream of the shunt, after fuse |
| B4 | STRING_5V | Kelvin sense downstream of shunt |
| A5 | STATUS_DATA_IN | 5 V logic status pixel input |
| B5 | STATUS_DATA_OUT | Regenerated status output to next slot |
| A6, B6 | Unconnected | Reserved |

A is front copper and B is back copper. Looking at the front with the insertion tip at the bottom, positions 1–6 run left to right. The carrier socket orientation is documented separately; this front-view convention must not be confused with the socket's component-side solder-tail view.

The Kelvin pair carries measurement signals, not load current. The status pixel draws from the fused 5 V node upstream of R1, so its current does not flow through the string shunt. The carrier translates GP20 to 5 V before slot 1. Use this card revision throughout the chain. Use the specified Würth 1312020030000 part; avoid driving an unpowered card. Swaps are power-off only. Enclosure guides must prevent reversed insertion.

## Validation and exports

After the shunt update: zero ERC violations, zero DRC violations, zero unrouted connections and zero schematic-parity issues. The shared checker verifies the edge pinout, card geometry, carrier monitoring connections and R1's selected value/part number.

Existing manufacturing folders are historical snapshots and were not regenerated. The shunt change does not change fabrication copper, but their embedded board metadata or assembly references may still say 50 mOhm. Use the current native design and **WSL2512R0250FEA** for new component purchases.

Do not rerun the archived creation scripts over the routed board. Schematic UUIDs and PCB footprint paths must remain linked so F8 updates the same components.

See [shared interface contract](../shared/README.md), [footprint audit](footprint-audit.md), and [carrier project](../pico-carrier/README.md).

## Status LED update — 2026-11-23

Restore point before this change: `3f7ae29`. D1 now uses Würth 1312020030000, with the manufacturer's rev26a footprint and matching STEP model. Library geometry is unchanged from Würth; its model path is project-relative. Symbol numbering is remapped while retaining existing schematic wires: 1 DOUT, 2 VDD (PERIPH_3V3), 3 DIN, 4 GND. The original D1 PCB position, rotation, UUID and schematic path are retained. All other footprints, traces, vias and outline geometry are unchanged. Copper zones were refilled.

ERC passes; the board/library footprint and schematic pin mapping were verified. The original layout passed DRC before replacement; the smaller D1 pads require local rerouting. Current DRC reports shorts from existing STATUS_DATA_IN tracks to D1 supply/ground pads, supply-via clearance, dangling old DIN/DOUT tracks, and an incomplete D1 ground thermal. Reconnect all four D1 pins before fabrication. C1/C2 remain 100 nF in their existing positions; place the LED bypass close to the new supply/ground pads when rerouting. Manufacturing exports are historical and must not be used for this changed layout.

Carrier assembly STEP snapshots have been refreshed to show the smaller LED. No carrier layout file changed. The shared interface checker currently flags pre-existing carrier GPIO and monitor-channel permutations against its older JSON contract; schematic and PCB agree with one another at those endpoints. These mappings were not changed here.

Source: https://www.we-online.com/en/components/products/WL-ICLED — KiCad_WL-ICLED (rev26a).zip. Würth CAD license and attribution are retained in `Wurth-CAD-LICENSE.txt`. D1's manufacturer STEP is under `../models/U_Wurth_WL-ICLED_1312020030000.step`.

## Status chain at 5 V — 2026-11-24

D1 retains the Würth 1312020030000 and its footprint. D1 VDD now connects to SHUNT_HI, with C3 providing local bypass. The interface pin assignments are unchanged. Use the matching carrier revision with U6 and generate fresh fabrication files for this routed revision.
