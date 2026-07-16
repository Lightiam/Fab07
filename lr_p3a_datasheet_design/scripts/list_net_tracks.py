import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    for netname in ["HBM4_VDDQL", "HBM4_VDDC"]:
        net = board.FindNet(netname)
        if not net:
            continue
        print(f"\nNet {netname} tracks:")
        count = 0
        for track in board.GetTracks():
            if track.GetNet() and track.GetNet().GetNetname() == netname:
                start = track.GetStart()
                end = track.GetEnd()
                sx, sy = pcbnew.ToMM(start.x), pcbnew.ToMM(start.y)
                ex, ey = pcbnew.ToMM(end.x), pcbnew.ToMM(end.y)
                is_via = isinstance(track, pcbnew.PCB_VIA)
                if is_via:
                    print(f"  Via at ({sx:.3f}, {sy:.3f})")
                else:
                    layer_id = track.GetLayer()
                    layer_name = board.GetLayerName(layer_id)
                    print(f"  Track from ({sx:.3f}, {sy:.3f}) to ({ex:.3f}, {ey:.3f}) on layer {layer_id} ({layer_name})")
                count += 1
        print(f"Total items on net {netname}: {count}")

if __name__ == "__main__":
    main()
