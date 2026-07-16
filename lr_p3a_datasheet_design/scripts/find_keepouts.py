import pcbnew
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    # Print keepout zones
    zones = list(board.Zones()) if hasattr(board, "Zones") else list(board.GetZones())
    print("Keepout/Rule Area Zones:")
    for i, zone in enumerate(zones):
        name_attrs = [attr for attr in dir(zone) if "Name" in attr]
        print(f"  {i+1}. Available Name Attributes: {name_attrs}")
        bbox = zone.GetBoundingBox()
        print(f"     BBox: X [{pcbnew.ToMM(bbox.GetX()):.3f}, {pcbnew.ToMM(bbox.GetRight()):.3f}], Y [{pcbnew.ToMM(bbox.GetY()):.3f}, {pcbnew.ToMM(bbox.GetBottom()):.3f}]")

if __name__ == "__main__":
    main()
