from pathlib import Path
import re, shutil, subprocess, sys, tempfile

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v60_difficulty.py SOURCE_HTML OUTPUT_HTML")

src = Path(sys.argv[1])
out = Path(sys.argv[2])
base = Path(__file__).with_name("build_v59_pwa.py")
subprocess.run([sys.executable, str(base), str(src), str(out)], check=True)
s = out.read_text(encoding="utf-8")


def one(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"V60 difficulty patch stopped: expected one {label}, found {count}")
    s = s.replace(old, new, 1)

# Difficulty is independent from game mode. Hard intentionally preserves V59 gameplay.
one(
    'function loadBest(){try{return +localStorage.getItem("junktris_best")||0}catch(e){return 0}}\n'
    'function saveBest(v){try{localStorage.setItem("junktris_best",String(v))}catch(e){}}',
    '''function bestKey(d,m){return "junktris_best_"+(d||selectedDifficulty||"easy")+"_"+(m||selectedMode||"line");}\n'
    'function loadBest(d,m){try{d=d||selectedDifficulty||"easy";m=m||selectedMode||"line";var v=localStorage.getItem(bestKey(d,m));if(v!==null)return +v||0;if(d==="hard")return +localStorage.getItem("junktris_best")||0;return 0;}catch(e){return 0}}\n'
    'function saveBest(v,d,m){try{localStorage.setItem(bestKey(d||gameDifficulty,m||gameMode),String(v))}catch(e){}}''',
    "difficulty-specific best-score storage",
)

old_state = 'var handMode=readPref("junktris_hand","right"),musicStyle=readPref("junktris_music_style","garage"),selectedMode=readPref("junktris_mode","line"),gameMode=selectedMode,settingsResumeAfter=false;'
new_state = '''var handMode=readPref("junktris_hand","right"),musicStyle=readPref("junktris_music_style","garage"),selectedMode=readPref("junktris_mode","line"),selectedDifficulty=readPref("junktris_difficulty","easy"),gameMode=selectedMode,gameDifficulty=selectedDifficulty,settingsResumeAfter=false;
if(selectedDifficulty!=="easy"&&selectedDifficulty!=="medium"&&selectedDifficulty!=="hard")selectedDifficulty="easy";
gameDifficulty=selectedDifficulty;
function difficultyConfig(d){
  if(d==="easy")return {label:"EASY",clear:12,pack:9,wt:1800,gravity:.60,lock:.70,speed:"SLOWER DROP"};
  if(d==="medium")return {label:"MEDIUM",clear:14,pack:11,wt:1600,gravity:.80,lock:.55,speed:"BALANCED"};
  return {label:"HARD",clear:16,pack:12,wt:1400,gravity:1,lock:.45,speed:"ORIGINAL"};
}
function applyDifficulty(){var c=difficultyConfig(gameDifficulty);WT_LIMIT=c.wt;CLEAR_AT=c.clear;PACK_AT=c.pack;}'''
one(old_state, new_state, "difficulty state")

# Landing page: difficulty first, mode second. Keep the existing visual language.
one(
    '<div class="kicker">Choose your game</div>\n        <div class="headline">Two game modes</div>\n        <div class="sub">Choose how you want to play before you start.</div>',
    '<div class="kicker">Choose your challenge</div>\n        <div class="headline">Pick a difficulty</div>\n        <div class="sub">Easy is built for your first load. Then choose a game mode.</div>',
    "landing challenge copy",
)

diff_html = '''      <div id="diffpick" aria-label="Choose difficulty">
        <button id="diffEasy" type="button"><span class="diffk">EASY</span><span class="diffd">Learn the load</span></button>
        <button id="diffMedium" type="button"><span class="diffk">MEDIUM</span><span class="diffd">Balanced</span></button>
        <button id="diffHard" type="button"><span class="diffk">HARD</span><span class="diffd">Original</span></button>
      </div>
'''
one('      <div id="modepick" aria-label="Choose game mode">', diff_html + '      <div id="modepick" aria-label="Choose game mode">', "landing difficulty picker")
one('<span class="moded">Clear full 16-cell rows.</span>', '<span class="moded" id="lineRule">Clear rows at 12/16.</span>', "Line Haul rule copy")
one('<span class="moded">Pack layers to 12/16+.</span>', '<span class="moded" id="tightRule">Pack layers to 9/16+.</span>', "Tight Pack rule copy")

# Settings: add a compact three-way difficulty selector without making Settings a new long screen.
old_settings = '''      <div class="setgroup">
        <div class="setlabel">Game mode</div>
        <div class="setrow"><button class="setopt" id="modeLineSet">Line Haul</button><button class="setopt" id="modeTightSet">Tight Pack</button></div>
        <div class="setnote">Line Haul clears only complete 16/16 rows. Tight Pack keeps every row and treats 12/16+ as efficiently packed. Changes apply on restart or the next truck.</div>
      </div>'''
new_settings = '''      <div class="setgroup">
        <div class="setlabel">Game mode</div>
        <div class="setrow"><button class="setopt" id="modeLineSet">Line Haul</button><button class="setopt" id="modeTightSet">Tight Pack</button></div>
        <div class="setlabel diffsetlabel">Difficulty</div>
        <div class="setrow three"><button class="setopt" id="diffEasySet">Easy</button><button class="setopt" id="diffMediumSet">Medium</button><button class="setopt" id="diffHardSet">Hard</button></div>
        <div class="setnote" id="rulesNote">Easy: slower drop · 1,800 lb axle · Line Haul 12/16 · Tight Pack 9/16+.</div>
      </div>'''
one(old_settings, new_settings, "settings difficulty controls")

# Responsive landing/layout polish for the extra selector.
diff_css = r'''
  /* V60 difficulty selector: one compact choice layer, without shrinking the truck board. */
  #modehero{top:61.2%;padding:7px 10px 6px;}
  #modehero .headline{font-size:14px;margin-bottom:2px}#modehero .sub{font-size:8px;}
  #diffpick{position:absolute;z-index:8;left:6%;right:6%;top:69.1%;height:5.2%;min-height:39px;display:grid;grid-template-columns:repeat(3,1fr);gap:6px;}
  #diffpick button{height:100%;min-height:39px;padding:5px 5px;border-radius:11px;background:rgba(58,46,39,.94);border:1px solid rgba(255,255,255,.1);color:rgba(255,243,226,.88);box-shadow:0 5px 14px rgba(0,0,0,.24);}
  #diffpick button .diffk{display:block;font-size:9px;font-weight:1000;letter-spacing:.08em;line-height:1;}
  #diffpick button .diffd{display:block;font-size:6px;font-weight:800;opacity:.65;letter-spacing:.02em;text-transform:none;margin-top:4px;}
  #diffpick button.on{background:linear-gradient(180deg,#FF9A52,#F06B16);border-color:rgba(255,220,185,.45);color:#211711;box-shadow:0 2px 0 rgba(255,255,255,.16) inset,0 8px 20px rgba(0,0,0,.25);}
  #diffpick button.on .diffd{opacity:.82;}
  #modepick{top:75.0%;height:7.7%;min-height:58px;}
  #modepick button{min-height:56px;padding:6px 8px;}
  #modepick button .modek{font-size:6px;margin-bottom:3px}#modepick button .modet{font-size:11px}#modepick button .moded{font-size:7px;margin-top:3px;}
  .setrow.three{grid-template-columns:repeat(3,1fr)}
  .diffsetlabel{margin-top:8px!important;}
  @media(max-height:720px){
    #modehero{top:60.5%;left:5%;right:5%;padding:5px 8px 4px}#modehero .headline{font-size:12px}#modehero .sub{font-size:7px}
    #diffpick{top:68.3%;left:5%;right:5%;height:5.1%;min-height:35px}#diffpick button{min-height:35px;padding:4px 3px}#diffpick button .diffk{font-size:8px}#diffpick button .diffd{font-size:5.5px;margin-top:3px}
    #modepick{top:74.0%;left:5%;right:5%;height:8.2%;min-height:55px}#modepick button{min-height:53px;padding:5px 7px}#modepick button .moded{font-size:6.5px}
  }
'''
if '</style>' not in s:
    raise SystemExit("V60 difficulty patch stopped: missing style closing tag")
s = s.replace('</style>', diff_css + '\n</style>', 1)

# Difficulty selection logic and dynamic rules copy.
old_mode_funcs = '''function modeLabel(m){return m==="tight"?"TIGHT PACK":"LINE HAUL";}
function setSelectedMode(m){
  selectedMode=(m==="tight")?"tight":"line";
  writePref("junktris_mode",selectedMode);
  syncModeUI();syncSettingsUI();
}'''
new_mode_funcs = '''function modeLabel(m){return m==="tight"?"TIGHT PACK":"LINE HAUL";}
function difficultyLabel(d){return difficultyConfig(d).label;}
function setSelectedMode(m){
  selectedMode=(m==="tight")?"tight":"line";
  writePref("junktris_mode",selectedMode);
  best=loadBest(selectedDifficulty,selectedMode);syncBest();
  syncModeUI();syncDifficultyUI();syncSettingsUI();
}
function setSelectedDifficulty(d){
  selectedDifficulty=(d==="hard")?"hard":(d==="medium"?"medium":"easy");
  writePref("junktris_difficulty",selectedDifficulty);
  best=loadBest(selectedDifficulty,selectedMode);syncBest();
  syncDifficultyUI();syncSettingsUI();
}
function syncDifficultyUI(){
  var ids=["diffEasy","diffMedium","diffHard","diffEasySet","diffMediumSet","diffHardSet"];
  for(var di=0;di<ids.length;di++){var de=document.getElementById(ids[di]);if(de)de.classList.remove("on");}
  var suffix=selectedDifficulty==="hard"?"Hard":selectedDifficulty==="medium"?"Medium":"Easy";
  var a=document.getElementById("diff"+suffix);if(a)a.classList.add("on");
  var b=document.getElementById("diff"+suffix+"Set");if(b)b.classList.add("on");
  var c=difficultyConfig(selectedDifficulty),line=document.getElementById("lineRule"),tight=document.getElementById("tightRule"),note=document.getElementById("startnote"),rules=document.getElementById("rulesNote");
  if(line)line.textContent="Clear rows at "+c.clear+"/16.";
  if(tight)tight.textContent="Pack layers to "+c.pack+"/16+.";
  if(note)note.textContent=c.label+" · "+(selectedMode==="tight"?"Tight Pack":"Line Haul")+" · "+c.speed.toLowerCase();
  if(rules)rules.textContent=c.label.charAt(0)+c.label.slice(1).toLowerCase()+": "+(c.gravity<1?Math.round((1-c.gravity)*100)+"% slower drop · ":"")+c.wt.toLocaleString()+" lb axle · Line Haul "+c.clear+"/16 · Tight Pack "+c.pack+"/16+.";
}'''
one(old_mode_funcs, new_mode_funcs, "difficulty selection functions")

# Make Settings highlighting include the difficulty choice.
one(
    'var ids=["handR","handL","musOn","musOff","trackGarage","trackHeavy","trackNight","modeLineSet","modeTightSet"];',
    'var ids=["handR","handL","musOn","musOff","trackGarage","trackHeavy","trackNight","modeLineSet","modeTightSet","diffEasySet","diffMediumSet","diffHardSet"];',
    "settings highlight ids",
)
one(
    '  var gm=document.getElementById(selectedMode==="tight"?"modeTightSet":"modeLineSet");if(gm)gm.classList.add("on");\n}',
    '  var gm=document.getElementById(selectedMode==="tight"?"modeTightSet":"modeLineSet");if(gm)gm.classList.add("on");\n  var ds=selectedDifficulty==="hard"?"diffHardSet":selectedDifficulty==="medium"?"diffMediumSet":"diffEasySet";var df=document.getElementById(ds);if(df)df.classList.add("on");\n}',
    "settings difficulty highlight",
)

# Bind both landing and Settings difficulty controls.
one(
    'bindBtn("modeTightSet",function(){setSelectedMode("tight");});',
    'bindBtn("modeTightSet",function(){setSelectedMode("tight");});\n'
    'bindBtn("diffEasy",function(){setSelectedDifficulty("easy");});\n'
    'bindBtn("diffMedium",function(){setSelectedDifficulty("medium");});\n'
    'bindBtn("diffHard",function(){setSelectedDifficulty("hard");});\n'
    'bindBtn("diffEasySet",function(){setSelectedDifficulty("easy");});\n'
    'bindBtn("diffMediumSet",function(){setSelectedDifficulty("medium");});\n'
    'bindBtn("diffHardSet",function(){setSelectedDifficulty("hard");});',
    "difficulty button bindings",
)

# Apply selected difficulty at the start of every truck/restart and load the matching best score.
one(
    'function reset(){\n  gameMode=selectedMode;tightRowBest=[];endSnapshot=null;',
    'function reset(){\n  gameMode=selectedMode;gameDifficulty=selectedDifficulty;applyDifficulty();best=loadBest(gameDifficulty,gameMode);syncBest();tightRowBest=[];endSnapshot=null;',
    "difficulty application on reset",
)
one(
    '  gravity=Math.min(4.8,1.32+0.22*(truckNo-1));',
    '  var dc0=difficultyConfig(gameDifficulty);gravity=Math.min(4.8*dc0.gravity,(1.32+0.22*(truckNo-1))*dc0.gravity);',
    "reset gravity scaling",
)
one(
    '  pops.push({x:ox+cell*CW/2,y:oy+cell*4,t:1.6,txt:modeLabel(gameMode)+" · TRUCK #"+truckNo,c:"#FFD24A"});',
    '  pops.push({x:ox+cell*CW/2,y:oy+cell*4,t:1.6,txt:difficultyLabel(gameDifficulty)+" · "+modeLabel(gameMode)+" · TRUCK #"+truckNo,c:"#FFD24A"});',
    "difficulty start label",
)

# Slow gravity and extend lock delay on Easy/Medium. Hard is mathematically identical to V59.
one(
    '  gravity=Math.min(5.4,1.32+0.22*(truckNo-1)+0.13*Math.floor((dropped||0)/4)+fillPct()*0.012);',
    '  var dc=difficultyConfig(gameDifficulty);gravity=Math.min(5.4*dc.gravity,(1.32+0.22*(truckNo-1)+0.13*Math.floor((dropped||0)/4)+fillPct()*0.012)*dc.gravity);',
    "spawn gravity scaling",
)
one(
    'if(ny>=ly){ active.py=ly; active.lock+=dt; if(active.lock>=0.45)lockPiece(); }',
    'if(ny>=ly){ active.py=ly; active.lock+=dt; if(active.lock>=difficultyConfig(gameDifficulty).lock)lockPiece(); }',
    "difficulty lock delay",
)

# Friendlier queue mix on Easy/Medium. Keep Hard exactly at the V59 weighting.
one(
    '    else w*=1+prog*.14;\n    ws.push(w);tot+=w;',
    '''    else w*=1+prog*.14;
    if(gameDifficulty==="easy"){
      if(key==="shed")w*=((dropped||0)<8?.02:.18);
      else if(key==="fridge"||key==="couch"||key==="mattress"||key==="dresser")w*=.60;
      else if(key==="washer"||key==="dryer"||key==="oven")w*=.82;
      else if(key==="trash"||key==="micro"||key==="recliner"||key==="twin"||key==="lamp")w*=1.28;
    }else if(gameDifficulty==="medium"){
      if(key==="shed")w*=((dropped||0)<6?.22:.55);
      else if(key==="fridge"||key==="couch"||key==="mattress"||key==="dresser")w*=.82;
      else if(key==="trash"||key==="micro"||key==="recliner"||key==="twin"||key==="lamp")w*=1.12;
    }
    ws.push(w);tot+=w;''',
    "difficulty spawn weighting",
)

# Initial landing selection/rules should reflect Easy by default (or the saved preference).
one('best=loadBest();syncBest();', 'best=loadBest();syncBest();syncDifficultyUI();', "initial difficulty UI sync")

# Static V60 release-candidate audit. The public V59 build is built separately and unaffected.
checks = {
    "Easy target 12/16": 'return {label:"EASY",clear:12,pack:9,wt:1800,gravity:.60,lock:.70' in s,
    "Medium target 14/16": 'return {label:"MEDIUM",clear:14,pack:11,wt:1600,gravity:.80,lock:.55' in s,
    "Hard preserves V59 rules": 'return {label:"HARD",clear:16,pack:12,wt:1400,gravity:1,lock:.45' in s,
    "difficulty landing picker": 'id="diffpick"' in s,
    "difficulty settings controls": 'id="diffEasySet"' in s and 'id="diffMediumSet"' in s and 'id="diffHardSet"' in s,
    "difficulty best-score separation": 'junktris_best_' in s and 'bestKey' in s,
    "difficulty applied on reset": 'gameDifficulty=selectedDifficulty;applyDifficulty()' in s,
    "difficulty gravity scaling": 'difficultyConfig(gameDifficulty);gravity=' in s,
    "difficulty lock delay": 'difficultyConfig(gameDifficulty).lock' in s,
    "Easy friendly queue": 'gameDifficulty==="easy"' in s and 'key==="shed"' in s,
    "three curb choices retained": 'for(var i=0;i<3;i++)' in s,
    "Shed retained": 'shed:{name:"Shed"' in s,
    "Junk Hauler guide retained": "Junk Hauler's Guide" in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("V60 audit failed: " + "; ".join(failed))

# Parse inline JavaScript if Node is available.
node = shutil.which("node")
if node:
    blocks = re.findall(r'<script>(.*?)</script>', s, flags=re.S)
    for idx, block in enumerate(blocks, 1):
        with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as tf:
            tf.write(block); name = tf.name
        try:
            cp = subprocess.run([node, '--check', name], text=True, capture_output=True)
            if cp.returncode != 0:
                raise SystemExit(f"V60 audit failed: JavaScript block {idx}: {cp.stderr.strip()}")
        finally:
            Path(name).unlink(missing_ok=True)

out.write_text(s, encoding="utf-8")
out.with_name("v60-audit.txt").write_text("V60 DIFFICULTY AUDIT: PASS\n" + "\n".join("PASS - "+k for k in checks) + "\n", encoding="utf-8")
print("V60 DIFFICULTY AUDIT: PASS")
for k in checks: print("PASS -", k)
