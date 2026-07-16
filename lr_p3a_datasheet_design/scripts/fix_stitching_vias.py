import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    # Identify GND net
    gnd_net = board.FindNet("GND")
    gnd_netcode = gnd_net.GetNetCode() if gnd_net else 8
    print(f"GND Netcode: {gnd_netcode}")
    
    # Collect vias to remove
    vias_to_remove = []
    all_vias_count = 0
    for track in board.GetTracks():
        if isinstance(track, pcbnew.PCB_VIA):
            all_vias_count += 1
            if track.GetNetCode() == gnd_netcode:
                vias_to_remove.append(track)
                
    print(f"Found {all_vias_count} vias in total, {len(vias_to_remove)} are GND stitching vias.")
    
    # Remove the vias
    for via in vias_to_remove:
        board.Remove(via)
        
    print(f"Removed {len(vias_to_remove)} GND stitching vias.")
    
    # Save the board
    print("Saving board...")
    board.Save(pcb_path)
    print("Done!")

if __name__ == "__main__":
    main()
