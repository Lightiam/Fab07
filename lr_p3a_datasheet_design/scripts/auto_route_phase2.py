import pcbnew
import os
from collections import defaultdict

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    # 1. Define Phase 2 nets and properties
    nets_config = {
        "HBM4_SIDECH_A": {"width": 0.10, "layer": 8},   # In3.Cu (L8 in pcb)
        "HBM4_SIDECH_B": {"width": 0.10, "layer": 8},
        "MGMT_A": {"width": 0.15, "layer": 0},          # F.Cu
        "MGMT_B": {"width": 0.15, "layer": 0},
        "BIAS_TUNE_A": {"width": 0.15, "layer": 0},
        "BIAS_TUNE_B": {"width": 0.15, "layer": 0},
        "TEC_TH_A": {"width": 0.15, "layer": 0},
        "TEC_TH_B": {"width": 0.15, "layer": 0},
        "PD_MON_A": {"width": 0.15, "layer": 0},
        "PD_MON_B": {"width": 0.15, "layer": 0}
    }
    
    # 2. Remove existing tracks for these nets to ensure idempotence
    tracks_to_remove = []
    for track in board.GetTracks():
        netname = track.GetNet().GetNetname()
        if netname in nets_config:
            tracks_to_remove.append(track)
            
    for track in tracks_to_remove:
        board.Remove(track)
    print(f"Removed {len(tracks_to_remove)} existing tracks.")

    # 3. Connect pads for each net using orthogonal comb routing
    for netname, config in nets_config.items():
        net = board.FindNet(netname)
        if not net:
            print(f"Warning: Net {netname} not found in board. Skipping.")
            continue
            
        width_mm = config["width"]
        layer_id = config["layer"]
        
        # Collect all pads for this net
        pads = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNet().GetNetname() == netname:
                    pads.append(pad)
                    
        if len(pads) < 2:
            print(f"Net {netname} has only {len(pads)} pads. Skipping routing.")
            continue
            
        # Group pads by Y coordinate (using a small tolerance of 0.05 mm)
        rows = defaultdict(list)
        for pad in pads:
            y_rounded = round(pcbnew.ToMM(pad.GetPosition().y), 3)
            rows[y_rounded].append(pad)
            
        # Draw horizontal tracks along each row
        segments_added = 0
        representative_pads = []
        
        for y_coord in sorted(rows.keys()):
            row_pads = rows[y_coord]
            # Sort pads by X coordinate
            row_pads.sort(key=lambda p: p.GetPosition().x)
            
            # Connect adjacent pads in the row
            for i in range(len(row_pads) - 1):
                p1 = row_pads[i].GetPosition()
                p2 = row_pads[i+1].GetPosition()
                
                if p1 == p2:
                    continue
                    
                track = pcbnew.PCB_TRACK(board)
                track.SetStart(p1)
                track.SetEnd(p2)
                track.SetWidth(pcbnew.FromMM(width_mm))
                track.SetLayer(layer_id)
                track.SetNet(net)
                board.Add(track)
                segments_added += 1
                
            # Keep the first pad as the representative pad for this row
            representative_pads.append(row_pads[0])
            
        # Draw vertical tracks to connect the rows together at their minimum X edges
        representative_pads.sort(key=lambda p: p.GetPosition().y)
        for i in range(len(representative_pads) - 1):
            p1 = representative_pads[i].GetPosition()
            p2 = representative_pads[i+1].GetPosition()
            
            # We want to route orthogonally, so draw a vertical track from p1 to p2's Y level
            # Since the representative pads are at the same X coordinate (or very close),
            # we draw a vertical line. To be precise, we connect (p1.x, p1.y) -> (p1.x, p2.y)
            # and then a horizontal line (p1.x, p2.y) -> (p2.x, p2.y) if their X coordinate differs.
            if p1 == p2:
                continue
                
            # Vertical segment
            track_v = pcbnew.PCB_TRACK(board)
            track_v.SetStart(p1)
            # End is at p1's X, but p2's Y
            end_pos = pcbnew.VECTOR2I(p1.x, p2.y)
            track_v.SetEnd(end_pos)
            track_v.SetWidth(pcbnew.FromMM(width_mm))
            track_v.SetLayer(layer_id)
            track_v.SetNet(net)
            board.Add(track_v)
            segments_added += 1
            
            # Horizontal jog (if X coordinates are not identical)
            if p1.x != p2.x:
                track_h = pcbnew.PCB_TRACK(board)
                track_h.SetStart(end_pos)
                track_h.SetEnd(p2)
                track_h.SetWidth(pcbnew.FromMM(width_mm))
                track_h.SetLayer(layer_id)
                track_h.SetNet(net)
                board.Add(track_h)
                segments_added += 1
                
        print(f"Net {netname}: Routed {segments_added} segments on layer {layer_id} with width {width_mm} mm using comb routing.")

    # 4. Pour GND and PWR_CORE zones
    print("Regenerating copper zones...")
    try:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
    except Exception as e:
        print(f"Warning: Zone filler failed to execute ({e}). Pours will update on next open in KiCad.")

    # 5. Save the board
    pcbnew.SaveBoard(pcb_path, board)
    print("PCB Phase 2 routing and planes update complete!")

if __name__ == "__main__":
    main()
