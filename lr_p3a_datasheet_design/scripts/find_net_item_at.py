import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    coords = [
        (177.2, 51.6), (178.0, 50.8), (87.2, 51.6), (89.6, 51.6), (179.6, 51.6), (179.6, 52.4)
    ]
    
    print("Items at coordinates:")
    for cx, cy in coords:
        print(f"\nCoordinates: ({cx}, {cy})")
        # Pads
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            for pad in fp.Pads():
                pos = pad.GetPosition()
                px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                if abs(px - cx) < 0.1 and abs(py - cy) < 0.1:
                    print(f"  Pad {ref}.{pad.GetName()} : net={pad.GetNet().GetNetname()} at ({px:.3f}, {py:.3f})")
                    
        # Tracks/Vias
        for track in board.GetTracks():
            pos = track.GetPosition()
            tx, ty = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            is_via = isinstance(track, pcbnew.PCB_VIA)
            if is_via:
                if abs(tx - cx) < 0.1 and abs(ty - cy) < 0.1:
                    netname = track.GetNet().GetNetname() if track.GetNet() else "None"
                    print(f"  Via : net={netname} at ({tx:.3f}, {ty:.3f})")
            else:
                # Segment check
                start = track.GetStart()
                end = track.GetEnd()
                sx, sy = pcbnew.ToMM(start.x), pcbnew.ToMM(start.y)
                ex, ey = pcbnew.ToMM(end.x), pcbnew.ToMM(end.y)
                # Check if coordinate lies on the segment
                # Simple bounding box check first
                if min(sx, ex) - 0.1 <= cx <= max(sx, ex) + 0.1 and min(sy, ey) - 0.1 <= cy <= max(sy, ey) + 0.1:
                    netname = track.GetNet().GetNetname() if track.GetNet() else "None"
                    print(f"  Segment : net={netname} from ({sx:.3f}, {sy:.3f}) to ({ex:.3f}, {ey:.3f}) on layer {track.GetLayer()}")

if __name__ == "__main__":
    main()
