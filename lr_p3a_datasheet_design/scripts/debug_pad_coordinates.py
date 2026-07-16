import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    # Let's search for pads, tracks, or vias near (318.3, 238.0) and (87.2, 42.0)
    targets = [
        ("TFLN_RF_B / BIAS_TUNE_B", 318.3, 238.0),
        ("HBM4_VDDQL / SERDES_200G_B", 87.2, 42.0),
        ("HBM4_VPP / SERDES_200G_B", 86.4, 42.0),
        ("SERDES_200G_B / VDD_IO", 179.6, 41.2)
    ]
    
    print("Items near targets:")
    for label, tx, ty in targets:
        print(f"\nTarget: {label} near ({tx}, {ty})")
        # Check pads
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            for pad in fp.Pads():
                pos = pad.GetPosition()
                px, py = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
                dist = ((px - tx)**2 + (py - ty)**2)**0.5
                if dist < 5.0:
                    print(f"  Pad {ref}.{pad.GetName()} : net={pad.GetNet().GetNetname()} at ({px:.3f}, {py:.3f}), dist={dist:.3f}")
                    
        # Check tracks/vias
        for track in board.GetTracks():
            pos = track.GetPosition()
            tx_mm, ty_mm = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            dist = ((tx_mm - tx)**2 + (ty_mm - ty)**2)**0.5
            if dist < 5.0:
                is_via = isinstance(track, pcbnew.PCB_VIA)
                netname = track.GetNet().GetNetname() if track.GetNet() else "GND"
                print(f"  Track/Via (via={is_via}) : net={netname} at ({tx_mm:.3f}, {ty_mm:.3f}), dist={dist:.3f}")

if __name__ == "__main__":
    main()
