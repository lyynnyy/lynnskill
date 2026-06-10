#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


A4_W, A4_H = 2480, 3508
WHITE = (255, 255, 255)
INK = (38, 42, 47)
MUTED = (108, 113, 122)
LINE = (222, 222, 222)
PALE = (248, 248, 248)

FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
]


def load_font(size: int, rounded: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_CANDIDATES[1:] + FONT_CANDIDATES[:1] if rounded else FONT_CANDIDATES
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


F_TITLE = load_font(78)
F_DAY = load_font(46, rounded=True)
F_H = load_font(44)
F_BODY = load_font(35)
F_SMALL = load_font(29)


def wrap(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font, fill, max_width: int, gap: int = 10) -> int:
    x, y = xy
    line = ""
    lines: list[str] = []
    for ch in text:
        trial = line + ch
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = ch
    if line:
        lines.append(line)
    for item in lines:
        draw.text((x, y), item, font=font, fill=fill)
        y += font.size + gap
    return y


def card(draw, box, radius=34):
    draw.rounded_rectangle(box, radius=radius, fill=WHITE, outline=LINE, width=3)


def icon(draw, kind: str, cx: int, cy: int):
    if kind == "target":
        draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=INK, width=6)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=INK)
    elif kind == "steps":
        for i in range(3):
            y = cy - 20 + i * 20
            draw.ellipse([cx - 28, y - 6, cx - 16, y + 6], fill=INK)
            draw.line([cx - 6, y, cx + 30, y], fill=INK, width=6)
    elif kind == "check":
        draw.line([cx - 26, cy, cx - 8, cy + 18, cx + 28, cy - 22], fill=INK, width=8)
    elif kind == "note":
        draw.rounded_rectangle([cx - 25, cy - 30, cx + 25, cy + 30], radius=8, outline=INK, width=6)
        draw.line([cx - 12, cy - 10, cx + 13, cy - 10], fill=INK, width=5)
        draw.line([cx - 12, cy + 8, cx + 13, cy + 8], fill=INK, width=5)
    else:
        draw.polygon(
            [(cx, cy - 34), (cx + 10, cy - 8), (cx + 36, cy), (cx + 10, cy + 8),
             (cx, cy + 34), (cx - 10, cy + 8), (cx - 36, cy), (cx - 10, cy - 8)],
            fill=INK,
        )


def list_block(draw, box, title: str, items: list[str], kind: str):
    x0, y0, x1, _ = box
    card(draw, box)
    draw.rounded_rectangle([x0 + 30, y0 + 30, x0 + 102, y0 + 102], radius=24, fill=PALE, outline=LINE, width=2)
    icon(draw, kind, x0 + 66, y0 + 66)
    draw.text((x0 + 122, y0 + 37), title, font=F_H, fill=INK)
    draw.line([x0 + 34, y0 + 128, x1 - 34, y0 + 128], fill=LINE, width=3)
    y = y0 + 158
    for item in items:
        draw.ellipse([x0 + 42, y + 13, x0 + 58, y + 29], fill=INK)
        y = wrap(draw, (x0 + 76, y), item, F_BODY, INK, x1 - x0 - 118, 8)
        y += 16


def make_task_page(plan: dict) -> Image.Image:
    img = Image.new("RGB", (A4_W, A4_H), WHITE)
    draw = ImageDraw.Draw(img)
    day = str(plan.get("day", ""))
    title = str(plan.get("title", "Learning Task"))
    duration = str(plan.get("duration", "15-30 min"))
    source = str(plan.get("source", ""))

    draw.rounded_rectangle([105, 95, 520, 205], radius=40, fill=WHITE, outline=INK, width=4)
    draw.text((158, 123), f"DAY {day}", font=F_DAY, fill=INK)
    draw.text((565, 96), title, font=F_TITLE, fill=INK)
    draw.text((568, 188), f"1 page | observe first | {duration}", font=F_SMALL, fill=MUTED)
    draw.line([105, 255, A4_W - 105, 255], fill=INK, width=4)

    card(draw, [105, 315, A4_W - 105, 625], radius=40)
    icon(draw, "spark", 185, 420)
    draw.text((250, 360), "Focus", font=F_H, fill=INK)
    wrap(draw, (250, 435), str(plan.get("focus", "")), F_BODY, INK, A4_W - 420, 8)
    chip_texts = ["Page 2 is the worksheet", duration, source]
    x = 170
    for chip in chip_texts:
        width = draw.textbbox((0, 0), chip, font=F_SMALL)[2]
        draw.rounded_rectangle([x, 535, min(x + width + 58, A4_W - 110), 588], radius=24, fill=WHITE, outline=LINE, width=2)
        draw.text((x + 28, 546), chip, font=F_SMALL, fill=MUTED)
        x += width + 88

    left, gap = 105, 36
    col_w = (A4_W - 210 - gap) // 2
    row_h = 530
    top = 700
    list_block(draw, [left, top, left + col_w, top + row_h], "Goal", plan.get("goal", []), "target")
    list_block(draw, [left + col_w + gap, top, A4_W - 105, top + row_h], "Steps", plan.get("steps", []), "steps")
    list_block(draw, [left, top + row_h + gap, left + col_w, top + row_h * 2 + gap], "Check", plan.get("check", []), "check")
    list_block(draw, [left + col_w + gap, top + row_h + gap, A4_W - 105, top + row_h * 2 + gap], "Notes", plan.get("notes", []), "note")

    y0 = 1840
    card(draw, [105, y0, A4_W - 105, 2575], radius=40)
    draw.text((155, y0 + 50), "Ability Progress", font=F_H, fill=INK)
    x = 155
    for item in plan.get("ability", [])[:4]:
        name = str(item.get("name", "Ability"))
        progress = str(item.get("progress", ""))
        card(draw, [x, y0 + 145, x + 500, y0 + 425], radius=30)
        icon(draw, "spark", x + 70, y0 + 245)
        draw.text((x + 125, y0 + 198), name, font=F_BODY, fill=INK)
        draw.text((x + 125, y0 + 258), progress, font=F_H, fill=INK)
        x += 545
    draw.text((155, y0 + 512), f"Review: {plan.get('review', '')}", font=F_BODY, fill=INK)
    wrap(draw, (155, y0 + 590), f"Encouragement: {plan.get('encouragement', '')}", F_BODY, INK, A4_W - 310, 8)

    draw.text((105, A4_H - 150), f"Day {day} task card | Page 2 is the full worksheet", font=F_SMALL, fill=MUTED)
    return img


def make_worksheet_page(path: Path) -> Image.Image:
    canvas = Image.new("RGB", (A4_W, A4_H), WHITE)
    worksheet = Image.open(path).convert("RGB")
    fitted = ImageOps.contain(worksheet, (A4_W, A4_H), Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((A4_W - fitted.width) // 2, (A4_H - fitted.height) // 2))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a two-page A4 learning task PDF.")
    parser.add_argument("--plan-json", required=True, type=Path)
    parser.add_argument("--worksheet-image", required=True, type=Path)
    parser.add_argument("--output-pdf", required=True, type=Path)
    parser.add_argument("--preview-task-png", type=Path)
    parser.add_argument("--preview-worksheet-png", type=Path)
    args = parser.parse_args()

    plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
    task = make_task_page(plan)
    worksheet = make_worksheet_page(args.worksheet_image)
    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
    task.save(args.output_pdf, "PDF", resolution=300.0, save_all=True, append_images=[worksheet])
    if args.preview_task_png:
        task.save(args.preview_task_png)
    if args.preview_worksheet_png:
        worksheet.save(args.preview_worksheet_png)


if __name__ == "__main__":
    main()
