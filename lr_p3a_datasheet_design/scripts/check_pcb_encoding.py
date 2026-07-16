import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    with open(pcb_path, "rb") as f:
        data = f.read()
        
    try:
        data.decode("utf-8")
        print("UTF-8 decoding succeeded! The file is valid UTF-8.")
    except UnicodeDecodeError as e:
        print(f"UTF-8 decoding failed at byte {e.start} (reason: {e.reason})")
        # Print surrounding bytes
        start = max(0, e.start - 50)
        end = min(len(data), e.end + 50)
        print(f"Surrounding bytes (hex): {data[start:end].hex()}")
        print(f"Surrounding bytes (decoded as latin-1): {data[start:end].decode('latin-1')}")

if __name__ == "__main__":
    main()
