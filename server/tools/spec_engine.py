"""Spec-driven drawing engine (hot-reloaded by tools.spec_builder on every call).

A spec is a JSON document:  {"ops": [ {...}, ... ]}
All geometry is in millimetres, page top-left origin (y grows downward).

Ops
  rect     x y w h [radius] [fill] [alpha] [stroke] [stroke_w] [dash] [shadow] [gradient] [fade] [name]
  ellipse  x y w h   (same style keys)
  curve    subpaths:[{closed, segs:[["m",x,y],["l",x,y],["c",x1,y1,x2,y2,x3,y3]]}]  (same style keys)
  text     text x y(ink top) [w(ink width)] font size_pt color [bold] [name]
  image    path x y w h [name]
  order    target to:"back"|"front"
  scale_page  w h [factor]   resize the page and scale all artwork about the page top-left
  move     target|targets [x|cx] [y] [dx] [dy]   reposition without resizing
  list     [y_min] [y_max]   read-only shape listing (set "measure_limit" in the spec to see rows)
  stroke style keys: stroke=[r,g,b]  stroke_w=mm  dash=true  cap/join rounded when "round":true
"""

from __future__ import annotations

import math
import os
from typing import Any

from core.operations import _with_bottom_left_reference, _safe_attr, _walk_shapes

_FOUNTAIN_LINEAR = 1


def _rgb(c):
    return [int(round(v)) for v in c]


def _cmyk(color, rgb):
    """Assign an RGB design value, then convert the colour to CMYK so the artwork is print-ready."""
    color.RGBAssign(*_rgb(rgb))
    try:
        color.ConvertToCMYK()
    except Exception:
        pass


def _apply_style(app, shape, op, warnings):
    # ---- fill
    grad = op.get("gradient")
    if grad:
        stops = grad["stops"]  # [[pos0-100,[r,g,b]], ...]  first/last = start/end
        c1 = app.CreateColor(); _cmyk(c1, stops[0][1])
        c2 = app.CreateColor(); _cmyk(c2, stops[-1][1])
        shape.Fill.ApplyFountainFill(
            StartColor=c1, EndColor=c2, Type=_FOUNTAIN_LINEAR,
            Angle=float(grad.get("angle", 90)), Steps=0, EdgePad=0, MidPoint=50,
        )
        f = shape.Fill.Fountain
        for pos, col in stops[1:-1]:
            cc = app.CreateColor(); _cmyk(cc, col)
            f.Colors.Add(cc, float(pos))
    elif op.get("fill") is not None:
        _cmyk(shape.Fill.UniformColor, op["fill"])
    else:
        shape.Fill.ApplyNoFill()

    # ---- outline
    if op.get("stroke") is not None:
        shape.Outline.Width = float(op.get("stroke_w", 0.3))
        _cmyk(shape.Outline.Color, op["stroke"])
        if op.get("round"):
            try:
                shape.Outline.LineJoin = 2
                shape.Outline.LineCaps = 1
            except Exception:
                pass
        if op.get("dash"):
            try:
                shape.Outline.Style = app.OutlineStyles(2)
            except Exception as exc:  # dash style index differs between versions
                warnings.append(f"dash style not applied: {exc}")
    else:
        shape.Outline.SetNoOutline()

    # ---- transparency
    alpha = op.get("alpha")
    if alpha is not None and float(alpha) < 0.999:
        try:
            shape.Transparency.ApplyUniformTransparency(int(round((1.0 - float(alpha)) * 100)))
        except Exception as exc:
            warnings.append(f"alpha not applied: {exc}")
    fade = op.get("fade")
    if fade:
        try:
            shape.Transparency.ApplyFountainTransparency(
                int(fade.get("from", 0)), int(fade.get("to", 100)),
                _FOUNTAIN_LINEAR, float(fade.get("angle", 90)), 0, 0, 50,
            )
        except Exception as exc:
            warnings.append(f"fade not applied: {exc}")

    # ---- drop shadow
    sh = op.get("shadow")
    if sh:
        try:
            col = app.CreateColor(); _cmyk(col, sh.get("color", [18, 54, 95]))
            shape.CreateDropShadow(
                Type=0, Opacity=int(sh.get("opacity", 20)), Feather=float(sh.get("blur", 8)),
                OffsetX=float(sh.get("dx", 0)), OffsetY=float(sh.get("dy", -6)), Color=col,
            )
        except Exception as exc:
            warnings.append(f"shadow not applied: {exc}")

    if op.get("name"):
        shape.Name = str(op["name"])


def _find(doc, target, named):
    if target in named:
        return named[target]
    for s, _ in _walk_shapes(doc.ActivePage.Shapes):   # also inside groups / PowerClip contents
        if str(s.StaticID) == str(target) or str(_safe_attr(s, "Name", "")) == str(target):
            return s
    raise ValueError(f"shape not found: {target}")


def _op_rect(ctx, op):
    doc, app, layer, ph = ctx["doc"], ctx["app"], ctx["layer"], ctx["ph"]
    x, y, w, h = float(op["x"]), float(op["y"]), float(op["w"]), float(op["h"])
    r = float(op.get("radius", 0))
    s = layer.CreateRectangle(x, ph - (y + h), x + w, ph - y, r, r, r, r)
    _apply_style(app, s, op, ctx["warnings"])
    return s


def _op_ellipse(ctx, op):
    app, layer, ph = ctx["app"], ctx["layer"], ctx["ph"]
    x, y, w, h = float(op["x"]), float(op["y"]), float(op["w"]), float(op["h"])
    s = layer.CreateEllipse(x, ph - (y + h), x + w, ph - y)
    _apply_style(app, s, op, ctx["warnings"])
    return s


def _len_angle(cx, cy, nx, ny):
    dx, dy = cx - nx, cy - ny
    return math.hypot(dx, dy), math.degrees(math.atan2(dy, dx))


def _op_curve(ctx, op):
    doc, app, layer, ph = ctx["doc"], ctx["app"], ctx["layer"], ctx["ph"]
    curve = doc.CreateCurve()
    made = False
    for path in op["subpaths"]:
        segs = path["segs"]
        if not segs or segs[0][0] != "m":
            continue
        px, py = float(segs[0][1]), ph - float(segs[0][2])
        sp = curve.CreateSubPath(px, py)
        made = True
        for seg in segs[1:]:
            if seg[0] == "l":
                nx, ny = float(seg[1]), ph - float(seg[2])
                sp.AppendLineSegment(nx, ny)
                px, py = nx, ny
            elif seg[0] == "c":
                c1x, c1y = float(seg[1]), ph - float(seg[2])
                c2x, c2y = float(seg[3]), ph - float(seg[4])
                nx, ny = float(seg[5]), ph - float(seg[6])
                sl, sa = _len_angle(c1x, c1y, px, py)
                el, ea = _len_angle(c2x, c2y, nx, ny)
                sp.AppendCurveSegment(nx, ny, sl, sa, el, ea)
                px, py = nx, ny
        if path.get("closed"):
            sp.Closed = True
    if not made:
        raise ValueError("curve without subpaths")
    s = layer.CreateCurve(curve)
    _apply_style(app, s, op, ctx["warnings"])
    return s


def _op_text(ctx, op):
    app, layer, ph = ctx["app"], ctx["layer"], ctx["ph"]
    text = str(op["text"]).replace("\r\n", "\r").replace("\n", "\r")
    font = op.get("font", "Segoe UI")
    size = float(op.get("size_pt", 12))
    try:
        s = layer.CreateArtisticText(0, 0, text, Font=font, Size=size, Bold=bool(op.get("bold", False)))
    except Exception:
        s = layer.CreateArtisticText(0, 0, text)
        from tools.text import _set_text_bold, _set_text_font, _set_text_size
        _set_text_font(s.Text, font)
        _set_text_size(s.Text, size)
        if op.get("bold"):
            _set_text_bold(s.Text, True)
    if op.get("bold"):
        # CreateArtisticText(Bold=...) is silently ignored on some builds; set it on the story as well.
        try:
            from tools.text import _set_text_bold
            _set_text_bold(s.Text, True)
        except Exception:
            pass
    _cmyk(s.Fill.UniformColor, op.get("color", [0, 0, 0]))
    try:
        s.Outline.SetNoOutline()
    except Exception:
        pass
    target_w = op.get("w")
    wv, hv = float(s.SizeWidth), float(s.SizeHeight)
    if target_w and wv > 0 and abs(wv - float(target_w)) / float(target_w) > 0.004:
        s.SetSize(float(target_w), hv)
        wv = float(s.SizeWidth)
    y_top = (float(op["yb"]) - hv) if "yb" in op else float(op["y"])
    x_left = (float(op["cx"]) - wv / 2.0) if "cx" in op else float(op["x"])
    # LeftX/BottomY are absolute page coordinates and do not depend on the ruler reference point.
    s.LeftX = x_left
    s.BottomY = ph - y_top - hv
    if op.get("name"):
        s.Name = str(op["name"])
    ctx["measure"].append({"text": text[:30], "w": round(wv, 2), "h": round(hv, 2),
                           "want_w": op.get("w"), "want_h": op.get("h")})
    return s


def _op_image(ctx, op):
    layer, page, ph = ctx["layer"], ctx["page"], ctx["ph"]
    path = os.path.abspath(op["path"])
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    before = {int(s.StaticID) for s in page.Shapes}
    layer.Import(path, 0, None)
    new = None
    for s in page.Shapes:
        if int(s.StaticID) not in before:
            new = s
    if new is None:
        raise RuntimeError("image import produced no shape")
    x, y, w, h = float(op["x"]), float(op["y"]), float(op["w"]), float(op["h"])
    new.SetSize(w, h)
    new.LeftX = x
    new.BottomY = ph - (y + h)
    if op.get("name"):
        new.Name = str(op["name"])
    return new


def _op_order(ctx, op):
    s = _find(ctx["doc"], op["target"], ctx["named"])
    to = op.get("to", "front")
    if to == "back":
        s.OrderToBack()
    elif to == "front":
        s.OrderToFront()
    elif to == "forward":
        s.OrderForwardOne()
    elif to == "backward":
        s.OrderBackOne()
    return s


def _op_place(ctx, op):
    """Move/resize an existing shape (by StaticID or name) to a top-left mm box."""
    s = _find(ctx["doc"], op["target"], ctx["named"])
    ph = ctx["ph"]
    x, y, w, h = float(op["x"]), float(op["y"]), float(op["w"]), float(op["h"])
    try:
        s.Outline.ScaleWithShape = False   # a re-box is a layout change: keep the stroke weight
    except Exception:
        pass
    s.SetSize(w, h)
    s.LeftX = x
    s.BottomY = ph - (y + h)
    return s


def _op_clip(ctx, op):
    """Put `target` inside container shape `container` (PowerClip), keeping its position."""
    s = _find(ctx["doc"], op["target"], ctx["named"])
    c = _find(ctx["doc"], op["container"], ctx["named"])
    s.AddToPowerClip(c, 0)
    return c


def _op_restyle(ctx, op):
    """Re-apply style keys (fade/alpha/shadow/...) to an existing shape."""
    s = _find(ctx["doc"], op["target"], ctx["named"])
    sub = {k: v for k, v in op.items() if k in ("fade", "alpha", "shadow")}
    if "fade" in sub or "alpha" in sub:
        pass
    _restyle_partial(ctx["app"], s, sub, ctx["warnings"])
    return s


def _restyle_partial(app, shape, sub, warnings):
    # Same code paths as _apply_style but without touching fill/outline.
    alpha = sub.get("alpha")
    if alpha is not None and float(alpha) < 0.999:
        shape.Transparency.ApplyUniformTransparency(int(round((1.0 - float(alpha)) * 100)))
    fade = sub.get("fade")
    if fade:
        shape.Transparency.ApplyFountainTransparency(
            int(fade.get("from", 0)), int(fade.get("to", 100)),
            _FOUNTAIN_LINEAR, float(fade.get("angle", 90)), 0, 0, 50,
        )


def _is_black(s):
    try:
        c = s.Fill.UniformColor
        return int(c.RGBRed) == 0 and int(c.RGBGreen) == 0 and int(c.RGBBlue) == 0
    except Exception:
        return False


def _op_match(ctx, op):
    """Find top-level shapes by bbox (top-left mm, +/- tol) and optional type/black filter, then act on them.

    op: x y w h [tol=3] [kind: "rect"|"text"] [black: true|false] action: "delete" | "shadow"
    """
    ph, tol = ctx["ph"], float(op.get("tol", 3))
    hits = []
    for s in list(ctx["page"].Shapes):
        try:
            x, y = float(s.LeftX), ph - float(s.TopY)
            w, h = float(s.SizeWidth), float(s.SizeHeight)
        except Exception:
            continue
        if (abs(x - op["x"]) > tol or abs(y - op["y"]) > tol or abs(w - op["w"]) > tol or abs(h - op["h"]) > tol):
            continue
        kind = op.get("kind")
        t = int(s.Type)
        if kind == "rect" and t != 1:
            continue
        if kind == "curve" and t != 3:
            continue
        if kind == "text" and t not in (3, 6):
            continue
        if "black" in op and _is_black(s) != bool(op["black"]):
            continue
        hits.append(s)
    for s in hits:
        if op.get("action") == "delete":
            s.Delete()
        elif op.get("action") == "move":
            s.LeftX = float(s.LeftX) + float(op.get("dx", 0))
            s.BottomY = float(s.BottomY) - float(op.get("dy", 0))   # dy > 0 moves down (top-left coords)
        elif op.get("action") == "shadow":
            sh = op["shadow"]
            col = ctx["app"].CreateColor(); _cmyk(col, sh.get("color", [0, 0, 0]))
            s.CreateDropShadow(Type=0, Opacity=int(sh.get("opacity", 60)), Feather=float(sh.get("blur", 8)),
                               OffsetX=float(sh.get("dx", 0)), OffsetY=float(sh.get("dy", 0)), Color=col)
    ctx["measure"].append({"match": len(hits), "action": op.get("action")})
    return None


def _op_save_as(ctx, op):
    """Save the document as .cdr under COREL_OUTPUT_ROOT, trying several COM call shapes."""
    from pathlib import Path
    path = Path(str(op["path"])).resolve(strict=False)
    if path.suffix.lower() != ".cdr":
        raise ValueError("save_as path must end with .cdr")
    root = os.environ.get("COREL_OUTPUT_ROOT", "").strip()
    if root:
        path.relative_to(Path(root).expanduser().resolve(strict=False))   # raises ValueError if outside
    if path.exists() and not op.get("overwrite"):
        raise FileExistsError(str(path))
    doc, app = ctx["doc"], ctx["app"]
    errs = []
    attempts = []
    attempts.append(lambda: doc.SaveAs(str(path)))
    def _with_opts():
        opts = app.CreateStructSaveAsOptions()
        try:
            opts.EmbedVectorFonts = bool(op.get("embed_fonts", True))
        except Exception:
            pass
        doc.SaveAs(str(path), opts)
    attempts.append(_with_opts)
    for fn in attempts:
        try:
            fn()
            ctx["measure"].append({"saved": str(path)})
            return None
        except Exception as exc:
            errs.append(str(exc)[:160])
    raise RuntimeError("SaveAs failed: " + " | ".join(errs))


def _op_goto_page(ctx, op):
    """Make page n (1-based) the target of the following ops."""
    doc = ctx["doc"]
    page = doc.Pages(int(op["n"]))
    page.Activate()
    ctx["page"] = page
    ctx["layer"] = doc.ActiveLayer
    ctx["ph"] = float(page.SizeHeight)
    return None


def _op_new_page(ctx, op):
    """Append a page (optionally resized) and make it the target of the following ops."""
    doc = ctx["doc"]
    doc.AddPages(1)
    page = doc.Pages.Last
    page.Activate()
    if op.get("w") and op.get("h"):
        page.SetSize(float(op["w"]), float(op["h"]))
    ctx["page"] = page
    ctx["layer"] = doc.ActiveLayer
    ctx["ph"] = float(page.SizeHeight)
    return None


def _op_save(ctx, op):
    """Save the document in place (it must already have a path)."""
    ctx["doc"].Save()
    ctx["measure"].append({"saved_in_place": str(ctx["doc"].FullFileName)})
    return None


def _op_clear(ctx, op):
    shapes = ctx["page"].Shapes
    if int(shapes.Count) > 0:
        shapes.All().Delete()
    return None


def _op_scale_page(ctx, op):
    """Resize the active page to w x h and scale every shape by `factor` (default: fit inside) about the page top-left.

    Outlines, corner radii and text sizes scale with the artwork, so the result stays editable.
    """
    page = ctx["page"]
    pw, ph = float(page.SizeWidth), float(page.SizeHeight)
    w, h = float(op["w"]), float(op["h"])
    f = float(op.get("factor") or min(w / pw, h / ph))
    for s, _ in _walk_shapes(page.Shapes):
        try:
            s.Outline.ScaleWithShape = True
        except Exception:
            pass
        try:
            s.Rectangle.RelativeCornerScaling = True
        except Exception:
            pass
    rng = page.Shapes.All()
    rng.StretchEx(0.0, ph, f, f, True)          # anchor = page top-left; True = scale paragraph text too
    x, y = float(rng.LeftX), ph - float(rng.TopY)
    page.SetSize(w, h)
    rng.Move(x - float(rng.LeftX), (h - y) - float(rng.TopY))   # keep top-left mm position whatever SetSize did
    ctx["ph"] = h
    ctx["measure"].append({"scaled": round(f, 6), "page": [w, h]})
    return None


def _op_move(ctx, op):
    """Move shapes without resizing. target | targets:[...]; absolute x|cx, y (top-left mm) and/or relative dx, dy (dy>0 = down)."""
    ph = ctx["ph"]
    for t in op.get("targets") or [op["target"]]:
        s = _find(ctx["doc"], t, ctx["named"])
        w, h = float(s.SizeWidth), float(s.SizeHeight)
        if "cx" in op:
            s.LeftX = float(op["cx"]) - w / 2.0
        if "x" in op:
            s.LeftX = float(op["x"])
        if "y" in op:
            s.BottomY = ph - float(op["y"]) - h
        if op.get("dx"):
            s.LeftX = float(s.LeftX) + float(op["dx"])
        if op.get("dy"):
            s.BottomY = float(s.BottomY) - float(op["dy"])
    return None


def _op_list(ctx, op):
    """Read-only: report shapes (nested too) as top-left mm boxes with type/name/text. Optional y_min / y_max filter."""
    ph = ctx["ph"]
    lo, hi = float(op.get("y_min", -1e9)), float(op.get("y_max", 1e9))
    for s, parents in _walk_shapes(ctx["page"].Shapes):
        try:
            x, y, w, h = float(s.LeftX), ph - float(s.TopY), float(s.SizeWidth), float(s.SizeHeight)
        except Exception:
            continue
        if y + h < lo or y > hi:
            continue
        t = int(_safe_attr(s, "Type", -1))
        row = {"id": int(s.StaticID), "t": t, "box": [round(v, 1) for v in (x, y, w, h)]}
        if parents:
            row["in"] = parents[-1]
        if _safe_attr(s, "Name", ""):
            row["name"] = str(s.Name)
        try:
            row["fill_type"] = int(s.Fill.UniformColor.Type)   # cdrColorType: 2 = CMYK, 3 = RGB
        except Exception:
            pass
        if t == 6:   # cdrTextShape
            try:
                row["text"] = str(s.Text.Story.Text)[:60]
                row["pt"] = round(float(s.Text.Story.Size), 1)
            except Exception:
                pass
        ctx["measure"].append(row)
    return None


_OPS = {"scale_page": _op_scale_page, "move": _op_move, "list": _op_list, "clear": _op_clear, "goto_page": _op_goto_page, "new_page": _op_new_page, "save": _op_save, "save_as": _op_save_as, "match": _op_match, "restyle": _op_restyle, "place": _op_place, "clip": _op_clip, "rect": _op_rect, "ellipse": _op_ellipse, "curve": _op_curve,
        "text": _op_text, "image": _op_image, "order": _op_order}


def run_spec(doc: Any, spec: dict, start: int = 0, limit: int | None = None) -> dict:
    app = doc.Application
    page = doc.ActivePage
    layer = doc.ActiveLayer
    ph = float(page.SizeHeight)
    ctx = {"doc": doc, "app": app, "page": page, "layer": layer, "ph": ph,
           "named": {}, "warnings": [], "measure": []}
    ops = spec["ops"]
    end = len(ops) if limit is None else min(len(ops), start + limit)
    errors, created = [], 0
    with _with_bottom_left_reference(doc):
        for i in range(start, end):
            op = ops[i]
            kind = op.get("op")
            try:
                fn = _OPS[kind]
                shape = fn(ctx, op)
                if op.get("name") and shape is not None:
                    ctx["named"][op["name"]] = shape
                created += 1
            except Exception as exc:
                errors.append({"i": i, "op": kind, "text": str(op.get("text", ""))[:30], "err": str(exc)[:300]})
    return {"total_ops": len(ops), "ran": [start, end], "ok": created, "errors": errors[:40],
            "error_count": len(errors), "warnings": sorted(set(ctx["warnings"]))[:10],
            "measure": ctx["measure"][:int(spec.get("measure_limit", 0))]}
