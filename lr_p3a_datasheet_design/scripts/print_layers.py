import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    print("Layer IDs and Names:")
    for i in range(128):
        name = board.GetLayerName(i)
        if name and "BAD INDEX" not in name:
            print(f"  ID {i:3d}: {name}")

if __name__ == "__main__":
    main()
