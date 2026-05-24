from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Iterable


def _font(size: int = 18, bold: bool = False):
    try:
        from PIL import ImageFont

        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                continue
        return ImageFont.load_default()
    except Exception:
        return None


def draw_panel(path: str | Path, title: str, lines: Iterable[str], size: tuple[int, int] = (1440, 900)) -> Path:
    from PIL import Image, ImageDraw

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, "#0e1116")
    draw = ImageDraw.Draw(img)
    title_font = _font(38, True)
    sub_font = _font(20)
    mono = _font(18)
    draw.rounded_rectangle((28, 28, size[0] - 28, size[1] - 28), radius=18, fill="#151a21", outline="#2b323d", width=2)
    draw.text((54, 50), title, font=title_font, fill="#eef2f6")
    draw.line((54, 104, size[0] - 54, 104), fill="#2b323d", width=2)
    y = 130
    for raw in lines:
        for line in textwrap.wrap(str(raw), width=120):
            draw.text((62, y), line, font=mono if line.startswith((">", "$", "run_id", "status", "-")) else sub_font, fill="#dbe7ef")
            y += 28
            if y > size[1] - 60:
                draw.text((62, y), "...", font=mono, fill="#99a4b3")
                img.save(path)
                return path
        y += 8
    img.save(path)
    return path


def draw_chart(path: str | Path, title: str, labels: list[str], values: list[float], color: str = "#49d2b4") -> Path:
    from PIL import Image, ImageDraw

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1100, 650
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = _font(32, True)
    font = _font(16)
    draw.text((50, 34), title, font=title_font, fill="#111827")
    chart_left, chart_top, chart_right, chart_bottom = 80, 110, width - 60, height - 105
    draw.rectangle((chart_left, chart_top, chart_right, chart_bottom), outline="#d1d5db", width=2)
    max_value = max(values) if values else 1
    max_value = max(max_value, 1)
    bar_area = chart_right - chart_left - 40
    bar_width = max(24, int(bar_area / max(len(values), 1) * 0.58))
    gap = max(20, int(bar_area / max(len(values), 1) * 0.42))
    x = chart_left + 30
    for label, value in zip(labels, values):
        bar_h = int((chart_bottom - chart_top - 40) * (value / max_value))
        y0 = chart_bottom - bar_h
        draw.rounded_rectangle((x, y0, x + bar_width, chart_bottom), radius=6, fill=color)
        draw.text((x, y0 - 24), f"{value:.2f}", font=font, fill="#111827")
        short = label[:12]
        draw.text((x - 6, chart_bottom + 12), short, font=font, fill="#374151")
        x += bar_width + gap
    draw.text((50, height - 48), "Generated from real ClawFlow runtime outputs.", font=font, fill="#6b7280")
    img.save(path)
    return path


def draw_diagram(path: str | Path, title: str, nodes: list[str], edges: list[tuple[int, int]]) -> Path:
    from PIL import Image, ImageDraw

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1400, 850
    img = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(img)
    title_font = _font(34, True)
    font = _font(17, True)
    draw.text((48, 34), title, font=title_font, fill="#0f172a")
    cols = 3
    positions = []
    for idx, node in enumerate(nodes):
        row, col = divmod(idx, cols)
        x = 80 + col * 420
        y = 130 + row * 155
        positions.append((x, y, x + 310, y + 82))
        draw.rounded_rectangle(positions[-1], radius=12, fill="#ffffff", outline="#1f2937", width=2)
        wrapped = textwrap.wrap(node, width=28)
        ty = y + 17
        for line in wrapped[:2]:
            draw.text((x + 18, ty), line, font=font, fill="#0f172a")
            ty += 23
    for a, b in edges:
        if a >= len(positions) or b >= len(positions):
            continue
        ax0, ay0, ax1, ay1 = positions[a]
        bx0, by0, bx1, by1 = positions[b]
        start = (ax1, (ay0 + ay1) // 2)
        end = (bx0, (by0 + by1) // 2)
        if by0 > ay1:
            start = ((ax0 + ax1) // 2, ay1)
            end = ((bx0 + bx1) // 2, by0)
        draw.line((start, end), fill="#0f766e", width=3)
        draw.ellipse((end[0] - 5, end[1] - 5, end[0] + 5, end[1] + 5), fill="#0f766e")
    img.save(path)
    return path

