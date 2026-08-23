from pathlib import Path
import subprocess, sys

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v59_audio_probe.py SOURCE_HTML OUTPUT_HTML")

src = Path(sys.argv[1])
out = Path(sys.argv[2])
polished = Path(__file__).with_name("build_v59_polished.py")
subprocess.run([sys.executable, str(polished), str(src), str(out)], check=True)
s = out.read_text(encoding="utf-8")


def one(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"V59 audio probe stopped: expected one {label}, found {count}")
    s = s.replace(old, new, 1)

# Chrome recommends click-style activation for reliable audible playback. Preserve the
# existing early pointer/touch listeners, but add release/click paths as well.
needle = 'document.addEventListener("keydown",armLandingMusic,{once:true,capture:true});'
replacement = needle + '''\ndocument.addEventListener("click",armLandingMusic,{once:true,capture:true});\ndocument.addEventListener("pointerup",armLandingMusic,{once:true,capture:true});\ndocument.addEventListener("touchend",armLandingMusic,{once:true,capture:true,passive:true});'''
one(needle, replacement, "landing activation listeners")

# On a real user activation, try the standard media element first and WebAudio second.
old_arm = '''function armLandingMusic(){\n  if(landingMusicArmed)return;\n  landingMusicArmed=true;\n  musicOn=true;writePref("junktris_music_on","1");syncMusicBtn();\n  startMusicReady(true);\n}'''
new_arm = '''function armLandingMusic(){\n  musicOn=true;writePref("junktris_music_on","1");syncMusicBtn();\n  tryLandingTheme().then(function(){landingMusicArmed=true;updateAudioProbe("gesture media playing");})\n    .catch(function(){startMusicReady(true).then(function(){landingMusicArmed=true;updateAudioProbe("gesture WebAudio playing");}).catch(function(e){updateAudioProbe("gesture failed: "+audioErr(e));});});\n}'''
one(old_arm, new_arm, "landing gesture audio function")

# Keep the exact autoplay failure reason so we stop guessing.
old_theme = '''function tryLandingTheme(){\n  var el=document.getElementById("landingTheme");\n  if(!el||!musicOn)return Promise.reject(new Error("Landing theme unavailable"));\n  try{el.volume=.72;var p=el.play();return p&&typeof p.then==="function"?p:Promise.resolve(true);}catch(e){return Promise.reject(e);}\n}'''
new_theme = '''var landingAudioLastError="";\nfunction audioErr(e){return e?(String(e.name||"Error")+(e.message?": "+e.message:"")):"unknown";}\nfunction tryLandingTheme(){\n  var el=document.getElementById("landingTheme");\n  if(!el||!musicOn)return Promise.reject(new Error("Landing theme unavailable"));\n  try{\n    el.volume=.72;\n    var p=el.play();\n    if(p&&typeof p.then==="function")return p.then(function(v){landingAudioLastError="";updateAudioProbe("media autoplay playing");return v;}).catch(function(e){landingAudioLastError=audioErr(e);updateAudioProbe("media autoplay blocked: "+landingAudioLastError);throw e;});\n    updateAudioProbe("media play() returned without promise");return Promise.resolve(true);\n  }catch(e){landingAudioLastError=audioErr(e);updateAudioProbe("media exception: "+landingAudioLastError);return Promise.reject(e);}\n}'''
one(old_theme, new_theme, "landing media play function")

# Query-only diagnostic. Normal players see nothing. Open with ?audioDebug=1 to show it.
probe = r'''
function audioProbeEnabled(){return /(?:\?|&)audioDebug=1(?:&|$)/.test(location.search);}
function ensureAudioProbe(){
  if(!audioProbeEnabled())return null;
  var d=document.getElementById("audioProbe");if(d)return d;
  d=document.createElement("div");d.id="audioProbe";
  d.style.cssText="position:fixed;left:8px;right:8px;top:8px;z-index:9999;background:rgba(0,0,0,.88);color:#9cffb0;border:1px solid #ff7a29;border-radius:8px;padding:7px 9px;font:10px/1.35 monospace;white-space:pre-wrap;pointer-events:none";
  document.body.appendChild(d);return d;
}
function updateAudioProbe(note){
  var d=ensureAudioProbe();if(!d)return;
  var el=document.getElementById("landingTheme"),ua=navigator.userActivation||{};
  d.textContent="AUDIO PROBE\n"+(note||"")+"\nuserActive="+!!ua.isActive+" hasBeenActive="+!!ua.hasBeenActive+
    "\nmedia="+(el?("paused="+el.paused+" ready="+el.readyState+" network="+el.networkState):"missing")+
    "\nmediaError="+(landingAudioLastError||"none")+"\nAudioContext="+(AC?AC.state:"not-created");
}
setTimeout(function(){updateAudioProbe("after 250ms");},250);
setTimeout(function(){updateAudioProbe("after 1500ms");},1500);
window.addEventListener("pageshow",function(){setTimeout(function(){updateAudioProbe("pageshow");},80);});
'''
one('function tryLandingTheme(){', probe + '\nfunction tryLandingTheme(){', "audio probe helpers")

out.write_text(s, encoding="utf-8")
print("V59 AUDIO PROBE: built successfully")
