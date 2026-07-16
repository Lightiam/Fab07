import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    for ref in ["U101", "U201"]:
        fp = board.FindFootprintByReference(ref)
        if not fp:
            print(f"Footprint {ref} not found.")
            continue
        bbox = fp.GetBoundingBox()
        print(f"Footprint {ref} bounding box:")
        print(f"  X: [{pcbnew.ToMM(bbox.GetX()):.3f}, {pcbnew.ToMM(bbox.GetRight()):.3f}]")
        print(f"  Y: [{pcbnew.ToMM(bbox.GetY()):.3f}, {pcbnew.ToMM(bbox.GetBottom()):.3f}]")
        print(f"  Center: ({pcbnew.ToMM(fp.GetPosition().x):.3f}, {pcbnew.ToMM(fp.GetPosition().y):.3f})")

if __name__ == "__main__":
    main()
