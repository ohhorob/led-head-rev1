Current power-manager update: dedicated regulated-5-V input module using Rob's WEBENCH TPS62091 circuit. It connects to carrier J19 using the existing ten-pin Mini-Fit power cable. A separate battery module is deferred; carrier J20 is reserved for it. See ../power-manager/README.md. The comparisons below are historical.

# Selected carrier power connection

J19 now uses a 10-position Molex Mini-Fit Jr 0039281103, with 0039012100 mating housing and 0039000039 female contacts. Pins 1–4 are parallel regulated 5 V inputs, pin 5 is peripheral 3.3 V, pins 6–10 are ground returns. Both regulated rails use one connector. This supersedes the earlier four-circuit power/separate signal-connector proposal. Review exact derating, harness construction and the expanded system power budget before fabrication; the power-manager mating circuitry is unfinished.

[Carrier connection details](README.md#power-board-input).

The earlier comparison and four-pin cost estimate below are retained as discussion history; they are not the current 10-position connector BOM or price quotation.

# Earlier connection options

Design discussion, 2026-11-20. Mini-Fit Jr is the preferred family, but the final circuit count, ratings and orientation have not been selected or placed. The carrier has now expanded to eight slots: 16 A for strings at 2 A each, plus overhead. The four-contact cable discussed below was an initial smaller-system option, not an approved 16 A interconnect.

## Load to design for

The initial carrier has three 2 A string channels: up to 6 A at 5 V for the strings, plus Pico, NeoTrellis and peripheral overhead. A five-card version would need up to 10 A for strings alone. These are connector/distribution targets, not a claim that the Pololu converter or battery system supports them. The original battery-mode budget was lower; review converter thermal limits and the aggregate load separately.

The interconnect carries regulated 5 V and common ground. The separate peripheral regulator supplies PERIPH_3V3; do not connect it to the Pico's 3V3(OUT). The power manager may also supply PG, source identification and a battery-voltage signal scaled safely for a 3.3 V ADC. Do not carry raw battery voltage onto an ADC pin. No auto source-selection circuit is proposed.

## Options

| Option | Arrangement | Advantages | Tradeoffs |
| --- | --- | --- | --- |
| **Short keyed cable — recommended for the first version** | Four-circuit Mini-Fit Jr power harness, using two +5 V and two GND circuits, plus a small separate connector for 3.3 V and status | Flexible board spacing; positive latch and polarization; easy to disconnect for bench work; through-hole headers | Requires crimps or a suitable premade harness; occupies edge space; two connectors |
| **2.54 mm header stack — best if minimum cost and a direct stack matter most** | A specified male/female pair, e.g. Samtec TSW/SSW; approximately 2×10 with several parallel power/ground contacts | Familiar through-hole soldering; inexpensive layout; power and control in one interface | Requires exact alignment, mating height and standoff spacing; exposed pins can be misaligned; generic headers do not have a dependable universal current rating |
| **Direct power connector stack** | A matched Mini-Fit board-to-board or Micro-Fit BMI pair, with a separate signal header if needed | Keyed power connection; no main power cable | More mechanical constraints and part-specific footprints; less attractive while board spacing is still changing |

Molex's cable selection guide lists Mini-Fit Jr at up to 9 A and Micro-Fit at up to 8.5 A for the listed families. These are maximum family ratings, not a promise for every terminal, circuit count, wire gauge or ambient temperature. Select the exact header, housing and terminal combination and check its derating table. Two power and two ground circuits aim to reduce individual contact load; do not simply double a catalogue maximum and declare the assembly rated for that total.

For the 2×10 option, a reasonable starting allocation is five +5 V contacts, five GND contacts, two peripheral 3.3 V contacts, PG, source selection, battery ADC and five spare contacts. At 6 A, five equally loaded power contacts carry 1.2 A each; at 10 A, 2 A each. Contact resistance and routing cause unequal sharing, so these are nominal allocation figures. Samtec's TSW/SSW specification quotes 4.7 A with **one pin powered per row**; this cannot be applied unchanged to a fully loaded connector. Check the multi-contact derating and chosen mating height before finalizing the stack. Put standoffs or printed supports near the connector so it does not carry the board's mechanical load.

## Suggested first-version harness

The high-current four-circuit connector carries 5 V, 5 V, GND and GND. The small connector carries peripheral 3.3 V, GND, PG, source select, divided battery ADC and a spare. This is a proposed signal set, not a frozen pin-number assignment. The ADC divider, PG/source signal voltage levels and power sequencing still need circuit review in the power-manager project.

A short premade harness can avoid buying a dedicated crimp tool, provided the exact connectors, terminal ratings, conductor size and pinout match. No price or stock claim has been made here.

## Sources

- [Molex cable assembly design guide, connector-selection table](https://www.molex.com/content/dam/molex/molex-dot-com/en_us/pdf/design-guides/987652-0361.pdf)
- [Molex Mini-Fit family, including board-to-board configurations](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/mini-fit-connectors)
- [Molex Micro-Fit family and BMI configurations](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/micro-fit-connectors)
- [Samtec TSW/SSW product specification, current-rating test conditions](https://suddendocs.samtec.com/productspecs/tsw-sxx.pdf)

## Preferred family and DigiKey cost check — 2026-11-20

User accepts Mini-Fit provided its DigiKey cost is reasonable. Use the four-circuit Mini-Fit Jr cable approach as the preferred direction. Header orientation, final pin numbering and exact derated current still require confirmation before adding the connector to both boards.

DigiKey's retrieved USD listings give this connector-only budget for the complete board-to-board cable link:

| Part | Manufacturer part | Quantity | Listed unit price | Extended |
| --- | --- | --- | --- | --- |
| Vertical four-contact PCB header | 0039281043 | 2 | $0.85 | $1.70 |
| Four-contact cable housing | 0039012040 | 2 | $0.31 | $0.62 |
| Loose female crimp contact, 18–24 AWG | 0039000039 | 8 | $0.17 | $1.36 |
| Total | | | | **$3.68** |

Sources: https://www.digikey.com/en/products/detail/molex/0039281043/61400 ; https://www.digikey.com/en/products/detail/molex/0039012040/61376 ; https://www.digikey.com/en/products/detail/molex-llc/0039000039/61448 . These are retrieved listing prices, not a checkout quotation; direct retrieval of some pages was blocked. Wire, the separate low-current signal connector, tax, shipping, any tariff and tooling are excluded. Confirm prices at checkout. If a suitable crimp tool is unavailable, compare precrimped leads or a premade harness before ordering loose contacts.
