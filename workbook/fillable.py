"""Adds fillable text fields to the rendered workbook PDF.
Reads field boxes (CSS px, page-relative) from fields.json produced by render.sh."""
import json, sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject, FloatObject,
                           NameObject, NumberObject, TextStringObject)

pdf, fields_json = sys.argv[1], sys.argv[2]
boxes = json.load(open(fields_json, encoding='utf-8'))
r = PdfReader(pdf); w = PdfWriter(); w.append(r)
PT = 0.75  # CSS px -> PDF points

font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'),
                         NameObject('/BaseFont'): NameObject('/Helvetica'), NameObject('/Encoding'): NameObject('/WinAnsiEncoding')})
font_ref = w._add_object(font)
acro = DictionaryObject({
    NameObject('/Fields'): ArrayObject(),
    NameObject('/NeedAppearances'): BooleanObject(True),
    NameObject('/DA'): TextStringObject('/Helv 0 Tf 0 g'),
    NameObject('/DR'): DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/Helv'): font_ref})}),
})
w._root_object[NameObject('/AcroForm')] = acro

for n, (pi, kind, x, y, bw, bh) in enumerate(boxes):
    page = w.pages[pi]
    H = float(page.mediabox.height)
    pad = 2
    x1, x2 = x * PT + pad, (x + bw) * PT - pad
    if kind == 'line':      # writing line: field sits just above the rule
        y_top, y_bot = y * PT + 2, (y + bh) * PT - 1
    else:
        y_top, y_bot = y * PT + pad, (y + bh) * PT - pad
    multiline = kind == 'area' or bh > 40
    flags = 4096 if multiline else 0  # 4096 = multiline
    size = 0 if multiline else 10
    field = DictionaryObject({
        NameObject('/Type'): NameObject('/Annot'), NameObject('/Subtype'): NameObject('/Widget'),
        NameObject('/FT'): NameObject('/Tx'), NameObject('/T'): TextStringObject(f'p{pi+1}_{kind}_{n}'),
        NameObject('/Rect'): ArrayObject([FloatObject(x1), FloatObject(H - y_bot), FloatObject(x2), FloatObject(H - y_top)]),
        NameObject('/F'): NumberObject(4), NameObject('/Ff'): NumberObject(flags),
        NameObject('/DA'): TextStringObject(f'/Helv {size} Tf 0.17 0.13 0.09 rg'),
        NameObject('/MK'): DictionaryObject(),
        NameObject('/P'): page.indirect_reference,
    })
    ref = w._add_object(field)
    if '/Annots' not in page:
        page[NameObject('/Annots')] = ArrayObject()
    page['/Annots'].append(ref)
    acro['/Fields'].append(ref)

w.add_metadata({'/Title': "First Flake: Josie's 7-Trip Field Workbook", '/Author': 'First Flake', '/Subject': 'A field workbook for beginner gold prospectors'})
w.write(pdf)
print(len(boxes), 'fillable fields added')
