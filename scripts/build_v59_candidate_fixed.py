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

out_path = Path(sys.argv[2])
s = out_path.read_text(encoding="utf-8")

# Keep the landing-page autoplay behavior that worked in V58, but make the
# automatic startup attempt more resilient across mobile page lifecycle timing.
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

# Turn Junk Hauler's Guide into a featured, discoverable settings card and move
# it directly below Game Mode. Leave the rest of Settings deliberately simple.
old_guide_group = '''      <div class="setgroup">
        <div class="setlabel">Know your junk</div>
        <div class="setrow"><button class="setopt setwide" id="junkguide">Junk Hauler's Guide</button></div>
      </div>
'''
count = s.count(old_guide_group)
if count != 1:
    raise SystemExit(f"V59 wrapper stopped: expected one old guide settings group, found {count}")
s = s.replace(old_guide_group, '', 1)

featured_guide = '''      <div class="setgroup junkguidegroup">
        <button class="junkguidecard" id="junkguide" type="button" aria-label="Open Junk Hauler's Guide">
          <span class="jgicon" aria-hidden="true">♻</span>
          <span class="jgcopy"><span class="jgbadge">KNOW YOUR JUNK</span><span class="jgtitle">Junk Hauler's Guide</span><span class="jgsub">See every junk item, size &amp; weight</span></span>
          <span class="jgarrow" aria-hidden="true">›</span>
        </button>
      </div>
'''
anchor = '''      <div class="setgroup">
        <div class="setlabel">One-hand controls</div>'''
count = s.count(anchor)
if count != 1:
    raise SystemExit(f"V59 wrapper stopped: expected one controls settings anchor, found {count}")
s = s.replace(anchor, featured_guide + anchor, 1)

featured_css = r'''
  /* Featured Junk Hauler's Guide card — the one intentionally branded Settings action. */
  .junkguidegroup{padding:9px 0 10px!important;}
  .junkguidecard{width:100%;min-height:68px;display:grid;grid-template-columns:44px minmax(0,1fr) 24px;gap:9px;align-items:center;text-align:left;padding:9px 10px!important;border-radius:14px!important;
    background:linear-gradient(135deg,#7A4A2E 0%,#5A3424 52%,#3B271F 100%)!important;color:#FFF3E2!important;border:1px solid rgba(255,154,82,.72)!important;
    box-shadow:0 1px 0 rgba(255,255,255,.14) inset,0 7px 18px rgba(0,0,0,.28),0 0 16px rgba(255,122,41,.08)!important;}
  .junkguidecard:active{transform:scale(.985)!important;filter:brightness(.97);}
  .jgicon{width:42px;height:42px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:24px;line-height:1;background:linear-gradient(180deg,#FF9A52,#E86A18);color:#241812;box-shadow:0 1px 0 rgba(255,255,255,.2) inset,0 4px 9px rgba(0,0,0,.22);}
  .jgcopy{display:flex;flex-direction:column;min-width:0;line-height:1.05}.jgbadge{font-size:6px;font-weight:1000;letter-spacing:.17em;color:#FFC08A;margin-bottom:4px}.jgtitle{font-size:11px;font-weight:1000;letter-spacing:.015em;text-transform:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.jgsub{font-size:7px;font-weight:700;color:rgba(255,243,226,.7);margin-top:5px;text-transform:none;letter-spacing:.01em}.jgarrow{font-size:27px;font-weight:700;color:#FFAA69;text-align:right;line-height:1;}
'''
if '</style>' not in s:
    raise SystemExit("V59 wrapper stopped: missing style closing tag for featured guide CSS")
s = s.replace('</style>', featured_css + '\n</style>', 1)

# Public-facing final polish: keep versioning internally, but don't show build/date
# clutter to players. Use the bottom landing strip for brand language instead.
s = s.replace('BUILD V59 CANDIDATE · AUG 23', 'LOAD IT. STACK IT. HAUL IT.', 1)

out_path.write_text(s, encoding="utf-8")
print("Applied V59 landing music retries, featured Junk Hauler guide, and public stamp cleanup")
