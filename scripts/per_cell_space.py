#!/usr/bin/env python3
"""For each justified line, compute the extra space per character cell that Thai justification
has to add, and compare the left-aligned and the justified rendering.

Usage: per_cell_space.py left-aligned.pdf justified.pdf RIGHT_EDGE_PT

A line is "not justified" when it ends at the same position in both PDFs.
tdf#168666: that happens exactly when the extra space is below 1 twip per cell.
"""
import sys

from line_ends import blocks


def is_cell(c):
    # Same test as SwScriptInfo::ThaiJustify(): marks above/below the base do not get space.
    o = ord(c)
    return not (0x0E34 <= o <= 0x0E3A or 0x0E47 <= o <= 0x0E4E or o == 0x0E31)


def thai_blocks(pdf):
    return [b for b in blocks(pdf) if sum(0x0E00 <= ord(c) <= 0x0E7F for c in "".join(b[0][1])) > 20]


if __name__ == "__main__":
    left, just, right = thai_blocks(sys.argv[1]), thai_blocks(sys.argv[2]), float(sys.argv[3])
    for p, (lb, jb) in enumerate(zip(left, just), 1):
        for i, ((x_left, words), (x_just, _)) in enumerate(zip(lb, jb), 1):
            if i == len(lb):
                continue  # the last line of a paragraph is not justified
            cells = sum(is_cell(c) for w in words for c in w) + len(words) - 1  # + blanks
            per_cell = (right - x_left) * 20 / (cells - 1)
            observed = "NOT justified" if abs(x_just - x_left) < 0.01 else "justified"
            print(f"paragraph {p} line {i}: cells={cells:3d} extra space={per_cell:5.2f} twip/cell"
                  f"  predicted={'NOT justified' if per_cell < 1 else 'justified':13s}  observed={observed}")
