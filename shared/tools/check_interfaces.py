#!/usr/bin/env python3
"""Read-only interface verification from freshly exported schematic netlists and PCBs.
Run: python3 shared/tools/check_interfaces.py [--contract PATH]
Carrier registrations use project, reference and a complete contacts mapping.
"""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]

def parse(text):
    stack = []
    root = None
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            else:
                root = node
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(token)
    if stack:
        raise ValueError('Unbalanced KiCad file')
    return root

def kids(node, name):
    return [v for v in node if isinstance(v, list) and v and v[0] == name]

def kid(node, name):
    return next(iter(kids(node, name)), None)

def value(token):
    return json.loads(token) if token.startswith('"') else token

def close(a, b):
    return math.isclose(float(a), float(b), abs_tol=0.005)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, default=ROOT/'shared/interfaces/string-card-v1.json')
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    cli = shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
    def check(project, reference, expected, mechanical=False):
        base = ROOT/project
        with tempfile.TemporaryDirectory(prefix='pico-interface-') as folder:
            xml = Path(folder)/'nets.xml'
            subprocess.run([cli, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml), str(base.with_suffix('.kicad_sch'))], check=True, capture_output=True, text=True)
            tree = ET.parse(xml)
        require(tree.find(f"./components/comp[@ref='{reference}']") is not None, f'{project}: missing schematic {reference}')
        schematic = {}
        for net in tree.findall('./nets/net'):
            for node in net.findall('node'):
                if node.get('ref') == reference:
                    schematic[node.get('pin')] = net.get('name')
        board = parse(base.with_suffix('.kicad_pcb').read_text())
        footprints = [f for f in kids(board, 'footprint') if any(value(p[1])=='Reference' and value(p[2])==reference for p in kids(f, 'property'))]
        require(len(footprints)==1, f'{project}: expected one PCB {reference}, found {len(footprints)}')
        if len(footprints)!=1:
            return
        footprint = footprints[0]
        pads = {value(p[1]):p for p in kids(footprint, 'pad') if value(p[1])}
        require(set(pads)==set(expected), f'{project}/{reference}: PCB contact set differs from contract')
        for pin, net in expected.items():
            actual = schematic.get(pin)
            if net is None:
                require(actual is None or actual.startswith('unconnected-('), f'{project}/{reference}.{pin}: reserved contact connected to {actual}')
            else:
                require(actual==net, f'{project}/{reference}.{pin}: schematic {actual!r}, expected {net!r}')
            if pin not in pads:
                continue
            n = kid(pads[pin], 'net')
            actual_pcb = value(n[-1]) if n else None
            require(actual_pcb==net or (net is None and actual_pcb and actual_pcb.startswith('unconnected-(')), f'{project}/{reference}.{pin}: PCB {actual_pcb!r}, expected {net!r}')
        # Check the stable symbol/footprint path used by F8 synchronization.
        component = tree.find(f"./components/comp[@ref='{reference}']")
        if component is not None:
            sheet = component.find('sheetpath')
            stamp = component.findtext('tstamps', '').strip().split()[0:1]
            if sheet is not None and stamp:
                expected_path = sheet.get('tstamps', '').rstrip('/')+'/'+stamp[0]
                path = kid(footprint, 'path')
                require(path is not None and value(path[1])==expected_path, f'{project}/{reference}: schematic/PCB UUID path mismatch')
        if mechanical:
            m = contract['mechanical']
            require(close(kid(kid(board,'general'),'thickness')[1],m['thickness_mm']), 'Card thickness differs from contract')
            pos = kid(footprint,'at')
            ox,oy = map(float,pos[1:3]);angle=float(pos[3]) if len(pos)>3 else 0
            require(close(angle,0), 'Card connector rotated; mechanical contract must be reviewed')
            for pin,pad in pads.items():
                at=kid(pad,'at');size=kid(pad,'size')
                require(close(ox+float(at[1]),m['contact_centres_x_mm'][int(pin[1:])-1]) and close(oy+float(at[2]),m['contact_centre_y_mm']), f'{pin}: contact position changed')
                require(all(close(a,b) for a,b in zip(size[1:3],m['contact_size_mm'])), f'{pin}: contact size changed')
                layer = 'F.Cu' if pin[0]=='A' else 'B.Cu'
                require(layer in [value(x) for x in kid(pad,'layers')[1:]], f'{pin}: contact face changed')
            expected_edges = {frozenset((tuple(a),tuple(b))) for a,b in zip(m['outline_mm'],m['outline_mm'][1:]+m['outline_mm'][:1])}
            edges=[]
            for line in kids(board,'gr_line'):
                if value(kid(line,'layer')[1])=='Edge.Cuts':
                    edges.append(frozenset(tuple(round(float(v),3) for v in kid(line,n)[1:3]) for n in ['start','end']))
            require(len(edges)==len(expected_edges) and set(edges)==expected_edges, 'Card outline differs from mechanical contract')
        print(f'Checked {project}: {reference}, {len(expected)} contacts')
    check(contract['daughter_project'], contract['daughter_reference'], contract['contacts'], True)
    for slot in contract['carrier_instances']:
        require(set(slot['contacts'])==set(contract['contacts']), f"{slot['reference']}: incomplete carrier mapping")
        check(slot['project'],slot['reference'],slot['contacts'])
    power_input = contract.get('peripheral_power_input')
    if power_input:
        check(power_input['project'], power_input['reference'], power_input['contacts'])
    measurement = contract.get('measurement')
    if measurement:
        # PAC1934 JQ pin numbers come from Microchip DS20005850E Table 3-1.
        for ref, first in [('U4', 1), ('U5', 5)]:
            expected = {'1': ref+'_SLOW', '2': 'PERIPH_3V3', '3': 'GND',
                        '4': 'I2C_SCL', '5': 'I2C_SDA',
                        '6': 'GND' if ref == 'U4' else 'PERIPH_3V3',
                        '15': 'PERIPH_3V3', '16': 'PERIPH_3V3', '17': 'GND'}
            for offset, (plus, minus) in enumerate([('11','12'), ('13','14'), ('8','7'), ('10','9')]):
                expected[plus] = f'S{first+offset}_SHUNT_HI'
                expected[minus] = f'S{first+offset}_5V'
            check('pico-carrier/pico-carrier', ref, expected)
        check(contract['daughter_project'], 'R1', {'1': 'SHUNT_HI', '2': 'STRING_5V'})
        sch = parse((ROOT/(contract['daughter_project']+'.kicad_sch')).read_text())
        resistor = next((s for s in kids(sch,'symbol') if any(value(p[1])=='Reference' and value(p[2])=='R1' for p in kids(s,'property'))), None)
        fields = {value(p[1]):value(p[2]) for p in kids(resistor,'property')} if resistor else {}
        require(math.isclose(float(fields.get('Resistance_Ohms', -1)), measurement['shunt_ohms'], rel_tol=1e-9, abs_tol=1e-9), 'R1 resistance differs from measurement configuration')
        require(fields.get('MPN') == 'WSL2512R0250FEA', 'R1 purchasing part differs from selected 25 mOhm shunt')
    if errors:
        print('\nFAIL\n'+'\n'.join(errors))
        return 1
    print('PASS: registered interfaces match schematic, PCB and mechanical contract.')
    if not contract['carrier_instances']:
        print('Carrier coverage pending: no sockets registered yet. Power interface is not defined.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
