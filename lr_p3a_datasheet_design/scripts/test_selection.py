import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    nets_config = {
        "HBM4_VDDQL": 56.4,
        "HBM4_VDDQ": 58.0,
        "HBM4_VPP": 42.0,
        "VDD_IO": 48.4,
        "HBM4_VDDC": 45.2,
    }
    
    for netname, target_y in nets_config.items():
        net = board.FindNet(netname)
        if not net:
            continue
            
        fp = board.FindFootprintByReference("U101")
        pads = []
        for pad in fp.Pads():
            if pad.GetNet() and pad.GetNet().GetNetname() == netname:
                pads.append(pad)
                
        p = min(pads, key=lambda p: abs(pcbnew.ToMM(p.GetPosition().y) - target_y))
        pos = p.GetPosition()
        print(f"Net {netname:10} (target Y={target_y:.1f}) -> Chosen pad {p.GetName()} at ({pcbnew.ToMM(pos.x):.3f}, {pcbnew.ToMM(pos.y):.3f})")

if __name__ == "__main__":
    main()
