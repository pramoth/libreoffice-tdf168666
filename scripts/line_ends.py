#!/usr/bin/env python3
"""Print where every text line of a PDF ends (xMax in pt), using poppler's pdftotext.

Usage: line_ends.py file.pdf
"""
import html
import re
import subprocess
import sys


def blocks(pdf):
    xml = subprocess.run(["pdftotext", "-bbox-layout", pdf, "-"], capture_output=True, text=True,
                         check=True).stdout
    for blk in re.findall(r"<block[^>]*>(.*?)</block>", xml, re.S):
        lines = []
        for x_max, body in re.findall(r'<line xMin="[\d.]+" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">(.*?)</line>',
                                      blk, re.S):
            words = [html.unescape(w) for w in re.findall(r">([^<]*)</word>", body)]
            lines.append((float(x_max), words))
        if lines:
            yield lines


if __name__ == "__main__":
    for b, lines in enumerate(blocks(sys.argv[1]), 1):
        print(f"block {b}:")
        for i, (x_max, words) in enumerate(lines, 1):
            text = " ".join(words).replace("\u200b", "")
            print(f"  line {i}: xMax={x_max:7.2f}  ...{text[-14:]}")
