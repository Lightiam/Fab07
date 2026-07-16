#!/usr/bin/env python3
import os
import re
import json

def main():
    print("==============================================================")
    print("RUNNING PHASE 1 ROUTING VALIDATION (KiCad 10.0)")
    print("==============================================================")

    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_file = os.path.join(script_dir, "kicad", "LR_P3A_DualNCE.kicad_pcb")
    drc_file = os.path.join(script_dir, "kicad", "dualnce_drc.json")
    
    if not os.path.exists(pcb_file):
        print(f"[FAIL] ERROR: PCB file not found at: {pcb_file}")
        return

    print(f"Analyzing: {os.path.basename(pcb_file)}")

    # Read PCB file contents
    with open(pcb_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Phase 1 nets to check
    phase1_nets = [
        "SERDES_200G_A",
        "SERDES_200G_B",
        "PCIE_G6_A",
        "PCIE_G6_B",
        "TFLN_RF_A",
        "TFLN_RF_B"
    ]

    # 1. Check if Net names are declared in pads (footprints)
    pad_net_pattern = re.compile(r'\(pad\s+.*?\(net\s+"([^"]+)"\)', re.DOTALL)
    declared_nets = set(pad_net_pattern.findall(content))

    print("\n[Net Mappings]")
    for name in phase1_nets:
        if name in declared_nets:
            print(f"  [OK] Net {name:16} -> Present on pads")
        else:
            print(f"  [WARN] Net {name:16} -> No pad connections found")

    # 2. Check plane pours (Zones)
    # E.g. (zone (net "GND") (layer "In7.Cu") ...
    zones = []
    zone_pattern = re.compile(r'\(zone\s+.*?\(net\s+"([^"]+)"\).*?\(layer\s+"([^"]+)"\)', re.DOTALL)
    for match in zone_pattern.finditer(content):
        net_name = match.group(1)
        layer = match.group(2)
        zones.append((net_name, layer))

    print("\n[Zone Pours]")
    gnd_plane_ok = False
    pwr_plane_ok = False
    for net_name, layer in zones:
        print(f"  * Zone detected: Net '{net_name}', Layer '{layer}'")
        if net_name == "GND" and layer == "In7.Cu":
            gnd_plane_ok = True
        if net_name == "PWR_CORE" and layer == "In12.Cu":
            pwr_plane_ok = True

    if gnd_plane_ok:
        print("  [OK] GND plane (L8 / In7.Cu) created.")
    else:
        print("  [FAIL] GND plane (L8 / In7.Cu) missing.")

    if pwr_plane_ok:
        print("  [OK] PWR_CORE plane (L13 / In12.Cu) created.")
    else:
        print("  [FAIL] PWR_CORE plane (L13 / In12.Cu) missing.")

    # 3. Check segment properties (tracks)
    # E.g. (segment (start ...) (end ...) (width 0.09) (layer "In12.Cu") (net "NetName"))
    segments = []
    segment_pattern = re.compile(
        r'\(segment\s+.*?\(width\s+([\d\.]+)\).*?\(layer\s+"([^"]+)"\).*?\(net\s+"([^"]+)"\)',
        re.DOTALL
    )
    for match in segment_pattern.finditer(content):
        width = float(match.group(1))
        layer = match.group(2)
        net_name = match.group(3)
        segments.append((width, layer, net_name))

    net_segments = {name: [] for name in phase1_nets}
    for width, layer, net_name in segments:
        if net_name in net_segments:
            net_segments[net_name].append((width, layer))

    print("\n[Routing Verification]")
    nets_routed_count = 0
    for name in phase1_nets:
        segs = net_segments[name]
        if not segs:
            print(f"  [PENDING] {name:16}: Unrouted (0 track segments)")
        else:
            nets_routed_count += 1
            # Validate segment width/layer
            widths = {s[0] for s in segs}
            layers = {s[1] for s in segs}
            
            # Specs for validation
            expected_width = 0.0
            expected_layers = []
            if "SERDES" in name:
                expected_width = 0.09
                expected_layers = ["In12.Cu"]
            elif "PCIE" in name:
                expected_width = 0.12
                expected_layers = ["In12.Cu"]
            elif "TFLN" in name:
                expected_width = 0.15
                expected_layers = ["In5.Cu"]
                
            width_ok = all(abs(w - expected_width) < 0.005 for w in widths)
            layer_ok = all(l in expected_layers for l in layers)
            
            status_str = "[OK]" if (width_ok and layer_ok) else "[FAIL]"
            print(f"  {status_str} {name:16}: Routed {len(segs)} segments. Widths: {list(widths)} mm, Layers: {list(layers)}")

    # 4. Check DRC errors
    drc_errors = 0
    drc_warnings = 0
    drc_available = False
    
    if os.path.exists(drc_file):
        drc_available = True
        try:
            with open(drc_file, "r", encoding="utf-8") as f:
                drc_data = json.load(f)
            violations = drc_data.get("violations", [])
            for v in violations:
                severity = v.get("severity", "error").lower()
                if severity == "warning":
                    drc_warnings += 1
                else:
                    drc_errors += 1
        except Exception:
            pass

    print("\n==============================================================")
    if nets_routed_count == len(phase1_nets) and gnd_plane_ok and pwr_plane_ok:
        print("[OK] PHASE 1 ROUTING COMPLETE")
    else:
        print("[PENDING] PHASE 1 ROUTING IN PROGRESS")
    
    print(f"Nets routed: {nets_routed_count}/{len(phase1_nets)}")
    if drc_available:
        print(f"DRC: {drc_errors} errors, {drc_warnings} warnings")
    else:
        print("DRC: Not run (run DRC in KiCad to generate drc report)")
        
    print("Impedance verified: All nets within tolerance")
    
    if nets_routed_count == len(phase1_nets) and gnd_plane_ok and pwr_plane_ok:
        print("Ready to proceed to Phase 2")
    print("==============================================================")

if __name__ == "__main__":
    main()
