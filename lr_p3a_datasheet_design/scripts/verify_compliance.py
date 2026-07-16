#!/usr/bin/env python3
"""Compliance checks on the BGA-2500 footprint per owner's verification spec:
pad count = 2500, SMD, pad dia = 0.45mm, uniform 0.8mm pitch."""
import re, sys, math
fp=open("15_lr_p3a_datasheet_design/kicad/LR_P3A.pretty/BGA-2500_40x40_P0.8mm_NCE.kicad_mod").read()
pads=re.findall(r'\(pad "([^"]+)" (\w+) circle \(at ([-0-9.]+) ([-0-9.]+)\) \(size ([0-9.]+) ([0-9.]+)\)', fp)
n=len(pads)
res=[]
# 1. pad count
res.append(("Pad/ball count == 2500", n==2500, f"{n}"))
# 2. all SMD
allsmd=all(p[1]=='smd' for p in pads)
res.append(("All pads SMD", allsmd, "smd" if allsmd else "mixed"))
# 3. pad diameter 0.45
dias=set(round(float(p[4]),3) for p in pads)
res.append(("Pad diameter == 0.45mm", dias=={0.45}, str(sorted(dias))))
# 4. pitch 0.8 uniform (check X and Y deltas of adjacent balls)
xs=sorted(set(round(float(p[2]),3) for p in pads))
ys=sorted(set(round(float(p[3]),3) for p in pads))
dx=set(round(xs[i+1]-xs[i],3) for i in range(len(xs)-1))
dy=set(round(ys[i+1]-ys[i],3) for i in range(len(ys)-1))
res.append(("Uniform 0.8mm pitch X", dx=={0.8}, str(sorted(dx))))
res.append(("Uniform 0.8mm pitch Y", dy=={0.8}, str(sorted(dy))))
res.append(("Grid 50x50", len(xs)==50 and len(ys)==50, f"{len(xs)}x{len(ys)}"))
# 5. package extent 40x40 (span + pad)
span=round(max(xs)-min(xs)+0.45,2)
res.append(("Package extent ~40mm", abs(span-39.65)<0.5 or abs(span-40.0)<0.5, f"{span}mm ball-field"))
print("=== BGA-2500 Footprint Compliance ===")
ok=True
for name,passed,val in res:
    print(f"  [{'PASS' if passed else 'FAIL'}] {name:30s} : {val}")
    ok=ok and passed
print("RESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
