#!/usr/bin/env python3
"""Create test/tdf168666.fodt: one justified Thai paragraph with an embedded, renamed subset of
Sarabun (SIL Open Font License 1.1), so the layout does not depend on installed fonts.

Usage: uv run --with fonttools scripts/make_test_document.py /path/to/Sarabun-Regular.ttf out.fodt
"""
import base64
import io
import sys
import textwrap

from fontTools import subset
from fontTools.ttLib import TTFont

TEXT = ("การสร้างชุมชนที่แท้จริงคือการยอมเปิดใจรับความเปราะบางของกันและกัน "
        "การยอมรับว่าเราต่างก็มีวันที่อ่อนแอและต้องการการประคับประคอง "
        "ความเป็นส่วนหนึ่งไม่ได้เกิดจากการที่เรามีไลฟ์สไตล์เหมือนกัน")
FAMILY = "Sarabun tdf168666"


def font_subset(path):
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    font = TTFont(path, recalcTimestamp=False)  # reproducible output
    subsetter = subset.Subsetter(opts)
    subsetter.populate(text=TEXT + " ")
    subsetter.subset(font)
    # Renamed so an installed Sarabun can never be picked instead of the embedded one.
    for rec in font["name"].names:
        if rec.nameID in (1, 4, 16):
            rec.string = FAMILY
        elif rec.nameID == 6:
            rec.string = "Sarabun-tdf168666"
        elif rec.nameID == 3:
            rec.string = "Sarabun-tdf168666-subset"
    out = io.BytesIO()
    font.save(out)
    return out.getvalue()


def document(font_bytes):
    b64 = "\n".join(textwrap.wrap(base64.b64encode(font_bytes).decode(), 76))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" office:version="1.4" office:mimetype="application/vnd.oasis.opendocument.text">
 <office:font-face-decls>
  <!-- Subset of Sarabun (SIL Open Font License 1.1), renamed to avoid clashing with an installed Sarabun -->
  <style:font-face style:name="{FAMILY}" svg:font-family="'{FAMILY}'" style:font-pitch="variable">
   <svg:font-face-src>
    <svg:font-face-uri loext:font-style="normal" loext:font-weight="normal">
     <office:binary-data>{b64}</office:binary-data>
     <svg:font-face-format svg:string="truetype"/>
    </svg:font-face-uri>
   </svg:font-face-src>
  </style:font-face>
 </office:font-face-decls>
 <office:styles>
  <style:default-style style:family="paragraph">
   <style:text-properties style:font-name="{FAMILY}" fo:font-size="14pt" fo:language="en" fo:country="US" style:font-name-complex="{FAMILY}" style:font-size-complex="14pt" style:language-complex="th" style:country-complex="TH"/>
  </style:default-style>
 </office:styles>
 <office:automatic-styles>
  <style:style style:name="P1" style:family="paragraph">
   <style:paragraph-properties fo:text-align="justify" style:justify-single-word="false"/>
  </style:style>
  <style:page-layout style:name="pm1">
   <style:page-layout-properties fo:page-width="21.001cm" fo:page-height="29.7cm" fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2cm" fo:margin-right="2cm"/>
  </style:page-layout>
 </office:automatic-styles>
 <office:master-styles>
  <style:master-page style:name="Standard" style:page-layout-name="pm1"/>
 </office:master-styles>
 <office:body>
  <office:text>
   <text:p text:style-name="P1">{TEXT}</text:p>
  </office:text>
 </office:body>
</office:document>
'''


if __name__ == "__main__":
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(document(font_subset(sys.argv[1])))
