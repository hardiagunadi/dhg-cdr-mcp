import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

from tools import spec_engine


class Shape:
    """Box in CorelDRAW coordinates (origin bottom-left, y up)."""

    def __init__(self, sid, left, bottom, w, h):
        self.StaticID, self.Name, self.Type = sid, "", 1
        self.LeftX, self.BottomY, self.SizeWidth, self.SizeHeight = left, bottom, w, h

    @property
    def TopY(self):
        return self.BottomY + self.SizeHeight


class Range:
    def __init__(self, shapes):
        self.shapes = shapes

    @property
    def LeftX(self):
        return min(s.LeftX for s in self.shapes)

    @property
    def TopY(self):
        return max(s.TopY for s in self.shapes)

    def StretchEx(self, cx, cy, fx, fy, chars):
        for s in self.shapes:
            s.LeftX = cx + (s.LeftX - cx) * fx
            s.BottomY = cy + (s.BottomY - cy) * fy
            s.SizeWidth *= fx
            s.SizeHeight *= fy

    def Move(self, dx, dy):
        for s in self.shapes:
            s.LeftX += dx
            s.BottomY += dy


class Shapes(list):
    Count = 0

    def All(self):
        return Range(self)


class Page:
    def __init__(self, w, h, shapes):
        self.SizeWidth, self.SizeHeight, self.Shapes = w, h, Shapes(shapes)

    def SetSize(self, w, h):
        self.SizeWidth, self.SizeHeight = w, h


class Doc:
    ReferencePoint = 0

    def __init__(self, page):
        self.ActivePage, self.ActiveLayer, self.Application = page, None, None


def top_left(page, s):
    return [round(v, 3) for v in (s.LeftX, page.SizeHeight - s.TopY, s.SizeWidth, s.SizeHeight)]


class SpecEngineTests(unittest.TestCase):
    def test_scale_page_then_move(self):
        a = Shape(1, 0, 0, 4000, 2300)         # full-page background
        b = Shape(2, 100, 2300 - 690 - 1100, 1960, 1100)   # top-left box (100, 690)
        page = Page(4000, 2300, [a, b])
        out = spec_engine.run_spec(Doc(page), {"ops": [
            {"op": "scale_page", "w": 2400, "h": 1600},
            {"op": "move", "target": 2, "dy": 10, "x": 50},
        ]})
        self.assertEqual(out["error_count"], 0, out["errors"])
        self.assertEqual((page.SizeWidth, page.SizeHeight), (2400, 1600))
        self.assertEqual(top_left(page, a), [0, 0, 2400, 1380])      # factor 0.6, anchored top-left
        self.assertEqual(top_left(page, b), [50, 424, 1176, 660])    # 690*0.6 + 10


if __name__ == "__main__":
    unittest.main()
