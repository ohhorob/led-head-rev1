# Shared board interfaces

The repository contains separate KiCad projects for separate physical boards. Open each `.kicad_pro` in Project Manager; its schematic and PCB share a basename. F8 updates that project's board only. Keep revisions in Git, not in copied project directories.

| Project | Responsibility | State |
| --- | --- | --- |
| `string-daughterboard` | One string's fuse, shunt, data translator, output connector and status pixel | Existing routed board, unchanged by this setup |
| `pico-carrier` | Pico 2 W, peripheral buses, current monitoring and daughtercard sockets | Populated schematic and unrouted PCB draft |
| `power-manager` | Input protection/selection, Pololu interface and peripheral 3.3 V supply | Empty starter project |

The original root-level `led-head-rev1` project remains the earlier combined board and a source of proven circuits/models. It is not automatically synchronized with the new boards. Control connectors and current monitoring have been migrated into the carrier; power-manager circuitry has not yet been migrated.

## Daughtercard interface v1

`interfaces/string-card-v1.json` is the explicit interface contract. `Interfaces.kicad_sym` provides `Interfaces:StringCardInterface` with the same 12 contact identifiers and no default footprint. The daughtercard retains its existing libraries and geometry. Future changes to the interface must update the contract, symbol and both mating designs together.

| Contact | Daughtercard net | Purpose/direction at daughtercard |
| --- | --- | --- |
| A1, B1 | GND | Power return |
| A2, B2 | IN_5V | 5 V input, paired power contacts |
| A3 | PERIPH_3V3 | 3.3 V input for status pixel and input-side logic |
| B3 | STRING_DATA_IN | 3.3 V data input |
| A4 | SHUNT_HI | Kelvin sense upstream of the shunt, after the fuse |
| B4 | STRING_5V | Kelvin sense downstream of the shunt |
| A5 | STATUS_DATA_IN | Status pixel data input |
| B5 | STATUS_DATA_OUT | Status pixel regenerated data output |
| A6, B6 | Unconnected | Reserved |

The sense contacts are measurements on the 5 V path, **not GPIO-level inputs**. Connect them to the current monitor's appropriate differential inputs. Each slot needs distinct string-data and sense nets. Status pixels can be chained; the final chain and GPIO assignments are not assigned yet. Shared 3.3 V must come from the planned peripheral regulator rather than relying on the Pico regulator's capacity.

## Mechanical contract

The card is 22 × 26.5 mm overall, with a 17.4 mm wide, 8 mm long tongue, nominal 1.6 mm board thickness and 2.54 mm contact pitch. The contract records the exact current outline and contact geometry so accidental changes are detected.

Contact convention: look at the daughtercard front, with the insertion tip at the bottom. A contacts are front copper, B contacts are back copper; positions 1–6 run left to right. This convention is not a verified drawing of the socket's solder-tail layout. Before creating/placing the **Sullins EBC06DRAS socket footprint**, verify the manufacturer drawing, numbering, mating face and physical part. Do not use the daughtercard finger footprint as the carrier socket land pattern. Allow space for the socket body/ears and the printed rails, with component clearance on both card faces. Carrier size, slot pitch and rail locations remain unassigned.

## Checking interfaces

From the repository root:

```sh
python3 shared/tools/check_interfaces.py
```

Requires KiCad CLI (`kicad-cli` on PATH, or the standard macOS installation). The checker exports a fresh schematic netlist into a temporary directory, then compares the interface against the actual PCB and schematic UUID path. It also checks daughtercard thickness, outline, contact location, size and face. It never writes design files.

When a carrier socket exists, add an entry to `carrier_instances` in the JSON contract:

```json
{
  "project": "pico-carrier/pico-carrier",
  "reference": "J_SLOT1",
  "contacts": {
    "A1": "GND", "B1": "GND",
    "A2": "IN_5V", "B2": "IN_5V",
    "A3": "PERIPH_3V3", "B3": "SLOT1_DATA",
    "A4": "SLOT1_SENSE_P", "B4": "SLOT1_SENSE_N",
    "A5": "SLOT1_STATUS_IN", "B5": "SLOT1_STATUS_OUT",
    "A6": null, "B6": null
  }
}
```

The example names are proposed local carrier net names, not assigned GPIOs. A pass with no carrier entries verifies the daughtercard only; the tool explicitly reports that limited coverage. It does not prove the physical socket orientation, current capacity, routing quality or overall electrical function. Continue to run ERC, DRC and schematic parity for each completed project.

The power-manager/carrier connector is deliberately not assigned. Establish its required current, supply rails, control/status signals and mechanical stack before freezing that second interface. Keep decoupling capacitors connected directly beside the supply pins they serve in the schematic.

## Carrier migration update

Eight carrier socket instances and two PAC1934 monitors are now registered. The carrier uses a common socket footprint in `Interfaces.pretty`, based on the Sullins C10876-K drawing. Physical mating still requires verification. See the carrier README for the checks and unfinished layout items, and its `power-connection-options.md` for interconnect choices.

## Selected monitoring hardware

Two PAC1934T-I/JQ devices replace the INA3221: U4 monitors slots 1–4 at I2C address 0x10; U5 monitors slots 5–8 at 0x1F. Both share the original monitor bus. The daughtercard's R1 is now 25 mOhm, WSL2512R0250FEA, with unchanged pads and routing. The interface checker also verifies monitor pin mappings and the selected shunt identity/value.
