import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    via_counts = {}
    for track in board.GetTracks():
        if isinstance(track, pcbnew.PCB_VIA):
            netcode = track.GetNetCode()
            via_counts[netcode] = via_counts.get(netcode, 0) + 1
            
    print("Vias grouped by net code:")
    for netcode, count in sorted(via_counts.items(), key=lambda x: x[1], reverse=True):
        netname = board.FindNet(netcode).GetNetname() if board.FindNet(netcode) else "Unknown"
        print(f"  Code: {netcode:3d} | Name: {netname:20} | Count: {count}")

if __name__ == "__main__":
    main()
