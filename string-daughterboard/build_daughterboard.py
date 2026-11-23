raise SystemExit("Archived creation helper: do not regenerate over the current design.")
from pathlib import Path
import uuid,json
O=Path('.'); rootid=str(uuid.uuid4())
def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s),ensure_ascii=False)
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
  self.items.append(f'(symbol (lib_id "Review:{kind}") (at {x} {y} {angle}) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{u}") (property "Reference" {q(ref)} (at {x} {y-5 if kind in ["R","Fuse","C","CP","Schottky","PWR_FLAG"] else y-((max(abs(p[3]) for p in D[kind][0]))+12)} 0) {eff(1.27)}) (property "Footprint" {q(fp)} (at {x} {y} 0) {eff(1,"hide")}) (property "Value" {q(val)} (at {x} {y-2.5 if kind in ["R","Fuse","C","CP","Schottky","PWR_FLAG"] else y-((max(abs(p[3]) for p in D[kind][0]))+9)} 0) {eff(1.0)}) '+''.join(f'(pin {q(p[0])} (uuid "{uid()}"))' for p in D[kind][0])+f'(instances (project "string-daughterboard" (path "{path}" (reference {q(ref)}) (unit 1)))))')
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
  text=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{self.id}") (paper "A3") (title_block (title {q(self.title)}) (date "2026-11-19") (rev "1 - REVIEW") (comment 1 "Single string card | PLACEMENT DRAFT")) (lib_symbols '+''.join(D[k][1] for k in sorted(self.used))+') '+''.join(self.items)+')'
  (O/(self.name+'.kicad_sch')).write_text(text)

# Run from this directory with KiCad's bundled Python. Refuse to overwrite edits.
import os, shutil
os.chdir(Path(__file__).resolve().parent)
if Path('string-daughterboard.kicad_pcb').exists():
 raise SystemExit('Project already exists; refusing to overwrite manual work.')
import pcbnew as k
F=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
local=Path('StringCard.pretty');local.mkdir(exist_ok=True)
parent=Path('..')
for name in ['Vishay_WSL2512_50mR','JST_XH_S3B-XH-A_1x03_P2.50mm_Horizontal']:
 shutil.copy2(parent/'HeadUnit.pretty'/(name+'.kicad_mod'),local/(name+'.kicad_mod'))
Path('fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "StringCard") (type "KiCad") (uri "${KIPRJMOD}/StringCard.pretty") (options "") (descr "String card footprints")))')
edge='Sullins_EBC06DRAS_Mating_Card_2x06_P2.54mm'
edgepads=[]
for i in range(6):
 for side,layer in [('A','F'),('B','B')]:
  edgepads.append(f'(pad "{side}{i+1}" connect rect (at {(i-2.5)*2.54} -3.75) (size 1.6 6.5) (layers "{layer}.Cu" "{layer}.Mask") (solder_mask_margin 0))')
(local/(edge+'.kicad_mod')).write_text(f'(footprint "{edge}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr exclude_from_pos_files exclude_from_bom) (property "Reference" "J1" (at 0 -9 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)))) (property "Value" "PCB fingers / EBC06DRAS" (at 0 -10.5 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15)))) '+''.join(edgepads)+')')
block('EdgeCard',[(f'A{i}',n,'passive') for i,n in enumerate(['GND','5V','3V3','SENSE+','STATUS_IN','RESERVED'],1)],[(f'B{i}',n,'passive') for i,n in enumerate(['GND','5V','DATA','SENSE-','STATUS_OUT','RESERVED'],1)],12.7)
block('StringOut', [('1','GND','passive'),('2','DATA','passive'),('3','5V','passive')],[],10.16)
block('TXU0101',[(1,'VCCA','power_in'),(2,'GND','power_in'),(3,'A','input')],[(6,'VCCB','power_in'),(5,'OE','input'),(4,'Y','output')],10.16)
block('StatusRGB',[(2,'DIN','input'),(1,'GND','power_in')],[(3,'VDD','power_in'),(4,'DOUT','output')],10.16)
define('PWR_FLAG',[('1','pwr',0,0,90,'power_out')],rect(-1,1,1,2))
s=Sheet('string-daughterboard','String daughterboard / Sullins EBC06DRAS',rootid)
b=k.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(k.FromMM(1.6))
nets={}; fps={}; expected={}
def net(n):
 if n not in nets:
  ni=k.NETINFO_ITEM(b,n);b.Add(ni);nets[n]=ni
 return nets[n]
def part(kind,ref,val,xy,pins,fp,pcbxy,angle=0,mpn=''):
 s.comp(kind,ref,val,*xy,pins,fp=fp)
 lib,name=fp.split(':'); p=local if lib=='StringCard' else F/(lib+'.pretty')
 f=k.FootprintLoad(str(p),name); assert f,fp
 f.SetReference(ref);f.SetValue(val);f.SetFPID(k.LIB_ID(lib,name))
 f.SetPath(k.KIID_PATH(s.symbols[ref]));f.SetSheetname('');f.SetSheetfile('string-daughterboard.kicad_sch')
 f.SetOrientationDegrees(angle);f.SetPosition(k.VECTOR2I(*[k.FromMM(v) for v in pcbxy]));b.Add(f)
 for pad in f.Pads():
  n=pins.get(pad.GetNumber())
  if n:pad.SetNet(net(n));expected[(ref,pad.GetNumber())]=n
 f.Value().SetVisible(False);f.Reference().SetTextSize(k.VECTOR2I(k.FromMM(.8),k.FromMM(.8)));f.Reference().SetTextThickness(k.FromMM(.15))
 fps[ref]=f
 # Manufacturer part is recorded in schematic value / README.
 return f
edgepins={'A1':'GND','B1':'GND','A2':'IN_5V','B2':'IN_5V','A3':'PERIPH_3V3','B3':'STRING_DATA_IN','A4':'SHUNT_HI','B4':'STRING_5V','A5':'STATUS_DATA_IN','B5':'STATUS_DATA_OUT','A6':None,'B6':None}
part('EdgeCard','J1','PCB fingers: mates EBC06DRAS',(60.96,66.04),edgepins,'StringCard:'+edge,(20,52))
part('Fuse','F1','3A / 0451003.MRL',(147.32,43.18),{'1':'IN_5V','2':'SHUNT_HI'},'Fuse:Fuse_Littelfuse-NANO2-451_453',(14,33),90,'0451003.MRL')
part('R','R1','50m / 1W / WSL2512R0500FEA',(238.76,43.18),{'1':'SHUNT_HI','2':'STRING_5V'},'StringCard:Vishay_WSL2512_50mR',(14,20),90,'WSL2512R0500FEA')
part('StringOut','J2','STRING: GND / DATA / 5V',(302.26,66.04),{'1':'GND','2':'STRING_DATA','3':'STRING_5V'},'StringCard:JST_XH_S3B-XH-A_1x03_P2.50mm_Horizontal',(22.5,6),180,'S3B-XH-A(LF)(SN)')
part('TXU0101','U1','TXU0101DBVR / string',(160.02,114.3),{'1':'PERIPH_3V3','2':'GND','3':'STRING_DATA_IN','4':'STRING_BUF','5':'PERIPH_3V3','6':'STRING_5V'},'Package_TO_SOT_SMD:SOT-23-6',(25,20),0,'TXU0101DBVR')
part('R','R2','220R / string data',(233.68,116.84),{'1':'STRING_BUF','2':'STRING_DATA'},'Resistor_SMD:R_0805_2012Metric',(25,14),0,'RC0805FR-07220RL')
part('C','C1','100n / next to U1 VCCA pin 1',(119.38,149.86),{'1':'PERIPH_3V3','2':'GND'},'Capacitor_SMD:C_0805_2012Metric',(21,23),0)
part('C','C2','100n / next to U1 VCCB pin 6',(210.82,149.86),{'1':'STRING_5V','2':'GND'},'Capacitor_SMD:C_0805_2012Metric',(25,24),0)
part('C','C3','10u / 16V / string output buffering',(330.2,139.7),{'1':'STRING_5V','2':'GND'},'Capacitor_SMD:C_1206_3216Metric',(15,12),0)
part('TXU0101','U2','TXU0101DBVR / status',(160.02,205.74),{'1':'PERIPH_3V3','2':'GND','3':'STATUS_DATA_IN','4':'STATUS_BUF','5':'PERIPH_3V3','6':'IN_5V'},'Package_TO_SOT_SMD:SOT-23-6',(26,33),0,'TXU0101DBVR')
part('StatusRGB','D1','OPSCO SK6812-B-012 / status',(330.2,205.74),{'1':'GND','2':'STATUS_LED_IN','3':'IN_5V','4':'STATUS_DATA_OUT'},'LED_SMD:LED_OPSCO_SK6812_PLCC4_5.0x5.0mm_P3.1mm',(33,17),0,'SK6812-B-012')
part('R','R3','220R / status data',(238.76,205.74),{'1':'STATUS_BUF','2':'STATUS_LED_IN'},'Resistor_SMD:R_0805_2012Metric',(33,24),90,'RC0805FR-07220RL')
for ref,val,xy,pins,pos in [('C4','100n / next to U2 VCCA pin 1',(119.38,241.3),{'1':'PERIPH_3V3','2':'GND'},(22,36)),('C5','100n / next to U2 VCCB pin 6',(210.82,241.3),{'1':'IN_5V','2':'GND'},(26,37)),('C6','100n / next to D1 VDD pin 3',(330.2,241.3),{'1':'IN_5V','2':'GND'},(34,12)),('C7','10u / 16V / status buffering',(330.2,165.1),{'1':'IN_5V','2':'GND'},(34,29))]:
 part('C',ref,val,xy,pins,'Capacitor_SMD:C_0805_2012Metric' if ref!='C7' else 'Capacitor_SMD:C_1206_3216Metric',pos)
for i,n in enumerate(['GND','IN_5V','PERIPH_3V3','STRING_5V'],1):s.comp('PWR_FLAG',f'#FLG0{i}','',25.4+i*45.72,261.62,{'1':n})
s.note(25.4,15.24,'STRING DAUGHTERBOARD — 2 A nominal / power OFF before swapping',2)
s.note(25.4,99.06,'J1 = PCB fingers, not a fitted socket.\nA = component face; B = back face.\nINA3221 remains on carrier.\nA4/B4 are Kelvin sense only.\nReserved A6/B6 are not connected.',1.4)
s.note(119.38,25.4,'POWER: fuse -> shunt -> string output',1.5)
s.note(119.38,172.72,'STATUS: independent 3.3 V input, local 5 V translation',1.5)
s.save()
# Closed notched outline; insertion tongue has no components or inner copper.
outline=[(0,0),(40,0),(40,44),(28.7,44),(28.7,52),(11.3,52),(11.3,44),(0,44),(0,0)]
for a,z in zip(outline,outline[1:]):
 sh=k.PCB_SHAPE();sh.SetShape(k.SHAPE_T_SEGMENT);sh.SetLayer(k.Edge_Cuts);sh.SetWidth(k.FromMM(.05));sh.SetStart(k.VECTOR2I(*[k.FromMM(v) for v in a]));sh.SetEnd(k.VECTOR2I(*[k.FromMM(v) for v in z]));b.Add(sh)
for i,pos in enumerate([(4,5),(36,5)],1):
 f=k.FootprintLoad(str(F/'MountingHole.pretty'),'MountingHole_2.7mm_M2.5');f.SetReference(f'H{i}');f.SetPosition(k.VECTOR2I(*[k.FromMM(v) for v in pos]));f.SetAttributes(k.FP_EXCLUDE_FROM_BOM|k.FP_EXCLUDE_FROM_POS_FILES|k.FP_BOARD_ONLY);b.Add(f)
for txt,pos,size in [('STRING CARD',(20,40),1),('GND  DATA  +5V',(20,10),.8),('POWER OFF TO SWAP',(20,42),.8)]:
 t=k.PCB_TEXT(b);t.SetText(txt);t.SetPosition(k.VECTOR2I(*[k.FromMM(v) for v in pos]));t.SetTextSize(k.VECTOR2I(k.FromMM(size),k.FromMM(size)));t.SetTextThickness(k.FromMM(.15));t.SetLayer(k.F_SilkS);b.Add(t)
k.SaveBoard('string-daughterboard.kicad_pcb',b)
Path('string-daughterboard.kicad_pro').write_text(json.dumps({'meta':{'filename':'string-daughterboard.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.2,'min_copper_edge_clearance':.3}}}},indent=2))
Path('expected-nets.json').write_text(json.dumps({ref+':'+pin:n for (ref,pin),n in expected.items()},indent=2))
print('Created schematic and placed, unrouted 40 x 52 mm board.')
