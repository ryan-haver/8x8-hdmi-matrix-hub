"""Generate clean, code-authored, in-house vector line icons for all 57 device icons.

Owned under WP-G1 / UI-22.
Replaces the old unlicensed potrace sprite traces with 100% original line vector artwork
under MPL-2.0, preserving filenames, viewBox="0 0 1024 1024", fill="currentColor",
and strict size budget (< 5,120 bytes per file).
"""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = REPO_ROOT / "web" / "assets" / "icons" / "svg"
ICON_PATHS_JSON = ICONS_DIR / "_icon-paths.json"
MAX_BUDGET = 5120


def r_rect(x: float, y: float, w: float, h: float, rx: float = 0) -> str:
    """Return path for a solid rectangle, optionally with rounded corners."""
    if rx <= 0:
        return f"M{x:.1f} {y:.1f}h{w:.1f}v{h:.1f}h{-w:.1f}Z"
    r = min(rx, w / 2, h / 2)
    return (
        f"M{x + r:.1f} {y:.1f}"
        f"h{w - 2 * r:.1f}"
        f"a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {r:.1f}"
        f"v{h - 2 * r:.1f}"
        f"a{r:.1f} {r:.1f} 0 0 1 {-r:.1f} {r:.1f}"
        f"h{-(w - 2 * r):.1f}"
        f"a{r:.1f} {r:.1f} 0 0 1 {-r:.1f} {-r:.1f}"
        f"v{-(h - 2 * r):.1f}"
        f"a{r:.1f} {r:.1f} 0 0 1 {r:.1f} {-r:.1f}"
        f"Z"
    )


def r_stroke_rect(x: float, y: float, w: float, h: float, s: float = 24, rx: float = 0) -> str:
    """Return path for a stroked rectangle border."""
    outer = r_rect(x, y, w, h, rx)
    inner_rx = max(0.0, rx - s)
    inner = r_rect(x + s, y + s, w - 2 * s, h - 2 * s, inner_rx)
    return f"{outer} {inner}"


def r_circle(cx: float, cy: float, r: float) -> str:
    """Return path for a solid circle."""
    return (
        f"M{cx - r:.1f} {cy:.1f}"
        f"a{r:.1f} {r:.1f} 0 1 0 {2 * r:.1f} 0"
        f"a{r:.1f} {r:.1f} 0 1 0 {-2 * r:.1f} 0"
        f"Z"
    )


def r_stroke_circle(cx: float, cy: float, r: float, s: float = 24) -> str:
    """Return path for a stroked circular ring."""
    outer = r_circle(cx, cy, r)
    inner = r_circle(cx, cy, max(1.0, r - s))
    return f"{outer} {inner}"


def r_line(x1: float, y1: float, x2: float, y2: float, s: float = 24) -> str:
    """Return path for a stroked line segment with rounded caps."""
    dx = x2 - x1
    dy = y2 - y1
    dist = (dx * dx + dy * dy) ** 0.5
    if dist < 1e-4:
        return r_circle(x1, y1, s / 2)
    ux = dx / dist
    uy = dy / dist
    px = -uy * (s / 2)
    py = ux * (s / 2)
    r = s / 2
    return (
        f"M{x1 + px:.1f} {y1 + py:.1f}"
        f"L{x2 + px:.1f} {y2 + py:.1f}"
        f"a{r:.1f} {r:.1f} 0 0 1 {2 * -px:.1f} {2 * -py:.1f}"
        f"L{x1 - px:.1f} {y1 - py:.1f}"
        f"a{r:.1f} {r:.1f} 0 0 1 {2 * px:.1f} {2 * py:.1f}"
        f"Z"
    )


def build_icon_paths() -> dict[str, str]:
    """Build original code-authored vector paths for all 57 device icons."""
    paths: dict[str, str] = {}

    # 1. Television
    paths["television"] = " ".join([
        r_stroke_rect(120, 180, 784, 490, s=28, rx=24),
        r_rect(480, 670, 64, 120),
        r_rect(340, 790, 344, 30, rx=15),
        r_circle(512, 636, 8),
    ])

    # 2. Curved TV
    paths["curved_tv"] = " ".join([
        r_stroke_rect(140, 200, 744, 470, s=28, rx=40),
        r_line(260, 670, 210, 790, s=28),
        r_line(764, 670, 814, 790, s=28),
        r_line(300, 700, 724, 700, s=18),
    ])

    # 3. Monitor
    paths["monitor"] = " ".join([
        r_stroke_rect(140, 160, 744, 470, s=28, rx=20),
        r_rect(480, 630, 64, 150),
        r_rect(360, 780, 304, 28, rx=14),
    ])

    # 4. Projector
    paths["projector"] = " ".join([
        r_stroke_rect(160, 360, 704, 290, s=28, rx=32),
        r_stroke_circle(360, 505, 95, s=22),
        r_circle(360, 505, 45),
        r_line(600, 420, 780, 420, s=18),
        r_line(600, 470, 780, 470, s=18),
        r_line(600, 520, 780, 520, s=18),
        r_rect(240, 650, 60, 24, rx=10),
        r_rect(724, 650, 60, 24, rx=10),
    ])

    # 5. Soundbar
    paths["soundbar"] = " ".join([
        r_stroke_rect(100, 430, 824, 164, s=24, rx=24),
        r_stroke_rect(460, 480, 104, 64, s=16, rx=10),
        r_line(160, 512, 400, 512, s=16),
        r_line(624, 512, 864, 512, s=16),
    ])

    # 6. AV Receiver
    paths["av_receiver"] = " ".join([
        r_stroke_rect(130, 250, 764, 524, s=28, rx=24),
        r_stroke_rect(320, 320, 384, 120, s=20, rx=12),
        r_stroke_circle(230, 480, 56, s=18),
        r_stroke_circle(794, 480, 56, s=18),
        r_circle(230, 640, 20),
        r_line(360, 640, 664, 640, s=20),
    ])

    # 7. Speaker
    paths["speaker"] = " ".join([
        r_stroke_rect(260, 150, 504, 724, s=28, rx=24),
        r_stroke_circle(512, 330, 75, s=20),
        r_circle(512, 330, 30),
        r_stroke_circle(512, 620, 150, s=26),
        r_circle(512, 620, 55),
    ])

    # 8. Subwoofer
    paths["subwoofer"] = " ".join([
        r_stroke_rect(180, 180, 664, 664, s=28, rx=24),
        r_stroke_circle(512, 470, 200, s=28),
        r_circle(512, 470, 80),
        r_stroke_circle(512, 740, 44, s=18),
    ])

    # 9. Headphones
    paths["headphones"] = " ".join([
        r_stroke_circle(512, 460, 270, s=32),
        r_rect(180, 440, 120, 240, rx=40),
        r_rect(724, 440, 120, 240, rx=40),
        r_rect(260, 480, 40, 160, rx=16),
        r_rect(724, 480, 40, 160, rx=16),
        r_rect(120, 710, 784, 200),  # subtract bottom half of circle
    ])

    # 10. Turntable
    paths["turntable"] = " ".join([
        r_stroke_rect(150, 240, 724, 544, s=28, rx=24),
        r_stroke_circle(420, 512, 190, s=24),
        r_circle(420, 512, 40),
        r_circle(740, 350, 34),
        r_line(740, 350, 580, 600, s=20),
        r_circle(230, 690, 24),
        r_circle(300, 690, 16),
    ])

    # 11. PlayStation 5
    paths["playstation_5"] = " ".join([
        r_stroke_rect(380, 140, 264, 744, s=28, rx=36),
        r_line(450, 180, 450, 840, s=16),
        r_line(574, 180, 574, 840, s=16),
        r_line(512, 220, 512, 800, s=24),
        r_circle(512, 200, 12),
        r_rect(320, 850, 384, 34, rx=16),
    ])

    # 12. Xbox Series X
    paths["xbox_series_x"] = " ".join([
        r_stroke_rect(310, 160, 404, 704, s=28, rx=16),
        r_line(360, 220, 664, 220, s=18),
        r_line(370, 460, 370, 700, s=18),
        r_circle(370, 290, 20),
        r_circle(650, 760, 14),
    ])

    # 13. Nintendo Switch
    paths["nintendo_switch"] = " ".join([
        r_stroke_rect(320, 270, 384, 484, s=24, rx=16),
        r_stroke_rect(170, 270, 130, 484, s=24, rx=40),
        r_stroke_rect(724, 270, 130, 484, s=24, rx=40),
        r_circle(235, 380, 28),
        r_circle(789, 580, 28),
        r_circle(789, 360, 16),
        r_circle(789, 410, 16),
        r_circle(764, 385, 16),
        r_circle(814, 385, 16),
        r_circle(235, 560, 16),
        r_circle(235, 610, 16),
        r_circle(210, 585, 16),
        r_circle(260, 585, 16),
    ])

    # 14. Steam Deck
    paths["steam_deck"] = " ".join([
        r_stroke_rect(130, 270, 764, 484, s=28, rx=50),
        r_stroke_rect(330, 330, 364, 364, s=22, rx=12),
        r_circle(230, 410, 32),
        r_circle(794, 410, 32),
        r_stroke_rect(205, 520, 60, 60, s=14, rx=8),
        r_stroke_rect(759, 520, 60, 60, s=14, rx=8),
    ])

    # 15. Wii
    paths["wii"] = " ".join([
        r_stroke_rect(370, 180, 200, 664, s=26, rx=16),
        r_line(470, 280, 470, 680, s=18),
        r_circle(470, 240, 18),
        r_circle(470, 740, 14),
        r_line(300, 840, 660, 840, s=24),
    ])

    # 16. NES Console
    paths["nes_console"] = " ".join([
        r_stroke_rect(170, 300, 684, 424, s=28, rx=16),
        r_line(170, 480, 854, 480, s=20),
        r_rect(240, 360, 280, 70, rx=8),
        r_circle(680, 580, 20),
        r_circle(760, 580, 20),
        r_line(240, 580, 360, 580, s=18),
        r_line(420, 580, 540, 580, s=18),
    ])

    # 17. SNES Console
    paths["snes_console"] = " ".join([
        r_stroke_rect(180, 280, 664, 464, s=28, rx=28),
        r_stroke_rect(300, 340, 424, 140, s=20, rx=14),
        r_line(250, 540, 350, 540, s=22),
        r_line(674, 540, 774, 540, s=22),
        r_circle(450, 620, 24),
        r_circle(574, 620, 24),
    ])

    # 18. Nintendo 64
    paths["n64"] = " ".join([
        r_stroke_rect(160, 310, 704, 404, s=28, rx=36),
        r_stroke_rect(330, 360, 364, 110, s=20, rx=16),
        r_circle(280, 580, 24),
        r_circle(430, 580, 24),
        r_circle(594, 580, 24),
        r_circle(744, 580, 24),
    ])

    # 19. GameCube
    paths["gamecube"] = " ".join([
        r_stroke_rect(240, 240, 544, 544, s=28, rx=32),
        r_stroke_circle(512, 440, 120, s=22),
        r_circle(512, 440, 40),
        r_circle(360, 660, 24),
        r_circle(460, 660, 24),
        r_circle(564, 660, 24),
        r_circle(664, 660, 24),
    ])

    # 20. Sega Genesis
    paths["sega_genesis"] = " ".join([
        r_stroke_rect(160, 280, 704, 464, s=28, rx=24),
        r_stroke_circle(450, 480, 130, s=22),
        r_line(360, 480, 540, 480, s=18),
        r_line(700, 380, 780, 380, s=20),
        r_line(700, 440, 780, 440, s=20),
        r_circle(280, 620, 22),
        r_circle(380, 620, 22),
    ])

    # 21. Dreamcast
    paths["dreamcast"] = " ".join([
        r_stroke_rect(200, 240, 624, 544, s=28, rx=32),
        r_stroke_circle(512, 460, 140, s=22),
        r_circle(512, 300, 16),
        r_circle(320, 670, 22),
        r_circle(440, 670, 22),
        r_circle(584, 670, 22),
        r_circle(704, 670, 22),
    ])

    # 22. Atari 2600
    paths["atari_2600"] = " ".join([
        r_stroke_rect(150, 300, 724, 424, s=28, rx=16),
        r_line(150, 460, 874, 460, s=24),
        r_line(260, 360, 764, 360, s=16),
        r_line(260, 400, 764, 400, s=16),
        r_circle(320, 560, 20),
        r_circle(420, 560, 20),
        r_circle(604, 560, 20),
        r_circle(704, 560, 20),
    ])

    # 23. PS2
    paths["ps2"] = " ".join([
        r_stroke_rect(190, 280, 644, 464, s=28, rx=14),
        r_line(190, 420, 834, 420, s=20),
        r_line(190, 560, 834, 560, s=20),
        r_rect(260, 330, 280, 44, rx=8),
        r_circle(740, 350, 20),
        r_circle(740, 640, 16),
    ])

    # 24. PS3
    paths["ps3"] = " ".join([
        r_stroke_rect(180, 290, 664, 444, s=28, rx=48),
        r_line(260, 420, 764, 420, s=20),
        r_circle(280, 560, 24),
        r_line(360, 560, 680, 560, s=18),
    ])

    # 25. PS4
    paths["ps4"] = " ".join([
        r_stroke_rect(180, 300, 664, 424, s=28, rx=12),
        r_line(180, 470, 844, 470, s=22),
        r_circle(260, 560, 20),
        r_line(340, 560, 540, 560, s=18),
        r_circle(760, 390, 18),
    ])

    # 26. Xbox 360
    paths["xbox_360"] = " ".join([
        r_stroke_rect(330, 160, 364, 704, s=28, rx=36),
        r_stroke_circle(512, 340, 55, s=18),
        r_line(420, 500, 604, 500, s=20),
        r_circle(512, 680, 20),
    ])

    # 27. Xbox One
    paths["xbox_one"] = " ".join([
        r_stroke_rect(160, 310, 704, 404, s=28, rx=14),
        r_line(512, 310, 512, 714, s=22),
        r_line(240, 450, 440, 450, s=18),
        r_circle(780, 430, 20),
    ])

    # 28. Xbox Controller
    paths["xbox_controller"] = " ".join([
        r_stroke_rect(170, 270, 684, 484, s=32, rx=70),
        r_circle(330, 420, 40),
        r_circle(694, 540, 40),
        r_stroke_rect(310, 520, 40, 40, s=14, rx=6),
        r_circle(674, 380, 18),
        r_circle(714, 420, 18),
        r_circle(674, 460, 18),
        r_circle(634, 420, 18),
        r_circle(512, 370, 24),
    ])

    # 29. PS Controller
    paths["ps_controller"] = " ".join([
        r_stroke_rect(170, 270, 684, 484, s=32, rx=70),
        r_circle(410, 560, 44),
        r_circle(614, 560, 44),
        r_circle(300, 420, 18),
        r_circle(340, 420, 18),
        r_circle(320, 400, 18),
        r_circle(320, 440, 18),
        r_circle(724, 420, 18),
        r_circle(684, 420, 18),
        r_circle(704, 400, 18),
        r_circle(704, 440, 18),
        r_stroke_rect(440, 340, 144, 80, s=16, rx=8),
    ])

    # 30. Apple TV
    paths["apple_tv"] = " ".join([
        r_stroke_rect(240, 280, 544, 464, s=28, rx=48),
        r_circle(512, 460, 60),
        r_line(460, 540, 564, 540, s=18),
        r_circle(512, 680, 12),
    ])

    # 31. Roku Stick
    paths["roku_stick"] = " ".join([
        r_stroke_rect(320, 250, 384, 544, s=28, rx=24),
        r_rect(432, 140, 160, 110, rx=10),
        r_line(400, 400, 624, 400, s=20),
        r_line(400, 480, 624, 480, s=20),
        r_circle(512, 660, 16),
    ])

    # 32. Fire TV
    paths["fire_tv"] = " ".join([
        r_stroke_rect(310, 270, 404, 504, s=28, rx=32),
        r_rect(432, 160, 160, 110, rx=10),
        r_stroke_circle(512, 480, 80, s=20),
        r_circle(512, 480, 30),
        r_circle(512, 680, 14),
    ])

    # 33. Chromecast
    paths["chromecast"] = " ".join([
        r_stroke_circle(512, 560, 210, s=28),
        r_line(512, 350, 512, 220, s=28),
        r_rect(432, 120, 160, 110, rx=10),
        r_stroke_circle(512, 560, 90, s=20),
    ])

    # 34. NVIDIA Shield
    paths["nvidia_shield"] = " ".join([
        r_stroke_rect(190, 290, 644, 444, s=28, rx=24),
        r_line(280, 550, 512, 360, s=24),
        r_line(512, 360, 744, 550, s=24),
        r_circle(512, 610, 18),
    ])

    # 35. Blu-ray Player
    paths["bluray_player"] = " ".join([
        r_stroke_rect(130, 390, 764, 244, s=28, rx=16),
        r_rect(220, 480, 280, 20, rx=8),
        r_stroke_rect(560, 460, 180, 60, s=16, rx=8),
        r_circle(800, 490, 18),
    ])

    # 36. Cable Box
    paths["cable_box"] = " ".join([
        r_stroke_rect(130, 380, 764, 264, s=28, rx=18),
        r_stroke_rect(240, 450, 260, 80, s=18, rx=10),
        r_circle(620, 490, 18),
        r_circle(690, 490, 18),
        r_circle(760, 490, 18),
    ])

    # 37. Gaming PC
    paths["gaming_pc"] = " ".join([
        r_stroke_rect(260, 140, 504, 744, s=28, rx=24),
        r_stroke_rect(330, 240, 364, 524, s=22, rx=16),
        r_circle(512, 380, 70),
        r_circle(512, 600, 70),
        r_circle(660, 185, 14),
    ])

    # 38. Laptop
    paths["laptop"] = " ".join([
        r_stroke_rect(220, 180, 584, 420, s=24, rx=16),
        r_rect(100, 680, 824, 70, rx=16),
        r_stroke_rect(420, 700, 184, 34, s=12, rx=6),
    ])

    # 39. Mac mini
    paths["mac_mini"] = " ".join([
        r_stroke_rect(220, 360, 584, 304, s=28, rx=48),
        r_circle(512, 590, 10),
        r_circle(512, 470, 36),
    ])

    # 40. HTPC
    paths["htpc"] = " ".join([
        r_stroke_rect(150, 320, 724, 384, s=28, rx=20),
        r_stroke_circle(280, 512, 70, s=20),
        r_stroke_rect(420, 450, 340, 120, s=18, rx=10),
        r_circle(814, 512, 18),
    ])

    # 41. HDMI Switch
    paths["hdmi_switch"] = " ".join([
        r_stroke_rect(120, 350, 784, 324, s=28, rx=16),
        r_circle(220, 440, 16),
        r_circle(300, 440, 16),
        r_circle(380, 440, 16),
        r_circle(460, 440, 16),
        r_circle(220, 560, 16),
        r_circle(300, 560, 16),
        r_circle(380, 560, 16),
        r_circle(460, 560, 16),
        r_stroke_rect(580, 430, 240, 140, s=18, rx=10),
    ])

    # 42. Server Rack
    paths["server_rack"] = " ".join([
        r_stroke_rect(220, 120, 584, 784, s=28, rx=16),
        r_stroke_rect(280, 200, 464, 120, s=18, rx=8),
        r_stroke_rect(280, 360, 464, 120, s=18, rx=8),
        r_stroke_rect(280, 520, 464, 120, s=18, rx=8),
        r_stroke_rect(280, 680, 464, 120, s=18, rx=8),
        r_circle(680, 260, 12),
        r_circle(680, 420, 12),
        r_circle(680, 580, 12),
        r_circle(680, 740, 12),
    ])

    # 43. Security Camera
    paths["security_camera"] = " ".join([
        r_stroke_rect(340, 340, 444, 224, s=26, rx=32),
        r_stroke_circle(720, 452, 60, s=20),
        r_circle(720, 452, 24),
        r_line(420, 564, 300, 720, s=26),
        r_rect(220, 700, 180, 40, rx=12),
    ])

    # 44. Movie Scene
    paths["movie_scene"] = " ".join([
        r_stroke_rect(200, 320, 624, 464, s=28, rx=20),
        r_stroke_rect(200, 220, 624, 90, s=22, rx=12),
        r_line(340, 220, 380, 310, s=18),
        r_line(500, 220, 540, 310, s=18),
        r_line(660, 220, 700, 310, s=18),
        r_line(280, 440, 744, 440, s=20),
        r_line(280, 540, 744, 540, s=20),
        r_line(280, 640, 540, 640, s=20),
    ])

    # 45. Gaming Scene
    paths["gaming_scene"] = " ".join([
        r_stroke_rect(220, 340, 584, 364, s=28, rx=50),
        r_circle(360, 460, 34),
        r_circle(664, 540, 34),
        r_circle(644, 430, 16),
        r_circle(684, 470, 16),
        r_line(512, 140, 512, 260, s=24),
        r_line(260, 200, 340, 290, s=24),
        r_line(764, 200, 684, 290, s=24),
    ])

    # 46. Sports Scene
    paths["sports_scene"] = " ".join([
        r_stroke_circle(512, 512, 300, s=28),
        r_stroke_circle(512, 512, 160, s=22),
        r_line(212, 512, 812, 512, s=24),
        r_line(512, 212, 512, 812, s=24),
    ])

    # 47. Music Scene
    paths["music_scene"] = " ".join([
        r_circle(340, 680, 60),
        r_circle(684, 600, 60),
        r_line(380, 680, 380, 280, s=24),
        r_line(724, 600, 724, 220, s=24),
        r_line(380, 280, 734, 220, s=44),
    ])

    # 48. Living Room
    paths["living_room"] = " ".join([
        r_stroke_rect(180, 420, 664, 324, s=28, rx=32),
        r_stroke_rect(140, 480, 110, 264, s=24, rx=24),
        r_stroke_rect(774, 480, 110, 264, s=24, rx=24),
        r_line(512, 420, 512, 744, s=20),
        r_rect(240, 744, 44, 50, rx=10),
        r_rect(740, 744, 44, 50, rx=10),
    ])

    # 49. Bedroom
    paths["bedroom"] = " ".join([
        r_stroke_rect(200, 260, 624, 524, s=28, rx=20),
        r_stroke_rect(200, 180, 624, 100, s=24, rx=12),
        r_stroke_rect(280, 320, 180, 110, s=18, rx=16),
        r_stroke_rect(564, 320, 180, 110, s=18, rx=16),
        r_line(200, 500, 824, 500, s=24),
    ])

    # 50. Office Room
    paths["office_room"] = " ".join([
        r_stroke_rect(320, 180, 384, 264, s=24, rx=14),
        r_line(512, 444, 512, 530, s=20),
        r_line(160, 540, 864, 540, s=28),
        r_line(220, 540, 220, 800, s=24),
        r_line(804, 540, 804, 800, s=24),
    ])

    # 51. Game Room
    paths["game_room"] = " ".join([
        r_stroke_rect(260, 160, 504, 724, s=28, rx=32),
        r_stroke_rect(320, 220, 384, 80, s=20, rx=10),
        r_stroke_rect(320, 350, 384, 230, s=22, rx=14),
        r_circle(420, 680, 26),
        r_circle(580, 660, 18),
        r_circle(640, 690, 18),
    ])

    # 52. Generic Device
    paths["generic_device"] = " ".join([
        r_stroke_rect(180, 320, 664, 384, s=28, rx=24),
        r_stroke_circle(320, 512, 48, s=16),
        r_circle(640, 512, 16),
        r_circle(720, 512, 16),
    ])

    # 53. Generic Input
    paths["generic_input"] = " ".join([
        r_stroke_rect(220, 300, 400, 424, s=28, rx=20),
        r_rect(620, 420, 120, 184, rx=12),
        r_line(740, 512, 880, 512, s=28),
        r_line(420, 420, 520, 512, s=24),
        r_line(520, 512, 420, 604, s=24),
    ])

    # 54. Generic Output
    paths["generic_output"] = " ".join([
        r_stroke_rect(160, 300, 400, 424, s=28, rx=20),
        r_line(560, 512, 840, 512, s=28),
        r_line(740, 420, 840, 512, s=24),
        r_line(740, 604, 840, 512, s=24),
    ])

    # 55. Settings Gear
    paths["settings_gear"] = " ".join([
        r_stroke_circle(512, 512, 280, s=56),
        r_circle(512, 512, 90),
        r_rect(472, 160, 80, 90, rx=10),
        r_rect(472, 774, 80, 90, rx=10),
        r_rect(160, 472, 90, 80, rx=10),
        r_rect(774, 472, 90, 80, rx=10),
        r_rect(260, 260, 80, 80, rx=10),
        r_rect(684, 684, 80, 80, rx=10),
        r_rect(684, 260, 80, 80, rx=10),
        r_rect(260, 684, 80, 80, rx=10),
    ])

    # 56. Tablet
    paths["tablet"] = " ".join([
        r_stroke_rect(220, 140, 584, 744, s=28, rx=36),
        r_stroke_rect(270, 200, 484, 584, s=18, rx=14),
        r_circle(512, 830, 16),
        r_circle(512, 170, 8),
    ])

    # 57. Device Icons Set (Matrix Switch Symbol)
    paths["device_icons_set.png"] = " ".join([
        r_stroke_rect(160, 160, 704, 704, s=28, rx=32),
        r_line(160, 394, 864, 394, s=18),
        r_line(160, 628, 864, 628, s=18),
        r_line(394, 160, 394, 864, s=18),
        r_line(628, 160, 628, 864, s=18),
        r_circle(394, 394, 30),
        r_circle(628, 394, 30),
        r_circle(394, 628, 30),
        r_circle(628, 628, 30),
    ])

    return paths


def generate_all() -> None:
    """Generate all SVG files and _icon-paths.json."""
    icon_paths = build_icon_paths()
    assert len(icon_paths) == 57, f"Expected 57 icons, got {len(icon_paths)}"

    json_data: dict[str, str] = {}

    for name, d in sorted(icon_paths.items()):
        # Normalize name for filename
        fname = f"{name}.svg"
        svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path fill="currentColor" fill-rule="evenodd" d="{d}"/></svg>\n'

        # Verify valid XML
        root = ET.fromstring(svg_content)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.get("viewBox") == "0 0 1024 1024"

        target_file = ICONS_DIR / fname
        target_file.write_text(svg_content, encoding="utf-8")
        file_size = len(target_file.read_bytes())
        assert file_size <= MAX_BUDGET, f"{fname} exceeded budget: {file_size} > {MAX_BUDGET}"

        # Key in json is icon name (without .svg)
        json_data[name] = d

    # Write formatted _icon-paths.json
    ICON_PATHS_JSON.write_text(json.dumps(json_data, indent=2) + "\n", encoding="utf-8")
    json_size = len(ICON_PATHS_JSON.read_bytes())
    print(f"Generated 57 clean SVG icons in {ICONS_DIR}")
    print(f"_icon-paths.json generated ({json_size} bytes)")


if __name__ == "__main__":
    generate_all()
