import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    nets = board.GetNetInfo().NetsByNetcode()
    print("Nets on board:")
    for netcode, netinfo in sorted(nets.items()):
        print(f"  Code: {netcode:3d} | Name: {netinfo.GetNetname()}")

if __name__ == "__main__":
    main()
