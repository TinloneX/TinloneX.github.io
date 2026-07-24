"""Build a diverse Chinese tech token pool from blog articles for digital rain.

Strategy: extract every unique 2-4 character Chinese-only slice from the
articles, plus a few standalone symbols. Target 200-300 tokens.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Collect all article body text
all_text = ""
for f in sorted(ROOT.glob("2021/*/*/*/index.html")):
    html = f.read_text(encoding="utf-8")
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", "", text)
    all_text += text

# Keep only Chinese chars
cn = "".join(c for c in all_text if "一" <= c <= "鿿")

# 2. Extract unique 2-4 char slices (step through evenly)
slices = set()
step = 3  # small step for thorough coverage
for i in range(0, len(cn) - 2, step):
    for sl in [2, 3, 4]:
        if i + sl <= len(cn):
            seg = cn[i : i + sl]
            slices.add(seg)

# 3. Pick 250 diverse slices (spread across the alphabetically sorted set)
sorted_slices = sorted(slices)
# Pick every Nth to spread across the full vocabulary range
nth = max(1, len(sorted_slices) // 250)
picked = sorted_slices[::nth][:250]

# Add a few standalone tech symbols for visual variety
picked.extend(["</>", "//", "::", "->", "{}"])

# 4. Verify no dangerous characters
token_str = "|".join(picked)
assert "`" not in token_str, "Backtick found in tokens!"
assert "$" not in token_str, "Dollar sign found in tokens!"

print(f"Chinese chars total: {len(cn)}")
print(f"Unique slices found: {len(slices)}")
print(f"Final tokens: {len(picked)}")
print(f"Token string length: {len(token_str)}")
print(f"Sample tokens: {picked[:15]}")

# 5. Inject into index.html
html_path = ROOT / "index.html"
html = html_path.read_text(encoding="utf-8")

# Find and replace the BLOG_TEXT line
lines = html.split("\n")
for i, line in enumerate(lines):
    if "const BLOG_TEXT" in line:
        lines[i] = f'      const TOKENS = `{token_str}`.split("|");'
        break
for i, line in enumerate(lines):
    if "const BT_LEN = BLOG_TEXT.length;" in line:
        lines[i] = ""
        break

html = "\n".join(lines)

# Replace old initDrops with token-based version
old_init_1 = """        DROPS.length = 0;
        const TL = TOKENS.length;
        const n = Math.floor(W / 20);
        for(let i=0;i<n;i++){
          const seq = [];
          for(let k=0;k<16;k++) seq.push(TOKENS[Math.floor(Math.random()*TL)]);
          DROPS.push({
            x: i*20 + (Math.random()-.5)*12,
            y: -(Math.random()*H),
            speed: Math.random()*2.2+1,
            len: Math.floor(Math.random()*10+6),
            seq,
            si: Math.floor(Math.random()*TL),
            hue: Math.random()<.12?300:195,
          });
        }"""

# Find the current initDrops
html = html.replace(old_init_1, "")  # remove old

# Actually, let me read the file to understand current state
html_path.write_text(html, encoding="utf-8")
print(f"\nIntermediate HTML: {len(html)} bytes")

# Now read back and apply remaining replacements
html = html_path.read_text(encoding="utf-8")

# Replace initDrops
old_init = """      function initDrops(){
        DROPS.length = 0;
        const n = Math.floor(W / 20);
        for(let i=0;i<n;i++){
          DROPS.push({
            x: i*20 + (Math.random()-.5)*12,
            y: -(Math.random()*H),
            speed: Math.random()*2.2+1,
            len: Math.floor(Math.random()*12+8),
            off: Math.floor(Math.random()*BT_LEN),
            hue: Math.random()<.12?300:195,
          });
        }
        dropsReady = true;
      }"""

new_init = """      function initDrops(){
        DROPS.length = 0;
        const n = Math.floor(W / 20);
        for(let i=0;i<n;i++){
          const seq = [];
          for(let k=0;k<16;k++) seq.push(TOKENS[Math.floor(Math.random()*TOKENS.length)]);
          DROPS.push({
            x: i*20 + (Math.random()-.5)*12,
            y: -(Math.random()*H),
            speed: Math.random()*2.2+1,
            len: Math.floor(Math.random()*10+6),
            seq,
            si: Math.floor(Math.random()*TOKENS.length),
            hue: Math.random()<.12?300:195,
          });
        }
        dropsReady = true;
      }"""

if old_init in html:
    html = html.replace(old_init, new_init)
    print("Replaced initDrops")
else:
    print("initDrops NOT FOUND - checking what's there")
    idx = html.find("function initDrops")
    if idx >= 0:
        print(html[idx:idx+500])

# Replace drawRain
old_draw = """      function drawRain(){
        if(!dropsReady) return;
        ctx.font = '13px "Courier New",monospace';
        ctx.textBaseline = 'top';
        for(const d of DROPS){
          d.y += d.speed;
          if(d.y - d.len*16 > H + 60){ d.y = -(d.len*16 + Math.random()*H*.5); d.off = (d.off + d.len) % BT_LEN; }
          for(let j=0;j<d.len;j++){
            const py = d.y - j*16;
            if(py < -20 || py > H+20) continue;
            const idx = (d.off + j) % BT_LEN;
            const ch = BLOG_TEXT[idx];
            const t = j===0?1:Math.pow(.84,j);
            ctx.fillStyle = `hsla(${d.hue},92%,68%,${t})`;
            ctx.fillText(ch, d.x, py);
          }
        }
      }"""

new_draw = """      function drawRain(){
        if(!dropsReady) return;
        ctx.font = '13px "Courier New",monospace';
        ctx.textBaseline = 'top';
        for(const d of DROPS){
          d.y += d.speed;
          if(d.y - d.len*16 > H + 60){ d.y = -(d.len*16 + Math.random()*H*.5); }
          for(let j=0;j<d.len;j++){
            const py = d.y - j*16;
            if(py < -20 || py > H+20) continue;
            const token = d.seq[(d.si + j) % d.seq.length];
            const t = j===0?1:Math.pow(.84,j);
            ctx.fillStyle = `hsla(${d.hue},92%,68%,${t})`;
            ctx.fillText(token, d.x, py);
          }
        }
      }"""

if old_draw in html:
    html = html.replace(old_draw, new_draw)
    print("Replaced drawRain")
else:
    print("drawRain NOT FOUND")

html_path.write_text(html, encoding="utf-8")
print(f"\nFinal HTML: {len(html)} bytes ({len(html)/1024:.1f} KB)")
