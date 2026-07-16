import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    
    with open(pcb_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    open_parens = content.count("(")
    close_parens = content.count(")")
    print(f"Open parentheses: {open_parens}")
    print(f"Close parentheses: {close_parens}")
    print(f"Difference (open - close): {open_parens - close_parens}")
    
    # Trace the structure to find where it is malformed
    stack = []
    lines = content.splitlines()
    for line_idx, line in enumerate(lines):
        for char_idx, char in enumerate(line):
            if char == '(':
                stack.append((line_idx + 1, char_idx + 1))
            elif char == ')':
                if not stack:
                    print(f"Extra closing parenthesis at line {line_idx + 1}, column {char_idx + 1}")
                else:
                    stack.pop()
                    
    if stack:
        print(f"There are {len(stack)} unclosed parentheses. The first unclosed parenthesis is at line {stack[0][0]}, column {stack[0][1]}:")
        print(lines[stack[0][0] - 1])

if __name__ == "__main__":
    main()
