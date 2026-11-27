#!/usr/bin/env python3
"""Verify the two power-manager/carrier cables against fresh KiCad netlists and PCB pads."""
from pathlib import Path
import json, subprocess, tempfile, xml.etree.ElementTree as ET
import shutil
from check_interfaces import parse, kids, kid, value
ROOT=Path(__file__).resolve().parents[2]
CLI=shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def main():
    contract=json.loads((ROOT/'shared/interfaces/power-manager-v1.json').read_text())
    errors=[];checks=[];projects={}
    for cable in contract['cables']:
        for end in cable['endpoints']:
            name=end['project'];ref=end['reference'];base=ROOT/name
            expected=end.get('contacts',cable['contacts'])
            if name not in projects:
                with tempfile.TemporaryDirectory() as temp:
                    output=Path(temp)/'nets.xml'
                    subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(output),str(base.with_suffix('.kicad_sch'))],check=True,capture_output=True)
                    netlist=ET.parse(output)
                board=parse(base.with_suffix('.kicad_pcb').read_text())
                projects[name]=(netlist,board)
            netlist,board=projects[name]
            actual={node.get('pin'):net.get('name') for net in netlist.findall('./nets/net') for node in net.findall('node') if node.get('ref')==ref}
            if actual!=expected:errors.append(f'{name}/{ref}: schematic pinout {actual} differs from contract')
            fps=[f for f in kids(board,'footprint') if any(value(p[1])=='Reference' and value(p[2])==ref for p in kids(f,'property'))]
            if len(fps)!=1:errors.append(f'{name}/{ref}: found {len(fps)} PCB footprints');continue
            f=fps[0]
            if value(f[1])!=end.get('footprint',cable['footprint']):errors.append(f'{name}/{ref}: wrong footprint assignment')
            actual={value(p[1]):value(kid(p,'net')[-1]) if kid(p,'net') else None for p in kids(f,'pad') if value(p[1])}
            if actual!=expected:errors.append(f'{name}/{ref}: PCB pinout {actual} differs from contract')
            checks.append(f'{name}/{ref}: {len(expected)} pins checked')
        if 'wiring' in cable:
            ends=cable['endpoints']
            left=ends[0].get('contacts',cable['contacts']);right=ends[1].get('contacts',cable['contacts'])
            wires=cable['wiring']
            if set(w['from_pin'] for w in wires)!=set(left) or set(w['to_pin'] for w in wires)!=set(right):
                errors.append(cable['name']+': incomplete cable wiring')
            for wire in wires:
                if left.get(wire['from_pin'])!=right.get(wire['to_pin']):errors.append(cable['name']+': cable connects different nets')
    print('\n'.join(checks+errors))
    if errors:raise SystemExit(1)
    print('PASS: registered power and reserved telemetry pinouts agree between schematics, PCBs and the shared contract.')
if __name__=='__main__':main()
