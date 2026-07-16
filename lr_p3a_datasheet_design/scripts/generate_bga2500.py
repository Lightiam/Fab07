#!/usr/bin/env python3
"""Generate the real NCE BGA-2500 footprint (.kicad_mod) + per-ball net allocation
from the owner-supplied Rev 3.0 pin-allocation spec. 50x50 grid, 0.8mm pitch,
0.45mm SMD (solder-mask-defined) pads."""
import csv, os
N=50; PITCH=0.8; PAD=0.45; SMO=PAD+0.050
# JEDEC-style row letters (skip I,O,Q,S,X,Z), extend to AA.. for >23
def row_letters(n):
    base=[c for c in "ABCDEFGHJKLMNPRTUVWY"]  # 20 single letters (JEDEC skip)
    out=list(base)
    pi=0
    while len(out)<n:
        for b in base:
            out.append(base[pi]+b)
            if len(out)>=n: break
        pi+=1
    return out[:n]
ROWS=row_letters(N)                    # 50 row labels (top->bottom)
COLS=[str(i) for i in range(1,N+1)]    # 50 columns (left->right)

def zone(r,c):
    """Return net name for grid position (r,c) 0-indexed, per owner allocation."""
    # edges/regions
    north = r < 5           # top -> SerDes
    south = r >= N-6        # bottom -> PCIe
    east  = c >= N-4        # right -> HBM4 interposer face
    nw    = (r < 6 and c < 6)
    center = (abs(r-(N-1)/2)<1 and abs(c-(N-1)/2)<1)
    core  = (10 <= c <= 40) and (9 <= r <= 37)   # cols N..AK, rows 10..38 (approx)
    return (north,south,east,nw,center,core)

# Allocate by target counts, filling from the specified regions first.
targets=[("PWR_CORE",612),("GND",624),("VDD_IO",96),
         ("HBM4_VDDC",40),("HBM4_VDDQL",40),("HBM4_VDDQ",40),("HBM4_VPP",16),
         ("HBM4_SIDECH",32),("PCIE_G6",144),("SERDES_200G",96),("MGMT",32),("THERMAL",4)]
alloc={}   # (r,c)->net
def take(region_fn, name, count):
    got=0
    for r in range(N):
        for c in range(N):
            if got>=count: return got
            if (r,c) in alloc: continue
            if region_fn(r,c): alloc[(r,c)]=name; got+=1
    return got

# region predicates
cen=(N-1)/2
# priority: fixed small/edge zones first, then core, then GND, then NC
take(lambda r,c: abs(r-cen)<=0.5 and abs(c-cen)<=1.5, "THERMAL", 4)   # 4 center balls
take(lambda r,c: r<6 and c<6, "MGMT", 32)                            # NW corner
take(lambda r,c: r<4, "SERDES_200G", 96)                             # North edge
take(lambda r,c: r>=N-5, "PCIE_G6", 144)                            # South edge
take(lambda r,c: c>=N-3, "HBM4_VDDC", 40)                           # East face
take(lambda r,c: c>=N-4, "HBM4_VDDQL", 40)
take(lambda r,c: c>=N-4, "HBM4_VDDQ", 40)
take(lambda r,c: c>=N-5, "HBM4_VPP", 16)
take(lambda r,c: c>=N-6, "HBM4_SIDECH", 32)
take(lambda r,c: r<8 or r>=N-8 or c<8 or c>=N-8, "VDD_IO", 96)      # outer rings
take(lambda r,c: (10<=c<=40 and 9<=r<=37), "PWR_CORE", 612)         # central core
# GND distributed across remaining, then NC
gnd=0
for r in range(N):
    for c in range(N):
        if (r,c) in alloc: continue
        if gnd<624 and ((r+c)%2==0):
            alloc[(r,c)]="GND"; gnd+=1
# everything still empty = NC
nc=0
for r in range(N):
    for c in range(N):
        if (r,c) not in alloc: alloc[(r,c)]="NC"; nc+=1

# write footprint
OUT="15_lr_p3a_datasheet_design/kicad/LR_P3A.pretty/BGA-2500_40x40_P0.8mm_NCE.kicad_mod"
lines=['(footprint "BGA-2500_40x40_P0.8mm_NCE" (version 20240108) (generator "lightrail_gen")',
       '  (layer "F.Cu")',
       '  (descr "NCE Gen3 composite module, BGA-2500, 40x40mm, 0.8mm pitch, 0.45mm SMD pads")',
       '  (attr smd)']
off=-(N-1)*PITCH/2
for r in range(N):
    for c in range(N):
        x=off+c*PITCH; y=off+r*PITCH
        name=f"{ROWS[r]}{COLS[c]}"
        lines.append(f'  (pad "{name}" smd circle (at {x:.4f} {y:.4f}) (size {PAD} {PAD}) '
                     f'(layers "F.Cu" "F.Paste" "F.Mask")(solder_mask_margin 0.025))')
# courtyard 40x40
h=20.0
lines.append(f'  (fp_rect (start {-h} {-h}) (end {h} {h}) (layer "F.CrtYd")(stroke (width 0.05)(type solid)))')
lines.append(')')
open(OUT,"w").write("\n".join(lines)+"\n")

# write net allocation CSV
os.makedirs("15_lr_p3a_datasheet_design/netmap",exist_ok=True)
with open("15_lr_p3a_datasheet_design/netmap/bga2500_ball_netmap.csv","w",newline='\n') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(["Ball","Row","Col","Net","Zone"])
    for r in range(N):
        for c in range(N):
            w.writerow([f"{ROWS[r]}{COLS[c]}",ROWS[r],COLS[c],alloc[(r,c)],""])

from collections import Counter
cc=Counter(alloc.values())
print("BGA-2500 footprint written. Ball allocation:")
for k,v in sorted(cc.items(),key=lambda x:-x[1]): print(f"  {v:5d}  {k}")
print("  TOTAL:", sum(cc.values()))
