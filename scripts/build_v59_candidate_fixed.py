from pathlib import Path
import sys

# Compatibility wrapper for the V59 candidate builder.
# V58 contains two inline script openings; the original builder expected one.
# This wrapper changes only that insertion rule so the Junk Hauler's Guide
# is inserted before the second/main game script, then executes the original
# guarded builder unchanged.

builder_path = Path(__file__).with_name("build_v59_candidate.py")
code = builder_path.read_text(encoding="utf-8")

old = "one('<script>\\n(function(){', guide_html + '\\n<script>\\n(function(){', \"main script opening\")"
new = '''marker = '<script>\\n(function(){'\ncount = s.count(marker)\nif count != 2:\n    raise SystemExit(f\"V59 patch stopped: expected two script openings before guide insertion, found {count}\")\npos = s.rfind(marker)\ns = s[:pos] + guide_html + '\\n' + s[pos:]'''

count = code.count(old)
if count != 1:
    raise SystemExit(f"V59 wrapper stopped: expected one original script-opening rule, found {count}")

code = code.replace(old, new, 1)
exec(compile(code, str(builder_path), "exec"), {"__name__": "__main__", "__file__": str(builder_path)})

# Preserve the landing-page autoplay behavior that worked in V58, but make
# the automatic startup attempt more resilient across mobile page lifecycle
# timing. The first pointer/touch/keyboard interaction remains the fallback.
out_path = Path(sys.argv[2])
s = out_path.read_text(encoding="utf-8")
old_music = '''function tryLandingMusic(){
  // Browsers may allow autoplay in some contexts. If not, the first touch below unlocks it.
  if(!musicOn)return;
  startMusicReady(true);
}
setTimeout(tryLandingMusic,60);
window.addEventListener("load",tryLandingMusic,{once:true});
document.addEventListener("pointerdown",armLandingMusic,{once:true,capture:true});
document.addEventListener("touchstart",armLandingMusic,{once:true,capture:true,passive:true});
document.addEventListener("keydown",armLandingMusic,{once:true,capture:true});'''
new_music = '''function tryLandingMusic(){
  // V59: keep retrying briefly during landing-page startup. Some mobile
  // browser launches allow WebAudio a moment after the document appears.
  if(landingMusicArmed||!musicOn)return;
  startMusicReady(true).then(function(){landingMusicArmed=true;}).catch(function(){});
}
var landingAutoAttempts=0,landingAutoTimer=null;
function landingMusicProbe(){
  if(landingMusicArmed||landingAutoAttempts>=10){if(landingAutoTimer){clearInterval(landingAutoTimer);landingAutoTimer=null;}return;}
  landingAutoAttempts++;tryLandingMusic();
}
tryLandingMusic();
setTimeout(tryLandingMusic,40);
window.addEventListener("load",tryLandingMusic,{once:true});
window.addEventListener("pageshow",tryLandingMusic);
window.addEventListener("focus",tryLandingMusic);
document.addEventListener("visibilitychange",function(){if(!document.hidden)tryLandingMusic();});
landingAutoTimer=setInterval(landingMusicProbe,220);
document.addEventListener("pointerdown",armLandingMusic,{once:true,capture:true});
document.addEventListener("touchstart",armLandingMusic,{once:true,capture:true,passive:true});
document.addEventListener("keydown",armLandingMusic,{once:true,capture:true});'''
count = s.count(old_music)
if count != 1:
    raise SystemExit(f"V59 wrapper stopped: expected one landing music block, found {count}")
s = s.replace(old_music, new_music, 1)
out_path.write_text(s, encoding="utf-8")
print("Applied resilient V59 landing music startup")
