import pcbnew
import os

def test_content(lines):
    temp_path = "temp_test_board.kicad_pcb"
    # Make sure we write in UTF-8
    with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)
    try:
        board = pcbnew.LoadBoard(temp_path)
        return board is not None
    except Exception:
        return False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    with open(pcb_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print(f"Total lines: {len(lines)}")
    if test_content(lines):
        print("Full file loads successfully!")
        return
        
    # Check if first part of the file loads
    # Lines 46627 is (embedded_fonts no), 46628 is a blank line.
    # The actual S-expression ends with a closing parenthesis.
    print("Testing original board content...")
    original_lines = lines[:46628] + [")\n"]
    if not test_content(original_lines):
        print("Original lines do not load! Searching corruption in original board...")
        low = 1
        high = 46628
    else:
        print("Original lines load successfully! Searching corruption in injected lines...")
        low = 46628
        high = len(lines)
        
    while low < high:
        mid = (low + high) // 2
        # Test content up to mid line index
        test_lines = lines[:mid] + [")\n"]
        if test_content(test_lines):
            # mid is safe, corruption must be in the remaining part
            low = mid + 1
        else:
            # mid is already corrupt, corruption is at or before mid
            high = mid
            
    print(f"First corrupt line found at line {low}:")
    print(repr(lines[low-1]))

if __name__ == "__main__":
    main()
