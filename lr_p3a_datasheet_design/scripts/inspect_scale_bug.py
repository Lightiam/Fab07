import re
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    with open(pcb_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print("Scanning segments...")
    segment_pattern = re.compile(r'\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)\s+\(width\s+([\d.-]+)\)\s+\(layer\s+"[^"]+"\)\s+\(net\s+\d+\)')
    segments = segment_pattern.findall(content)
    print(f"Found {len(segments)} segments total.")
    large_segments = [s for s in segments if abs(float(s[0])) > 1000 or abs(float(s[4])) > 5]
    print(f"Found {len(large_segments)} segments with suspected scale-by-10000 issue.")
    if large_segments:
        print(f"Sample large segment: {large_segments[0]}")
        
    print("\nScanning vias...")
    via_pattern = re.compile(r'\(via\s+\(at\s+([\d.-]+)\s+([\d.-]+)\)\s+\(size\s+([\d.-]+)\)\s+\(drill\s+([\d.-]+)\)\s+\(layers\s+"[^"]+"\s+"[^"]+"\)\s+\(net\s+\d+\)')
    vias = via_pattern.findall(content)
    print(f"Found {len(vias)} vias total.")
    large_vias = [v for v in vias if abs(float(v[0])) > 1000 or abs(float(v[2])) > 5]
    print(f"Found {len(large_vias)} vias with suspected scale-by-10000 issue.")
    if large_vias:
        print(f"Sample large via: {large_vias[0]}")

if __name__ == "__main__":
    main()
