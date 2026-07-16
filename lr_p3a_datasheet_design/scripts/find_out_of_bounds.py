import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    print("Out-of-bounds Footprints:")
    for fp in board.GetFootprints():
        pos = fp.GetPosition()
        x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        if x < 0 or x > 230 or y < 0 or y > 150:
            print(f"  Footprint {fp.GetReference()} at ({x:.3f}, {y:.3f})")
            
    print("\nOut-of-bounds Tracks/Vias:")
    for track in board.GetTracks():
        pos = track.GetPosition()
        x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        if x < 0 or x > 230 or y < 0 or y > 150:
            is_via = isinstance(track, pcbnew.PCB_VIA)
            netname = track.GetNet().GetNetname() if track.GetNet() else "GND"
            print(f"  Track/Via (via={is_via}) : net={netname} at ({x:.3f}, {y:.3f})")

if __name__ == "__main__":
    main()
