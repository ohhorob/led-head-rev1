# Daughterboard footprint audit — 19 November 2026

Scope: saved daughterboard, before routing. Assembly method: hand placement
with solder paste and hot-air reflow. This audit supersedes the earlier choice
of oversized iron-soldering pad variants. Part body sizes remain 0805, 1206,
SOT-23-6 and 5050; no tiny QFN/BGA packages are used.

## Results and selected footprints

Dimensions below are millimetres in the footprint's unrotated local coordinates.

| References | Selected footprint | Dimensional and pin checks | Result |
|---|---|---|---|
| U1 | StringCard:TI_TXU0101_DBV0006A_Reflow | Six pads 1.10 × 0.60, X = ±1.30, 0.95 lead pitch. TI DBV0006A example board/stencil layout. Pins 1 VCCA, 2 GND, 3 A, 4 BY, 5 OE, 6 VCCB. | Corrected from oversized iron pads to TI reflow dimensions. |
| D1 | StringCard:Worldsemi_WS2812B_V6_5050_Reflow | Four pads 1.50 × 1.00, X = ±2.45, Y = ±1.65; 3.40 inner horizontal gap and 4.30 overall vertical span. Pin 1 VDD upper left, 2 DOUT lower left, 3 GND lower right, 4 DIN upper right in top view. | Generic footprint's 0.90 pad height increased to manufacturer's 1.00. Copper and schematic pinout agree. |
| R1 | StringCard:Vishay_WSL2512 | Two pads 1.65 × 3.68; inner gap 4.06, centre spacing 5.71. Vishay WSL2512, **0.007–0.5 Ω** resistance range. Fits WSL2512R0250FEA. | Correct; retained. Not a generic 2512 assumption. |
| F1 | StringCard:Littelfuse_451_453_Reflow | Two pads 1.96 × 3.15, inner gap 2.95, outside span 6.87 (manufacturer rounds to 6.86). Nonpolar. | Correct; retained copper dimensions and captured in local library. |
| J2 | StringCard:JST_XH_S3B-XH-A_1x03_P2.50mm_Horizontal | Three holes at 2.50 pitch, 0.95 drill within JST's 0.90–1.00 recommendation; pads 1.70 × 1.95. No locating boss on the specified part. Pin 1 GND, 2 DATA, 3 STRING_5V. | Correct S3B-XH-A side-entry geometry. Through-hole connector, installed after SMT. |
| R2 | StringCard:R_0805_Reflow | KiCad nominal 0805/2012 metric pattern, pads 1.025 × 1.40, centres ±0.9125. | Appropriate for hot-air reflow; no enlargement needed. |
| C1, C2, C6 | StringCard:C_0805_Reflow | KiCad nominal 0805/2012 metric pattern. Nonpolar 100 nF ceramic capacitors. | Appropriate; buy the specified 0805 body size. |
| C3, C7 | StringCard:C_1206_Reflow | KiCad nominal 1206/3216 metric pattern. Nonpolar 10 µF ceramic capacitors. | Appropriate; buy 1206, not a substitute 0805/1210. Check effective capacitance at operating voltage when choosing exact MPN. |
| H1, H2 | MountingHole_2.7mm_M2.5 | 2.70 nonplated clearance holes; no electrical net. | Appropriate for M2.5 hardware. |
| J1 | StringCard:Sullins_EBC06DRAS_Mating_Card_2x06_P2.54mm | Six fingers per face at 2.54 pitch, 12.70 first-to-last span; 1.60 × 6.50 copper fingers, no paste. Board 1.60 thick is within socket's 1.57 ±0.20 specification. | Socket specifications checked; physical fit remains untested. See below. |

All newly selected SMT land patterns are copied into **StringCard.pretty**.
The schematic and PCB reference those local versions, so a system-library
update will not silently change their pad geometry. Existing component
positions, rotations, PCB faces, footprint UUIDs and schematic links were retained.

## Card-edge boundary of this audit

The 17.40-wide tongue was chosen to clear the drawing's nominal 17.78 slot.
Its 8.00 projection allows the socket's 6.73 insertion depth. Finger copper
starts 0.50 from the leading edge and extends 6.50 back. This is a designed
mating edge, **not a manufacturer-supplied mating-card footprint**. The socket
drawing does not fully specify a recommended finger pattern or a guaranteed
mating-card width tolerance. Validate it with a 1:1 print and the actual socket
before ordering boards; a small bare-board fit coupon is preferable if fit is
critical. No physical test has been performed or claimed.

A1–A6 and B1–B6 are our daughterboard contact labels. The future carrier must
map them to Sullins' actual socket A/B numbering and insertion direction using
the connector drawing; do not infer the back-face order from a front view.
The present connector has no polarization feature. Card guides/retention must
prevent reverse insertion. It is power-off swappable only. No solder paste on
the fingers. Keep the mating and manual-bevel area free of other copper.

## Hot-air assembly and routing implications

- 0805 passives are large enough for tweezers and hot air; 1206 bulk ceramics
  and the 5050 pixel are larger still. The SOT-23-6 driver has accessible leads
  and 0.95 pitch. Increasing these package sizes is not necessary.
- Use controlled, similar paste deposits on each pair of passive pads. Large
  asymmetric copper pours can heat unevenly; consider thermal spokes where
  electrically appropriate. Keep shunt sense traces Kelvin-connected to the
  resistor terminals and do not use the sense contacts for load current.
- Avoid vias within solder pads. Leave space for tweezers and the hot-air nozzle.
- Reflow SMT parts before fitting the JST plastic connector. J2 remains a
  conventional through-hole soldering operation; hot air alone is less
  convenient for it than an iron. Do not treat its PA66 housing as an SMT
  reflow-rated component.
- Double-sided placement is allowed, but no components were flipped during
  this audit. Plan the assembly order/support so reheating the second face
  does not release the first face's parts.
- The LED package's chamfer is at **pin 3 / GND**. The footprint's pin-1 marker
  identifies VDD; do not align the chamfer with that marker by assumption.

## Validation

ERC: zero violations. DRC: zero geometric violations. Schematic-to-PCB parity:
zero issues. All 41 connected pad/net assignments checked. Thirty expected
unrouted connections remain: this is not a routed or manufacturing-ready board.
See DRC.json, ERC.json, footprint-audit.json and validation.json.

## Source documents

- TI TXU0101 datasheet, DBV0006A mechanical/board/stencil drawings, printed pages 43–45: https://www.ti.com/lit/ds/symlink/txu0101.pdf
- Worldsemi WS2812B-V6 manufacturer datasheet, package/land pattern and pinout, page 2: https://datasheet.lcsc.com/datasheet/pdf/0689d8fd6dabfc7959e82552d4ffad8b.pdf?productCode=C52917433
- Vishay WSL, document 30100, page 2: https://www.vishay.com/docs/30100/wsl.pdf
- Littelfuse 451/453 dimensions/recommended pad layout: https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1
- JST XH, PCB layout and side-entry header: https://www.jst-mfg.com/product/pdf/eng/eXH.pdf
- Sullins manufacturer drawing C10876 (distributor-hosted copy): https://www.ic-components.ru/files/cc/EBC10DRAS.pdf

Subsequent change: R3 removed, with D1 DIN wired directly to STATUS_DATA_IN.
The status LED requires no inter-pixel series resistor. The earlier 41-pad/30-airwire
counts are historical; see validation.json for current counts.
