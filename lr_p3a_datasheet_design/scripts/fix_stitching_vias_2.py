import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    # Target net ID 8 (which is MGMT_B, but was used for stitching vias)
    target_netcode = 8
    print(f"Targeting Netcode: {target_netcode} (MGMT_B)")
    
    # Collect vias to remove
    vias_to_remove = []
    all_vias_count = 0
    for track in board.GetTracks():
        if isinstance(track, pcbnew.PCB_VIA):
            all_vias_count += 1
            if track.GetNetCode() == target_netcode:
                vias_to_remove.append(track)
                
    print(f"Found {all_vias_count} vias in total, {len(vias_to_remove)} are on netcode {target_netcode}.")
    
    # Remove the vias
    for via in vias_to_remove:
        board.Remove(via)
        
    print(f"Removed {len(vias_to_remove)} vias on netcode {target_netcode}.")
    
    # Save the board
    print("Saving board...")
    board.Save(pcb_path)
    print("Done!")

if __name__ == "__main__":
    main()
