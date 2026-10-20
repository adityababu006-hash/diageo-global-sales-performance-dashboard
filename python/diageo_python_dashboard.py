"""Create a high-resolution executive sales dashboard with pandas and Pillow.

Synthetic portfolio dataset — not official Diageo sales data.
"""

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "diageo_sales_powerbi_ready.csv"
OUTPUT = ROOT / "images" / "dashboard-preview.png"

WIDTH, HEIGHT = 2800, 1700
NAVY = "#0B1526"
CARD = "#F7F4EE"
GOLD = "#C9A45C"
BLUE = "#6F8FAF"
TEAL = "#2A8C82"
RED = "#C65D57"
INK = "#152235"
MUTED = "#697586"
GRID = "#D6D9DE"
WHITE = "#F4F6F8"
BEVEL_LIGHT = "#FFF5D2"
BEVEL_DARK = "#6E5226"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu")
        / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental")
        / ("Arial Bold.ttf" if bold else "Arial.ttf"),
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(str(candidate), size)
        except OSError:
            continue
    return ImageFont.load_default()


def money_m(value: float, decimals: int = 1) -> str:
    return f"£{value / 1_000_000:.{decimals}f}M"


def label(draw: ImageDraw.ImageDraw, xy, value: str, size: int, color=INK, bold=False, anchor="la", shadow=False) -> None:
    if shadow:
        draw.text((xy[0] + 2, xy[1] + 2), value, fill=(0, 0, 0, 55), font=font(size, bold), anchor=anchor)
    draw.text(xy, value, fill=color, font=font(size, bold), anchor=anchor)


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def vertical_gradient(size, top: str, bottom: str) -> Image.Image:
    w, h = size
    top_rgb, bottom_rgb = rgb(top), rgb(bottom)
    gradient = Image.new("RGBA", (w, h))
    pixels = gradient.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        color = tuple(round(top_rgb[i] * (1 - t) + bottom_rgb[i] * t) for i in range(3)) + (255,)
        for x in range(w):
            pixels[x, y] = color
    return gradient


def raised_box(image: Image.Image, draw: ImageDraw.ImageDraw, box, radius=18, top="#FFFDF8", bottom="#E9E1D4", outline=GOLD, shadow_offset=12) -> None:
    x1, y1, x2, y2 = map(int, box)
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset),
        radius=radius,
        fill=(0, 0, 0, 145),
    )
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    mask = Image.new("L", (x2 - x1, y2 - y1), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, x2 - x1 - 1, y2 - y1 - 1), radius=radius, fill=255)
    image.paste(vertical_gradient((x2 - x1, y2 - y1), top, bottom), (x1, y1), mask)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, outline=outline, width=3)
    draw.line((x1 + radius, y1 + 3, x2 - radius, y1 + 3), fill=BEVEL_LIGHT, width=4)
    draw.line((x1 + 3, y1 + radius, x1 + 3, y2 - radius), fill=BEVEL_LIGHT, width=4)
    draw.line((x1 + radius, y2 - 3, x2 - radius, y2 - 3), fill=BEVEL_DARK, width=4)
    draw.line((x2 - 3, y1 + radius, x2 - 3, y2 - radius), fill=BEVEL_DARK, width=4)


def panel(image: Image.Image, draw: ImageDraw.ImageDraw, box, title: str) -> tuple[int, int, int, int]:
    raised_box(image, draw, box, radius=20, top="#FFFDF8", bottom="#EDE5D9", outline="#D2B46B")
    x1, y1, x2, y2 = box
    label(draw, (x1 + 30, y1 + 24), title, 27, INK, True)
    return x1 + 34, y1 + 82, x2 - 28, y2 - 32


def horizontal_bars(draw, box, rows, name_col, value_col, color) -> None:
    x1, y1, x2, y2 = box
    values = rows[value_col].astype(float).tolist()
    names = rows[name_col].astype(str).tolist()
    maximum = max(values) if values else 1
    row_h = (y2 - y1) / max(len(rows), 1)
    label_w = min(240, int((x2 - x1) * 0.31))
    bar_x = x1 + label_w
    for i, (name, value) in enumerate(zip(names, values)):
        cy = y1 + row_h * (i + 0.5)
        bh = min(30, row_h * 0.52)
        label(draw, (bar_x - 15, cy), name, 19, MUTED, False, "ra")
        draw.rounded_rectangle((bar_x + 5, cy - bh / 2 + 7, x2 + 5, cy + bh / 2 + 7), radius=8, fill="#B4B7BC")
        draw.rounded_rectangle((bar_x, cy - bh / 2, x2, cy + bh / 2), radius=8, fill="#E7E9EC")
        fill_x = bar_x + (x2 - bar_x) * value / maximum
        draw.rounded_rectangle((bar_x + 5, cy - bh / 2 + 7, fill_x + 5, cy + bh / 2 + 7), radius=8, fill=BEVEL_DARK)
        draw.rounded_rectangle((bar_x, cy - bh / 2, fill_x, cy + bh / 2), radius=8, fill=color)
        draw.line((bar_x + 8, cy - bh / 2 + 4, max(bar_x + 8, fill_x - 8), cy - bh / 2 + 4), fill=BEVEL_LIGHT, width=3)
        value_x = min(fill_x + 12, x2 - 3)
        anchor = "ra" if value_x >= x2 - 25 else "la"
        label(draw, (value_x, cy), money_m(value, 2), 17, INK, True, anchor)


def line_chart(draw, box, rows) -> None:
    x1, y1, x2, y2 = box
    left, top, right, bottom = x1 + 84, y1 + 20, x2 - 18, y2 - 54
    max_value = rows["Net_Revenue_GBP"].max() * 1.12
    for i in range(5):
        gy = top + (bottom - top) * i / 4
        draw.line((left, gy, right, gy), fill=GRID, width=2)
        axis_value = max_value * (4 - i) / 4
        label(draw, (left - 12, gy), f"£{axis_value / 1000:.0f}k", 17, MUTED, False, "ra")

    def points(column):
        vals = rows[column].tolist()
        return [
            (
                left + (right - left) * idx / max(len(vals) - 1, 1),
                bottom - (bottom - top) * value / max_value,
            )
            for idx, value in enumerate(vals)
        ]

    revenue_points = points("Net_Revenue_GBP")
    profit_points = points("Gross_Profit_GBP")
    draw.line([(x + 5, y + 7) for x, y in revenue_points], fill="#66552E", width=9, joint="curve")
    draw.line([(x + 5, y + 7) for x, y in profit_points], fill="#40576F", width=8, joint="curve")
    draw.line(revenue_points, fill=GOLD, width=7, joint="curve")
    draw.line(profit_points, fill=BLUE, width=6, joint="curve")
    for idx in range(0, len(rows), 4):
        x = left + (right - left) * idx / max(len(rows) - 1, 1)
        label(draw, (x, bottom + 28), rows.iloc[idx]["Month_Start"].strftime("%b\n%Y"), 16, MUTED, anchor="ma")
    draw.rounded_rectangle((left, top - 2, left + 34, top + 10), radius=5, fill=GOLD)
    label(draw, (left + 46, top + 4), "Net Revenue", 17, INK, True, "lm")
    draw.rounded_rectangle((left + 210, top - 2, left + 244, top + 10), radius=5, fill=BLUE)
    label(draw, (left + 256, top + 4), "Gross Profit", 17, INK, True, "lm")


df = pd.read_csv(SOURCE, parse_dates=["Order_Date", "Month_Start"])

revenue = df["Net_Revenue_GBP"].sum()
gross_profit = df["Gross_Profit_GBP"].sum()
units = int(df["Units_Sold"].sum())
target = df["Sales_Target_GBP"].sum()
margin = gross_profit / revenue
target_achievement = revenue / target

max_date = df["Order_Date"].max()
current = df.loc[
    (df["Order_Date"] >= pd.Timestamp(max_date.year, 1, 1)) & (df["Order_Date"] <= max_date),
    "Net_Revenue_GBP",
].sum()
prior = df.loc[
    (df["Order_Date"] >= pd.Timestamp(max_date.year - 1, 1, 1))
    & (df["Order_Date"] <= max_date - pd.DateOffset(years=1)),
    "Net_Revenue_GBP",
].sum()
yoy = current / prior - 1

monthly = (
    df.groupby("Month_Start", as_index=False)
    .agg(Net_Revenue_GBP=("Net_Revenue_GBP", "sum"), Gross_Profit_GBP=("Gross_Profit_GBP", "sum"))
    .sort_values("Month_Start")
)
brand = df.groupby("Brand", as_index=False).agg(Net_Revenue_GBP=("Net_Revenue_GBP", "sum")).sort_values("Net_Revenue_GBP")
country = (
    df.groupby("Country", as_index=False)
    .agg(Net_Revenue_GBP=("Net_Revenue_GBP", "sum"))
    .nlargest(8, "Net_Revenue_GBP")
    .sort_values("Net_Revenue_GBP")
)
channel = (
    df.groupby("Channel", as_index=False)
    .agg(Net_Revenue_GBP=("Net_Revenue_GBP", "sum"), Gross_Profit_GBP=("Gross_Profit_GBP", "sum"))
    .sort_values("Net_Revenue_GBP")
)
category = (
    df.groupby("Category", as_index=False)
    .agg(Net_Revenue_GBP=("Net_Revenue_GBP", "sum"), Gross_Profit_GBP=("Gross_Profit_GBP", "sum"))
    .sort_values("Net_Revenue_GBP")
)
promotion = df.groupby("Promotion_Flag", as_index=False).agg(
    Transactions=("Transaction_ID", "nunique"),
    Revenue=("Net_Revenue_GBP", "sum"),
    Gross_Profit=("Gross_Profit_GBP", "sum"),
)
promotion["Revenue_per_Tx"] = promotion["Revenue"] / promotion["Transactions"]
promotion["GP_per_Tx"] = promotion["Gross_Profit"] / promotion["Transactions"]
promotion["Margin"] = promotion["Gross_Profit"] / promotion["Revenue"]

image = vertical_gradient((WIDTH, HEIGHT), "#07101D", "#142844")
draw = ImageDraw.Draw(image)

label(draw, (70, 58), "DIAGEO  GLOBAL SALES PERFORMANCE", 54, WHITE, True, shadow=True)
label(draw, (72, 122), "Synthetic Commercial Analytics Portfolio | 2023–2026 | Data through 31 Aug 2026", 25, "#CED7E2")

kpis = [
    ("TOTAL NET REVENUE", money_m(revenue), INK),
    ("GROSS PROFIT", money_m(gross_profit), INK),
    ("PROFIT MARGIN", f"{margin:.1%}", INK),
    ("UNITS SOLD", f"{units / 1000:.0f}K", INK),
    ("TARGET ACHIEVEMENT", f"{target_achievement:.1%}", RED if target_achievement < 1 else TEAL),
    ("YOY REVENUE GROWTH (YTD)", f"{yoy:+.1%}", TEAL if yoy >= 0 else RED),
]
gap = 24
card_w = (WIDTH - 140 - gap * 5) // 6
for idx, (title, value, color) in enumerate(kpis):
    x1 = 70 + idx * (card_w + gap)
    x2 = x1 + card_w
    raised_box(image, draw, (x1, 180, x2, 330), radius=20, top="#FFFDF5", bottom="#E6D7B8", outline=GOLD, shadow_offset=11)
    label(draw, ((x1 + x2) / 2, 225), title, 18, MUTED, True, "ma")
    label(draw, ((x1 + x2) / 2, 282), value, 37, color, True, "mm")

trend_box = (70, 360, 1700, 940)
brand_box = (1725, 360, 2730, 940)
country_box = (70, 970, 900, 1450)
channel_box = (925, 970, 1810, 1450)
category_box = (1835, 970, 2730, 1450)
line_chart(draw, panel(image, draw, trend_box, "Revenue & Profit Trend"), monthly)
horizontal_bars(draw, panel(image, draw, brand_box, "Brand Performance"), brand, "Brand", "Net_Revenue_GBP", GOLD)
horizontal_bars(draw, panel(image, draw, country_box, "Top Markets by Revenue"), country, "Country", "Net_Revenue_GBP", BLUE)
horizontal_bars(draw, panel(image, draw, channel_box, "Revenue by Sales Channel"), channel, "Channel", "Net_Revenue_GBP", GOLD)
horizontal_bars(draw, panel(image, draw, category_box, "Sales by Category"), category, "Category", "Net_Revenue_GBP", BLUE)

raised_box(image, draw, (70, 1480, 2730, 1620), radius=20, top="#FFFDF8", bottom="#E8DED0", outline="#D2B46B")
label(draw, (100, 1510), "Promotion Impact — observed association, not causality", 26, INK, True)
no = promotion.loc[promotion["Promotion_Flag"] == "No"].iloc[0]
yes = promotion.loc[promotion["Promotion_Flag"] == "Yes"].iloc[0]
no_text = f"NO PROMOTION   Revenue / transaction £{no['Revenue_per_Tx']:,.0f}   |   GP / transaction £{no['GP_per_Tx']:,.0f}   |   Margin {no['Margin']:.1%}"
yes_text = f"PROMOTION   Revenue / transaction £{yes['Revenue_per_Tx']:,.0f}   |   GP / transaction £{yes['GP_per_Tx']:,.0f}   |   Margin {yes['Margin']:.1%}"
label(draw, (100, 1570), no_text, 21, INK)
label(draw, (1460, 1570), yes_text, 21, INK)

label(draw, (WIDTH / 2, 1660), "Synthetic portfolio dataset — not official Diageo sales data.", 20, "#CED7E2", False, "ma")
image.convert("RGB").save(OUTPUT, quality=95)
print(OUTPUT)
