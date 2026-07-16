import re
import uuid
import os

def fix_segment_tstamp(match):
    content = match.group(0)
    # If segment doesn't contain tstamp, add it
    if "tstamp" not in content:
        new_uuid = str(uuid.uuid4())
        # Replace the final closing paren with (tstamp "uuid") )
        return content[:-1] + f' (tstamp "{new_uuid}"))'
    return content

def fix_via_tstamp(match):
    content = match.group(0)
    # If tstamp is present but not quoted, quote it
    # Format: (tstamp 00000000-0000-0000-0000-000000000000)
    unquoted_match = re.search(r'\(tstamp\s+([0-9a-fA-F-]+)\)', content)
    if unquoted_match:
        tstamp_val = unquoted_match.group(1)
        # Generate a new unique uuid to avoid duplicate tstamps
        new_uuid = str(uuid.uuid4())
        content = content.replace(f'(tstamp {tstamp_val})', f'(tstamp "{new_uuid}")')
    return content

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    print(f"Reading board file: {pcb_path}")
    with open(pcb_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print("Fixing segment tstamps...")
    segment_pattern = re.compile(r'\(segment\s+\(start\s+[\d.-]+\s+[\d.-]+\)\s+\(end\s+[\d.-]+\s+[\d.-]+\)\s+\(width\s+[\d.-]+\)\s+\(layer\s+"[^"]+"\)\s+\(net\s+[^\s)]+\)\)')
    new_content, count1 = segment_pattern.subn(fix_segment_tstamp, content)
    print(f"Applied tstamp fixes to {count1} segments.")
    
    print("Fixing via tstamps...")
    # Matches via with unquoted tstamp
    via_pattern = re.compile(r'\(via\s+\(at\s+[\d.-]+\s+[\d.-]+\)\s+\(size\s+[\d.-]+\)\s+\(drill\s+[\d.-]+\)\s+\(layers\s+"[^"]+"\s+"[^"]+"\)\s+\(net\s+[^\s)]+\)\s+\(tstamp\s+([0-9a-fA-F-]+)\)\)')
    new_content, count2 = via_pattern.subn(fix_via_tstamp, new_content)
    print(f"Applied tstamp fixes to {count2} vias.")
    
    print("Saving corrected layout file...")
    with open(pcb_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
        
    print("Done!")

if __name__ == "__main__":
    main()
