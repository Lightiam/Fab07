import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    # 1. Define Phase 1 nets and properties
    nets_config = {
        "SERDES_200G_A": {"width": 0.09, "layer": 26}, # In12.Cu (L13 in pcb)
        "SERDES_200G_B": {"width": 0.09, "layer": 26},
        "PCIE_G6_A": {"width": 0.12, "layer": 26},
        "PCIE_G6_B": {"width": 0.12, "layer": 26},
        "TFLN_RF_A": {"width": 0.15, "layer": 12},     # In5.Cu (L6 in pcb)
        "TFLN_RF_B": {"width": 0.15, "layer": 12}
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

    # 3. Connect pads for each net using Nearest Neighbor routing
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
            
        # Nearest-Neighbor TSP heuristic to find a short daisy-chain path
        unvisited = list(pads)
        curr = unvisited.pop(0)
        path = [curr]
        
        while unvisited:
            curr_pos = curr.GetPosition()
            # Find nearest pad
            nearest_idx = min(
                range(len(unvisited)), 
                key=lambda i: (unvisited[i].GetPosition() - curr_pos).EuclideanNorm()
            )
            curr = unvisited.pop(nearest_idx)
            path.append(curr)
            
        # Draw tracks between adjacent pads in the path
        segments_added = 0
        for i in range(len(path) - 1):
            p1 = path[i].GetPosition()
            p2 = path[i+1].GetPosition()
            
            # Skip if they are exactly at the same location
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
            
        print(f"Net {netname}: Routed {segments_added} segments on layer {layer_id} with width {width_mm} mm.")

    # 4. Pour GND and PWR_CORE zones
    # Remove existing zones for GND and PWR_CORE to avoid duplication
    zones_to_remove = []
    # Support both zones property and GetZones function depending on KiCad version
    try:
        zones_list = list(board.Zones())
    except AttributeError:
        zones_list = list(board.GetZones())
        
    for zone in zones_list:
        zone_netname = zone.GetNet().GetNetname() if zone.GetNet() else ""
        if zone_netname in ["GND", "PWR_CORE"]:
            zones_to_remove.append(zone)
            
    for zone in zones_to_remove:
        board.Remove(zone)
    print(f"Removed {len(zones_to_remove)} existing plane zones.")

    # Setup plane pour boundaries: 0.5 to 229.5 mm (W=230, H=150)
    boundary_pts = [
        pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(0.5)),
        pcbnew.VECTOR2I(pcbnew.FromMM(229.5), pcbnew.FromMM(0.5)),
        pcbnew.VECTOR2I(pcbnew.FromMM(229.5), pcbnew.FromMM(149.5)),
        pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(149.5))
    ]

    # Create GND zone (L8 = 16)
    gnd_net = board.FindNet("GND")
    if gnd_net:
        gnd_zone = pcbnew.ZONE(board)
        gnd_zone.SetLayer(16) # In7.Cu
        gnd_zone.SetNet(gnd_net)
        gnd_zone.SetIsRuleArea(False)
        outline = gnd_zone.Outline()
        outline.NewOutline()
        for pt in boundary_pts:
            outline.Append(pt)
        board.Add(gnd_zone)
        print("GND plane zone created on layer 16 (In7.Cu).")
        
    # Create PWR_CORE zone (L13 = 26)
    pwr_net = board.FindNet("PWR_CORE")
    if pwr_net:
        pwr_zone = pcbnew.ZONE(board)
        pwr_zone.SetLayer(26) # In12.Cu
        pwr_zone.SetNet(pwr_net)
        pwr_zone.SetIsRuleArea(False)
        outline = pwr_zone.Outline()
        outline.NewOutline()
        for pt in boundary_pts:
            outline.Append(pt)
        board.Add(pwr_zone)
        print("PWR_CORE plane zone created on layer 26 (In12.Cu).")

    # Fill all zones
    print("Regenerating copper zones...")
    try:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
    except Exception as e:
        print(f"Warning: Zone filler failed to execute ({e}). Pours will update on next open in KiCad.")

    # 5. Save the board
    pcbnew.SaveBoard(pcb_path, board)
    print("PCB routing and planes update complete!")

if __name__ == "__main__":
    main()
