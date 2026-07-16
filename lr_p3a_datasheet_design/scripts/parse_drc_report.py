import json
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    drc_path = os.path.join(script_dir, "..", "kicad", "temp_drc.json")
    
    with open(drc_path, "r", encoding="utf-8") as f:
        drc = json.load(f)
        
    violations = drc.get("violations", [])
    print(f"Total violations in report: {len(violations)}")
    
    # Group by type and severity
    counts = {}
    for v in violations:
        v_type = v.get("type", "unknown")
        severity = v.get("severity", "unknown")
        key = (v_type, severity)
        counts[key] = counts.get(key, 0) + 1
        
    for (v_type, severity), count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  Type: {v_type:30} | Severity: {severity:10} | Count: {count}")

if __name__ == "__main__":
    main()
