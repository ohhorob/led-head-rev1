# Carrier assembly preview

The carrier PCB has model references for eight assembled string daughtercards on J21-J28 and a Pico 2 W on J10, with two male header strips. All routing and footprint positions are unchanged.

Daughtercard source: current string-daughterboard/string-daughterboard.kicad_pcb, STEP export at origin (20,26.5) mm. Export includes all available component STEP models; F1 uses the project Littelfuse model and R1 uses the generic KiCad 2512 resistor envelope. String_daughtercard_assembled.step is the flat export. String_daughtercard_inserted.step is oriented for the vertical sockets: x flipped, front copper facing the project A row, nominal insertion depth 7.54 mm, card tip 7.95 mm above carrier top. Card thickness is centered in the slot. The exported dielectric solid is z=0..1.51 mm, so the inserted model applies y=source_z-0.755 mm (corrected from +0.8 mm on 2026-11-21).

These are snapshots: re-export after daughtercard mechanical/component-placement changes. KiCad does not live-link separate PCB files.

Pico source: https://github.com/gowthambiraj/rpi-pico2w-kicad/blob/main/Raspberrypi%20pico2%20W.step (community model, retrieved 2026-11-21). Not manufacturer-certified. Body dimensions checked: 21 x 51 x 1 mm; USB at the pin-1/pin-40 end. Model does not include the WH JST SWD socket. Raw model kept as Raspberry_Pi_Pico_2_W_community.step; normalized copy Raspberry_Pi_Pico_2_W_socketed.step positions board underside 11.04 mm above carrier, based on the generic 8.50 mm female socket plus 2.54 mm male header spacer. Actual connector stack height should be checked if using this for an enclosure. Male header models retain their solder tails.

Pico references are PCB-local on J10; refreshing J10 from the stock KiCad footprint library may remove them. Daughtercard references are also included in the project's DCWN socket library footprint, so socket refreshes retain them. Individual models can be hidden via footprint Properties > 3D Models.

Verification: all non-model PCB S-expressions are identical before and after adding these model references. Board saved to disk; reload the open PCB before saving in KiCad.

## Power connector J19

Molex_0039281103_simplified.step is a generated visualization, not manufacturer CAD. Model envelope 22.20 x 9.60 x 12.80 mm, pin pitch 4.20 mm, tail rows 5.50 mm, tail length 3.50 mm. Cavities, latch and contacts simplified; do not use for detailed mating/retention checks. Drawing: Molex catalog reproduced at https://static.rapidonline.com/pdf/22-3810e.pdf page 2. Matching KiCad model was absent from local installation and upstream library; Molex STEP downloads timed out. Only the existing J19 model filename changed in PCB.

### J19 exact model replacement

Replaced the simplified J19 model with the downloaded TraceParts/Molex exact-part 0039281103 STP, source archive 195927578-659-0039281103.zip (reference 39281103, no PCB retention pegs). Original kept as Molex_0039281103_source.stp. Normalized copy Molex_0039281103.step: x=-X+8.4, y=Z-2.55, z=Y. Body aligns with existing footprint: x=-2.7..19.5, y=-7.35..2.25; tail row centers y=0,-5.5; pin pitch 4.2; height 12.8; tail length 3.5. Solid validated. Model filename is the only PCB change. This supersedes the simplified-model notes above.
