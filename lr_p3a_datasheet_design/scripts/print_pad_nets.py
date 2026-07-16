import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    pads_to_check = [
        ("U101", "P43"), ("U101", "P44"), ("U101", "P42"),
        ("U201", "P43"), ("U201", "P44"), ("U201", "P42")
    ]
    
    print("Pad Net Assignments:")
    for ref, padname in pads_to_check:
        fp = board.FindFootprintByReference(ref)
        if not fp:
            continue
        pad = None
        for p in fp.Pads():
            if p.GetName() == padname:
                pad = p
                break
        if pad:
            netname = pad.GetNet().GetNetname() if pad.GetNet() else "None"
            pos = pad.GetPosition()
            print(f"  {ref}.{padname} : net={netname} at ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f})")

if __name__ == "__main__":
    main()
