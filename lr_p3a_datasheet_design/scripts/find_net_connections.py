import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    nets_to_check = [
        "SERDES_200G_A", "SERDES_200G_B",
        "PCIE_G6_A", "PCIE_G6_B",
        "TFLN_RF_A", "TFLN_RF_B",
        "HBM4_SIDECH_A", "HBM4_SIDECH_B",
        "MGMT_A", "MGMT_B",
        "TEC_TH_A", "TEC_TH_B",
        "PD_MON_A", "PD_MON_B",
        "BIAS_TUNE_A", "BIAS_TUNE_B"
    ]
    
    print("Net Connections:")
    for netname in nets_to_check:
        net = board.FindNet(netname)
        if not net:
            print(f"  Net {netname} not found.")
            continue
            
        fp_pins = []
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            for pad in fp.Pads():
                if pad.GetNet() and pad.GetNet().GetNetname() == netname:
                    fp_pins.append(f"{ref}.{pad.GetName()}")
        print(f"  Net {netname:20} : {len(fp_pins)} pads -> {', '.join(fp_pins[:10])}")
        if len(fp_pins) > 10:
            print(f"    ... and {len(fp_pins)-10} more pads")

if __name__ == "__main__":
    main()
