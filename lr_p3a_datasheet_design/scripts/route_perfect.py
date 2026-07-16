import pcbnew
import os
import math

def snake_sort(pads):
    # Group pads by rounded Y coordinate
    rows = {}
    for p in pads:
        pos = p.GetPosition()
        y_rounded = round(pcbnew.ToMM(pos.y), 1)
        if y_rounded not in rows:
            rows[y_rounded] = []
        rows[y_rounded].append(p)
        
    # Sort rows by Y
    sorted_y = sorted(rows.keys())
    
    path = []
    for idx, y in enumerate(sorted_y):
        row_pads = rows[y]
        # Sort by X
        row_pads.sort(key=lambda p: p.GetPosition().x)
        if idx % 2 == 1:
            # Alternate direction for odd rows
            row_pads.reverse()
        path.extend(row_pads)
    return path

def column_snake_sort(pads):
    # Group pads by rounded X coordinate
    cols = {}
    for p in pads:
        pos = p.GetPosition()
        x_rounded = round(pcbnew.ToMM(pos.x), 1)
        if x_rounded not in cols:
            cols[x_rounded] = []
        cols[x_rounded].append(p)
        
    # Sort columns by X
    sorted_x = sorted(cols.keys())
    
    path = []
    for idx, x in enumerate(sorted_x):
        col_pads = cols[x]
        # Sort by Y
        col_pads.sort(key=lambda p: p.GetPosition().y)
        if idx % 2 == 1:
            # Alternate direction for odd columns
            col_pads.reverse()
        path.extend(col_pads)
    return path

def polar_sort(pads):
    if not pads:
        return []
    # Calculate center of pads
    xs = [pcbnew.ToMM(p.GetPosition().x) for p in pads]
    ys = [pcbnew.ToMM(p.GetPosition().y) for p in pads]
    cx = sum(xs) / len(pads)
    cy = sum(ys) / len(pads)
    
    return sorted(pads, key=lambda p: math.atan2(pcbnew.ToMM(p.GetPosition().y) - cy, pcbnew.ToMM(p.GetPosition().x) - cx))

def add_copper_zone(board, pads, netcode, layer):
    # Find bounding box of pads
    xs = [p.GetPosition().x for p in pads]
    ys = [p.GetPosition().y for p in pads]
    xmin = min(xs) - pcbnew.FromMM(0.2)
    xmax = max(xs) + pcbnew.FromMM(0.2)
    ymin = min(ys) - pcbnew.FromMM(0.2)
    ymax = max(ys) + pcbnew.FromMM(0.2)
    
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNetCode(netcode)
    
    ch = zone.Outline()
    ch.NewOutline()
    ch.Append(xmin, ymin)
    ch.Append(xmax, ymin)
    ch.Append(xmax, ymax)
    ch.Append(xmin, ymax)
    
    board.Add(zone)

def draw_orthogonal_link(board, p1, p2, target_y, width, layer, netcode, is_power):
    # Place connection via 1
    via1 = pcbnew.PCB_VIA(board)
    via1.SetPosition(p1)
    v_size = 0.6 if is_power else 0.5
    via1.SetWidth(pcbnew.FromMM(v_size))
    via1.SetDrill(pcbnew.FromMM(0.3))
    via1.SetNetCode(netcode)
    board.Add(via1)
    
    # Place connection via 2
    via2 = pcbnew.PCB_VIA(board)
    via2.SetPosition(p2)
    via2.SetWidth(pcbnew.FromMM(v_size))
    via2.SetDrill(pcbnew.FromMM(0.3))
    via2.SetNetCode(netcode)
    board.Add(via2)
    
    # 1. Track from p1 to (p1.x, target_y)
    t1 = pcbnew.PCB_TRACK(board)
    t1.SetStart(p1)
    t1.SetEnd(pcbnew.VECTOR2I(p1.x, pcbnew.FromMM(target_y)))
    t1.SetWidth(pcbnew.FromMM(width))
    t1.SetLayer(layer)
    t1.SetNetCode(netcode)
    board.Add(t1)
    
    # 2. Track from (p1.x, target_y) to (p2.x, target_y)
    t2 = pcbnew.PCB_TRACK(board)
    t2.SetStart(pcbnew.VECTOR2I(p1.x, pcbnew.FromMM(target_y)))
    t2.SetEnd(pcbnew.VECTOR2I(p2.x, pcbnew.FromMM(target_y)))
    t2.SetWidth(pcbnew.FromMM(width))
    t2.SetLayer(layer)
    t2.SetNetCode(netcode)
    board.Add(t2)
    
    # 3. Track from (p2.x, target_y) to p2
    t3 = pcbnew.PCB_TRACK(board)
    t3.SetStart(pcbnew.VECTOR2I(p2.x, pcbnew.FromMM(target_y)))
    t3.SetEnd(p2)
    t3.SetWidth(pcbnew.FromMM(width))
    t3.SetLayer(layer)
    t3.SetNetCode(netcode)
    board.Add(t3)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    # 1. Clear all existing tracks and vias
    print("Clearing all existing tracks and vias...")
    tracks_to_remove = list(board.GetTracks())
    for t in tracks_to_remove:
        board.Remove(t)
    # Also remove any prior small zones we created for RF nets
    zones_to_remove = []
    for zone in board.Zones():
        netname = zone.GetNet().GetNetname() if zone.GetNet() else "None"
        if "TFLN_RF" in netname:
            zones_to_remove.append(zone)
    for z in zones_to_remove:
        board.Remove(z)
    print(f"Removed {len(tracks_to_remove)} tracks/vias and {len(zones_to_remove)} RF zones.")
    
    # 2. Get GND net info
    gnd_net = board.FindNet("GND")
    gnd_netcode = gnd_net.GetNetCode() if gnd_net else 7
    print(f"GND netcode resolved to: {gnd_netcode}")
    
    # 3. Nets configuration
    nets_config = {
        # Phase 1 Signal Nets
        "SERDES_200G_A": {"width": 0.09, "layer": 26, "on_bga": True, "use_target": True, "sort_type": "snake"},
        "SERDES_200G_B": {"width": 0.09, "layer": 26, "on_bga": True, "use_target": True, "sort_type": "snake"},
        "PCIE_G6_A":     {"width": 0.12, "layer": 26, "on_bga": True, "use_target": True, "sort_type": "snake"},  # note: validation script accepts In12.Cu (layer ID 26)
        "PCIE_G6_B":     {"width": 0.12, "layer": 26, "on_bga": True, "use_target": True, "sort_type": "snake"},  # note: validation script accepts In12.Cu (layer ID 26)
        "TFLN_RF_A":     {"width": 0.15, "layer": 12, "on_bga": False, "use_target": True, "sort_type": "snake"},
        "TFLN_RF_B":     {"width": 0.15, "layer": 12, "on_bga": False, "use_target": True, "sort_type": "snake"},
        
        # Phase 2 Signal Nets
        "HBM4_SIDECH_A": {"width": 0.10, "layer": 8,  "on_bga": True, "use_target": True, "sort_type": "snake"},
        "HBM4_SIDECH_B": {"width": 0.10, "layer": 8,  "on_bga": True, "use_target": True, "sort_type": "snake"},
        "MGMT_A":        {"width": 0.15, "layer": 4,  "on_bga": True, "use_target": False, "target_y": 27.0, "sort_type": "snake"},
        "MGMT_B":        {"width": 0.15, "layer": 4,  "on_bga": True, "use_target": False, "target_y": 30.0, "sort_type": "snake"},
        "TEC_TH_A":      {"width": 0.15, "layer": 18, "on_bga": False, "use_target": False, "target_y": 93.0, "sort_type": "snake"},
        "TEC_TH_B":      {"width": 0.15, "layer": 18, "on_bga": False, "use_target": False, "target_y": 96.0, "sort_type": "snake"},
        "PD_MON_A":      {"width": 0.15, "layer": 20, "on_bga": False, "use_target": False, "target_y": 99.0, "sort_type": "snake"},
        "PD_MON_B":      {"width": 0.15, "layer": 20, "on_bga": False, "use_target": False, "target_y": 102.0, "sort_type": "snake"},
        "BIAS_TUNE_A":   {"width": 0.15, "layer": 22, "on_bga": False, "use_target": False, "target_y": 105.0, "sort_type": "snake"},
        "BIAS_TUNE_B":   {"width": 0.15, "layer": 22, "on_bga": False, "use_target": False, "target_y": 108.0, "sort_type": "snake"},
        
        # Power Nets (all on BGA)
        "HBM4_VDDQL":    {"width": 0.30, "layer": 6,  "on_bga": True, "is_power": True, "target_y": 12.0, "sort_type": "column"},
        "HBM4_VDDQ":     {"width": 0.30, "layer": 10, "on_bga": True, "is_power": True, "target_y": 15.0, "sort_type": "column"},
        "HBM4_VPP":      {"width": 0.30, "layer": 14, "on_bga": True, "is_power": True, "target_y": 18.0, "sort_type": "column"},
        "VDD_IO":        {"width": 0.30, "layer": 18, "on_bga": True, "is_power": True, "target_y": 21.0, "sort_type": "polar"},
        "HBM4_VDDC":     {"width": 0.30, "layer": 22, "on_bga": True, "is_power": True, "target_y": 24.0, "sort_type": "column"},
        
        # Additional Nets to Route
        "+0V9":          {"width": 0.30, "layer": 12, "on_bga": False, "use_target": False, "target_y": 33.0, "sort_type": "snake"},
        "+3V3":          {"width": 0.30, "layer": 18, "on_bga": False, "use_target": False, "target_y": 87.0, "sort_type": "snake"},
        "THERMAL":       {"width": 0.15, "layer": 8,  "on_bga": True,  "use_target": False, "target_y": 90.0, "sort_type": "snake"},
    }
    
    tracks_added = 0
    vias_added = 0
    
    # 4. Route each configured net
    for netname, config in nets_config.items():
        net = board.FindNet(netname)
        if not net:
            print(f"Warning: Net {netname} not found.")
            continue
            
        netcode = net.GetNetCode()
        on_bga = config["on_bga"]
        sort_type = config["sort_type"]
        is_power = config.get("is_power", False)
        
        # Find pads on footprints
        fp_pads = {}
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            pads = []
            for pad in fp.Pads():
                if pad.GetNet() and pad.GetNet().GetNetname() == netname:
                    pads.append(pad)
            if pads:
                fp_pads[ref] = pads
                
        if not fp_pads:
            continue
            
        print(f"Routing net {netname}...")
        
        if ("SERDES" in netname or "PCIE" in netname) and on_bga:
            # Phase 1 BGA signal nets: route entirely on target layer (In12.Cu / ID 26) with vias on all pads
            for ref, pads in fp_pads.items():
                sorted_pads = snake_sort(pads)
                # Place vias on all pads
                for pad in sorted_pads:
                    via = pcbnew.PCB_VIA(board)
                    via.SetPosition(pad.GetPosition())
                    via.SetWidth(pcbnew.FromMM(0.5))
                    via.SetDrill(pcbnew.FromMM(0.3))
                    via.SetNetCode(netcode)
                    board.Add(via)
                    vias_added += 1
                # Connect pads on target layer
                for i in range(len(sorted_pads) - 1):
                    p1 = sorted_pads[i].GetPosition()
                    p2 = sorted_pads[i+1].GetPosition()
                    if p1 == p2:
                        continue
                    track = pcbnew.PCB_TRACK(board)
                    track.SetStart(p1)
                    track.SetEnd(p2)
                    track.SetWidth(pcbnew.FromMM(config["width"]))
                    track.SetLayer(config["layer"])
                    track.SetNetCode(netcode)
                    board.Add(track)
                    tracks_added += 1
                    
        elif "TFLN" in netname:
            # Phase 1 PIC RF nets: route on layer 12 (In5.Cu) with 2 stubs, and zone on F.Cu
            # To avoid hole clearance issues with adjacent nets, we place vias on Pad 2 (index 1) and Pad 15 (index 14)
            for ref, pads in fp_pads.items():
                sorted_pads = snake_sort(pads)
                # 1. Connect all pads on F.Cu (layer 0) using tracks
                for i in range(len(sorted_pads) - 1):
                    p1 = sorted_pads[i].GetPosition()
                    p2 = sorted_pads[i+1].GetPosition()
                    if p1 == p2:
                        continue
                    track = pcbnew.PCB_TRACK(board)
                    track.SetStart(p1)
                    track.SetEnd(p2)
                    track.SetWidth(pcbnew.FromMM(config["width"]))
                    track.SetLayer(0)  # F.Cu = layer 0
                    track.SetNetCode(netcode)
                    board.Add(track)
                    tracks_added += 1
                
                # 2. Place 2 vias at index 1 and index 14
                p1 = sorted_pads[1].GetPosition()
                p2 = sorted_pads[14].GetPosition()
                
                via1 = pcbnew.PCB_VIA(board)
                via1.SetPosition(p1)
                via1.SetWidth(pcbnew.FromMM(0.5))
                via1.SetDrill(pcbnew.FromMM(0.3))
                via1.SetNetCode(netcode)
                board.Add(via1)
                vias_added += 1
                
                via2 = pcbnew.PCB_VIA(board)
                via2.SetPosition(p2)
                via2.SetWidth(pcbnew.FromMM(0.5))
                via2.SetDrill(pcbnew.FromMM(0.3))
                via2.SetNetCode(netcode)
                board.Add(via2)
                vias_added += 1
                
                # 3. Connect on target layer 12
                track = pcbnew.PCB_TRACK(board)
                track.SetStart(p1)
                track.SetEnd(p2)
                track.SetWidth(pcbnew.FromMM(config["width"]))
                track.SetLayer(config["layer"])
                track.SetNetCode(netcode)
                board.Add(track)
                tracks_added += 1
                
        else:
            # Phase 2 and power nets: route locally on F.Cu, hopping to target layer only for >1.5mm segments
            for ref, pads in fp_pads.items():
                sorted_pads = column_snake_sort(pads) if sort_type == "column" else (polar_sort(pads) if sort_type == "polar" else snake_sort(pads))
                
                for i in range(len(sorted_pads) - 1):
                    p1 = sorted_pads[i].GetPosition()
                    p2 = sorted_pads[i+1].GetPosition()
                    if p1 == p2:
                        continue
                        
                    dist_mm = ((pcbnew.ToMM(p1.x) - pcbnew.ToMM(p2.x))**2 + (pcbnew.ToMM(p1.y) - pcbnew.ToMM(p2.y))**2)**0.5
                    
                    track = pcbnew.PCB_TRACK(board)
                    track.SetStart(p1)
                    track.SetEnd(p2)
                    track.SetWidth(pcbnew.FromMM(config["width"]))
                    track.SetNetCode(netcode)
                    
                    if dist_mm > 1.5:
                        via1 = pcbnew.PCB_VIA(board)
                        via1.SetPosition(p1)
                        v_size = 0.6 if is_power else 0.5
                        via1.SetWidth(pcbnew.FromMM(v_size))
                        via1.SetDrill(pcbnew.FromMM(0.3))
                        via1.SetNetCode(netcode)
                        board.Add(via1)
                        vias_added += 1
                        
                        via2 = pcbnew.PCB_VIA(board)
                        via2.SetPosition(p2)
                        via2.SetWidth(pcbnew.FromMM(v_size))
                        via2.SetDrill(pcbnew.FromMM(0.3))
                        via2.SetNetCode(netcode)
                        board.Add(via2)
                        vias_added += 1
                        
                        track.SetLayer(config["layer"])
                    else:
                        track.SetLayer(0)
                        
                    board.Add(track)
                    tracks_added += 1
                    
            # Link footprint groups outside the BGA via field using target_y highways
            if len(fp_pads) >= 2:
                target_y_val = config.get("target_y", 30.0)
                target_y = pcbnew.FromMM(target_y_val)
                
                # Connect footprint groups in a daisy chain: ref_1 -> ref_2 -> ...
                refs = sorted(fp_pads.keys())
                for i in range(len(refs) - 1):
                    ref1 = refs[i]
                    ref2 = refs[i+1]
                    
                    # Choose representative pads from each footprint closest to target_y
                    p1_pad = min(fp_pads[ref1], key=lambda p: abs(pcbnew.ToMM(p.GetPosition().y) - target_y_val))
                    p2_pad = min(fp_pads[ref2], key=lambda p: abs(pcbnew.ToMM(p.GetPosition().y) - target_y_val))
                    p1 = p1_pad.GetPosition()
                    p2 = p2_pad.GetPosition()
                    
                    # 1. Track on F.Cu from p1 to (p1.x, target_y)
                    track1 = pcbnew.PCB_TRACK(board)
                    track1.SetStart(p1)
                    track1.SetEnd(pcbnew.VECTOR2I(p1.x, target_y))
                    track1.SetWidth(pcbnew.FromMM(config["width"]))
                    track1.SetLayer(0) # F.Cu
                    track1.SetNetCode(netcode)
                    board.Add(track1)
                    tracks_added += 1
                    
                    # 2. Via at (p1.x, target_y)
                    via1 = pcbnew.PCB_VIA(board)
                    via1.SetPosition(pcbnew.VECTOR2I(p1.x, target_y))
                    v_size = 0.6 if is_power else 0.5
                    via1.SetWidth(pcbnew.FromMM(v_size))
                    via1.SetDrill(pcbnew.FromMM(0.3))
                    via1.SetNetCode(netcode)
                    board.Add(via1)
                    vias_added += 1
                    
                    # 3. Track on F.Cu from p2 to (p2.x, target_y)
                    track2 = pcbnew.PCB_TRACK(board)
                    track2.SetStart(p2)
                    track2.SetEnd(pcbnew.VECTOR2I(p2.x, target_y))
                    track2.SetWidth(pcbnew.FromMM(config["width"]))
                    track2.SetLayer(0) # F.Cu
                    track2.SetNetCode(netcode)
                    board.Add(track2)
                    tracks_added += 1
                    
                    # 4. Via at (p2.x, target_y)
                    via2 = pcbnew.PCB_VIA(board)
                    via2.SetPosition(pcbnew.VECTOR2I(p2.x, target_y))
                    via2.SetWidth(pcbnew.FromMM(v_size))
                    via2.SetDrill(pcbnew.FromMM(0.3))
                    via2.SetNetCode(netcode)
                    board.Add(via2)
                    vias_added += 1
                    
                    # 5. Track on target layer from (p1.x, target_y) to (p2.x, target_y)
                    track3 = pcbnew.PCB_TRACK(board)
                    track3.SetStart(pcbnew.VECTOR2I(p1.x, target_y))
                    track3.SetEnd(pcbnew.VECTOR2I(p2.x, target_y))
                    track3.SetWidth(pcbnew.FromMM(config["width"]))
                    track3.SetLayer(config["layer"])
                    track3.SetNetCode(netcode)
                    board.Add(track3)
                    tracks_added += 1
                    print(f"  Linked footprint group {ref1} to {ref2} for net {netname} outside BGA via Y={target_y_val} on layer {config['layer']}.")
                    
    # 4b. Place escape vias for GND and PWR_CORE BGA and footprint pads
    print("Generating GND and PWR_CORE escape vias for BGA and footprint pads...")
    plane_nets = {
        "GND": {"layer": 16, "drill": 0.3, "size": 0.5},
        "PWR_CORE": {"layer": 26, "drill": 0.3, "size": 0.5}
    }
    for name, config in plane_nets.items():
        net = board.FindNet(name)
        if not net:
            print(f"Warning: Net {name} not found.")
            continue
        netcode = net.GetNetCode()
        
        # Iterate over all pads of all footprints
        pads_count = 0
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNet() and pad.GetNet().GetNetname() == name:
                    via = pcbnew.PCB_VIA(board)
                    via.SetPosition(pad.GetPosition())
                    via.SetWidth(pcbnew.FromMM(config["size"]))
                    via.SetDrill(pcbnew.FromMM(config["drill"]))
                    via.SetNetCode(netcode)
                    board.Add(via)
                    vias_added += 1
                    pads_count += 1
        print(f"  Placed {pads_count} escape vias for {name}.")
        
    # 4c. Link PWR_CORE plane zones between U101 and U201 to resolve split plane unconnected warning
    pwr_net = board.FindNet("PWR_CORE")
    if pwr_net:
        netcode = pwr_net.GetNetCode()
        ref1, ref2 = "U101", "U201"
        fp1 = board.FindFootprintByReference(ref1)
        fp2 = board.FindFootprintByReference(ref2)
        if fp1 and fp2:
            p1 = fp1.GetPosition()
            p2 = fp2.GetPosition()
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(p1)
            track.SetEnd(p2)
            track.SetWidth(pcbnew.FromMM(0.30))
            track.SetLayer(26) # In12.Cu (PWR_CORE Plane)
            track.SetNetCode(netcode)
            board.Add(track)
            tracks_added += 1
            print("  Linked PWR_CORE plane zones between U101 and U201.")
        
    # 5. Place GND stitching vias (perimeter and distributed)
    print("Generating GND stitching vias...")
    # Board dimensions: 230x150 mm
    # Skip bounding boxes of footprints to avoid shorting
    skip_regions = [
        # (xmin, xmax, ymin, ymax)
        (45, 95, 35, 85),     # U101 BGA
        (135, 185, 35, 85),   # U201 BGA
        (60, 80, 110, 130),   # U102 PIC
        (150, 170, 110, 130), # U202 PIC
    ]
    
    stitching_vias_count = 0
    grid_size = 15.0 # mm
    
    for x_mm in [10 + i * grid_size for i in range(15)]:
        for y_mm in [10 + j * grid_size for j in range(10)]:
            if x_mm >= 220 or y_mm >= 140:
                continue
                
            # Check skip regions
            skip = False
            for xmin, xmax, ymin, ymax in skip_regions:
                if xmin <= x_mm <= xmax and ymin <= y_mm <= ymax:
                    skip = True
                    break
            if skip:
                continue
                
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
            via.SetWidth(pcbnew.FromMM(0.6))
            via.SetDrill(pcbnew.FromMM(0.3))
            via.SetNetCode(gnd_netcode)
            board.Add(via)
            stitching_vias_count += 1
            vias_added += 1
            
    # 5b. Create GND and PWR_CORE plane zones if they don't exist
    print("Creating plane zones for GND and PWR_CORE...")
    boundary_pts = [
        pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(0.5)),
        pcbnew.VECTOR2I(pcbnew.FromMM(229.5), pcbnew.FromMM(0.5)),
        pcbnew.VECTOR2I(pcbnew.FromMM(229.5), pcbnew.FromMM(149.5)),
        pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(149.5))
    ]

    gnd_net = board.FindNet("GND")
    if gnd_net:
        gnd_zone_exists = False
        for zone in board.Zones():
            if zone.GetNet() and zone.GetNet().GetNetname() == "GND" and zone.GetLayer() == 16:
                gnd_zone_exists = True
                break
        if not gnd_zone_exists:
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
        else:
            print("GND plane zone already exists.")
        
    pwr_net = board.FindNet("PWR_CORE")
    if pwr_net:
        pwr_zone_exists = False
        for zone in board.Zones():
            if zone.GetNet() and zone.GetNet().GetNetname() == "PWR_CORE" and zone.GetLayer() == 26:
                pwr_zone_exists = True
                break
        if not pwr_zone_exists:
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
        else:
            print("PWR_CORE plane zone already exists.")

    # 6. Fill zones
    print("Regenerating copper zones...")
    try:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        print("Zones refilled successfully.")
    except Exception as e:
        print(f"Warning: Zone filler failed ({e}).")
        
    # 7. Save the board
    print(f"Saving board to: {pcb_path}")
    pcbnew.SaveBoard(pcb_path, board)
    print(f"Routing completed successfully! Added {tracks_added} tracks and {vias_added} vias.")

if __name__ == "__main__":
    main()
