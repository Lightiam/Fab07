import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    nets = ["HBM4_VDDQ", "HBM4_VDDQL", "HBM4_VPP"]
    for netname in nets:
        net = board.FindNet(netname)
        if not net:
            print(f"Net {netname} not found.")
            continue
            
        print(f"Net {netname} pads:")
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            pads = []
            for pad in fp.Pads():
                if pad.GetNet().GetNetname() == netname:
                    pads.append(pad)
            if pads:
                print(f"  Footprint {ref}: {len(pads)} pads")
                # Print coordinates of first 5 pads as sample
                for i, pad in enumerate(pads[:5]):
                    pos = pad.GetPosition()
                    print(f"    Pad {pad.GetName()}: ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f})")
                if len(pads) > 5:
                    print(f"    ... and {len(pads)-5} more pads")

if __name__ == "__main__":
    main()
