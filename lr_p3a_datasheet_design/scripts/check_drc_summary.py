import json
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    drc_path = os.path.join(script_dir, "..", "kicad", "temp_drc.json")
    
    if not os.path.exists(drc_path):
        print(f"DRC report not found at: {drc_path}")
        return
        
    with open(drc_path, "r", encoding="utf-8") as f:
        drc = json.load(f)
        
    unconnected = drc.get("unconnected_items", [])
    
    print(f"Total unconnected items: {len(unconnected)}")
    
    # Analyze unconnected nets
    net_counts = {}
    for item in unconnected:
        # Check what items are unconnected
        sub_items = item.get("items", [])
        nets = set()
        for sub in sub_items:
            desc = sub.get("description", "")
            # Extract net name in brackets, e.g. [NetName]
            import re
            m = re.search(r'\[([^\]]+)\]', desc)
            if m:
                nets.add(m.group(1))
            else:
                # check if there is other pattern
                pass
        for net in nets:
            net_counts[net] = net_counts.get(net, 0) + 1
            
    print("\nUnconnected counts by Net:")
    for net, count in sorted(net_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  Net: {net:25} | Count: {count}")
        
    if unconnected:
        print("\nDetailed breakdown of first 10 unconnected items:")
        for idx, item in enumerate(unconnected[:10]):
            print(f"\nItem {idx+1}:")
            for sub in item.get("items", []):
                print(f"  - {sub.get('description')}")
                
if __name__ == "__main__":
    main()
