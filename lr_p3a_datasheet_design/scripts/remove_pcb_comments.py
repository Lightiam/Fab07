import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    print(f"Reading board file: {pcb_path}")
    with open(pcb_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    cleaned_lines = []
    removed_count = 0
    for line in lines:
        if line.strip().startswith(";"):
            removed_count += 1
            continue
        cleaned_lines.append(line)
        
    print(f"Removed {removed_count} comment lines.")
    
    print("Saving cleaned layout file...")
    with open(pcb_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(cleaned_lines)
        
    print("Done!")

if __name__ == "__main__":
    main()
