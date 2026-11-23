# Sullins EBC06DCWN model and footprint verification

Verified against Sullins engineering drawing C11424 Revision D (CW/CT termination), sheets 1-3. Local copy: ../shared/reference/Sullins_C11424_RevD_CW_CT.pdf.

The no-ear N housing uses dimension C = 21.84 mm for six positions. Overall depth = 9.40 mm, height above seating plane = 15.49 mm. Earlier use of F = 19.05 mm as the body length was incorrect; corrected 2026-11-21.

## Land pattern

- Six positions per row, 12 pads total.
- Pitch 2.54 mm; end-to-end pin-center span 12.70 mm (dimension A).
- Row spacing 5.08 mm, pad center coordinates y = +/-2.54 mm.
- No mounting-ear holes.
- 1.10 mm finished plated holes, exceeding manufacturer minimum 0.89 mm; CW tails nominal 0.64 x 0.38 mm.
- Oval pads 1.70 x 2.20 mm; narrow annulus 0.30 mm.
- 0.25 mm track midway between pads has 0.295 mm clearance each side.
- Fab outline 21.84 x 9.40 mm; courtyard adds 0.50 mm all around.
- Project A/B pad numbering retained to match schematic and daughtercard. A1 is a project identifier, not a claim about manufacturer's odd/even pin numbers. The unkeyed daughtercard must be inserted with the intended A/B face orientation; inverted insertion is not electrically equivalent.

## 3D model

Sullins_EBC06DCWN_simplified.step is a generated, valid solid mechanical preview with correct envelope and tail centers. Includes 3.18 mm tails and approximate slot (internal springs omitted). Do not use its simplified interior for a precision mating/contact simulation.

The original user-supplied EBC06D_straight.step has 5.08 mm row spacing but a right-angle-family eared housing. The later EBC06DCWN.step has approximately correct 19.05 x 9.40 x 15.49 envelope dimensions except that length is too short, and 3.81 mm tail row spacing. Both originals remain untouched in Downloads and are not attached to the footprint.

## Current PCB

At verification time the saved pico-carrier PCB still has DRAS footprints with 3.96 mm row spacing. Neither PCB nor schematic was changed by this verification. Update from schematic with footprint replacement enabled, then refresh from library to obtain the corrected outline. Actual fit has not been tested with a connector sample.
