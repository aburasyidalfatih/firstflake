"""Makes public/family-pack-mockup.webp (the small image in the checkout order bump)
from pages of private/family-pack.pdf. Needs pdftoppm (poppler) and Pillow.
Run:  python familypack/mockup.py
"""
import subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageFilter

HERE = Path(__file__).parent
PDF = HERE.parent / 'private' / 'family-pack.pdf'
OUT = HERE.parent / 'public' / 'family-pack-mockup.webp'
W, H = 640, 440


def page_img(n, tmp):
    stem = Path(tmp) / f'p{n}'
    subprocess.run(['pdftoppm', '-f', str(n), '-l', str(n), '-r', '90', '-png', '-singlefile', str(PDF), str(stem)], check=True)
    return Image.open(f'{stem}.png').convert('RGBA')


def place(canvas, im, height, angle, cx, cy):
    im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    shadow.putalpha(im.getchannel('A').point(lambda a: 70 if a else 0))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    x, y = cx - im.width // 2, cy - im.height // 2
    canvas.alpha_composite(shadow, (x + 6, y + 10))
    canvas.alpha_composite(im, (x, y))


with tempfile.TemporaryDirectory() as tmp:
    cover, bingo, cert = page_img(1, tmp), page_img(7, tmp), page_img(16, tmp)
    canvas = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    place(canvas, cert, 330, 9, 466, 222)
    place(canvas, bingo, 330, -7, 176, 224)
    place(canvas, cover, 384, 0, 320, 218)
    canvas.convert('RGB').save(OUT, 'WEBP', quality=82, method=6)
print(OUT, OUT.stat().st_size, 'bytes')
