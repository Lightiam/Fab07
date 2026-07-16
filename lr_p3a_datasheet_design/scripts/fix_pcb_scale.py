import re
import os

fixed_segments_count = 0
fixed_vias_count = 0

def fix_segment(match):
    global fixed_segments_count
    x1 = float(match.group(1))
    y1 = float(match.group(2))
    x2 = float(match.group(3))
    y2 = float(match.group(4))
    w = float(match.group(5))
    layer = match.group(6)
    net = match.group(7)
    
    if abs(x1) > 1000 or abs(y1) > 1000 or abs(x2) > 1000 or abs(y2) > 1000 or w > 10:
        x1 /= 10000.0
        y1 /= 10000.0
        x2 /= 10000.0
        y2 /= 10000.0
        w /= 10000.0
        fixed_segments_count += 1
        return f'(segment (start {x1:.6f} {y1:.6f}) (end {x2:.6f} {y2:.6f}) (width {w:.6f}) (layer "{layer}") (net {net}))'
    return match.group(0)

def fix_via(match):
    global fixed_vias_count
    x = float(match.group(1))
    y = float(match.group(2))
    size = float(match.group(3))
    drill = float(match.group(4))
    l1 = match.group(5)
    l2 = match.group(6)
    net = match.group(7)
    tstamp = match.group(8)
    
    if abs(x) > 1000 or abs(y) > 1000 or size > 10:
        x /= 10000.0
        y /= 10000.0
        size /= 10000.0
        drill /= 10000.0
        fixed_vias_count += 1
        return f'(via (at {x:.6f} {y:.6f}) (size {size:.6f}) (drill {drill:.6f}) (layers "{l1}" "{l2}") (net {net}) (tstamp {tstamp}))'
    return match.group(0)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    print(f"Reading board file: {pcb_path}")
    with open(pcb_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    segment_pattern = re.compile(r'\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)\s+\(width\s+([\d.-]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+([^\s)]+)\)\)')
    via_pattern = re.compile(r'\(via\s+\(at\s+([\d.-]+)\s+([\d.-]+)\)\s+\(size\s+([\d.-]+)\)\s+\(drill\s+([\d.-]+)\)\s+\(layers\s+"([^"]+)"\s+"([^"]+)"\)\s+\(net\s+([^\s)]+)\)\s+\(tstamp\s+([^\s)]+)\)\)')
    
    fixed_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("(segment") and not stripped.endswith("\n") and len(stripped.split("\n")) == 1:
            new_line = segment_pattern.sub(fix_segment, stripped)
            indent = line[:len(line) - len(line.lstrip())]
            fixed_lines.append(indent + new_line + "\n")
        elif stripped.startswith("(via") and not stripped.endswith("\n") and len(stripped.split("\n")) == 1:
            new_line = via_pattern.sub(fix_via, stripped)
            indent = line[:len(line) - len(line.lstrip())]
            fixed_lines.append(indent + new_line + "\n")
        else:
            fixed_lines.append(line)
            
    print(f"Fixed {fixed_segments_count} segments and {fixed_vias_count} vias.")
    
    # Save back to file
    print("Saving corrected layout file...")
    with open(pcb_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(fixed_lines)
        
    print("Done!")

if __name__ == "__main__":
    main()
