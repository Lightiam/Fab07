import json
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    drc_path = os.path.join(script_dir, "..", "kicad", "temp_drc.json")
    
    with open(drc_path, "r", encoding="utf-8") as f:
        drc = json.load(f)
        
    violations = drc.get("violations", [])
    errors = [v for v in violations if v.get("severity") == "error"]
    
    print(f"Critical DRC Errors ({len(errors)}):")
    for i, e in enumerate(errors):
        v_type = e.get("type", "unknown")
        desc = e.get("description", "no description")
        items = e.get("items", [])
        item_descs = []
        for item in items:
            item_descs.append(f"{item.get('name', 'unknown')} at {item.get('pos', 'unknown')}")
        print(f"  {i+1:2d}. Type: {v_type:20} | Desc: {desc}")
        print(f"      Items: {'; '.join(item_descs)}")

if __name__ == "__main__":
    main()
