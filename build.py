from pathlib import Path
import uuid,json
O=Path('.'); rootid=str(uuid.uuid4())
def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s))
def eff(sz=1.27,extra=''):return f'(effects (font (size {sz} {sz})) {extra})'
def line(x1,y1,x2,y2):return f'(polyline (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (fill (type none)))'
def rect(x1,y1,x2,y2):return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default)) (fill (type background)))'
# pin = number,name,x,y,angle,type
D={}
def define(name,pins,graphics):
 D[name]=(pins,f'(symbol "Review:{name}" (pin_names (offset 1)) (exclude_from_sim no) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 5 0) {eff()}) (property "Value" "{name}" (at 0 -5 0) {eff()}) (symbol "{name}_0_1" {graphics}) (symbol "{name}_1_1" '+''.join(f'(pin {t} line (at {x} {y} {a}) (length 5.08) (name {q(n)} {eff(1.0)}) (number {q(num)} {eff(1.0)}))' for num,n,x,y,a,t in pins)+'))')
def block(name,left,right,width=20,spacing=5.08):
 width=round(width/1.27)*1.27
 n=max(len(left),len(right)); h=(n-1)*spacing/2+4
 pins=[]
 for side,arr in [(-1,left),(1,right)]:
  for i,item in enumerate(arr):
   num,label,t=item;pins.append((str(num),label,side*(width+5.08),(n-1)*spacing/2-i*spacing,0 if side<0 else 180,t))
 define(name,pins,rect(-width,h,width,-h))
# two terminal symbols; pin endpoints at +/-7.62, lead to +/-2.54
p2=[('1','',-7.62,0,0,'passive'),('2','',7.62,0,180,'passive')]
define('R',p2,rect(-2.54,1.016,2.54,-1.016))
define('Fuse',p2,rect(-2.54,1.27,2.54,-1.27)+line(-2.54,0,2.54,0))
define('C',p2,line(-1.0,-2.54,-1.0,2.54)+line(1,-2.54,1,2.54)+line(-2.54,0,-1,0)+line(1,0,2.54,0))
define('CP',[('1','+',-7.62,0,0,'passive'),('2','-',7.62,0,180,'passive')],line(-1,-2.54,-1,2.54)+line(1,-2.54,1,2.54)+line(-2.54,0,-1,0)+line(1,0,2.54,0))
define('Schottky',[('2','A',-7.62,0,0,'passive'),('1','K',7.62,0,180,'passive')],line(-2.54,0,-1.5,0)+line(-1.5,-2,-1.5,2)+line(-1.5,2,1.5,0)+line(1.5,0,-1.5,-2)+line(1.5,-2,1.5,2)+line(1.5,0,2.54,0)+line(1.5,2,2.3,2)+line(1.5,-2,.7,-2))
class Sheet:
 def __init__(self,name,title,id=None):self.name=name;self.title=title;self.id=id or uid();self.items=[];self.used=set();self.expected={};self.symbols={};self.kinds={}
 def note(self,x,y,txt,size=1.4):self.items.append(f'(text {q(txt)} (at {x} {y} 0) {eff(size,"(justify left top)")} (uuid "{uid()}"))')
 def wire(self,x,y,xx,yy):self.items.append(f'(wire (pts (xy {x} {y}) (xy {xx} {yy})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
 def label(self,x,y,net):self.items.append(f'(global_label {q(net)} (shape bidirectional) (at {x} {y} 0) {eff(1.27,"(justify left)")} (uuid "{uid()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) {eff(1.0,"hide")}))')
 def comp(self,kind,ref,val,x,y,nets,angle=0,fp=""):
  x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
  self.used.add(kind);u=uid();path='/'+rootid if self.id==rootid else '/'+rootid+'/'+self.id
  self.symbols[ref]=path+'/'+u; self.kinds[ref]=kind
  self.items.append(f'(symbol (lib_id "Review:{kind}") (at {x} {y} {angle}) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{u}") (property "Reference" {q(ref)} (at {x} {y-5 if kind in ["R","Fuse","C","CP","Schottky","PWR_FLAG"] else y-((max(abs(p[3]) for p in D[kind][0]))+12)} 0) {eff(1.27)}) (property "Footprint" {q(fp)} (at {x} {y} 0) {eff(1,"hide")}) (property "Value" {q(val)} (at {x} {y-2.5 if kind in ["R","Fuse","C","CP","Schottky","PWR_FLAG"] else y-((max(abs(p[3]) for p in D[kind][0]))+9)} 0) {eff(1.0)}) '+''.join(f'(pin {q(p[0])} (uuid "{uid()}"))' for p in D[kind][0])+f'(instances (project "led-head-rev1" (path "{path}" (reference {q(ref)}) (unit 1)))))')
  import math
  for num,n,px,py,a,t in D[kind][0]:
   # local positive y up; at angle90 local x becomes up
   c=round(math.cos(math.radians(angle)));s=round(math.sin(math.radians(angle)))
   xx=round(x+px*c-py*s,4);yy=round(y-px*s-py*c,4)
   net=nets.get(num)
   if net is None:self.items.append(f'(no_connect (at {xx} {yy}) (uuid "{uid()}"))');continue
   self.expected[(ref,num)]=net
   aa=(a+angle)%360
   dx,dy={0:(-22.86,0),180:(5.08,0),90:(0,5.08),270:(0,-5.08)}[aa]
   self.wire(xx,yy,xx+dx,yy+dy);self.label(xx+dx,yy+dy,net)
 def save(self):
  text=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{self.id}") (paper "A3") (title_block (title {q(self.title)}) (date "2026-11-15") (rev "1 - REVIEW") (comment 1 "Three WS2812 strings | ENGINEERING REVIEW")) (lib_symbols '+''.join(D[k][1] for k in sorted(self.used))+') '+''.join(self.items)+')'
  (O/(self.name+'.kicad_sch')).write_text(text)
import csv
from collections import defaultdict
import pcbnew as k
F = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
parts={}
custom=Path('HeadUnit.pretty')
custom.mkdir(exist_ok=True)
xt_name='AMASS_XT30PW-F_1x02_P2.50mm_Horizontal'
xt_original=F/'Connector_AMASS.pretty'/(xt_name+'.kicad_mod')
(custom/(xt_name+'.kicad_mod')).write_text(xt_original.read_text().replace('(layer "F.SilkS")','(layer "Dwgs.User")'))
xt60_name = 'AMASS_XT60PW-M_1x02_P7.20mm_Horizontal'
xt60_original = F/'Connector_AMASS.pretty'/(xt60_name+'.kicad_mod')
# Housing projects past the PCB edge; keep the body outline on fabrication layers.
xt60_body = xt60_original.read_text().replace('(layer "F.SilkS")', '(layer "Dwgs.User")')
(custom/(xt60_name+'.kicad_mod')).write_text(xt60_body)
# Top view from the STEP file. KiCad Y is the inverse of the model Y.
buck_footprint = 'Pololu_D36V50Fx_Direct'
buck_x = (6.35, 8.89, 11.43, 13.97, 16.51, 19.05)
buck_rows = (-1.27, -3.81)
buck_pads = []
for row, y in enumerate(buck_rows):
 for col, x in enumerate(buck_x):
  pin = row * len(buck_x) + col + 1
  shape = 'rect' if pin == 1 else 'circle'
  buck_pads.append(f'(pad "{pin}" thru_hole {shape} (at {x} {y}) (size 1.90 1.90) (drill 1.02) (layers "*.Cu" "*.Mask"))')
buck_supports = [(2.159,-2.159),(23.241,-2.159),(2.159,-23.241)]
support_marks = ''.join(
 f'(fp_circle (center {x} {y}) (end {x+1.0922} {y}) (stroke (width 0.15) (type solid)) (fill none) (layer "Dwgs.User"))'
 for x,y in buck_supports
)
(custom/(buck_footprint+'.kicad_mod')).write_text(
 f'(footprint "{buck_footprint}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr through_hole) '
 '(fp_rect (start 0 0) (end 25.4 -25.4) (stroke (width 0.15) (type solid)) (fill none) (layer "F.Fab")) '
 '(fp_rect (start 5.05 0) (end 20.35 -5.11) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd")) '
 + support_marks + ''.join(buck_pads)
 + '(model "${KIPRJMOD}/models/d36v50fx-step-down-voltage-regulator.step" (offset (xyz 0 0 8.5)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0))))'
)
# TI RPW0010A land pattern for TPS25970A; power leads have stepped lands.
efuse_fp = 'TI_RPW0010A_VQFN_HR'
efuse_lands = []
for i, y in enumerate((-.7125,-.2375,.2375,.7125)):
 for n,x in ((i+1,-.9),(10-i,.9)):
  efuse_lands.append((n,x,y,.6,.25))
for n,sign in ((5,-1),(6,1)):
 efuse_lands.extend(((n,sign*.25,.325,.30 if n == 5 else .25,1.75),
                     (n,sign*.35,-.225,.25,.65),
                     (n,sign*.375,-.7,.2,.3)))
efuse_pads = ''.join(
 f'(pad "{n}" smd roundrect (at {x} {y}) (size {w} {h}) '
 '(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15))'
 for n,x,y,w,h in efuse_lands
)
(custom/(efuse_fp+'.kicad_mod')).write_text(
 f'(footprint "{efuse_fp}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr smd) '
 '(duplicate_pad_numbers_are_jumpers yes) (clearance .12) '
 '(fp_rect (start -1 -1) (end 1 1) (stroke (width .12) (type solid)) (fill none) (layer "F.Fab")) '
 '(fp_rect (start -1.45 -1.45) (end 1.45 1.45) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd")) '
 '(fp_circle (center -1.45 -.72) (end -1.38 -.72) (stroke (width .12) (type solid)) (fill none) (layer "F.SilkS")) '
 + efuse_pads + ')'
)
Path('fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "HeadUnit")(type "KiCad")(uri "${KIPRJMOD}/HeadUnit.pretty")(options "")(descr "Local XT, Pololu and eFuse footprints")))')

root=Sheet('led-head-rev1','LED Head Unit | Rev 1',rootid)
power=Sheet('power','Battery, power selection and distribution')
control=Sheet('control','Pico 2 W sockets and keypad interface')
io=Sheet('led-io','LED outputs, isolation and shunt monitoring')
protection=Sheet('inlet','Shared inlet protection and status')
for i,(sheet,title) in enumerate([(power,'Battery and power'),(control,'Controller'),(io,'LED outputs and sensing'),(protection,'Inlet protection and status')]):
 x=25+(i%3)*125;y=48 if i<3 else 158
 root.items.append(f'(sheet (at {x} {y}) (size 102 25) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid "{sheet.id}") (property "Sheetname" {q(title)} (at {x} {y-1} 0) {eff(1.27,"(justify left bottom)")}) (property "Sheetfile" "{sheet.name}.kicad_sch" (at {x} {y+26} 0) {eff(1,"(justify left top)")}))')
root.note(25,20,'LED HEAD UNIT / REV 1',2.5)
root.note(25,95,'3S LiPo or protected camper 12 V via XT60 harness. A regulated 5 V source uses the same XT60 through the protected bypass.\nPanel NKK S333 selects buck / OFF / external 5 V. Common 0 V.\n3 x WS2812 channels on GP4, GP5, GP6. 6 A LED total on external power.\nKeep battery LED budget to 4.5 A pending enclosed thermal testing.\nSee README for wiring, design status and copper calculations.',1.6)
def con(kind,names):
 block(kind,[],[(i+1,s,'passive') for i,s in enumerate(names)],max(9,max(map(len,names))))
con('Power2',['+','GND'])
block('InletEFuse',[(1,'EN','passive'),(2,'OVLO','passive'),(5,'IN','passive'),(8,'GND','passive')],[(6,'OUT','passive'),(7,'DVDT','passive'),(9,'ILM','passive'),(10,'ITIMER','passive'),(4,'FLT','passive'),(3,'DNC','passive')])
block('StatusLDO',[(2,'IN','passive'),(1,'GND','passive')],[(3,'OUT','passive'),(4,'NC','passive'),(5,'NC','passive')],14)
block('FaultGate',[(6,'PG','passive'),(3,'DELAY','passive'),(1,'IN1','passive'),(2,'GND','passive')],[(4,'OUT','passive'),(5,'VCC','passive')],14)
con('Data2',['DATA','GND'])
con('Switch',['BUCK 5V','RAIL RETURN','EXT 5V'])
con('SwitchLogic',['BUCK EN','SW GND','BATT SELECT'])
block('PololuBuck',[(1,'VRP','passive'),(2,'EN','passive'),(3,'VOUT','passive'),(4,'VOUT','passive'),(5,'GND','passive'),(6,'VIN','passive')],[(7,'VRP','passive'),(8,'PG','passive'),(9,'VOUT','passive'),(10,'VOUT','passive'),(11,'GND','passive'),(12,'VIN','passive')],19)
con('Trellis',['GND','3V3','SDA','SCL'])
# Socket symbols carry physical Pico pin numbers via net labels.
con('PicoL',['GP0','GP1','GND','GP2','GP3','GP4','GP5','GND','GP6','GP7','GP8','GP9','GND','GP10','GP11','GP12','GP13','GND','GP14','GP15'])
con('PicoR',['GP16','GP17','GND','GP18','GP19','GP20','GP21','GND','GP22','RUN','GP26','GP27','AGND','GP28','ADC VREF','3V3 OUT','3V3 EN','GND','VSYS','VBUS'])
block('INA3221',[(12,'IN1+','input'),(11,'IN1-','input'),(15,'IN2+','input'),(14,'IN2-','input'),(2,'IN3+','input'),(1,'IN3-','input'),(4,'VS','power_in'),(16,'VPU','input'),(5,'A0','input')],[(7,'SDA','bidirectional'),(6,'SCL','input'),(3,'GND','power_in'),(17,'EP','passive'),(8,'WARN','open_collector'),(9,'CRIT','open_collector'),(10,'PV','open_collector'),(13,'TC','open_collector')],15)
block('TXU0101',[(1,'VCCA','power_in'),(2,'GND','power_in'),(3,'A','input')],[(6,'VCCB','power_in'),(5,'OE','input'),(4,'Y','output')],13)
block('MOS',[(1,'G','input')],[(2,'S','passive'),(3,'D','passive')],10)
define('PWR_FLAG',[('1','',0,0,90,'power_out')],line(-1,1,0,2)+line(0,2,1,1)+line(1,1,-1,1))
def fp(lib,name):
 return f'{lib}:{name}'
r0805=fp('Resistor_SMD','R_0805_2012Metric')
c0805=fp('Capacitor_SMD','C_0805_2012Metric')
sot23=fp('Package_TO_SOT_SMD','SOT-23')
def terminal(n):
 return fp('TerminalBlock_Phoenix',f'TerminalBlock_Phoenix_MKDS-1,5-{n}-5.08_1x{n:02}_P5.08mm_Horizontal')
def place(sheet,kind,ref,value,xy,nets,footprint,pos,mpn='',rot=0):
 pins={str(i):n for i,n in enumerate(nets,1) if n} if isinstance(nets,list) else {str(i):n for i,n in nets.items()}
 sheet.comp(kind,ref,value,*xy,pins,fp=footprint)
 parts[ref]=(value,footprint,pos,rot,pins,mpn)
def r(sh,ref,val,xy,pins,pos,mpn='',foot=r0805,rot=0):
 place(sh,'R',ref,val,xy,pins,foot,pos,mpn,rot)
def c(sh,ref,val,xy,pins,pos,mpn='',foot=c0805,rot=0,kind='C'):
 place(sh,kind,ref,val,xy,pins,foot,pos,mpn,rot)
G='GND'; V='3V3'; RAIL='LED_5V'
power.note(15,14,'PANEL WIRING AND PROTECTED INPUTS',2)
power.note(15,24,'Board-mounted XT60PW-M. Keep the 5 A battery-side fuse in the harness. Use fused, protected camper distribution.\nJ3: match NKK solder lug numbering per wiring table. Keep high-current wiring short.',1.3)
place(power,'Power2','J1','XT60PW-M SHARED DC INPUT',(55,55),[G,'BAT_RAW'],fp('HeadUnit',xt60_name),(89,16.5),'XT60PW-M',270)
place(power,'Switch','J3','NKK S333 PANEL HARNESS',(55,135),['BUCK_5V',RAIL,'EXT_5V'],terminal(3),(66,65.5),'1715734',180)
place(power,'SwitchLogic','J5','PANEL LOGIC',(160,195),['BUCK_EN',G,'BATT_SEL_N'],fp('Connector_JST','JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical'),(79,65),'B3B-XH-A(LF)(SN)')
place(power,'PololuBuck','MOD1','POLOLU D36V50F5 DIRECT MOUNT',(70,219),
      ['VRP','BUCK_EN','BUCK_5V','BUCK_5V',G,'BAT_RAW','VRP','PG','BUCK_5V','BUCK_5V',G,'BAT_RAW'],
      fp('HeadUnit',buck_footprint),(74,54),'4091')
r(power,'R1','13.7k UVLO',(160,63),['BUCK_EN',G],(84,29))
r(power,'R2','100k ADC top',(160,95),['BAT_SENSE_SW','BAT_ADC'],(70,32))
r(power,'R3','10k ADC bottom',(255,95),['BAT_ADC',G],(66,32))
c(power,'C1','100n ADC filter',(345,95),['BAT_ADC',G],(66,35))
place(power,'MOS','Q1','BSS84 P-channel',(153,135),{1:'ADC_GATE',2:'VRP',3:'BAT_SENSE_SW'},sot23,(77,34),'BSS84,215')
place(power,'MOS','Q2','2N7002 N-channel',(255,135),{1:V,2:G,3:'ADC_GATE'},sot23,(77,39),'2N7002,215')
r(power,'R4','100k gate pull-up',(350,135),['VRP','ADC_GATE'],(77,31))
r(power,'R5','10k PG pull-up',(160,175),[V,'PICO_PG'],(65,38))
r(power,'R6','10k select pull-up',(255,175),[V,'PICO_BATT_SEL_N'],(69,39))
c(power,'C2','1000uF 16V',(160,220),[RAIL,G],(65,47),'EEU-FR1C102L',fp('Capacitor_THT','CP_Radial_D10.0mm_P5.00mm'),0,'CP')
for i,(x,n) in enumerate([(142,G),(220,RAIL),(272,'PICO_VSYS')],1):
 power.comp('PWR_FLAG',f'#FLG0{i}','',x,248,{'1':n})
control.note(15,12,'PICO 2 W / SOCKETED',2)
socket=fp('Connector_PinSocket_2.54mm','PinSocket_1x20_P2.54mm_Vertical')
place(control,'PicoL','J10','Pico socket 1-20',(60,95),{2:'DEBUG_COPY',3:G,6:'GP4',7:'GP5',8:G,9:'GP6',10:'PICO_BATT_SEL_N',11:'I2C_SDA',12:'I2C_SCL',13:G,14:'PICO_PG',16:'TRELLIS_SCL',17:'TRELLIS_SDA',18:G},socket,(56,40),'',270)
place(control,'PicoR','J11','Pico socket 21-40',(160,95),{3:G,8:G,11:'BAT_ADC',13:G,16:V,18:G,19:'PICO_VSYS'},socket,(7.74,57.78),'',90)
# The Pico's onboard 3.3 V regulator drives the socket output.
control.comp('PWR_FLAG','#FLG04','',258,42,{'1':V})
place(control,'Schottky','D1','SS14',(340,75),{2:RAIL,1:'PICO_VSYS'},fp('Diode_SMD','D_SMA'),(51,52.5),'SS14-E3/61T',180)
place(control,'Trellis','J12','NEOTRELLIS JST-PH',(255,120),[G,V,'TRELLIS_SDA','TRELLIS_SCL'],fp('Connector_JST','JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical'),(10.05,27.5),'B4B-PH-K-S(LF)(SN)',270)
r(control,'R7','4.7k I2C SDA pull-up',(245,155),[V,'I2C_SDA'],(24.5,35),rot=270)
r(control,'R8','4.7k I2C SCL pull-up',(345,155),[V,'I2C_SCL'],(26,31.5),rot=270)
con('Probe',['SIGNAL','GND'])
probe_header=fp('Connector_PinHeader_2.54mm','PinHeader_1x02_P2.54mm_Vertical')
place(control,'Probe','TP1','GP1 SCOPE COPY',(255,190),['DEBUG_COPY',G],probe_header,(56,32),rot=90)
place(control,'Probe','TP2','I2C0 SDA TEST',(245,177),['I2C_SDA',G],probe_header,(17,35.8),rot=90)
place(control,'Probe','TP3','I2C0 SCL TEST',(345,177),['I2C_SCL',G],probe_header,(17,31.5),rot=90)
place(control,'Probe','TP4','TRELLIS SDA TEST',(245,236),['TRELLIS_SDA',G],probe_header,(4,28))
place(control,'Probe','TP5','TRELLIS SCL TEST',(345,236),['TRELLIS_SCL',G],probe_header,(4,35))
control.note(220,207,'GP8/9 = I2C0; GP7 = battery select; GP10 = buck PG.\nGP26 = ADC0. Existing pixel outputs GP4/5/6.\nVerify NeoTrellis cable pin order at both mating faces.\nNeoTrellis uses software I2C: GP13 SDA (pin 17), GP12 SCL (pin 16).\nNeoTrellis uses keypad pull-ups. R7/R8 bias hardware I2C0 only.\nUSB-only: VSYS diode blocks rail backfeed.',1.3)
# Three physically identical power lanes, arranged at the connector edge.
from math import *
for i,x in enumerate([23,43,63],1):
 sx=70+(i-1)*130
 bx=x-3.5 if i==1 else x
 dy=-.045 if i==1 else 0
 sense=f'S{i}_SHUNT_HI'; load=f'S{i}_5V'; buf=f'S{i}_BUF'; data=f'S{i}_DATA'
 io.comp('PWR_FLAG',f'#FLG{4+i:02}','',sx+28,60,{'1':load})
 io.note(sx-40,12,f'STRING {i}',1.8)
 place(io,'Fuse',f'F{i}','3A 125V NANO2',(sx,27),[RAIL,sense],fp('Fuse','Fuse_Littelfuse-NANO2-451_453'),(bx,22.5+dy),'0451003.MRL',90)
 r(io,f'R{10+i}','50m 1W 1%',(sx,42),[sense,load],(bx,14+dy),'WSL2512R0500FEA',fp('Resistor_SMD','R_2512_6332Metric'),90)
 place(io,'Power2',f'J{20+i}','XT30PW-F / FUSED 5V',(sx,63),[G,load],fp('HeadUnit',xt_name),(bx-5,7),'XT30PW-F')
 place(io,'TXU0101',f'U{i}','TXU0101DBVR',(sx,94),[V,G,f'GP{i+3}',buf,V,load],fp('Package_TO_SOT_SMD','SOT-23-6'),(bx+12,24+dy),'TXU0101DBVR')
 r(io,f'R{20+i}','220R DATA',(sx,118),[buf,data],(bx+11,19.5+dy))
 place(io,'Data2',f'J{30+i}','XH DATA / GND',(sx,139),[data,G],fp('Connector_JST','JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical'),(x+11,14.5),'B2B-XH-A(LF)(SN)')
 c(io,f'C{10+i}','100n VCCA',(sx,157),[V,G],((30.5,32) if i==1 else (x+11,28)))
 c(io,f'C{20+i}','100n VCCB',(sx,172),[load,G],(bx+5.7,13+dy))
 c(io,f'C{30+i}','10u 16V X7R',(sx,187),[load,G],(bx+5.4,18.6+dy),'',fp('Capacitor_SMD','C_1206_3216Metric'),90)
inets={1:'S3_5V',2:'S3_SHUNT_HI',3:G,4:V,5:G,6:'I2C_SCL',7:'I2C_SDA',11:'S1_5V',12:'S1_SHUNT_HI',14:'S2_5V',15:'S2_SHUNT_HI',16:V,17:G}
place(io,'INA3221','U4','INA3221AIRGVR / I2C 0x40',(105,245),inets,fp('Package_DFN_QFN','Texas_RGV0016A_VQFN-16-1EP_4x4mm_P0.65mm_EP2.1x2.1mm'),(46,33.3),'INA3221AIRGVR')
c(io,'C40','100n INA supply',(260,230),[V,G],(51.6,34.4))
io.note(230,248,'Kelvin pairs from each shunt pad.\nThe translators are powered by their own fused outputs.\nTXU0101 isolates outputs when either supply is off.\nAll string power returns and data grounds share GND.',1.3)
# The selector remains manual. Hardware UV/OV thresholds guard the 5 V throw.
P = protection
AON = 'STATUS_3V3'
protection.note(15,12,'SHARED INLET / HARDWARE CUTOFF',2)
place(P,'InletEFuse','U5','TPS25970ARPWR',(104,78),
      {1:'BYPASS_EN',2:'BYPASS_OV',5:'BAT_RAW',6:'EXT_5V',7:'BYPASS_DVDT',8:G,9:'BYPASS_ILM'},
      fp('HeadUnit',efuse_fp),(86,7.5),'TPS25970ARPWR')
r(P,'R41','34.8k OV upper',(200,35),['BAT_RAW','BYPASS_OV'],(80,4),'RT0805BRD0734K8L')
r(P,'R42','10k OV lower',(300,35),['BYPASS_OV',G],(80,7),'RT0805BRD0710KL')
r(P,'R43','768R ILIM',(200,60),['BYPASS_ILM',G],(90,4.5),'RC0805FR-07768RL')
c(P,'C41','2.2u 50V input',(200,85),['BAT_RAW',G],(82,16.5),'GRM21BR71H225KA73L',c0805,180)
c(P,'C42','6.8n soft start',(300,60),['BYPASS_DVDT',G],(92,10),'C0805C682K5RACTU')
r(P,'R44','10k output bleed',(300,85),['EXT_5V',G],(81,19.5),'RC0805FR-0710KL')
r(P,'R51','26.1k UV upper',(200,105),['BAT_RAW','BYPASS_EN'],(80,9.5),'RC0805FR-0726K1L')
r(P,'R52','10k UV lower',(300,105),['BYPASS_EN',G],(84,3),'RC0805FR-0710KL')
sod323 = fp('Diode_SMD','D_SOD-323')
def status_diode(ref, value, xy, cathode, anode, pos, footprint=sod323, mpn='BAT54WS-7-F'):
 place(P,'Schottky',ref,value,xy,[cathode,anode],footprint,pos,mpn)
place(P,'StatusLDO','U6','TLV70433DBVR',(75,142),{1:G,2:'BAT_RAW',3:AON,4:G,5:G},
      fp('Package_TO_SOT_SMD','SOT-23-5'),(86,35),'TLV70433DBVR')
c(P,'C43','1u 50V LDO input',(170,132),['BAT_RAW',G],(90,35),'GRM21BR71H105KA12L')
c(P,'C44','4.7u 16V LDO output',(260,132),[AON,G],(81.5,35),'GRM21BR71C475KA73L')
r(P,'R45','10k PG bias',(92,183),[AON,'PG'],(83.5,39),'RC0805FR-0710KL')
r(P,'R46','10k BAT bias',(92,205),[AON,'BATT_SEL_N'],(87.5,39),'RC0805FR-0710KL')
r(P,'R47','100k delay',(92,227),['BATT_SEL_N','BAT_DELAY_N'],(91.5,39),'RC0805FR-07100KL')
c(P,'C45','4.7u BAT delay',(182,227),['BAT_DELAY_N',AON],(91.5,43),'GRM21BR71C475KA73L')
status_diode('D2','PG isolation',(182,183),'PG','PICO_PG',(75,42))
status_diode('D3','BAT isolation',(182,205),'BATT_SEL_N','PICO_BATT_SEL_N',(75,45))
status_diode('D4','Fast delay reset',(270,227),'BAT_DELAY_N','BATT_SEL_N',(93,37))
place(P,'FaultGate','U7','SN74LVC1G57DBVR',(270,177),
      [G,G,'BAT_DELAY_N','BUCK_FAULT',AON,'PG'],fp('Package_TO_SOT_SMD','SOT-23-6'),(87,43),'SN74LVC1G57DBVR')
c(P,'C46','100n gate bypass',(350,145),[AON,G],(85,46),'C0805C104K5RACTU')
r(P,'R48','680R red',(339,199),['BUCK_FAULT','RED_A'],(91,58),'RC0805FR-07680RL')
r(P,'R49','1k green',(339,244),[RAIL,'GREEN_A'],(92.5,62),'RC0805FR-071KL')
led0805 = fp('LED_SMD','LED_0805_2012Metric')
status_diode('D5','RED BUCK FAULT',(382,199),G,'RED_A',(88.7,61.5),led0805,'LTST-C170KRKT')
status_diode('D6','GREEN LED POWER',(382,244),G,'GREEN_A',(96,61.5),led0805,'LTST-C170KGKT')
for sheet in (root,power,control,io,protection): sheet.save()
(O/'HeadUnit.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(v[1].replace('"Review:', '"',1) for v in D.values())+')')
(O/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Review")(type "KiCad")(uri "${KIPRJMOD}/HeadUnit.kicad_sym")(options "")(descr "Head unit symbols")))')
b=k.BOARD()
b.SetCopperLayerCount(4)
nets={}
def point(x,y):
 return k.VECTOR2I(k.FromMM(x),k.FromMM(y))
for n in sorted({n for spec in parts.values() for n in spec[4].values()}):
 net=k.NETINFO_ITEM(b,n)
 b.Add(net)
 nets[n]=net
loaded={}
for ref,(value,footprint,pos,rot,pins,mpn) in parts.items():
 lib,name=footprint.split(':')
 f=k.FootprintLoad(str(custom.resolve() if lib=='HeadUnit' else F/(lib+'.pretty')),name)
 if f is None: raise ValueError(footprint)
 f.SetFPIDAsString(footprint)
 f.SetReference(ref); f.SetValue(value); f.Value().SetText(value)
 if ref.startswith('TP'): f.SetAttributes(f.GetAttributes() & ~k.FP_EXCLUDE_FROM_BOM)
 f.SetPath(k.KIID_PATH(next(sh.symbols[ref] for sh in (power,control,io,protection) if ref in sh.symbols)))
 f.SetPosition(point(*pos)); f.SetOrientationDegrees(rot)
 f.Value().SetVisible(False)
 f.Reference().SetVisible(False)
 b.Add(f)
 loaded[ref]=f
 padnums={p.GetNumber() for p in f.Pads()}
 if not set(pins)<=padnums: raise ValueError((ref,pins,padnums))
 for p in f.Pads():
  if p.GetNumber() in pins: p.SetNet(nets[pins[p.GetNumber()]])
  elif p.GetNumber():
   kind=next(sh.kinds[ref] for sh in (power,control,io,protection) if ref in sh.kinds)
   pinname=next(pin[1] for pin in D[kind][0] if pin[0]==p.GetNumber())
   name=f'unconnected-({ref}-{pinname.replace(chr(32),chr(95))}-Pad{p.GetNumber()})'
   no=k.NETINFO_ITEM(b,name);b.Add(no);p.SetNet(no)
def shape(a,z,layer,width):
 s=k.PCB_SHAPE(b); s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(point(*a));s.SetEnd(point(*z));s.SetLayer(layer);s.SetWidth(k.FromMM(width));b.Add(s)
outline=[(0,0),(100,0),(100,73),(0,73),(0,52),(11,52),(11,42),(0,42)]
for a,z in zip(outline,outline[1:]+outline[:1]): shape(a,z,k.Edge_Cuts,.05)
def label(txt,xy,sz=1):
 t=k.PCB_TEXT(b);t.SetText(txt);t.SetPosition(point(*xy));t.SetLayer(k.F_SilkS);t.SetTextSize(point(sz,sz));t.SetTextThickness(k.FromMM(.15));b.Add(t)
for i,x in enumerate([19.5,43,63],1):
 label(f'PWR {i}',(x-2.5,3.2))
 label('-', (x-7.4,9),.9)
 label('+', (x+2.4,9),.9)
label('LED HEAD UNIT / REV 1',(19,64),1.25)
label('RF',(13,44.5),.8)
label('USB',(60,44.5))
label('XT60 INPUT',(81,22),.85)
label('-',(85.7,16.5),.9)
label('+',(85.7,23.7),.9)
label('PANEL S333',(46,67))
label('J12 NEOTRELLIS',(11,23.6),1)
label('I0 SDA',(12.2,36.6),.8)
label('TR SDA',(4.2,25.5),.8)
label('I0 SCL',(14.2,29),.8)
label('TR SCL',(4.2,33),.8)
label('GP1',(56,34.5),.8)
label('DATA 1',(34,10.4),0.9)
label('DATA 2',(54,10.4),0.9)
label('DATA 3',(74,10.4),0.9)
label('J5 SW LOGIC',(82,60.2),0.85)
label('MOD1 POLOLU',(87,55.7),.85)
label('FAULT',(88.7,64),.8)
label('POWER',(96,64),.8)
def pxy(ref,num):
 p=next(p for p in loaded[ref].Pads() if p.GetNumber()==str(num))
 pt=p.GetPosition()
 return k.ToMM(pt.x),k.ToMM(pt.y)
def track(net,ly,w,*points):
 for a,z in zip(points,points[1:]):
  if hypot(a[0]-z[0],a[1]-z[1])<.0001: continue
  t=k.PCB_TRACK(b); t.SetStart(point(*a));t.SetEnd(point(*z));t.SetWidth(k.FromMM(w));t.SetLayer(ly);t.SetNet(nets[net]);b.Add(t)
def via(net,x,y,d=.85,dr=.4):
 v=k.PCB_VIA(b);v.SetPosition(point(x,y));v.SetWidth(k.FromMM(d));v.SetDrill(k.FromMM(dr));v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu);v.SetNet(nets[net]);b.Add(v)
for i,x in enumerate([19.5,43,63],1):
 a,z=pxy(f'F{i}',1),pxy(f'F{i}',2)
 # Pad 1 is the rail-side pad. Rotations are verified from actual pad coordinates.
 if a[1]<z[1]: raise ValueError((i,a,z))
 track(RAIL,k.F_Cu,2.3,a,(x,26.7))
 for dx in [-.66,.66]:
  for y in [25.4,26.7]: via(RAIL,x+dx,y,.80,.4)
 track(f'S{i}_SHUNT_HI',k.F_Cu,1.9,z,pxy(f'R{10+i}',1))
 track(f'S{i}_5V',k.F_Cu,1.9,pxy(f'R{10+i}',2),pxy(f'J{20+i}',2))
track(RAIL,k.B_Cu,4.8,(19.5,25.8),(63,25.8),(64,56),(60.92,60),pxy('J3',2))
# RPW power pads fan out on top copper. The bypass output changes layers through six vias.
track('BAT_RAW',k.F_Cu,.3,(85.75,8.45),(85.75,9.15),(84.6,10.3))
track('BAT_RAW',k.F_Cu,1.5,(84.6,10.3),(84,10.9),(84,13))
track('BAT_RAW',k.F_Cu,2.4,(84,13),(84,18.7),pxy('J1',2))
track('EXT_5V',k.F_Cu,.3,(86.25,8.45),(86.25,9.15),(87.4,10.3))
track('EXT_5V',k.F_Cu,1.5,(87.4,10.3),(87.4,12.4))
for x in (86.95,87.85):
 for y in (10.6,11.5,12.4):
  via('EXT_5V',x,y,.76,.4)
track('EXT_5V',k.B_Cu,1.9,(87.4,10.6),(87.4,12.4),(84.55,15.25))
track('EXT_5V',k.B_Cu,4.2,(84.55,15.25),(81,21.4),(81,24),(76.8,28.2),(76.8,53.2),(75,55),(75,70.35),(55.84,70.35),pxy('J3',3))
# Each regulator output contact contributes to the common 4 mm trunk.
for upper, lower in [(9,3),(10,4)]:
 track('BUCK_5V',k.F_Cu,1.9,pxy('MOD1',upper),pxy('MOD1',lower))
track('BUCK_5V',k.F_Cu,1.9,pxy('MOD1',3),(85.43,55),(86.7,56.27))
track('BUCK_5V',k.F_Cu,1.9,pxy('MOD1',4),(87.97,55),(86.7,56.27))
track('BUCK_5V',k.F_Cu,4.0,(86.7,56.27),(79.5,56.27),(74.77,61),(69,61),pxy('J3',1))
track('BAT_RAW',k.F_Cu,2.4,pxy('J1',2),(89,29),(96,36),(96,47.24),pxy('MOD1',12))
track('BAT_RAW',k.F_Cu,1.9,pxy('MOD1',12),pxy('MOD1',6))
# Carry the fault output between the regulator header columns on In2.Cu.
track('BUCK_FAULT',k.F_Cu,.25,pxy('U7',4),(89.24,43.95))
via('BUCK_FAULT',89.24,43.95,.65,.30)
track('BUCK_FAULT',k.In2_Cu,.2,(89.24,43.95),(89.24,57.15),(89.55,57.46))
via('BUCK_FAULT',89.55,57.46,.65,.30)
track('BUCK_FAULT',k.F_Cu,.25,(89.55,57.46),pxy('R48',1))
track(RAIL,k.B_Cu,2.3,pxy('C2',1),(64,47))
# Short VSYS run and a bottom-layer feed from the bulk capacitor to the isolation diode.
track('PICO_VSYS',k.F_Cu,.65,pxy('D1',1),(53,57.32),pxy('J11',19))
track(RAIL,k.F_Cu,.65,pxy('D1',2),(49,50.9))
via(RAIL,49,50.4)
track(RAIL,k.B_Cu,.65,(49,50.9),(52.9,47),(64,47))
# The ground return plane is filled after routing. Heavy pads use solid attachment.
for layer in (k.In1_Cu,k.B_Cu):
 z=k.ZONE(b);z.SetLayer(layer);z.SetNet(nets[G]);z.SetLocalClearance(k.FromMM(.26));z.SetPadConnection(k.ZONE_CONNECTION_FULL)
 poly=z.Outline();poly.NewOutline()
 for x,y in outline: poly.Append(point(x,y))
 b.Add(z)
for i,xy in enumerate(((4.5,5),(96,5),(95,68),(4.5,68)),1):
 f=k.FootprintLoad(str(F/'MountingHole.pretty'),'MountingHole_3.2mm_M3')
 f.SetFPIDAsString('MountingHole:MountingHole_3.2mm_M3')
 f.SetReference(f'H{i}');f.SetPosition(point(*xy))
 f.SetAttributes(f.GetAttributes() | k.FP_BOARD_ONLY | k.FP_EXCLUDE_FROM_BOM | k.FP_EXCLUDE_FROM_POS_FILES)
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 b.Add(f)
 loaded[f'H{i}']=f
from route import route_board
route_board(b, k, loaded, parts, nets, track, via)
k.SaveBoard(str(O/'led-head-rev1.kicad_pcb'),b)
with open(O/'SMT-BOM.csv','w',newline='') as f:
 out=csv.writer(f);out.writerow(['Comment','Designator','Footprint','Manufacturer Part Number','LCSC Part #'])
 lcsc={'TXU0101DBVR':'C7136368','INA3221AIRGVR':'C181255','0451003.MRL':'C13982','WSL2512R0500FEA':'C413486'}
 r_values={'13.7k':'13K7','100k':'100KL','10k':'10KL','4.7k':'4K7','220R':'220RL'}
 for ref,(value,foot,pos,rot,pins,mpn) in parts.items():
  if loaded[ref].GetAttributes()&k.FP_SMD and not ref.startswith('TP'):
   family=value.split()[0]
   if not mpn and family in r_values:
    mpn='RC0805FR-07'+r_values[family].rstrip('L')+'L'
   if not mpn and family=='100n':
    mpn='C0805C104K5RACTU'
   if not mpn and family=='10u':
    mpn='GRM31CR71C106KA01L'
   out.writerow([value,ref,foot.split(':')[1],mpn,lcsc.get(mpn,'')])
with open(O/'SMT-CPL.csv','w',newline='') as f:
 out=csv.writer(f);out.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
 for ref,(value,foot,pos,rot,pins,mpn) in parts.items():
  if loaded[ref].GetAttributes()&k.FP_SMD and not ref.startswith('TP'):
   out.writerow([ref,f'{pos[0]:.3f}mm',f'{-pos[1]:.3f}mm','Top',rot])
if not (O/'led-head-rev1.kicad_pro').exists(): (O/'led-head-rev1.kicad_pro').write_text('{}\n')
