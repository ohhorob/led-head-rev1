# Via-in-pad audit

Source: saved led-head-rev1.kicad_pcb; SHA-256 bce7216808801950b9206546fa36873a195d98d8c8c29d615a7dbb08715328b2

42 pads have via-hole overlap (45 pad/via intersections). 2 additional pads touch a via copper ring only. No layout changes made.

Coordinates are absolute KiCad board X/Y in mm, with Y increasing downward. These are via-center coordinates, not component origins. Assessment uses the actual pad copper polygons and circular via drills, on each external copper layer. Copper-only contact is listed separately; it is not a drilled hole inside a pad. Plated holes belonging to connector footprints are not counted as vias.

## Via holes overlapping pads

| Reference | Pad | Net | Side | Via center X, Y (mm) | Drill (mm) | Center location |
|---|---|---|---|---|---|---|
| C40 | 1 | 3V3 | F.Cu | 32.0000, 28.8000 | 0.30 | Inside pad |
| C40 | 2 | GND | F.Cu | 32.0000, 30.5000 | 0.30 | Inside pad |
| C41 | 2 | GND | F.Cu | 81.0000, 13.0000 | 0.30 | Inside pad |
| C42 | 2 | GND | F.Cu | 93.0000, 10.0000 | 0.30 | Inside pad |
| C43 | 2 | GND | F.Cu | 91.0000, 35.0000 | 0.30 | Inside pad |
| C44 | 2 | GND | F.Cu | 82.5000, 35.0000 | 0.30 | Inside pad |
| C45 | 1 | BAT_DELAY_N | F.Cu | 90.5000, 42.7500 | 0.30 | Inside pad |
| C46 | 1 | STATUS_3V3 | F.Cu | 84.2500, 46.0000 | 0.30 | Inside pad |
| C46 | 2 | GND | F.Cu | 85.7500, 45.7500 | 0.30 | Inside pad |
| C53 | 2 | GND | F.Cu | 9.5000, 5.0000 | 0.30 | Inside pad |
| C54 | 2 | GND | F.Cu | 33.0000, 1.5000 | 0.30 | Inside pad |
| C55 | 2 | GND | F.Cu | 49.0000, 1.5000 | 0.30 | Inside pad |
| C56 | 2 | GND | F.Cu | 16.0000, 51.0000 | 0.30 | Outside pad; hole intersects edge |
| C57 | 2 | GND | F.Cu | 16.0000, 43.5000 | 0.30 | Inside pad |
| C58 | 2 | GND | F.Cu | 64.0000, 6.5000 | 0.30 | Inside pad |
| D5 | 1 | GND | F.Cu | 72.0000, 3.5000 | 0.30 | Outside pad; hole intersects edge |
| D6 | 1 | GND | F.Cu | 68.0000, 3.5000 | 0.30 | Outside pad; hole intersects edge |
| D7 | 1 | GND | F.Cu | 12.0000, 9.0000 | 0.30 | Inside pad |
| D7 | 2 | STATUS_RGB_1 | F.Cu | 15.0000, 9.0000 | 0.30 | Inside pad |
| D8 | 1 | GND | F.Cu | 29.0000, 9.0000 | 0.30 | Inside pad |
| D9 | 1 | GND | F.Cu | 46.0000, 9.0000 | 0.30 | Inside pad |
| F1 | 1 | LED_5V | F.Cu | 25.3175, 25.1537 | 0.40 | Inside pad |
| F1 | 1 | LED_5V | F.Cu | 25.3175, 26.4463 | 0.40 | Inside pad |
| F2 | 1 | LED_5V | F.Cu | 42.3175, 26.4463 | 0.40 | Inside pad |
| F2 | 1 | LED_5V | F.Cu | 42.3175, 25.1537 | 0.40 | Inside pad |
| F3 | 1 | LED_5V | F.Cu | 59.3175, 26.4463 | 0.40 | Inside pad |
| F3 | 1 | LED_5V | F.Cu | 59.3175, 25.1537 | 0.40 | Inside pad |
| J13 | 3 | GND | F.Cu | 29.5000, 62.5000 | 0.30 | Inside pad |
| R1 | 1 | BUCK_EN | F.Cu | 83.0000, 29.2500 | 0.30 | Inside pad |
| R1 | 2 | GND | F.Cu | 85.0000, 29.0000 | 0.30 | Inside pad |
| R3 | 2 | GND | F.Cu | 67.0000, 32.0000 | 0.30 | Inside pad |
| R43 | 2 | GND | F.Cu | 91.0000, 4.5000 | 0.30 | Inside pad |
| R44 | 1 | EXT_5V | F.Cu | 81.0000, 16.8250 | 0.30 | Inside pad |
| R44 | 2 | GND | F.Cu | 81.0000, 14.5000 | 0.30 | Inside pad |
| R52 | 2 | GND | F.Cu | 87.5000, 4.5000 | 0.30 | Outside pad; hole intersects edge |
| U1 | 2 | GND | F.Cu | 27.0000, 18.0000 | 0.30 | Inside pad |
| U2 | 2 | GND | F.Cu | 44.0000, 18.0000 | 0.30 | Inside pad |
| U3 | 2 | GND | F.Cu | 61.0000, 18.0000 | 0.30 | Inside pad |
| U6 | 1 | GND | F.Cu | 84.7500, 34.0000 | 0.30 | Inside pad |
| U6 | 4 | GND | F.Cu | 87.2500, 36.0000 | 0.30 | Inside pad |
| U6 | 5 | GND | F.Cu | 87.2500, 33.7500 | 0.30 | Inside pad |
| U7 | 1 | GND | F.Cu | 85.7500, 42.0000 | 0.30 | Inside pad |
| U7 | 2 | GND | F.Cu | 85.7500, 43.0000 | 0.30 | Inside pad |
| U7 | 6 | PG | F.Cu | 88.0000, 41.7500 | 0.30 | Inside pad |
| U8 | 4 | STATUS_RGB_1 | F.Cu | 19.9500, 45.8125 | 0.30 | Inside pad |

## Copper-ring contact only

| Reference | Pad | Net | Via center X, Y (mm) |
|---|---|---|---|
| R42 | 2 | GND | 82.0000, 2.5000 |
| U7 | 5 | STATUS_3V3 | 87.2500, 43.0000 |
