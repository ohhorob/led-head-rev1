# Current monitoring for six or eight strings

Research: 2026-11-20. Decision implemented: two PAC1934T-I/JQ devices, eight socket positions, and 25 mOhm WSL2512R0250FEA daughtercard shunts.

## Recommendation

Use two Microchip **PAC1934T-I/JQ** devices for eight independent string measurements. Each provides four high-side shunt measurements, bus-voltage readings and power/energy accumulation over I2C. Its supply and separate I/O supply support the carrier's 3.3 V peripheral rail. The 0–32 V common-mode range covers the 5 V strings without a level-shifting circuit in the measurement path. Two address selections allow both devices on the existing monitor bus.

The JQ version is 16-pin **4 × 4 mm UQFN with 0.65 mm pitch**, not the tiny WLCSP version. This remains a leadless package, but is a reasonable hot-air assembly choice in my judgment. The manufacturer's land pattern provides 0.80 × 0.35 mm peripheral pads. The exposed pad is not internally connected; grounding it is recommended. Treat the footprint as a new, datasheet-checked land pattern rather than reusing the INA3221 footprint by size alone.

DigiKey's retrieved US listing gives **$1.94 each**, approximately **$3.88 for both ICs**, with stock listed. This excludes bypass capacitors, address resistors, shunts, tax, shipping and any tariffs. Listing prices and stock must be checked at purchase; direct retrieval can be intermittent.

## Shunt range needs an explicit decision

PAC1934 and PAC1944 have a 100 mV full-scale shunt measurement range. With the existing 50 mΩ resistor:

- 2 A produces 100 mV: exactly full scale, with no tolerance/transient measurement headroom.
- Above that, measurement clips; the IC is not an electronic current limiter.

My recommendation is **25 mΩ** for a new population of daughtercards. At 2 A this produces 50 mV and dissipates 0.10 W, while the nominal measurement range extends to 4 A. The existing 3 A fuse remains a separate protection function. Select a matching-rated 2512 resistor; changing the resistance need not change the finger interface or routing. Firmware must use the actual shunt resistance. This value change is now implemented in the daughtercard schematic and PCB metadata. Copper and pad geometry are unchanged.

A lower shunt value also changes error as a percentage of measured current. Review the desired low-current accuracy before finalizing; nominal ADC resolution alone is not system accuracy.

## Other candidates examined

| Part | Independent shunt channels | Package | Assessment |
| --- | ---: | --- | --- |
| PAC1934T-I/JQ | 4 | UQFN-16, 4 × 4 mm, 0.65 mm pitch | Preferred balance of cost, routing and hot-air assembly; two devices cover eight strings |
| PAC1944T-E/4MX | 4 | Wettable-flank VQFN-16, 3 × 3 mm, 0.50 mm pitch | Good electrical match; 0–9 V bus range and programmable current/voltage/power alerts; DigiKey lists about $2.02 each, $4.04 for two. Smaller pads than PAC1934 |
| LTC2991 | 4 differential, despite eight voltage-input pins | MSOP-16 with exposed leads | Easier visual solder inspection, but the 5 V common mode requires an appropriate 5 V supply, and guaranteed I2C high threshold is 0.7 × VCC. Therefore it needs bus level translation with the 3.3 V Pico. More expensive and more support circuitry; not preferred |
| LTC2980 | 8 current-capable differential channels | 144-ball, 12 × 12 mm BGA | Genuine one-chip eight-shunt possibility. Its 16-channel power-manager architecture supports current measurement on odd channels, ±170 mV differential and inputs up to 6 V. Excessive package/routing/configuration complexity for this hobby carrier |
| MAX34407/MAX34417 | 4 | Wafer-level ball/bump packages | Functional alternatives, but the package works against the assembly goal |
| INA4235 | 4 | DSBGA | Only 80 mV maximum shunt range and a tiny ball-grid package; not preferred |
| MAX34406 | 4 analog amplifiers | TQFN-24 | Requires a separate ADC, so it is not a direct digital-monitor replacement |
| INA4180/INA4181 | 4 analog amplifiers | TSSOP-20 | Useful leaded-package architecture if QFN avoidance becomes the main goal: two amplifiers plus an eight-channel ADC. Adds circuitry and loses the integrated digital monitor's simplicity |

There is no reason to settle for three INA3221s before considering the inexpensive PAC1934/PAC1944 alternatives.

## Firmware and protection details

The PAC1934's ALERT functions cover conversion/accumulator events; it does not provide the PAC1944's programmable current-limit alert feature. The carrier currently leaves the INA3221 hardware alert outputs unused and uses physical fuses for string protection, so this does not remove an implemented hardware shutdown function. Firmware reads the PAC1934 values and calculates current using the chosen shunts.

Microchip's April 2025 errata DS80001160A describes excess supply current after REFRESH at sampling rates below 1024 samples/s. For affected revision 03h, the stated workaround repeats the mode write around REFRESH. Record this in the future firmware driver; it is not a reason by itself to reject this part.

## Sources checked

- [PAC1934 datasheet: electrical requirements, address selection, package, land pattern and alerts](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/PAC1931-Family-Data-Sheet-DS20005850E.pdf)
- [PAC1934 current silicon errata, April 2025](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/Errata/PAC1931-2-3-4-Silicon-Errata-and-Data-Sheet-Clarification-DS80001160.pdf)
- [PAC1934 DigiKey US listing](https://www.digikey.com/en/products/detail/microchip-technology/PAC1934T-I-JQ/9453134)
- [PAC1944 datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/PAC194X-Family-Data-Sheet-DS20006543.pdf)
- [PAC1944 DigiKey US listing](https://www.digikey.com/en/products/detail/microchip-technology/PAC1944T-E-4MX/13985815)
- [LTC2991 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/2991ff.pdf)
- [LTC2980 datasheet, current-mode limits and package](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc2980.pdf)
- [ADI discussion of current-capable odd channels](https://www.analog.com/en/resources/analog-dialogue/articles/current-sensing-with-pmbus-digital-power-system-managers-part-1.html)
- [MAX34417 package and functionality](https://www.analog.com/en/products/max34417.html)
- [MAX34406 analog-output architecture](https://www.analog.com/en/products/max34406.html)
- [TI INA4180 quad analog current-sense amplifier](https://www.ti.com/product/INA4180)
- [TI INA4181 quad analog current-sense amplifier](https://www.ti.com/product/INA4181)
- [TI INA4235 package and measurement range](https://www.ti.com/product/INA4235)
