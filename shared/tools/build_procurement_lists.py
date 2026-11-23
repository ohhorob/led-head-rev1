#!/usr/bin/env python3
"""Build purchasing snapshots from the 2026-11-23 live DigiKey My Lists audit.

Read-only with respect to KiCad. Prices/stock are snapshots, not an API feed.
"""
import csv
from pathlib import Path
import sys
from collections import defaultdict
from check_interfaces import parse, kids, value

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'procurement' / '2026-11-23'
OUT.mkdir(parents=True, exist_ok=True)

# Board|references|MPN|DigiKey ordering number|quantity|direct stock|unit USD
DATA = '''power-manager|J1|XT60PW-M||1||
power-manager|J5|0039281103|WM3804-ND|1|0|1.64
power-manager|U1|TPS62091RGTR|296-46388-1-ND|1|2708|2.74
power-manager|C1 C2|CL31A226KAHNNNE|1276-3047-1-ND|2|95267|0.45
power-manager|L1|74439346010|732-74439346010CT-ND|1|0|4.05
power-manager|C4|C0805C392J5GACTU|399-C0805C392J5GACTUCT-ND|1|3804|0.82
power-manager|C3|C0805C103K5RACTU|399-C0805C103K5RACTUCT-ND|1|1329018|0.15
power-manager|R1|RC0805FR-07499KL|311-499KCRCT-ND|1|344754|0.10
power-manager|R2|RC0805FR-071KL|311-1.00KCRCT-ND|1|447743|0.10
power-manager|D1|LTST-C170KGKT|160-1414-1-ND|1|397537|0.19
power-manager|TP1 TP2 TP3|TSW-102-07-G-S|612-TSW-102-07-G-S-ND|3|68923|0.19
string-daughterboard|D1|WS2812B-V6||1||
string-daughterboard|J2|S3B-XH-A|455-S3B-XH-A-ND|1|0|0.18
string-daughterboard|C1 C2|C0805C104K5RACTU|399-C0805C104K5RACTUCT-ND|2|10023435|0.18
string-daughterboard|U1|TXU0101DBVR|296-TXU0101DBVRCT-ND|1|33800|0.77
string-daughterboard|F1|0451003.MRL|F2583CT-ND|1|14062|2.47
string-daughterboard|R1|WSL2512R0250FEA|WSLG-.025CT-ND|1|34725|1.07
string-daughterboard|R2|RC0805FR-07220RL|311-220CRCT-ND|1|222442|0.11
pico-carrier|J21 J22 J23 J24 J25 J26 J27 J28|EBC06DCWN|S3293-ND|8|1815|2.82
pico-carrier|U4 U5|PAC1934T-I/JQ|PAC1934T-I/JQCT-ND|2|27034|1.94
pico-carrier|C40 C41 C42 C43|C0805C104K5RACTU|399-C0805C104K5RACTUCT-ND|4|10023435|0.18
pico-carrier|R5 R6 R30 R31|RC0805FR-0710KL|311-10.0KCRCT-ND|4|1167208|0.10
pico-carrier|R7 R8|RC0805FR-074K7L|311-4.70KCRCT-ND|2|437979|0.10
pico-carrier|J19|0039281103|WM3804-ND|1|0|1.64
pico-carrier|J20|B5B-XH-A|455-B5B-XH-A-ND|1|67683|0.20
pico-carrier|J10 J11|PPPC201LFBN-RC|S7053-ND|2|11946|1.20
pico-carrier|J15 J18|TSW-104-07-G-D|612-TSW-104-07-G-D-ND|2|3857|0.66
pico-carrier|J12|B4B-PH-K-S|455-1706-ND|1|87290|0.20
pico-carrier|TP2 TP3 TP4 TP5|TSW-102-07-G-S|612-TSW-102-07-G-S-ND|4|68923|0.19
pico-carrier|J13|FTSH-105-01-L-DV|612-FTSH-105-01-L-DV-ND|1|21503|1.05
pico-carrier|J17|B6B-PH-K-S|455-1708-ND|1|34268|0.28
pico-carrier|D1|SS14|SS14CT-ND|1|96389|0.44
pico-carrier|J16|TSW-106-07-G-S|612-TSW-106-07-G-S-ND|1|1725|0.56
pico-carrier|J14|TSW-103-07-G-S|612-TSW-103-07-G-S-ND|1|67805|0.27
pico-carrier|MODULE|SC1634|2648-SC1634-ND|1|3500|8.00'''

LISTS = {'power-manager':'HZ4VK28SG5', 'string-daughterboard':'2CJ5LZI7OT', 'pico-carrier':'FSEIH7W2E7'}
FALLBACK = {
 '0039281103': ('Mouser', '538-39-28-1103', 'https://www.mouser.com/en/ProductDetail/Molex/39-28-1103?qs=KHty%2FoMxDPmmZSKus1aviw%3D%3D', 'Exact part. Mouser page retrieved today: 6634 in stock; $1.68 each. DigiKey direct expected 18-Dec-2026.'),
 '74439346010': ('Mouser', '710-74439346010', 'https://www.mouser.com/en/ProductDetail/Wurth-Elektronik/74439346010?qs=rQFj71Wb1eVjgfvHnpR1NQ%3D%3D', 'Exact part. Mouser indexed listing: 681 stock, crawled last week; verify checkout stock. DigiKey direct expected 25-Nov-2026.'),
 'XT60PW-M': ('Jameco', '2844439', 'https://www.jameco.com/z/XT60PW-M-Amass-XT60-Socket-Male-Terminals-45A-500V-2-Pin-Right-Angle-PCB-Mount_2844439.html', 'Exact Amass right-angle part listed at $0.79, 301 stock in retrieved listing. No exact DigiKey match; no verified Mouser/Amazon offer found. Confirm supplied suffix against drawing.'),
 'WS2812B-V6': ('TME international', 'WS2812B-V6', 'https://www.tme.com/us/en-us/details/ws2812b-v6/smd-colour-leds/worldsemi/', 'Exact V6 5050 part; current retrieved TME page lists only 8 units, international offer. No verified DigiKey/Mouser/Amazon source. Shipping/availability not confirmed at checkout. Do not replace with unspecified WS2812B.'),
 'S3B-XH-A': ('Newark', '74M4770', 'https://www.newark.com/jst-japan-solderless-terminals/s3b-xh-a-lf-sn/header-right-angle-3way/dp/74M4770', 'Exact S3B-XH-A(LF)(SN), Newark listing shows 10511 stock; UK stock delivery quoted 4-6 business days in indexed listing. DigiKey direct expected 14-Dec-2026; Mouser out of stock. No substitute selected.'),
}

def write_csv(path, rows, fields):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

groups=defaultdict(list)
coverage=[]
for line in DATA.splitlines():
    board,refs,mpn,sku,qty,stock,price=line.split('|')
    supplier,alt_sku,url,note=FALLBACK.get(mpn,('DigiKey',sku,'','Direct stock verified in logged-in My Lists on 2026-11-23.'))
    if refs=='MODULE': note+=' Pico 2 WH already owned; included for completeness, not an additional purchase recommendation.'
    if refs=='J20' and board=='pico-carrier': note+=' Reserved future battery telemetry; optional for dedicated 5V setup.'
    groups[board].append(dict(Reference=refs,Quantity_per_board=int(qty),MPN=mpn,DigiKey_Part_Number=sku,DigiKey_Direct_Stock=stock,DigiKey_Unit_USD=price,Preferred_Supplier=supplier,Alternate_Order_Number=alt_sku if supplier!='DigiKey' else '',Supplier_URL=url,Notes=note))

for board,rows in groups.items():
    schem={}
    for file in (ROOT/board).glob('*.kicad_sch'):
        for s in kids(parse(file.read_text()),'symbol'):
            p={value(x[1]):value(x[2]) for x in kids(s,'property')}
            if p.get('Footprint') and not p.get('Reference','').startswith('#'):
                schem[p['Reference']]=p
    selected={ref:row for row in rows for ref in row['Reference'].split() if ref!='MODULE'}
    physical={r:p for r,p in schem.items() if not p['Footprint'].startswith('MountingHole:') and not(board=='string-daughterboard' and r=='J1')}
    assert set(selected)==set(physical), (board,sorted(set(physical)-set(selected)),sorted(set(selected)-set(physical)))
    for ref,p in schem.items():
        row=selected.get(ref)
        coverage.append(dict(Board=board,Reference=ref,Value=p.get('Value',''),Footprint=p['Footprint'],Selected_MPN=row['MPN'] if row else '',Disposition='Purchasable component' if row else 'PCB feature; no purchased component'))
    for row in rows:
        row['Footprints']='; '.join(sorted({schem[r]['Footprint'] for r in row['Reference'].split() if r in schem}))
    write_csv(OUT/(board+'-sourcing.csv'),rows,list(rows[0]))
    write_csv(OUT/(board+'-digikey-import.csv'),[{'Part Number':r['DigiKey_Part_Number'] or r['MPN'],'Quantity':r['Quantity_per_board'],'Customer Reference':r['Reference']} for r in rows],['Part Number','Quantity','Customer Reference'])
write_csv(OUT/'schematic-coverage.csv',coverage,list(coverage[0]))

combined={}
for board,rows in groups.items():
    for r in rows:
        if r['Reference']=='MODULE' or (board=='pico-carrier' and r['Reference']=='J20'): continue
        n=8 if board=='string-daughterboard' else 1
        if r['MPN'] not in combined:
            combined[r['MPN']]=dict(MPN=r['MPN'],Quantity=0,DigiKey_Part_Number=r['DigiKey_Part_Number'],Preferred_Supplier=r['Preferred_Supplier'],Supplier_URL=r['Supplier_URL'],Notes=r['Notes'])
        combined[r['MPN']]['Quantity']+=r['Quantity_per_board']*n
write_csv(OUT/'one-carrier-one-power-eight-cards.csv',list(combined.values()),list(next(iter(combined.values()))))
print('Verified complete purchased-component coverage:', {b:len(rs) for b,rs in groups.items()})
print('Wrote',OUT)
