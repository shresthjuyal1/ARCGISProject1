"""Generate the README figure from the land-cover temperatures in the report.

Uses only the Python standard library and writes an SVG to figures/.
Values are the median land surface temperatures in
report/landsat_thermal_analysis.pdf.

    python3 scripts/make_figures.py
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "figures"

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
INK, MUTED, GRID = "#1f2328", "#656d76", "#d0d7de"

# (land cover, median surface temperature in deg C)
LAND_COVER = [
    ("Urban", 35.2304),
    ("Suburban", 27.2136),
    ("Fallow agriculture", 26.5264),
    ("Agriculture with crops", 18.4168),
    ("Forest", 13.3786),
    ("Water", 11.4806),
]
SCENE_MEAN = 15.81

# Cool-to-hot ramp, interpolated by temperature
RAMP = [(10, (9, 105, 218)), (20, (191, 135, 0)), (36, (207, 34, 46))]


def color_for(t):
    for (t0, c0), (t1, c1) in zip(RAMP, RAMP[1:]):
        if t <= t1:
            f = max(0.0, (t - t0) / (t1 - t0))
            return "#" + "".join(f"{round(a + (b - a) * f):02x}" for a, b in zip(c0, c1))
    return "#" + "".join(f"{c:02x}" for c in RAMP[-1][1])


def text(x, y, s, size=13, fill=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>\n')


def land_cover_chart():
    width, row_h = 820, 44
    left, right, top = 200, 720, 92
    height = top + row_h * len(LAND_COVER) + 56
    t_max = 40

    def px(v):
        return left + v / t_max * (right - left)

    body = text(24, 34, "Surface temperature by land cover", 18, weight="600")
    body += text(24, 56, "Median land surface temperature, Landsat thermal band, 25 May 2023, Mississauga / Greater Toronto.", 12, MUTED)

    axis_y = top + row_h * len(LAND_COVER)
    for t in range(0, t_max + 1, 10):
        body += f'<line x1="{px(t):.1f}" y1="{top - 6}" x2="{px(t):.1f}" y2="{axis_y}" stroke="{GRID}"/>\n'
        body += text(px(t), axis_y + 18, f"{t} °C", 11, MUTED, "middle")

    mean_x = px(SCENE_MEAN)
    # Draw the mean line row by row, leaving a gap wherever it would cross a value label.
    body += f'<line x1="{mean_x:.1f}" y1="{top - 20}" x2="{mean_x:.1f}" y2="{top}" stroke="{INK}" stroke-dasharray="4,3"/>\n'
    for i, (_, t) in enumerate(LAND_COVER):
        label_lo, label_hi = px(t) + 4, px(t) + 72
        if not label_lo <= mean_x <= label_hi:
            y0 = top + i * row_h
            body += f'<line x1="{mean_x:.1f}" y1="{y0}" x2="{mean_x:.1f}" y2="{y0 + row_h}" stroke="{INK}" stroke-dasharray="4,3"/>\n'
    body += text(mean_x + 5, top - 10, f"scene mean {SCENE_MEAN:.1f} °C", 11, INK)

    for i, (name, t) in enumerate(LAND_COVER):
        y = top + i * row_h + 8
        color = color_for(t)
        body += f'<rect x="{left}" y="{y}" width="{px(t) - left:.1f}" height="{row_h - 16}" fill="{color}" rx="3"/>\n'
        cy = y + (row_h - 16) / 2 + 5
        body += text(left - 12, cy, name, 13, INK, "end")
        body += text(px(t) + 8, cy, f"{t:.1f} °C", 13, color, weight="600")

    body += text(24, height - 14, "Urban surfaces were ~24 °C hotter than open water at the time of the overpass.", 12, MUTED)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="{FONT}">\n'
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>\n{body}</svg>\n')


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "land_cover_temperature.svg").write_text(land_cover_chart())
    print(f"Wrote figures to {OUT}")


if __name__ == "__main__":
    main()
