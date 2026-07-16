import pcbnew
import csv
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    bom_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE_BOM.csv")
    
    board = pcbnew.LoadBoard(pcb_path)
    bom_data = []
    
    for fp in board.GetFootprints():
        ref = str(fp.GetReference())
        val = str(fp.GetValue())
        try:
            footprint = str(fp.GetFPID().GetLibItemName())
        except AttributeError:
            footprint = str(fp.GetFPID().GetFPName())
            
        bom_data.append({
            "Reference": ref,
            "Value": val,
            "Footprint": footprint
        })
        
    # Group by Value + Footprint
    grouped = {}
    for item in bom_data:
        key = (item["Value"], item["Footprint"])
        if key not in grouped:
            grouped[key] = {
                "Refs": [],
                "Value": item["Value"],
                "Footprint": item["Footprint"],
                "Qty": 0,
                "DNP": ""
            }
        grouped[key]["Refs"].append(item["Reference"])
        grouped[key]["Qty"] += 1
        
    # Format references and write to CSV
    with open(bom_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Refs", "Value", "Footprint", "Qty", "DNP"])
        for key in sorted(grouped.keys()):
            item = grouped[key]
            refs_str = ", ".join(sorted(item["Refs"]))
            writer.writerow([refs_str, item["Value"], item["Footprint"], item["Qty"], item["DNP"]])
            
    print(f"BOM exported successfully to: {bom_path}")

if __name__ == "__main__":
    main()
