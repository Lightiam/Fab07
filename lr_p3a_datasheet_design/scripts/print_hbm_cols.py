import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    for netname in ["HBM4_VDDQL", "HBM4_VDDC"]:
        fp = board.FindFootprintByReference("U101")
        pads = []
        for pad in fp.Pads():
            if pad.GetNet() and pad.GetNet().GetNetname() == netname:
                pads.append(pad)
        print(f"\nNet {netname} pads ({len(pads)} total):")
        # Group by rounded X coordinate (column)
        cols = {}
        for p in pads:
            pos = p.GetPosition()
            x = round(pcbnew.ToMM(pos.x), 1)
            y = round(pcbnew.ToMM(pos.y), 1)
            if x not in cols:
                cols[x] = []
            cols[x].append((p.GetName(), y))
            
        for x in sorted(cols.keys()):
            col_pads = sorted(cols[x], key=lambda item: item[1])
            pad_strs = [f"{name}(Y={y:.1f})" for name, y in col_pads]
            print(f"  Col X={x:.1f} ({len(col_pads)} pads): {', '.join(pad_strs)}")

if __name__ == "__main__":
    main()
