import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    print("Footprints on board:")
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        pos = fp.GetPosition()
        print(f"  {ref} at ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f})")

if __name__ == "__main__":
    main()
