"""Rebuild index.html rain tokens as consecutive Chinese chars from blog articles.

Each rain column picks a random offset into a continuous stream of single
Chinese characters extracted in article order. The column then displays
chars sequentially from that offset — so every column shows real,
continuous blog prose flowing down.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Extract all Chinese characters in original article order
all_text = ""
for f in sorted(ROOT.glob("2021/*/*/*/index.html")):
    html = f.read_text(encoding="utf-8")
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", "", text)
    all_text += text

# Keep only Chinese chars, in order
cn = "".join(c for c in all_text if "一" <= c <= "鿿")

# Trim to ~6000 chars for reasonable HTML size
cn = cn[:6000]

# Every character is a single token
# We use a JS string — each char is accessible by index
assert "`" not in cn, "backtick in blog text"
assert "$" not in cn, "$ in blog text"

print(f"Chinese chars: {len(cn)}")
print(f"Sample (chars 100-160): {cn[100:160]}")

# 2. Read and patch index.html
html_path = ROOT / "index.html"
html = html_path.read_text(encoding="utf-8")

# Replace the TOKENS line
old_tokens = html[html.find("const TOKENS=") : html.find(";", html.find("const TOKENS=")) + 1]
new_tokens = f'const BLOG = "{cn}";'
html = html.replace(old_tokens, new_tokens)

# Replace initDrops — each column gets a random offset into BLOG
old_init = """      function initDrops(){
        DROPS.length = 0;
        const n = Math.floor(W / 20);
        for(let i=0;i<n;i++){
          const seq = [];
          for(let k=0;k<8;k++) seq.push(TOKENS[Math.floor(Math.random()*TOKENS.length)]);
          DROPS.push({
            x: i*20 + (Math.random()-.5)*12,
            y: -(Math.random()*H),
            speed: Math.random()*2.2+1,
            len: Math.floor(Math.random()*5+3),
            seq,
            si: Math.floor(Math.random()*TOKENS.length),
            hue: Math.random()<.12?300:195,
          });
        }
        dropsReady = true;
      }"""

new_init = """      function initDrops(){
        DROPS.length = 0;
        const BL = BLOG.length;
        const n = Math.floor(W / 20);
        for(let i=0;i<n;i++){
          DROPS.push({
            x: i*20 + (Math.random()-.5)*12,
            y: -(Math.random()*H),
            speed: Math.random()*2.2+1,
            len: Math.floor(Math.random()*5+3),
            off: Math.floor(Math.random()*BL),
            hue: Math.random()<.12?300:195,
          });
        }
        dropsReady = true;
      }"""

assert old_init in html, "old_init not found!"
html = html.replace(old_init, new_init)

# Replace drawRain — reads consecutive chars from BLOG starting at off
old_draw = """      function drawRain(){
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

new_draw = """      function drawRain(){
        if(!dropsReady) return;
        const BL = BLOG.length;
        ctx.font = '13px "Courier New",monospace';
        ctx.textBaseline = 'top';
        for(const d of DROPS){
          d.y += d.speed;
          if(d.y - d.len*16 > H + 60){ d.y = -(d.len*16 + Math.random()*H*.5); d.off = Math.floor(Math.random()*BL); }
          for(let j=0;j<d.len;j++){
            const py = d.y - j*16;
            if(py < -20 || py > H+20) continue;
            const ch = BLOG[(d.off + j) % BL];
            const t = j===0?1:Math.pow(.84,j);
            ctx.fillStyle = `hsla(${d.hue},92%,68%,${t})`;
            ctx.fillText(ch, d.x, py);
          }
        }
      }"""

assert old_draw in html, "old_draw not found!"
html = html.replace(old_draw, new_draw)

html_path.write_text(html, encoding="utf-8")
print(f"\nDone! HTML: {len(html)} bytes ({len(html)/1024:.1f} KB)")
print(f"BLOG string: {len(cn)} Chinese chars (continuous blog text)")
