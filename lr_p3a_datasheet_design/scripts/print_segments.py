import pcbnew
import os

def snake_sort(pads):
    rows = {}
    for p in pads:
        pos = p.GetPosition()
        y_rounded = round(pcbnew.ToMM(pos.y), 1)
        if y_rounded not in rows:
            rows[y_rounded] = []
        rows[y_rounded].append(p)
    sorted_y = sorted(rows.keys())
    path = []
    for idx, y in enumerate(sorted_y):
        row_pads = rows[y]
        row_pads.sort(key=lambda p: p.GetPosition().x)
        if idx % 2 == 1:
            row_pads.reverse()
        path.extend(row_pads)
    return path

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pcb_path = os.path.join(script_dir, "..", "kicad", "LR_P3A_DualNCE.kicad_pcb")
    board = pcbnew.LoadBoard(pcb_path)
    
    net = board.FindNet("HBM4_VDDQL")
    fp = board.FindFootprintByReference("U201")
    pads = [p for p in fp.Pads() if p.GetNet() and p.GetNet().GetNetname() == "HBM4_VDDQL"]
    
    sorted_pads = snake_sort(pads)
    print(f"Total pads sorted: {len(sorted_pads)}")
    for i in range(len(sorted_pads) - 1):
        p1 = sorted_pads[i].GetPosition()
        p2 = sorted_pads[i+1].GetPosition()
        x1, y1 = pcbnew.ToMM(p1.x), pcbnew.ToMM(p1.y)
        x2, y2 = pcbnew.ToMM(p2.x), pcbnew.ToMM(p2.y)
        dist_mm = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
        print(f"Segment {i:2d}: ({x1:.3f}, {y1:.3f}) -> ({x2:.3f}, {y2:.3f}) | dist_mm = {dist_mm:.3f} | greater_than_1 = {dist_mm > 1.0}")

if __name__ == "__main__":
    main()
