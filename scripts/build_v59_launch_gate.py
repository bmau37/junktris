from pathlib import Path
import subprocess, sys

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v59_launch_gate.py SOURCE_HTML OUTPUT_HTML")

src = Path(sys.argv[1])
out = Path(sys.argv[2])
base = Path(__file__).with_name("build_v59_audio_probe.py")
subprocess.run([sys.executable, str(base), str(src), str(out)], check=True)
s = out.read_text(encoding="utf-8")


def one(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"V59 launch gate stopped: expected one {label}, found {count}")
    s = s.replace(old, new, 1)

# A polished pre-landing audio-unlock gate. Browsers that permit autoplay skip it
# automatically; browsers that block audible autoplay get one intentional tap before
# the real landing page is revealed. That makes the landing page itself arrive with sound.
gate_css = r'''
  #launchGate{position:fixed;inset:0;z-index:9998;display:flex;align-items:center;justify-content:center;padding:24px;background:
    radial-gradient(circle at 50% 30%,rgba(255,122,41,.13),transparent 33%),linear-gradient(180deg,#11100f 0%,#080706 100%);
    color:#FFF3E2;text-align:center;transition:opacity .28s ease,visibility .28s ease;}
  #launchGate.hide{opacity:0;visibility:hidden;pointer-events:none;}
  .launchbox{width:min(100%,430px);display:flex;flex-direction:column;align-items:center;gap:10px;}
  .launchkicker{font-size:9px;font-weight:1000;letter-spacing:.24em;text-transform:uppercase;color:#FF9A52;}
  .launchlogo{font-size:clamp(42px,13vw,68px);font-weight:1000;letter-spacing:-.055em;line-height:.92;color:#FFF3E2;text-shadow:0 8px 30px rgba(0,0,0,.5);}
  .launchrule{width:72px;height:3px;border-radius:999px;background:linear-gradient(90deg,#FFB06F,#F0660D);box-shadow:0 0 18px rgba(255,122,41,.4);margin:5px 0 2px;}
  .launchsub{max-width:310px;font-size:11px;line-height:1.45;color:rgba(255,243,226,.72);}
  #launchBtn{margin-top:10px;width:min(100%,330px);min-height:62px;flex:none;border-radius:17px;padding:0 20px;background:linear-gradient(180deg,#FFB06F 0%,#FF8A3D 52%,#EB6512 100%);color:#211711;
    border:1px solid rgba(255,226,198,.45);box-shadow:0 2px 0 rgba(255,255,255,.22) inset,0 -3px 0 rgba(121,39,2,.3) inset,0 12px 30px rgba(0,0,0,.4);font-size:14px;font-weight:1000;letter-spacing:.12em;text-transform:uppercase;}
  #launchBtn:active{transform:scale(.985);filter:brightness(.96);}
  .launchhint{font-size:8px;font-weight:900;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,243,226,.45);}
'''
one('</style>', gate_css + '\n</style>', 'style closing tag')

gate_html = r'''
<div id="launchGate" role="dialog" aria-label="Launch Junktris with sound">
  <div class="launchbox">
    <div class="launchkicker">Load. Stack. Haul.</div>
    <div class="launchlogo">JUNKTRIS</div>
    <div class="launchrule"></div>
    <div class="launchsub">A fast junk-hauling packing game built to play with sound.</div>
    <button id="launchBtn" type="button">Tap to Load Junktris&nbsp;&nbsp;›</button>
    <div class="launchhint">Sound starts with the game</div>
  </div>
</div>
'''
one('<body>\n', '<body>\n' + gate_html + '\n', 'body opening for launch gate')

launch_js = r'''
var launchGateDone=false;
function hideLaunchGate(){
  if(launchGateDone)return;launchGateDone=true;
  var g=document.getElementById("launchGate");if(g)g.classList.add("hide");
}
function launchWithSound(){
  if(launchGateDone)return;
  musicOn=true;writePref("junktris_music_on","1");syncMusicBtn();
  // Resume WebAudio during the same user gesture even if the media-element theme wins.
  // This keeps the later handoff into gameplay immediate and reliable.
  try{audioOn();}catch(e){}
  var p=tryLandingTheme();
  if(p&&typeof p.then==="function"){
    p.then(function(){landingMusicArmed=true;hideLaunchGate();updateAudioProbe("launch gate media playing");})
     .catch(function(){
       startMusicReady(true).then(function(){landingMusicArmed=true;hideLaunchGate();updateAudioProbe("launch gate WebAudio playing");})
       .catch(function(e){updateAudioProbe("launch gate audio failed: "+audioErr(e));hideLaunchGate();});
     });
  }else{
    landingMusicArmed=true;hideLaunchGate();
  }
}
(function(){
  var b=document.getElementById("launchBtn");
  if(b){b.addEventListener("pointerup",launchWithSound,{once:true});b.addEventListener("click",launchWithSound,{once:true});}
  // If this browser genuinely allows audible autoplay, don't make the player tap a gate.
  var tries=0,t=setInterval(function(){
    tries++;
    var el=document.getElementById("landingTheme");
    if((el&&!el.paused)||(landingMusicArmed&&AC&&AC.state==="running")){clearInterval(t);hideLaunchGate();}
    else if(tries>=12)clearInterval(t);
  },120);
})();
'''
one('function audioProbeEnabled(){', launch_js + '\nfunction audioProbeEnabled(){', 'launch gate JavaScript insertion')

# Release-safety markers.
for marker in ['id="launchGate"', 'id="launchBtn"', 'function launchWithSound()', 'function hideLaunchGate()']:
    if marker not in s:
        raise SystemExit(f"V59 launch gate audit failed: missing {marker}")

out.write_text(s, encoding='utf-8')
print('V59 LAUNCH GATE: built successfully')
