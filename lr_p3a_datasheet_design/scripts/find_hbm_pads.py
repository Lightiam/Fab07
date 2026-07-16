import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    print(f"Loading PCB from: {pcb_path}")
    print(f"File exists: {os.path.exists(pcb_path)}")
    board = pcbnew.LoadBoard(pcb_path)
    
    nets = ["HBM4_VDDQ", "HBM4_VDDQL", "HBM4_VPP"]
    for netname in nets:
        net = board.FindNet(netname)
        if not net:
            print(f"Net {netname} not found.")
            continue
            
        pads = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNet().GetNetname() == netname:
                    pads.append(pad)
                    
        print(f"Net {netname} has {len(pads)} pads:")
        # Group by footprint
        fp_pads = {}
        for pad in pads:
            fp_ref = pad.GetParent().GetReference()
            if fp_ref not in fp_pads:
                fp_pads[fp_ref] = []
            fp_pads[fp_ref].append(pad)
            
        for fp_ref, fp_p in fp_pads.items():
            xs = [pcbnew.ToMM(p.GetPosition().x) for p in fp_p]
            ys = [pcbnew.ToMM(p.GetPosition().y) for p in fp_p]
            print(f"  Footprint {fp_ref}: {len(fp_p)} pads, X bounds: [{min(xs):.3f}, {max(xs):.3f}], Y bounds: [{min(ys):.3f}, {max(ys):.3f}]")

if __name__ == "__main__":
    main()
