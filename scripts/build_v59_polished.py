from pathlib import Path
import base64, io, math, re, struct, subprocess, sys, tempfile, wave, shutil

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v59_polished.py SOURCE_HTML OUTPUT_HTML")

src = Path(sys.argv[1])
out = Path(sys.argv[2])
fixed = Path(__file__).with_name("build_v59_candidate_fixed.py")
subprocess.run([sys.executable, str(fixed), str(src), str(out)], check=True)
s = out.read_text(encoding="utf-8")


def one(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"V59 polish stopped: expected exactly one {label}, found {count}")
    s = s.replace(old, new, 1)


# Final public-facing naming and mobile polish. Internal versioning stays in Git/GitHub.
one(
    "<title>Junktris — V59 Candidate</title>",
    '<title>Junktris</title>\n<meta name="theme-color" content="#17110e">\n<meta name="application-name" content="Junktris">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n<meta name="description" content="Junktris — load it, stack it, haul it.">',
    "public title/meta",
)

# Restore the final music identities while preserving the existing internal style keys.
one('id="trackGarage">Garage Groove</button>', 'id="trackGarage">Chill</button>', "Chill track label")
one('id="trackHeavy">Heavy Haul</button>', 'id="trackHeavy">Metal</button>', "Metal track label")


# Create a short, original, self-contained landing beat as an HTMLMediaElement bridge.
# Audible autoplay remains subject to browser policy, but this gives the browser a standard
# media-element autoplay path in addition to the existing WebAudio path that worked before.
def make_landing_wav() -> str:
    sr = 16000
    dur = 4.0
    n = int(sr * dur)
    sig = [0.0] * n

    def add_tone(start, length, freq, amp, decay=4.0, shape="sine"):
        a = max(0, int(start * sr)); b = min(n, int((start + length) * sr))
        for i in range(a, b):
            t = (i / sr) - start
            env = math.exp(-decay * t)
            ph = 2 * math.pi * freq * t
            if shape == "square":
                v = 1.0 if math.sin(ph) >= 0 else -1.0
            elif shape == "tri":
                v = 2 / math.pi * math.asin(math.sin(ph))
            else:
                v = math.sin(ph)
            sig[i] += amp * env * v

    def add_kick(start, amp=0.55):
        a = max(0, int(start * sr)); b = min(n, int((start + .22) * sr))
        for i in range(a, b):
            t = (i / sr) - start
            freq = 110 - 72 * min(1, t / .16)
            env = math.exp(-18 * t)
            sig[i] += amp * env * math.sin(2 * math.pi * freq * t)

    def add_noise(start, length, amp, decay):
        # deterministic pseudo-noise so the build is reproducible
        x = 0x5A17
        a = max(0, int(start * sr)); b = min(n, int((start + length) * sr))
        for i in range(a, b):
            x = (1103515245 * x + 12345) & 0x7fffffff
            noise = (x / 0x7fffffff) * 2 - 1
            t = (i / sr) - start
            sig[i] += amp * math.exp(-decay * t) * noise

    # 8-beat loop at 120 BPM: punchy, original, no sampled/copyrighted audio.
    beat = .5
    bass = [73.42, 73.42, 87.31, 65.41, 73.42, 98.00, 65.41, 58.27]
    for b in range(8):
        st = b * beat
        add_kick(st, .48 if b in (0, 4) else .40)
        if b % 2 == 1:
            add_noise(st, .16, .13, 16)
        add_noise(st + .25, .055, .035, 38)
        add_tone(st, .42, bass[b], .18, 3.3, "tri")
    # Sparse hook stabs to make the first impression feel intentional rather than like a metronome.
    for st, fr in ((.0, 293.66), (.75, 349.23), (1.5, 261.63), (2.5, 293.66), (3.25, 392.00)):
        add_tone(st, .22, fr, .08, 7.0, "square")
        add_tone(st, .24, fr / 2, .055, 6.5, "tri")

    peak = max(1e-9, max(abs(v) for v in sig))
    scale = 0.50 / peak
    pcm = bytearray()
    for v in sig:
        vv = max(-1.0, min(1.0, v * scale))
        pcm += struct.pack('<h', int(vv * 32767))

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(pcm))
    return base64.b64encode(buf.getvalue()).decode('ascii')


landing_b64 = make_landing_wav()
audio_tag = f'<audio id="landingTheme" autoplay loop playsinline preload="auto" aria-hidden="true" src="data:audio/wav;base64,{landing_b64}" style="display:none"></audio>'
one('<body>', '<body>\n' + audio_tag, "landing audio element")

# Prefer the media-element bridge for the landing page. If the browser blocks it, fall back
# immediately to the existing WebAudio startup/retry path and then the first-touch unlock.
landing_helper = r'''
function tryLandingTheme(){
  var el=document.getElementById("landingTheme");
  if(!el||!musicOn)return Promise.reject(new Error("Landing theme unavailable"));
  try{el.volume=.72;var p=el.play();return p&&typeof p.then==="function"?p:Promise.resolve(true);}catch(e){return Promise.reject(e);}
}
function stopLandingTheme(){
  var el=document.getElementById("landingTheme");
  if(!el)return;
  try{el.pause();el.currentTime=0;}catch(e){}
}
'''
one('function tryLandingMusic(){', landing_helper + '\nfunction tryLandingMusic(){', "landing media helper insertion")
one(
    '  if(landingMusicArmed||!musicOn)return;\n  startMusicReady(true).then(function(){landingMusicArmed=true;}).catch(function(){});',
    '  if(landingMusicArmed||!musicOn)return;\n  tryLandingTheme().then(function(){landingMusicArmed=true;}).catch(function(){startMusicReady(true).then(function(){landingMusicArmed=true;}).catch(function(){});});',
    "landing media first-start path",
)
one(
    'bindBtn("sbtn",function(){\n  musicOn=true;',
    'bindBtn("sbtn",function(){\n  stopLandingTheme();\n  landingMusicArmed=false;\n  musicOn=true;',
    "landing-to-game audio handoff",
)

# Static release-candidate audit. These checks deliberately stop deployment of V59 if a
# future edit silently breaks one of the locked rules.
expected_pool = ['trash','micro','recliner','loveseat','twin','washer','dryer','coffee','tv','oven','dresser','mattress','shed','couch','fridge','lamp']
m = re.search(r'var POOL=\[(.*?)\];', s)
if not m:
    raise SystemExit('V59 audit failed: POOL not found')
pool = re.findall(r'"([^"]+)"', m.group(1))
if pool != expected_pool:
    raise SystemExit(f'V59 audit failed: unexpected pool {pool}')

checks = {
    'exactly 16 active junk items': len(pool) == 16,
    'Dining Table removed': 'name:"Dining Table"' not in s,
    'Coffee Table retained': 'name:"Coffee Table"' in s,
    'Twin Mattress retained': 'name:"Twin Mattress"' in s,
    'Queen Mattress retained': 'name:"Queen Mattress"' in s,
    'Recliner uses dedicated art': 'art:"recliner"' in s,
    'Dryer uses dedicated art': 'art:"dryer"' in s,
    'Shed is 6x4': 'shed:{name:"Shed",wt:420,art:"shed",mask:["######","######","######","######"]' in s,
    'Shed bonus moment exists': 'SHED JOB!  BIG LOAD · BIG PAYOUT' in s,
    'three curb choices preserved': 'for(var i=0;i<3;i++)' in s,
    'Line Haul requires 16/16': 'var CLEAR_AT=16' in s,
    'Tight Pack target is 12/16': 'var PACK_AT=12' in s,
    'weight limit preserved': 'var WT_LIMIT=1400' in s,
    'Junk Hauler guide present': "Junk Hauler's Guide" in s,
    'featured guide present': 'class="junkguidecard"' in s,
    'public build/date stamp removed': 'BUILD V59 CANDIDATE · AUG 23' not in s,
    'public browser title cleaned': '<title>Junktris</title>' in s,
    'Chill label present': 'id="trackGarage">Chill</button>' in s,
    'Metal label present': 'id="trackHeavy">Metal</button>' in s,
    'Night Shift label present': 'id="trackNight">Night Shift</button>' in s,
    'landing audio bridge present': 'id="landingTheme"' in s and 'tryLandingTheme' in s,
}
failed = [k for k, v in checks.items() if not v]
if failed:
    raise SystemExit('V59 audit failed: ' + '; '.join(failed))

# Parse every inline script with Node when available. This catches syntax damage without
# executing DOM-dependent game code.
node = shutil.which('node')
if node:
    blocks = re.findall(r'<script>(.*?)</script>', s, flags=re.S)
    for idx, block in enumerate(blocks, 1):
        with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as tf:
            tf.write(block); temp_name = tf.name
        try:
            cp = subprocess.run([node, '--check', temp_name], text=True, capture_output=True)
            if cp.returncode != 0:
                raise SystemExit(f'V59 audit failed: JavaScript block {idx} syntax error: {cp.stderr.strip()}')
        finally:
            Path(temp_name).unlink(missing_ok=True)

out.write_text(s, encoding='utf-8')
report = ['V59 POLISH AUDIT: PASS'] + [f'PASS - {k}' for k in checks]
out.with_name('v59-audit.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
print('\n'.join(report))
