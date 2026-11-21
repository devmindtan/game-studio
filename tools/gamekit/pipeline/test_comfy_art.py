"""python3 -m unittest discover -s tools/gamekit/pipeline -p 'test_comfy_art.py' (không cần máy GPU)."""
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import comfy_art  # noqa: E402


class PixelizeTest(unittest.TestCase):
    def blurry(self):
        im = Image.new("RGB", (768, 768), (168, 170, 166))
        d = ImageDraw.Draw(im)
        d.rectangle([330, 150, 430, 650], fill=(40, 50, 80))      # thân
        d.rectangle([340, 90, 420, 150], fill=(230, 170, 140))    # đầu
        d.rectangle([300, 300, 460, 330], fill=(120, 40, 40))     # khăn
        return im.filter(ImageFilter.GaussianBlur(6))             # mờ như ảnh SDXL

    def test_crisp_sprite_at_target_height(self):
        px = comfy_art.pixelize(self.blurry(), height=30, colors=6)
        self.assertEqual(px.height, 30)
        self.assertLess(px.width, 20)
        alphas = {a for *_, a in px.getdata()}
        self.assertEqual(alphas, {0, 255})                        # không pixel bán trong suốt
        self.assertLessEqual(len(comfy_art.palette_of(px)), 6)
        self.assertEqual(px.getpixel((0, 0))[3], 0)               # góc là nền đã bỏ
        # màu nền không lọt vào palette, màu da (vùng nhỏ) còn giữ
        hexes = [c["hex"] for c in comfy_art.palette_of(px)]
        skin = [h for h in hexes if int(h[1:3], 16) > 180 and int(h[5:7], 16) < 170]
        self.assertTrue(skin, hexes)


if __name__ == "__main__":
    unittest.main()
