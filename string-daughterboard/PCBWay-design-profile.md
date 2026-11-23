# PCBWay two-layer design profile

Configured 20 November 2026 for this daughterboard. This is a project-specific
standard-process profile, not a claim that PCBWay has one universal set of
limits for every material, thickness, colour and copper weight.

## Ordering specification matched by the design

Two copper layers, FR-4, 1.6 mm nominal finished thickness, 1 oz copper per
side, green solder mask, white legend, ENIG finish. SMT assembly is by the
user. Both PCB faces can carry components. Ordinary plated through vias,
tented on both sides. No blind/buried vias, microvias, filled/capped via-in-pad,
controlled impedance or castellated edges. ENIG on the card fingers and
occasional power-off swapping are intentional; hard gold and factory bevel
are not selected. These order options still need to be entered on PCBWay's
quote; the KiCad profile does not change any online order.

The stackup records 0.035 mm copper on each face, 0.01 mm mask per face and
a nominal 1.51 mm FR-4 core to sum to 1.60 mm. Core construction, dielectric
constant and loss tangent are nominal modelling values, not a contracted
PCBWay laminate or impedance stackup. Finished board thickness tolerance
must remain compatible with the card socket.

## Routing and DRC settings

| Setting | Installed value |
|---|---:|
| Minimum copper clearance | 0.20 mm |
| Minimum track width | 0.15 mm |
| Default signal width | 0.25 mm |
| PERIPH_3V3 netclass width | 0.40 mm |
| IN_5V, SHUNT_HI, STRING_5V netclass width | 1.20 mm |
| Default through via | 0.70 mm pad / 0.30 mm hole |
| Additional via presets | 0.80/0.40 and 1.00/0.50 mm |
| Minimum via diameter / drilled hole | 0.60 / 0.30 mm |
| Minimum annular ring | 0.15 mm |
| Hole-to-hole clearance | 0.30 mm |
| Copper-to-hole clearance | 0.25 mm |
| Copper-to-routed-board-edge clearance | 0.30 mm |
| Via copper ring to any pad copper, including same net | 0.10 mm |
| Solder mask expansion | 0.05 mm per side |
| Mask minimum web | 0.11 mm |
| Mask opening to unrelated copper | 0.05 mm |
| Solder paste margin and percentage adjustment | 0 / 0 |
| Minimum legend height / stroke | 0.80 / 0.15 mm |
| Legend clearance to mask openings and other legend | 0.15 mm |
| Default new legend size / stroke | 1.00 / 0.15 mm |

Track presets: 0.20, 0.25, 0.30, 0.40, 0.50, 0.80, 1.00, 1.20, 1.50,
2.00 mm plus netclass selection. Auto-inherit width from an existing track is
turned off in the project's local settings so it does not unexpectedly keep
an old narrow width. Choose netclass width in the routing toolbar when you
want the per-net defaults. Manual width overrides still work; KiCad checks
the hard minimum. Do not enable routing that ignores DRC violations.

Power widths are routing defaults, not proof of current/temperature capability.
The shunt's Kelvin sense routes share the SHUNT_HI/STRING_5V nets but can be
manually narrowed as sense-only conductors. Check complete 2 A paths, pad
fanouts, shared returns and via current sharing before fabrication release.

No via-to-pad exemption is made for same-net copper. The custom rule deliberately
flags vias in or touching pads. It avoids the earlier assembly/process issue.
Blind, buried and microvias are prohibited by a separate custom rule.

## Ground zones

Existing zone outlines, net assignments and priority are retained. Their local
settings and new-zone defaults now use 0.20 mm clearance, 0.20 mm minimum
fill width, 0.25 mm thermal gap and 0.30 mm thermal spokes. This is a layout
choice, not a PCBWay-mandated thermal pattern. Two connected thermal spokes
are required. Island removal is retained. Fill does not join copper across
the laminate: the two ground planes still need a physical ground connection.

## Published limits versus our margin

PCBWay's standard capabilities page lists 0.10 mm minimum track/spacing,
0.15 mm annular ring and 0.25 mm routed copper-to-edge spacing. Its detailed
1 oz process table uses larger values for routine work; we chose 0.15 mm
minimum tracks and 0.20 mm spacing rather than targeting the absolute limit.
The 0.30 mm drill choice also avoids tiny-hole processing. Green mask is
specified because its mask-bridge requirements are less restrictive than
some other colours. For 1 oz green mask, their guidance calls for at least
0.19 mm IC copper-pad spacing to retain a bridge; U1 has 0.35 mm.

Reference pages, checked 20 November 2026:
- https://www.pcbway.com/capabilities.html
- https://www.pcbway.com/pcb_prototype/PCB_Solder_mask.html
- https://www.pcbway.com/pcb_prototype/PCB_Silkscreen.html
- KiCad rule semantics: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html

## Validation and present findings

The custom rules parse and execute under KiCad 10. The existing 57 track/via
items were preserved, including their positions and widths. No tracks were
rerouted or added, and no footprints were replaced by this configuration.
DRC with zone refill reports:

- Two pad/via clearance findings around the GND card-edge contacts.
- Six legend clearances/overlaps.
- Four missing electrical connections (PERIPH_3V3 between faces, ground pours,
  the two IN_5V card-edge contacts, and SHUNT_HI to the edge contact).
- Nine footprint-ID mismatches: the saved PCB contains older footprint versions,
  whereas the schematic requests the audited local reflow footprints. Resolve
  this deliberately before replacing pads under existing routing.

See PCBWay-profile-DRC.json for current locations. These are reported, not
suppressed. This profile is ready to guide further layout; the board is not
yet a clean manufacturing release. DRC does not check all milling radii,
card insertion fit, tolerances, soldering process, thermal performance or
connector orientation. Use a real-socket fit check and final Gerber/drill review.

Close and reopen the entire project to load all project/board/custom-rule settings.
Do not save a stale PCB Editor window over these disk changes. Refill zones
with B after reopening; the validation run refilled in memory without changing
existing routes. The pre-change files are backed up in the repository's .history.
