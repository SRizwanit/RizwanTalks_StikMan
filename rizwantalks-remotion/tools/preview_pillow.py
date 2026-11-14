"""RizwanTalks intro: 10s, 720x720, 30fps. Minimalist stick-figure style.
Run: python3 make_video.py  ->  out/rizwantalks_intro.mp4
"""
import math, os, subprocess, glob
from PIL import Image, ImageDraw, ImageFont, ImageChops

W = H = 720
SS = 2                      # supersampling for smooth lines
FPS, DUR = 30, 10
N = FPS * DUR
GRAY, DARK, INK = (200, 200, 200), (45, 45, 45), (20, 20, 20)

# ---------- font ----------
def find_font():
    for pat in ["Poppins-MediumItalic.ttf", "Poppins-Italic.ttf", "Inter*Italic*"]:
        r = glob.glob("/usr/share/fonts/**/" + pat, recursive=True)
        if r:
            return r[0]
FONT = find_font()

# ---------- timeline (frame ranges) ----------
SHOTS = [  # start, end, caption, camera(cx, cy, zoom), mood
    (0, 12, "", (360, 345, 1.0), "intro"),
    (12, 55, "HELLO!", (360, 345, 1.0), "wave"),
    (55, 100, "WELCOME", (360, 225, 3.0), "happy"),
    (100, 135, "TO", (360, 215, 3.6), "talk"),
    (135, 300, "RIZWANTALKS", (360, 345, 1.0), "reveal"),
]

def ease_out_back(t):
    t = max(0, min(1, t)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def shot_at(f):
    for s in SHOTS:
        if s[0] <= f < s[1]:
            return s
    return SHOTS[-1]

# ---------- drawing ----------
class Cam:
    def __init__(self, cx, cy, z, pop=1.0, dy=0.0):
        self.cx, self.cy, self.z, self.pop, self.dy = cx, cy, z, pop, dy
        self.lw = max(2.2, 2.4 * self.z ** 0.3) * SS
    def p(self, x, y, char=True):
        if char:
            x = (x - 360) * self.pop + 360
            y = (y - 520) * self.pop + 520 + self.dy
        return ((x - self.cx) * self.z + W / 2) * SS, ((y - self.cy) * self.z + H / 2) * SS
    def r(self, v):
        return v * self.z * self.pop * SS

def shaded(img, cam, shape, shift, fill=(255, 255, 255)):
    """fill shape white, add gray crescent (shape minus shifted shape), outline."""
    S = W * SS
    m1 = Image.new("L", (S, S), 0); shape(ImageDraw.Draw(m1), 0, 0, 255)
    m2 = Image.new("L", (S, S), 0)
    sh = cam.r(shift)
    shape(ImageDraw.Draw(m2), sh, -sh * 0.6, 255)
    cres = ImageChops.subtract(m1, m2)
    img.paste(fill, (0, 0), m1)
    img.paste(GRAY, (0, 0), cres)
    d = ImageDraw.Draw(img)
    shape(d, 0, 0, None)  # outline pass

def line(d, cam, pts, w=None):
    P = [cam.p(*q) for q in pts]
    w = int(w or cam.lw)
    d.line(P, fill=INK, width=w, joint="curve")
    for x, y in (P[0], P[-1]):
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=INK)

def draw_char(img, cam, t, f, mood, speaking):
    d = ImageDraw.Draw(img)
    bob = 0
    if mood == "reveal":
        bob = -abs(math.sin(t * math.pi * 1.6)) * 7
    elif mood in ("wave", "talk", "happy"):
        bob = math.sin(t * 6) * 2
    cam.dy += bob

    # ground shadow
    gx, gy = cam.p(360, 520, False)
    rx, ry = cam.r(48), cam.r(5)
    d.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=(222, 222, 222))
    # legs
    line(d, cam, [(342, 428), (342, 516)]); line(d, cam, [(378, 428), (378, 516)])

    # body (rounded dress)
    def body(dr, dx, dy, fill):
        a = cam.p(318, 292); b = cam.p(402, 430)
        dr.rounded_rectangle([a[0] + dx, a[1] + dy, b[0] + dx, b[1] + dy],
                             radius=cam.r(30), corners=(True, True, False, False),
                             fill=fill, outline=INK if fill is None else None, width=int(cam.lw))
    shaded(img, cam, lambda dr, dx, dy, fill: body(dr, dx, dy, fill), 14)
    d = ImageDraw.Draw(img)

    # arms
    ph = t * math.pi * 2
    sL, sR = (322, 312), (398, 312)
    if mood in ("wave", "reveal"):
        ang = 0.55 * math.sin(ph * 2.2)
        elbow = (462, 300)
        hand = (elbow[0] + 56 * math.sin(ang), elbow[1] - 56 * math.cos(ang))
        line(d, cam, [sR, elbow, hand])
    else:
        line(d, cam, [sR, (414, 365), (410, 405)])
    if mood == "reveal":
        ang = -0.55 * math.sin(ph * 2.2 + 1.2)
        elbow = (258, 300)
        hand = (elbow[0] + 56 * math.sin(ang), elbow[1] - 56 * math.cos(ang))
        line(d, cam, [sL, elbow, hand])
    else:
        line(d, cam, [sL, (306, 365), (310, 405)])

    # head
    hx, hy, hr = 360, 225, 70
    def head(dr, dx, dy, fill):
        c = cam.p(hx, hy); r = cam.r(hr)
        dr.ellipse([c[0] - r + dx, c[1] - r + dy, c[0] + r + dx, c[1] + r + dy],
                   fill=fill, outline=INK if fill is None else None, width=int(cam.lw))
    shaded(img, cam, lambda dr, dx, dy, fill: head(dr, dx, dy, fill), 15)
    d = ImageDraw.Draw(img)

    # face
    ex = 24
    look = math.sin(t * 1.3) * 2
    blink = (f % 90) in (40, 41, 42)
    brow_up = 5 if mood in ("wave", "happy", "reveal") else 2
    if mood in ("happy",) or (mood == "reveal" and (f // 15) % 2 == 0):
        for s in (-1, 1):  # happy closed eyes ^ ^
            cx_, cy_ = hx + s * ex + look, hy - 4
            P = [cam.p(cx_ + k, cy_ - 7 * math.sin(math.pi * (k + 8) / 16)) for k in range(-8, 9, 2)]
            d.line(P, fill=INK, width=int(cam.lw), joint="curve")
    elif blink:
        for s in (-1, 1):
            line(d, cam, [(hx + s * ex + look - 6, hy - 2), (hx + s * ex + look + 6, hy - 2)])
    else:
        for s in (-1, 1):
            line(d, cam, [(hx + s * ex + look, hy - 12), (hx + s * ex + look, hy + 2)])
            line(d, cam, [(hx + s * ex + look - 9, hy - 22 - brow_up * 0.4),
                          (hx + s * ex + look + 9, hy - 22 - brow_up * 0.4)])
    # mouth
    my = hy + 30
    amp = 0.0
    if speaking:
        amp = 0.5 + 0.5 * abs(math.sin(f * 0.9))
    if amp > 0.05:
        mw, mh = 13, 4 + 12 * amp
        c = cam.p(hx + look, my)
        mw_, mh_ = cam.r(mw), cam.r(mh)
        d.pieslice([c[0] - mw_, c[1] - mh_, c[0] + mw_, c[1] + mh_], 0, 180, fill=INK)
        d.rectangle([c[0] - mw_, c[1] - mh_ * 0.12, c[0] + mw_, c[1] + mh_ * 0.02], fill=INK)
        d.rectangle([c[0] - mw_ * 0.6, c[1] - mh_ * 0.02, c[0] + mw_ * 0.6, c[1] + mh_ * 0.22], fill=(255, 255, 255))
    else:
        line(d, cam, [(hx - 9 + look, my + 2), (hx + 9 + look, my + 2)])
    cam.dy -= bob

def caption(img, text, local_f, big):
    if not text:
        return
    d = ImageDraw.Draw(img)
    size = int((54 if big else 36) * SS)
    pop = ease_out_back(local_f / 5.0)
    fnt = ImageFont.truetype(FONT, max(8, int(size * (0.6 + 0.4 * pop))))
    bb = d.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = (W * SS - tw) / 2 - bb[0], 38 * SS - bb[1]
    d.text((x, y), text, font=fnt, fill=(60, 60, 60))
    if big:  # hand-drawn underline that wipes in
        prog = min(1, max(0, (local_f - 10) / 14.0))
        y0 = y + bb[1] + th + 16 * SS
        x0, x1 = (W * SS - tw) / 2, (W * SS + tw) / 2
        pts = [(x0 + (x1 - x0) * k / 40, y0 + 3 * SS * math.sin(k / 40 * 9)) for k in range(int(41 * prog))]
        if len(pts) > 1:
            d.line(pts, fill=INK, width=int(2.4 * SS), joint="curve")

def frame(f):
    start, end, text, (cx, cy, z), mood = shot_at(f)
    local = f - start
    prog = local / max(1, end - start)
    z = z * (1 + 0.05 * prog) if mood in ("happy", "talk") else z
    pop = ease_out_back(f / 12.0) if f < 14 else 1.0
    pop = max(0.01, pop)
    img = Image.new("RGB", (W * SS, H * SS), (255, 255, 255))
    cam = Cam(cx, cy, z, pop)
    speaking = mood in ("wave", "happy", "talk", "reveal") and (
        (mood != "reveal") or local < 75)
    if mood == "wave" and local < 3:
        speaking = False
    draw_char(img, cam, f / FPS, f, mood, speaking)
    # fade in of the very first frames is avoided (hard cut style); caption pops
    caption(img, text, local, big=(mood == "reveal"))
    return img.resize((W, H), Image.LANCZOS)

def main():
    os.makedirs("out", exist_ok=True)
    out = "out/rizwantalks_intro.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(N):
        p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait()
    print("wrote", out)

if __name__ == "__main__":
    main()
