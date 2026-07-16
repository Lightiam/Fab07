import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    for ref in ["U102", "U202"]:
        fp = board.FindFootprintByReference(ref)
        if not fp:
            print(f"Footprint {ref} not found.")
            continue
            
        pos = fp.GetPosition()
        print(f"Footprint {ref} position: ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f})")
        print("  Pads (first 5):")
        pads = list(fp.Pads())
        for pad in pads[:5]:
            pad_pos = pad.GetPosition()
            print(f"    Pad {pad.GetName()}: ({pcbnew.ToMM(pad_pos.x):.3f}, {pcbnew.ToMM(pad_pos.y):.3f})")

if __name__ == "__main__":
    main()
