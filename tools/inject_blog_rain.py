"""Inject blog article text as digital rain chars into index.html."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Extract blog article text
all_text = ""
for f in sorted(ROOT.glob("2021/*/*/*/index.html")):
    html = f.read_text(encoding="utf-8")
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", "", text)
    all_text += text

# Keep only Chinese chars + tech symbols
CLEAN = "".join(c for c in all_text if "一" <= c <= "鿿" or c in "0123456789<>/|{}[]#@&.")
CLEAN = CLEAN[:8000]

# 2. Read index.html
html_path = ROOT / "index.html"
html = html_path.read_text(encoding="utf-8")

# 3. Replace the CHARS line and rain logic
old_chars_line = "const CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789<>/\\\\|{}[]#@&';"

new_rain_js = f"""const BLOG_TEXT = "{CLEAN}";
      const BT_LEN = BLOG_TEXT.length;"""

# Replace CHARS with BLOG_TEXT
html = html.replace(old_chars_line, new_rain_js)

# 4. Replace the old rain init/draw logic
# Old initDrops - replace the chars/ci creation
old_init = """function initDrops(){
        DROPS.length = 0;
        const n = Math.floor(W / 20);
        for(let i=0;i<n;i++){
          DROPS.push({
            x: i*20 + (Math.random()-.5)*12,
            y: -(Math.random()*H),
            speed: Math.random()*2.2+1,
            len: Math.floor(Math.random()*12+8),
            chars: Array.from({length:24},()=>CHARS[Math.floor(Math.random()*CHARS.length)]),
            ci: Math.floor(Math.random()*CHARS.length),
            hue: Math.random()<.12?300:195,
          });
        }
        dropsReady = true;
      }"""

new_init = """function initDrops(){
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

html = html.replace(old_init, new_init)

# 5. Replace drawRain
old_draw = """function drawRain(){
        if(!dropsReady) return;
        ctx.font = '13px "Courier New",monospace';
        ctx.textBaseline = 'top';
        for(const d of DROPS){
          d.y += d.speed;
          if(d.y - d.len*16 > H + 60){ d.y = -(d.len*16 + Math.random()*H*.5); d.ci=Math.floor(Math.random()*CHARS.length); }
          for(let j=0;j<d.len;j++){
            const py = d.y - j*16;
            if(py < -20 || py > H+20) continue;
            const t = j===0?1:Math.pow(.84,j);
            ctx.fillStyle = `hsla(${d.hue},92%,68%,${t})`;
            ctx.fillText(d.chars[(d.ci+j)%d.chars.length], d.x, py);
          }
        }
      }"""

new_draw = """function drawRain(){
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

html = html.replace(old_draw, new_draw)

# 6. Write back
html_path.write_text(html, encoding="utf-8")
print(f"Done. BLOG_TEXT length: {len(CLEAN)} chars")
print(f"HTML size: {len(html)} bytes")
