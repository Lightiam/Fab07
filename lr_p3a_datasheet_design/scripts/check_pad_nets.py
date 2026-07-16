import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    for ref in ["U101", "U201"]:
        fp = board.FindFootprintByReference(ref)
        pad = fp.FindPadByNumber("E7")
        netname = pad.GetNet().GetNetname() if pad.GetNet() else "None"
        pos = pad.GetPosition()
        print(f"Footprint {ref} pad E7: net={netname} at ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f})")

if __name__ == "__main__":
    main()
