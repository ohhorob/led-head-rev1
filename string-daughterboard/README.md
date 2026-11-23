# String daughterboard

Open `string-daughterboard.kicad_pro` in KiCad Project Manager. This is the existing manually routed daughtercard in the same repository as the carrier and power-manager projects.

One string channel has:

- F1: Littelfuse 0451003.MRL, 3 A fuse.
- **R1: Vishay WSL2512R0250FEA, 25 mOhm, 1%, 1 W, 2512.**
- U1: TXU0101 data translator, followed by R2, 220 ohm.
- J2: right-angle JST-XH output; pin 1 GND, pin 2 DATA, pin 3 string +5 V.
- D1: Worldsemi WS2812B-V6 status pixel on peripheral 3.3 V.
- C1/C2: 100 nF bypass capacitors. The schematic connects them directly beside their device supply pins.

The new shunt value replaces 50 mOhm. At 2 A it drops 50 mV and dissipates 0.10 W. The carrier uses two PAC1934 monitors; the 100 mV sense range corresponds to nominal 4 A full scale with this resistor. Firmware must use 0.025 ohm. The 3 A fuse is not a precise 2 A current limiter.

The R1 footprint now has the value-neutral name `StringCard:Vishay_WSL2512`. Its pad geometry is unchanged. The older `_50mR` library item is retained only as a legacy definition; the current schematic and board use the value-neutral item. No track, via, zone, outline, component position or pad geometry changed during the shunt update.

## Card interface and mechanics

J1 is the PCB edge itself, mating with a carrier-mounted Sullins EBC06DRAS. Do not fit a socket on this daughtercard. Nominal board thickness is 1.6 mm, with six contacts per face at 2.54 mm pitch. The present board is 22 × 26.5 mm overall, including its 17.4 mm wide × 8 mm tongue. Printed rails provide retention; there are no mounting holes on this daughtercard. Check physical mating and card-facing direction with the socket before fabrication.

| Finger | Net | Purpose |
| --- | --- | --- |
| A1, B1 | GND | Parallel power returns |
| A2, B2 | IN_5V | Parallel regulated 5 V input contacts, 2 A nominal total |
| A3 | PERIPH_3V3 | Driver input/status supply |
| B3 | STRING_DATA_IN | 3.3 V string data |
| A4 | SHUNT_HI | Kelvin sense upstream of the shunt, after fuse |
| B4 | STRING_5V | Kelvin sense downstream of shunt |
| A5 | STATUS_DATA_IN | Status pixel input |
| B5 | STATUS_DATA_OUT | Regenerated status output to next slot |
| A6, B6 | Unconnected | Reserved |

A is front copper and B is back copper. Looking at the front with the insertion tip at the bottom, positions 1–6 run left to right. The carrier socket orientation is documented separately; this front-view convention must not be confused with the socket's component-side solder-tail view.

The Kelvin pair carries measurement signals, not load current. Status pixel current comes from PERIPH_3V3 and is not included in the string shunt measurement. Use the specified WS2812B-V6 part; avoid driving an unpowered card. Swaps are power-off only. Enclosure guides must prevent reversed insertion.

## Validation and exports

After the shunt update: zero ERC violations, zero DRC violations, zero unrouted connections and zero schematic-parity issues. The shared checker verifies the edge pinout, card geometry, carrier monitoring connections and R1's selected value/part number.

Existing manufacturing folders are historical snapshots and were not regenerated. The shunt change does not change fabrication copper, but their embedded board metadata or assembly references may still say 50 mOhm. Use the current native design and **WSL2512R0250FEA** for new component purchases.

Do not rerun the archived creation scripts over the routed board. Schematic UUIDs and PCB footprint paths must remain linked so F8 updates the same components.

See [shared interface contract](../shared/README.md), [footprint audit](footprint-audit.md), and [carrier project](../pico-carrier/README.md).
