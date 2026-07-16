import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    print(f"Reading board file: {pcb_path}")
    with open(pcb_path, "rb") as f:
        data = f.read()
        
    # Attempt to decode as UTF-8, fallback to CP1252 and replace
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        print("Detected encoding issue, decoding as CP1252/latin-1...")
        text = data.decode("latin-1")
        
    # Replace non-ASCII / corrupt characters with standard ASCII equivalents
    text = text.replace("≤", "<=")
    text = text.replace("±", "+-")
    text = text.replace("%", "<=")
    text = text.replace("A", "+-")
    text = text.replace("\ufffd%", "<=")
    text = text.replace("A\ufffd", "+-")
    
    print("Writing corrected UTF-8 board file...")
    with open(pcb_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        
    print("PCB file encoding fix completed successfully!")

if __name__ == "__main__":
    main()
