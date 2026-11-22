#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the downloadable résumé files from the original .docx.

    python3 scripts/build_resume_pdf.py

Outputs (both in assets/):
  * Jayant_Singh_Singoria_Resume_2025.pdf   — generated here, styled to match the site
  * Jayant_Singh_Singoria_Resume_2025.docx — a web-safe copy of your original

Uses ONLY the Python standard library. No pip install, no LibreOffice, no Word.
Edit OMIT_PHONE / ACCENT below to change behaviour.
"""

import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, 'assets')

BASENAME = 'Jayant_Singh_Singoria_Resume_2025'
ORIGINAL_DOCX = os.path.join(ROOT, BASENAME + '.docx')
OUT_DOCX = os.path.join(ASSETS, BASENAME + '.docx')
OUT_PDF = os.path.join(ASSETS, BASENAME + '.pdf')

# The site shows email + LinkedIn only. Keep the downloads consistent.
# Set to False if you want the phone number in the public downloads too.
OMIT_PHONE = True
PHONE_RE = re.compile(r'\+?91[-\s]?\d{4}[-\s]?\d{3}[-\s]?\d{3}')

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'

# --- typography / palette (RGB 0..1) ----------------------------------------
INK = (0.129, 0.118, 0.102)
INK2 = (0.298, 0.275, 0.239)
GRAY = (0.512, 0.478, 0.424)
PLUM = (0.482, 0.176, 0.333)
AMBER = (0.757, 0.514, 0.184)
RULE = (0.82, 0.79, 0.74)

PAGE_W, PAGE_H = 595.28, 841.89          # A4
ML, MR = 48.0, 48.0
CW = PAGE_W - ML - MR
TOP, BOTTOM = 792.0, 60.0

# --- Adobe standard font metrics (widths per 1000 units) --------------------
_HELV = """278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278
556 556 556 556 556 556 556 556 556 556 278 278 584 584 584 556
1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778
667 778 722 667 611 722 667 944 667 667 611 278 278 278 469 556
333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556
556 556 333 500 278 556 500 722 500 500 500 334 260 334 584"""
_BOLD = """278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278
556 556 556 556 556 556 556 556 556 556 278 278 584 584 584 556
1015 722 722 722 722 667 611 778 722 278 556 722 611 833 722 778
667 778 722 667 611 722 667 944 667 667 611 278 278 278 469 556
333 556 611 556 611 556 333 611 611 278 278 556 278 889 611 611
611 611 389 556 333 611 556 778 556 556 500 334 260 334 584"""
WIDTHS = {
    'F1': dict(zip(range(32, 127), [int(v) for v in _HELV.split()])),
    'F2': dict(zip(range(32, 127), [int(v) for v in _BOLD.split()])),
}
for _d in WIDTHS.values():
    _d.setdefault(9, 278)  # tab-ish fallback
    for _c in range(127, 256):
        _d[_c] = 556

SUBS = {
    '–': '-', '—': '-', '−': '-', '→': '->', '←': '<-', '·': ' / ',
    '’': "'", '‘': "'", '“': '"', '”': '"', '…': '...', '•': '-',
    '\xa0': ' ', '✳': '*', '✓': 'v', '↗': '', '↓': '', '|': '|',
}


def ascii_safe(s):
    for k, v in SUBS.items():
        s = s.replace(k, v)
    return ''.join(ch if 32 <= ord(ch) < 127 else ' ' for ch in s)


def char_w(ch, font, size):
    if font == 'F4':
        return 0.600 * size
    return WIDTHS[font].get(ord(ch), 556) / 1000.0 * size


def text_w(s, font, size):
    return sum(char_w(c, font, size) for c in s)


def pdf_escape(s):
    return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


# --- tiny PDF writer ---------------------------------------------------------
class PDF:
    def __init__(self):
        self.pages = []
        self.cmds = []
        self.y = TOP

    def _emit(self, s):
        self.cmds.append(s)

    def new_page(self):
        if self.cmds:
            self.pages.append(self.cmds)
        self.cmds = []
        self.y = TOP

    def ensure(self, space):
        if self.y - space < BOTTOM:
            self.new_page()

    def text(self, x, y, s, font='F1', size=9, color=INK2, spacing=0):
        if not s:
            return
        self._emit(
            'BT /%s %.2f Tf %.3f %.3f %.3f rg %.2f Tc '
            '1 0 0 1 %.2f %.2f Tm (%s) Tj ET'
            % (font, size, color[0], color[1], color[2], spacing,
               x, y, pdf_escape(s))
        )

    def rule(self, x1, y, x2, color=RULE, width=0.6):
        self._emit('%.3f %.3f %.3f RG %.2f w %.2f %.2f m %.2f %.2f l S'
                   % (color[0], color[1], color[2], width, x1, y, x2, y))

    def dot(self, x, y, size=1.7, color=AMBER):
        self._emit('%.3f %.3f %.3f rg %.2f %.2f %.2f %.2f re f'
                   % (color[0], color[1], color[2], x, y, size, size))

    def wrap(self, s, font, size, width):
        """Word-wrap plain text -> list of lines."""
        out, line = [], ''
        for word in s.split(' '):
            cand = word if not line else line + ' ' + word
            if text_w(cand, font, size) <= width or not line:
                line = cand
            else:
                out.append(line)
                line = word
        if line:
            out.append(line)
        return out or ['']

    def wrap_rich(self, chars, size, width):
        """chars = [(char, bold)] -> list of [(char, bold)] lines."""
        lines, cur, cur_w = [], [], 0.0
        # tokenise into words, preserving bold flags
        words, word = [], []
        for ch, bold in chars:
            if ch == ' ':
                if word:
                    words.append(word)
                word = []
            else:
                word.append((ch, bold))
        if word:
            words.append(word)
        for word in words:
            ww = sum(char_w(c, 'F2' if b else 'F1', size) for c, b in word)
            sep = char_w(' ', 'F1', size) if cur else 0
            if cur and cur_w + sep + ww > width:
                lines.append(cur)
                cur, cur_w = [], 0.0
                sep = 0
            if cur:
                cur.append((' ', False))
                cur_w += sep
            cur.extend(word)
            cur_w += ww
        if cur:
            lines.append(cur)
        return lines or [[]]

    def draw_rich(self, line, x, y, size=9.2, color=INK2):
        cx = x
        seg, bold = '', None
        for ch, b in line:
            if b != bold and seg:
                self.text(cx, y, seg, 'F2' if bold else 'F1', size, color)
                cx += text_w(seg, 'F2' if bold else 'F1', size)
                seg = ''
            bold = b
            seg += ch
        if seg:
            self.text(cx, y, seg, 'F2' if bold else 'F1', size, color)

    def save(self, path, title, author):
        if self.cmds:
            self.pages.append(self.cmds)
            self.cmds = []
        total = len(self.pages)
        for i, cmds in enumerate(self.pages, 1):
            cmds.append('%.3f %.3f %.3f RG 0.5 w %.2f 48 m %.2f 48 l S'
                        % (RULE[0], RULE[1], RULE[2], ML, PAGE_W - MR))
            cmds.append('BT /F1 7.2 Tf %.3f %.3f %.3f rg 1 0 0 1 %.2f 36 Tm (%s) Tj ET'
                        % (GRAY[0], GRAY[1], GRAY[2], ML,
                           pdf_escape('Jayant Singh Singoria  /  jaysin60.github.io')))
            page_lbl = 'Page %d of %d' % (i, total)
            cmds.append('BT /F1 7.2 Tf %.3f %.3f %.3f rg 1 0 0 1 %.2f 36 Tm (%s) Tj ET'
                        % (GRAY[0], GRAY[1], GRAY[2],
                           PAGE_W - MR - text_w(page_lbl, 'F1', 7.2),
                           pdf_escape(page_lbl)))

        objects = {}
        objects[1] = '<< /Type /Catalog /Pages 2 0 R >>'
        font_objs = {
            3: 'Helvetica', 4: 'Helvetica-Bold',
            5: 'Helvetica-Oblique', 6: 'Courier',
        }
        # /Pages object (2) filled in after page objects are numbered
        page_ids = []
        next_id = 7
        for cmds in self.pages:
            page_id, stream_id = next_id, next_id + 1
            next_id += 2
            page_ids.append(page_id)
            stream = ('\n'.join(cmds)).encode('latin-1', 'replace')
            objects[page_id] = (
                '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] '
                '/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 6 0 R >> >> '
                '/Contents %d 0 R >>' % (PAGE_W, PAGE_H, stream_id)
            )
            objects[stream_id] = ('<< /Length %d >>\nstream\n' % len(stream)).encode() \
                + stream + b'\nendstream'
        objects[2] = '<< /Type /Pages /Kids [%s] /Count %d >>' % (
            ' '.join('%d 0 R' % p for p in page_ids), total)
        for oid, base in font_objs.items():
            objects[oid] = ('<< /Type /Font /Subtype /Type1 /BaseFont /%s '
                            '/Encoding /WinAnsiEncoding >>' % base)
        info_id = next_id
        objects[info_id] = ('<< /Title (%s) /Author (%s) /Producer (build_resume_pdf.py) >>'
                            % (pdf_escape(title), pdf_escape(author)))

        out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offsets = {}
        for oid in sorted(objects):
            offsets[oid] = len(out)
            body = objects[oid]
            if isinstance(body, str):
                body = body.encode('latin-1')
            out += ('%d 0 obj\n' % oid).encode() + body + b'\nendobj\n'
        xref = len(out)
        max_id = max(objects)
        out += ('xref\n0 %d\n' % (max_id + 1)).encode()
        out += b'0000000000 65535 f \n'
        for oid in range(1, max_id + 1):
            out += ('%010d 00000 n \n' % offsets.get(oid, 0)).encode()
        out += ('trailer\n<< /Size %d /Root 1 0 R /Info %d 0 R >>\n'
                'startxref\n%d\n%%%%EOF\n' % (max_id + 1, info_id, xref)).encode()
        with open(path, 'wb') as f:
            f.write(out)
        return total


# --- docx parsing ------------------------------------------------------------
def read_paragraphs(xml_bytes):
    root = ET.fromstring(xml_bytes)
    body = root.find(W + 'body')
    paras = []
    for p in body.iter(W + 'p'):
        runs = []
        for r in p.iter(W + 'r'):
            t = ''.join(x.text or '' for x in r.iter(W + 't'))
            if not t:
                continue
            rpr = r.find(W + 'rPr')
            bold = rpr is not None and rpr.find(W + 'b') is not None
            runs.append([t, bold])
        text = ''.join(t for t, _ in runs).strip()
        if not text:
            continue
        ppr = p.find(W + 'pPr')
        is_list = ppr is not None and ppr.find(W + 'numPr') is not None
        all_bold = bool(runs) and all(b for _, b in runs)
        paras.append({'text': text, 'runs': runs, 'list': is_list, 'bold': all_bold})
    return paras


def strip_phone_text(s):
    s = PHONE_RE.sub('', s)
    s = re.sub(r'\s*\|\s*\|\s*', '  |  ', s)
    s = re.sub(r'[ \t]{3,}', '  ', s)
    return s.strip()


def write_web_docx(src_path, out_path):
    """Copy the original .docx, minus the phone number in the contact line."""
    zin = zipfile.ZipFile(src_path, 'r')
    xml = zin.read('word/document.xml').decode('utf-8')
    if OMIT_PHONE:
        # Keep the original namespace prefixes so Word/Pages still open the file.
        for prefix, uri in re.findall(r'xmlns:([A-Za-z0-9]+)="([^"]+)"', xml):
            ET.register_namespace(prefix, uri)
        root = ET.fromstring(xml)
        for p in root.iter(W + 'p'):
            ts = list(p.iter(W + 't'))
            joined = ''.join(t.text or '' for t in ts)
            if '9550' not in joined and '+91' not in joined:
                continue
            ts[0].text = strip_phone_text(joined)
            ts[0].set(XML_SPACE, 'preserve')
            for t in ts[1:]:
                t.text = ''
        xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
               + ET.tostring(root, encoding='unicode'))
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                data = xml.encode('utf-8')
            zout.writestr(item, data)
    zin.close()


SECTIONS = {
    'PROFESSIONAL SUMMARY', 'CORE SKILLS', 'WORK EXPERIENCE',
    'EDUCATION', 'CERTIFICATIONS',
}
DATE_RE = re.compile(r'\b(?:19|20)\d{2}\b|Present')


def classify(paras):
    out, section = [], ''
    for i, p in enumerate(paras):
        t = ascii_safe(p['text'])
        if OMIT_PHONE:
            t = strip_phone_text(t)
        kind = 'body'
        if i == 0:
            kind = 'name'
        elif i == 1:
            kind = 'role'
        elif i == 2:
            kind = 'contact'
        elif p['text'].strip().upper() in SECTIONS:
            kind = 'section'
            section = p['text'].strip().upper()
        elif p['list']:
            kind = 'bullet'
        elif p['bold'] and len(t) < 70:
            kind = 'company' if section == 'WORK EXPERIENCE' else 'degree'
        elif section == 'WORK EXPERIENCE' and DATE_RE.search(t) and '|' in t:
            kind = 'jobline'
        elif section == 'WORK EXPERIENCE':
            kind = 'bullet'
        elif section == 'CORE SKILLS' and ':' in t[:40]:
            kind = 'skill'
        out.append(dict(p, text=t, kind=kind, section=section))
    return out


def rich_chars(p):
    chars = []
    for t, bold in p['runs']:
        for ch in ascii_safe(t):
            chars.append((ch, bold))
    if OMIT_PHONE:
        # remove phone chars by rebuilding from sanitised plain text, keeping
        # bold flags from the first run where possible
        plain = strip_phone_text(ascii_safe(p['text']))
        original = ascii_safe(p['text'])
        if plain != original:
            return [(c, False) for c in plain]
    return chars


# --- layout ------------------------------------------------------------------
def build_pdf(paras, path):
    pdf = PDF()

    def line_plain(s, font, size, color, leading, indent=0, after=0, spacing=0, bullet=False):
        lines = pdf.wrap(s, font, size, CW - indent)
        for ln in lines:
            pdf.ensure(leading)
            if bullet:
                pdf.dot(ML + 2, pdf.y - leading + 3.4)
            pdf.text(ML + indent, pdf.y - leading, ln, font, size, color, spacing)
            pdf.y -= leading
        pdf.y -= after

    def line_rich(chars, size=9.2, color=INK2, leading=12.4, after=2.5):
        for ln in pdf.wrap_rich(chars, size, CW):
            pdf.ensure(leading)
            pdf.draw_rich(ln, ML, pdf.y - leading, size, color)
            pdf.y -= leading
        pdf.y -= after

    for p in paras:
        t, kind = p['text'], p['kind']

        if kind == 'name':
            pdf.ensure(34)
            pdf.text(ML, pdf.y - 24, t, 'F2', 21, PLUM)
            pdf.y -= 27

        elif kind == 'role':
            pdf.ensure(16)
            pdf.text(ML, pdf.y - 11, t, 'F2', 8.4, PLUM, spacing=0.25)
            pdf.y -= 14

        elif kind == 'contact':
            pdf.ensure(16)
            pdf.text(ML, pdf.y - 10, t, 'F1', 8.0, GRAY)
            pdf.y -= 13
            pdf.rule(ML, pdf.y, PAGE_W - MR, PLUM, 1.1)
            pdf.y -= 14

        elif kind == 'section':
            pdf.ensure(30)
            pdf.y -= 8
            pdf.text(ML, pdf.y - 9, t, 'F2', 8.6, PLUM, spacing=0.9)
            pdf.y -= 12
            pdf.rule(ML, pdf.y, PAGE_W - MR, PLUM, 0.7)
            pdf.y -= 12

        elif kind == 'body':
            line_plain(t, 'F1', 9.2, INK2, 12.6, after=5)

        elif kind == 'skill':
            line_rich(rich_chars(p), size=9.2, leading=12.3, after=3)

        elif kind == 'company':
            pdf.ensure(20)
            pdf.y -= 5
            pdf.text(ML, pdf.y - 11, t, 'F2', 10.5, INK)
            pdf.y -= 14

        elif kind == 'degree':
            pdf.ensure(18)
            pdf.text(ML, pdf.y - 11, t, 'F2', 10.0, INK)
            pdf.y -= 14

        elif kind == 'jobline':
            parts = t.rsplit('|', 1)
            left = parts[0].strip()
            right = parts[1].strip() if len(parts) > 1 else ''
            pdf.ensure(16)
            pdf.text(ML, pdf.y - 10, left, 'F2', 9.1, INK2)
            if right:
                pdf.text(PAGE_W - MR - text_w(right, 'F1', 8.1), pdf.y - 10,
                         right, 'F1', 8.1, GRAY)
            pdf.y -= 15

        elif kind == 'bullet':
            pdf.ensure(13)
            lines = pdf.wrap(t, 'F1', 9.0, CW - 15)
            for j, ln in enumerate(lines):
                pdf.ensure(12.2)
                if j == 0:
                    pdf.dot(ML + 2.5, pdf.y - 12.2 + 3.3)
                pdf.text(ML + 15, pdf.y - 12.2, ln, 'F1', 9.0, INK2)
                pdf.y -= 12.2
            pdf.y -= 2.5

    n = pdf.save(path, 'Jayant Singh Singoria - Resume 2025', 'Jayant Singh Singoria')
    return n


def main():
    src = ORIGINAL_DOCX if os.path.exists(ORIGINAL_DOCX) else OUT_DOCX
    if not os.path.exists(src):
        sys.exit('Could not find the source .docx. Expected: ' + ORIGINAL_DOCX)

    z = zipfile.ZipFile(src)
    xml = z.read('word/document.xml')
    z.close()

    paras = read_paragraphs(xml)
    if not paras:
        sys.exit('No paragraphs found in the .docx')

    write_web_docx(src, OUT_DOCX)
    os.makedirs(ASSETS, exist_ok=True)
    pages = build_pdf(classify(paras), OUT_PDF)

    print('Read %d paragraphs from %s' % (len(paras), os.path.basename(src)))
    print('Wrote %s (%d pages, %d bytes)' % (OUT_PDF, pages, os.path.getsize(OUT_PDF)))
    print('Wrote %s (web-safe copy, phone %s)' %
          (OUT_DOCX, 'removed' if OMIT_PHONE else 'kept'))


if __name__ == '__main__':
    main()
