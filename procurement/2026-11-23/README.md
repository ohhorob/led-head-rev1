# Board component sourcing — 23 November 2026

Three separate lists were created and verified in Rob's logged-in DigiKey account:

| Board | DigiKey list | Grouped lines | Direct DigiKey shortages |
| --- | --- | ---: | --- |
| Pico carrier | [Pico carrier](https://www.digikey.com/en/mylists/list/FSEIH7W2E7) | 17 | Mini-Fit header |
| String daughtercard | [String daughtercard](https://www.digikey.com/en/mylists/list/2CJ5LZI7OT) | 7 | Exact V6 status LED; right-angle JST header |
| Dedicated 5 V power module | [Power module](https://www.digikey.com/en/mylists/list/HZ4VK28SG5) | 11 | XT60; Mini-Fit header; inductor |

Each online list is for **one board**, grouped by exact orderable part number. The carrier includes all eight card sockets. Cut tape/small quantities are used; no purchases were made. The lists remain non-public. Stock is a snapshot, not a reservation, and price excludes shipping, taxes and possible tariffs.

## Sources for shortages

| Exact part | Required for one carrier + one power board + eight cards | Source | Evidence and limitation |
| --- | ---: | --- | --- |
| Molex 0039281103 / 39-28-1103 | 2 | [Mouser 538-39-28-1103](https://www.mouser.com/en/ProductDetail/Molex/39-28-1103?qs=KHty%2FoMxDPmmZSKus1aviw%3D%3D) | Page retrieved today: 6,634 in stock, $1.68 each. DigiKey direct has none; expected 18 December. |
| Wurth 74439346010 | 1 | [Mouser](https://www.mouser.com/en/ProductDetail/Wurth-Elektronik/74439346010?qs=rQFj71Wb1eVjgfvHnpR1NQ%3D%3D) | Indexed supplier listing shows 681, crawled last week; direct page timed out. Confirm before ordering. DigiKey direct expects replenishment 25 November. |
| AMASS XT60PW-M | 1 | [Jameco 2844439](https://www.jameco.com/z/XT60PW-M-Amass-XT60-Socket-Male-Terminals-45A-500V-2-Pin-Right-Angle-PCB-Mount_2844439.html) | Retrieved listing: 301 available, $0.79 each. Confirm exact supplied suffix/drawing before purchase. |
| JST S3B-XH-A(LF)(SN) | 8 | [Newark 74M4770](https://www.newark.com/jst-japan-solderless-terminals/s3b-xh-a-lf-sn/header-right-angle-3way/dp/74M4770) | Exact part, listing shows 10,511 in stock; quoted UK-stock delivery 4–6 business days. DigiKey and Mouser direct stock are zero. |
| Worldsemi WS2812B-V6, 5050 | 8 | [TME international](https://www.tme.com/us/en-us/details/ws2812b-v6/smd-colour-leds/worldsemi/) | Current retrieved page shows **only 8**. Exact V6 is required for the existing 3.3 V status supply. International offer; delivery and checkout availability still need confirmation. No spares at that listed stock level. |

DigiKey was checked first, followed by Mouser and searches for exact Amazon offers. No verified exact Amazon listing was found for the V6 LED or right-angle XT60, so traceable electronics distributors are recorded instead. Generic WS2812B, WS2812B-B-V6, other packages and connector variants have not been silently substituted.

## What the local files contain

- `*-sourcing.csv`: exact manufacturer part numbers, references, quantities per board, live DigiKey direct stock, recorded prices and fallback URLs/limitations.
- `*-digikey-import.csv`: compact re-import files. Unmatched items remain explicit; these are not all-in-stock order files.
- `schematic-coverage.csv`: every footprint-bearing schematic item, including the mounting holes and edge fingers excluded from purchases.
- `one-carrier-one-power-eight-cards.csv`: combined requirements for an eight-string system, with no spare allowance. It excludes the already-owned Pico and optional future battery telemetry J20.

The inventory was read from the current KiCad schematics, including hierarchy, rather than the old combined-board BOM. PCB reference inventories and footprint IDs were also checked against the schematics, with no extra PCB components or footprint-ID mismatches found. No KiCad design files or routing were changed. This is a purchasing audit, not a new electrical/DFM review.

## Selection details

Previously unspecified 0805 passives use KEMET 100 nF 50 V X7R capacitors and Yageo 1% resistors. Standard 2.54 mm male headers use Samtec TSW series; the two Pico sockets use Sullins PPPC201LFBN-RC. These selections match the existing nominal package/pin geometry. Pico socket height and mechanical clearances should still be checked against the actual socket/model when building an enclosure.

The SS14 diode is explicitly onsemi SS14 in SMA (DigiKey SS14CT-ND). The LED remains Worldsemi V6 and the translator remains TI TXU0101DBVR in SOT-23-6. No replacement semiconductor or revised PCB land pattern is assumed.

The carrier list includes the already-owned **SC1634 Pico 2 WH** as a reference line and **J20 future battery telemetry** as an optional line; remove those from the purchase if not required. Mounting holes and daughtercard J1 fingers are fabricated features, not purchased parts. Loose standoffs, screws, soldering consumables, external peripherals, power supplies, and mating harnesses are outside these board-component lists.

The last observed DigiKey line totals were $44.88 carrier (includes $8 Pico and $0.20 optional J20), $4.96 per daughtercard (excludes unmatched LED; includes backordered JST), and $11.26 power module (excludes unmatched XT60; includes backordered header/inductor). These are **incomplete checkout budgets**, not an immediately shippable all-in price.

Online list notes identify the fallbacks and shortages. DigiKey's CSV export stalled, so the local records were generated from observed list data and independently checked for complete schematic coverage. Rebuild this dated snapshot with `python3 shared/tools/build_procurement_lists.py`; do not interpret rebuilding as refreshing supplier inventory.
