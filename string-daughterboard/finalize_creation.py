raise SystemExit("Archived creation helper: do not regenerate over the current design.")
from pathlib import Path
import re,json,xml.etree.ElementTree as E
import pcbnew as k
p=Path(__file__).resolve().parent; f=p/'string-daughterboard.kicad_sch';s=f.read_text()
# Set only J1's instance BOM attribute to match the integral copper footprint.
a=s.index('(symbol (lib_id "Review:EdgeCard")');z=s.index('(uuid',a)
s=s[:a]+s[a:z].replace('(in_bom yes)','(in_bom no)')+s[z:];f.write_text(s)
# Publish embedded symbol definitions as an ordinary project-local library.
a=s.index('(lib_symbols ')+len('(lib_symbols ');i=a;depth=1;quote=False;escape=False
while depth:
 c=s[i]
 if quote:
  if escape:escape=False
  elif c=='\\':escape=True
  elif c=='"':quote=False
 elif c=='"':quote=True
 elif c=='(':depth+=1
 elif c==')':depth-=1
 i+=1
libs=s[a:i-1];libs=re.sub(r'\(symbol "Review:([^\"]+)"',r'(symbol "\1"',libs)
(p/'StringCard.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+libs+')')
(p/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Review") (type "KiCad") (uri "${KIPRJMOD}/StringCard.kicad_sym") (options "") (descr "String daughterboard symbols")))')
b=k.LoadBoard(str(p/'string-daughterboard.kicad_pcb'));edge=next(x for x in b.GetFootprints() if x.GetReference()=='J1')
for pad in edge.Pads():
 if pad.GetNumber() in ['A6','B6']:
  n=k.NETINFO_ITEM(b,'unconnected-(J1-RESERVED-Pad'+pad.GetNumber()+')');b.Add(n);pad.SetNet(n)
for d in b.GetDrawings():
 if isinstance(d,k.PCB_TEXT) and d.GetText()=='GND  DATA  +5V':d.SetPosition(k.VECTOR2I(k.FromMM(20),k.FromMM(8.9)))
k.SaveBoard(str(p/'string-daughterboard.kicad_pcb'),b)
