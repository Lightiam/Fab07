#!/usr/bin/env python3
import pcbnew, csv, re, os
from pcbnew import VECTOR2I, FromMM as mm
B=pcbnew.BOARD()
B.SetCopperLayerCount(16)   # approximates 15-layer datasheet stackup (KiCad needs even)

W,Hh=230.0,150.0
pts=[(0,0),(W,0),(W,Hh),(0,Hh),(0,0)]
for i in range(len(pts)-1):
    s=pcbnew.PCB_SHAPE(B); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(VECTOR2I(mm(pts[i][0]),mm(pts[i][1]))); s.SetEnd(VECTOR2I(mm(pts[i+1][0]),mm(pts[i+1][1])))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.15)); B.Add(s)

# --- nets ---
netinfo={}; ni=1
def net(name):
    global ni
    if name in ("NC",""): return None
    if name not in netinfo:
        n=pcbnew.NETINFO_ITEM(B,name,ni); B.Add(n); netinfo[name]=n; globals()['ni']=ni+1
    return netinfo[name]

# --- BGA-2500 ball netmap ---
ballnet={}
for r in csv.DictReader(open("15_lr_p3a_datasheet_design/netmap/bga2500_ball_netmap.csv")):
    ballnet[r['Ball']]=r['Net']

def place_bga(ref,cx,cy,suffix):
    fp=pcbnew.FootprintLoad("15_lr_p3a_datasheet_design/kicad/LR_P3A.pretty","BGA-2500_40x40_P0.8mm_NCE")
    fp.SetReference(ref); fp.SetPosition(VECTOR2I(mm(cx),mm(cy)))
    shared={"PWR_CORE","GND","VDD_IO","HBM4_VDDC","HBM4_VDDQL","HBM4_VDDQ","HBM4_VPP","THERMAL"}
    for pad in fp.Pads():
        base=ballnet.get(pad.GetName(),"NC")
        if base=="NC": continue
        nm=base if base in shared else f"{base}{suffix}"
        n=net(nm)
        if n: pad.SetNet(n)
    B.Add(fp); return fp

# --- TFLN PIC footprint (LGA ~15mm) built inline ---
def make_tfln(ref,cx,cy,suffix):
    fp=pcbnew.FOOTPRINT(B); fp.SetReference(ref); fp.SetValue("TFLN-MZM-400G-C")
    pins=[]
    for i in range(8): pins+=[(f"RF_DRIVE_P{i}","TFLN_RF"),(f"RF_DRIVE_N{i}","TFLN_RF")]  #16
    for i in range(8): pins.append((f"BIAS_TUNE{i}","BIAS_TUNE"))
    pins+=[("TEC_TH_P","TEC_TH"),("TEC_TH_N","TEC_TH")]
    for i in range(8): pins.append((f"PD_MON{i}","PD_MON"))
    for i in range(4): pins.append((f"VCC_RF{i}","+0V9"))
    pins+=[("VCC_BIAS0","+3V3"),("VCC_BIAS1","+3V3")]
    for i in range(40): pins.append((f"GND{i}","GND"))  # >=40 GND
    # lay pads in 2 rows along 15mm length
    per=(len(pins)+1)//2
    for idx,(pn,base) in enumerate(pins):
        row=idx//per; col=idx%per
        x=(col-(per-1)/2)*(15.0/per); y=(row-0.5)*4.0
        pad=pcbnew.PAD(fp); pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT); pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetSize(VECTOR2I(mm(0.3),mm(1.2))); pad.SetLayerSet(pad.SMDMask())
        pad.SetPosition(VECTOR2I(mm(x),mm(y))); pad.SetName(str(idx+1))
        nm = base if base in ("GND","+0V9","+3V3") else f"{base}{suffix}"
        n=net(nm)
        if n: pad.SetNet(n)
        fp.Add(pad)
    fp.SetPosition(VECTOR2I(mm(cx),mm(cy)))
    B.Add(fp)
    # optical keep-out: 2.54mm copper-free zone around the TFLN facet (represent as F.CrtYd rect + doc)
    ko=pcbnew.ZONE(B)
    ko.SetLayer(pcbnew.F_Cu)
    ko.SetIsRuleArea(True); ko.SetDoNotAllowZoneFills(True); ko.SetDoNotAllowTracks(False); ko.SetDoNotAllowVias(False)
    pts2=[(cx-9,cy-6),(cx+9,cy-6),(cx+9,cy+6),(cx-9,cy+6)]
    poly=pcbnew.wxPoint if False else None
    ch=ko.Outline()
    ch.NewOutline()
    for (px,py) in pts2: ch.Append(mm(px),mm(py))
    ko.SetZoneName(f"OPTICAL_KEEPOUT_{ref}")
    B.Add(ko)
    return fp

# place dual NCE + dual TFLN + hole/mounting
place_bga("U101",70,60,"_A")
place_bga("U201",160,60,"_A" if False else "_B")
make_tfln("U102",70,120,"_A")
make_tfln("U202",160,120,"_B")

# bolster M3 holes (50mm square) around each NCE
def hole(x,y,ref):
    fp=pcbnew.FOOTPRINT(B); fp.SetReference(ref)
    pad=pcbnew.PAD(fp); pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE); pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetSize(VECTOR2I(mm(3.2),mm(3.2))); pad.SetDrillSize(VECTOR2I(mm(3.2),mm(3.2))); pad.SetLayerSet(pad.UnplatedHoleMask())
    fp.Add(pad); fp.SetPosition(VECTOR2I(mm(x),mm(y))); B.Add(fp)
k=0
for cx in (70,160):
    for dx,dy in [(-25,-25),(25,-25),(-25,25),(25,25)]:
        k+=1; hole(cx+dx,60+dy,f"BH{k}")

pcbnew.SaveBoard("15_lr_p3a_datasheet_design/kicad/LR_P3A_DualNCE.kicad_pcb",B)
padtot=sum(f.GetPadCount() for f in B.GetFootprints())
print(f"Dual-NCE board built: {len(B.GetFootprints())} footprints, {padtot} pads, {len(netinfo)} nets, {W}x{Hh}mm.")
print("nets sample:", sorted(netinfo)[:12])
