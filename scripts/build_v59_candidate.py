from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v59_candidate.py SOURCE_HTML OUTPUT_HTML")

src_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
s = src_path.read_text(encoding="utf-8")


def one(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"V59 patch stopped: expected exactly one {label}, found {count}")
    s = s.replace(old, new, 1)

# Candidate identity only. V58 remains untouched.
one("<title>Junktris</title>", "<title>Junktris — V59 Candidate</title>", "page title")
one("BUILD V58 FINAL · AUG 22", "BUILD V59 CANDIDATE · AUG 23", "build stamp")
one("JUNKTRIS v58 FINAL", "JUNKTRIS v59 CANDIDATE", "internal build label")

# Locked roster changes.
one(
    'loveseat:{name:"2-Seat Couch",wt:135,soft:1,squishAt:105,art:"couch",mask:["####","####"],comp:["####"]}',
    'loveseat:{name:"Loveseat",wt:135,soft:1,squishAt:105,art:"couch",mask:["####","####"],comp:["####"]}',
    "loveseat label",
)
one(
    'recliner:{name:"Recliner",wt:95,soft:1,squishAt:85,art:"chair",mask:["###","###"],comp:["###"]}',
    'recliner:{name:"Recliner",wt:95,soft:1,squishAt:85,art:"recliner",mask:["###","###"],comp:["###"]}',
    "recliner art mapping",
)
one(
    'dryer:{name:"Dryer",wt:130,art:"washer",mask:["###","###","###"]}',
    'dryer:{name:"Dryer",wt:130,art:"dryer",mask:["###","###","###"]}',
    "dryer art mapping",
)
one(
    '  table:{name:"Dining Table",wt:75,art:"bench",mask:["#####","#####"]},\n',
    '',
    "dining table definition",
)
one(
    '  lamp:{name:"Floor Lamp",wt:12,frag:1,crush:30,art:"lamp",mask:["#","#","#","#"]}\n};',
    '  lamp:{name:"Floor Lamp",wt:12,frag:1,crush:30,art:"lamp",mask:["#","#","#","#"]},\n'
    '  shed:{name:"Shed",wt:420,art:"shed",mask:["######","######","######","######"],bonus:450,rare:1}\n};',
    "shed definition insertion",
)
one(
    'var POOL=["trash","micro","recliner","loveseat","twin","washer","dryer","coffee","tv","oven","dresser","mattress","table","couch","fridge","lamp"];\n'
    'var WEIGHTS=[13,11,11,11,10,9,9,10,7,7,6,6,7,6,3,3];',
    'var POOL=["trash","micro","recliner","loveseat","twin","washer","dryer","coffee","tv","oven","dresser","mattress","shed","couch","fridge","lamp"];\n'
    'var WEIGHTS=[13,11,11,11,10,9,9,10,7,7,6,6,1.4,6,3,3];',
    "spawn pool",
)
one(
    'if(key==="couch"||key==="fridge"||key==="dresser"||key==="mattress"||key==="table")w*=.76+prog*.66;',
    'if(key==="couch"||key==="fridge"||key==="dresser"||key==="mattress"||key==="shed")w*=.76+prog*.66;',
    "large anchor weighting",
)
one(
    'if(k==="dresser"||k==="coffee"||k==="table")return "wood";',
    'if(k==="dresser"||k==="coffee"||k==="shed")return "wood";',
    "wood material mapping",
)

# Recliner: unmistakably upholstered, no table-like legs.
recliner_art = r'''    else if(kind==="recliner"){
    c.fillStyle=grad(c,x,y,w,h,"#A87852","#6A472D");
    rr(c,x+w*.12,y+h*.04,w*.76,h*.5,u*.09);c.fill();c.stroke();
    c.fillStyle=grad(c,x,y+h*.34,w,h*.45,"#B9855B","#744D31");
    rr(c,x+w*.13,y+h*.38,w*.74,h*.37,u*.08);c.fill();c.stroke();
    c.fillStyle=grad(c,x,y+h*.3,w,h*.42,"#9B6B46","#5E3E28");
    rr(c,x+w*.02,y+h*.31,w*.18,h*.43,u*.07);c.fill();c.stroke();
    rr(c,x+w*.8,y+h*.31,w*.18,h*.43,u*.07);c.fill();c.stroke();
    c.fillStyle=grad(c,x,y+h*.68,w,h*.3,"#9A6947","#5A3A27");
    rr(c,x+w*.29,y+h*.72,w*.42,h*.23,u*.06);c.fill();c.stroke();
    c.strokeStyle="rgba(66,40,24,.5)";c.lineWidth=Math.max(1,u*.025);
    c.beginPath();c.moveTo(x+w*.26,y+h*.2);c.quadraticCurveTo(x+w*.5,y+h*.11,x+w*.74,y+h*.2);c.stroke();
    c.fillStyle="#30231A";rr(c,x+w*.84,y+h*.56,w*.035,h*.17,u*.015);c.fill();
  }
'''
one('    else if(kind==="mattress"){', recliner_art + '    else if(kind==="mattress"){', "recliner draw branch")

# Dryer: clearly distinct from the washer, with a large rectangular dryer door.
dryer_art = r'''    else if(kind==="dryer"){
    c.fillStyle=grad(c,x,y,w,h,"#D5D6D3","#969995");
    rr(c,x+w*.01,y+h*.01,w*.98,h*.98,u*.055);c.fill();c.stroke();
    c.fillStyle=grad(c,x,y,w,h*.24,"#D9DBD8","#A3A6A2");
    rr(c,x+w*.04,y+h*.04,w*.92,h*.2,u*.03);c.fill();c.stroke();
    c.fillStyle="#4A4F50";c.beginPath();c.arc(x+w*.73,y+h*.14,Math.max(2,u*.075),0,7);c.fill();
    c.fillStyle="#697174";rr(c,x+w*.13,y+h*.09,w*.3,h*.09,u*.02);c.fill();
    c.fillStyle="#B8BBB7";rr(c,x+w*.12,y+h*.32,w*.76,h*.53,u*.055);c.fill();c.stroke();
    c.fillStyle="#888D8C";rr(c,x+w*.2,y+h*.39,w*.6,h*.38,u*.045);c.fill();
    c.fillStyle="rgba(255,255,255,.17)";rr(c,x+w*.23,y+h*.42,w*.54,h*.09,u*.025);c.fill();
    c.fillStyle="#5C6262";rr(c,x+w*.14,y+h*.43,w*.035,h*.25,u*.015);c.fill();
  }
'''
one('  else if(kind==="tv"){', dryer_art + '  else if(kind==="tv"){', "dryer draw branch")

# Rare 6x4 shed: oversized, box-tight, front-facing double doors.
shed_art = r'''  else if(kind==="shed"){
    c.fillStyle=grad(c,x,y+h*.2,w,h*.8,"#B79A72","#7A5D3F");
    rr(c,x+w*.035,y+h*.22,w*.93,h*.75,u*.035);c.fill();c.stroke();
    c.fillStyle="#49382D";
    c.beginPath();c.moveTo(x+w*.01,y+h*.27);c.lineTo(x+w*.5,y+h*.02);c.lineTo(x+w*.99,y+h*.27);c.closePath();c.fill();c.stroke();
    c.fillStyle="#6F5845";
    c.beginPath();c.moveTo(x+w*.08,y+h*.26);c.lineTo(x+w*.5,y+h*.075);c.lineTo(x+w*.92,y+h*.26);c.closePath();c.fill();
    c.strokeStyle="rgba(72,52,36,.48)";c.lineWidth=Math.max(1,u*.018);
    for(var sl=1;sl<12;sl++){var sx=x+w*(.04+sl*.077);c.beginPath();c.moveTo(sx,y+h*.28);c.lineTo(sx,y+h*.95);c.stroke();}
    c.fillStyle="#927451";rr(c,x+w*.27,y+h*.42,w*.46,h*.53,u*.02);c.fill();c.stroke();
    c.strokeStyle="#443328";c.lineWidth=Math.max(1.5,u*.026);c.beginPath();c.moveTo(x+w*.5,y+h*.43);c.lineTo(x+w*.5,y+h*.94);c.stroke();
    c.fillStyle="#31261F";rr(c,x+w*.46,y+h*.63,w*.08,h*.055,u*.015);c.fill();
    c.fillStyle="#3C3027";rr(c,x+w*.43,y+h*.13,w*.14,h*.08,u*.015);c.fill();
    c.strokeStyle="rgba(230,210,178,.35)";c.lineWidth=Math.max(1,u*.014);
    for(var sv=1;sv<4;sv++){c.beginPath();c.moveTo(x+w*.45,y+h*(.145+sv*.014));c.lineTo(x+w*.55,y+h*(.145+sv*.014));c.stroke();}
  }
'''
one('  else if(kind==="lamp"){', shed_art + '  else if(kind==="lamp"){', "shed draw branch")

# The shed is a lucrative awkward job. Keep the exact bonus provisional for playtesting.
one(
    '  var pts=Math.round(40+it.def.wt*0.15);',
    '  var pts=Math.round(40+it.def.wt*0.15);\n'
    '  if(it.key==="shed"){pts+=(it.def.bonus||0);pop(it,"SHED JOB!  BIG LOAD · BIG PAYOUT","#FFD24A",1.22);sfx("haul");}',
    "shed placement bonus",
)

# Junk Hauler's Guide UI. It draws from the same DEFS + drawArt routine as gameplay.
guide_css = r'''
  /* V59 Junk Hauler's Guide */
  .setwide{grid-column:1/-1;background:linear-gradient(180deg,#6B4934,#4A3125)!important;border-color:rgba(255,122,41,.5)!important;color:#FFF3E2!important;}
  #guidev{position:fixed;inset:0;z-index:86;display:none;padding:10px;background:rgba(8,7,6,.96);backdrop-filter:blur(5px);}
  #guidev.show{display:flex;align-items:center;justify-content:center;}
  #guidepanel{width:min(100%,520px);height:min(94vh,850px);display:flex;flex-direction:column;overflow:hidden;border-radius:18px;background:linear-gradient(180deg,#2A211C,#15100D);border:1px solid rgba(255,255,255,.1);box-shadow:0 24px 60px rgba(0,0,0,.55);}
  .guidehead{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;padding:12px;border-bottom:1px solid rgba(255,122,41,.2);}
  .guidetitle{font-size:18px;font-weight:1000;letter-spacing:-.02em}.guidesub{font-size:8px;font-weight:900;letter-spacing:.16em;text-transform:uppercase;color:var(--orange);margin-top:2px;}
  #gclose{flex:none;width:36px;height:36px;padding:0;border-radius:10px;font-size:16px;background:#493A32;}
  #guidegrid{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;display:grid;grid-template-columns:1fr 1fr;gap:7px;padding:9px;align-content:start;}
  .gcard{min-width:0;border-radius:11px;padding:7px;background:linear-gradient(180deg,#342720,#241B16);border:1px solid rgba(255,255,255,.07);text-align:center;}
  .gcanvas{display:block;width:100%;height:76px;background:radial-gradient(circle at 50% 35%,rgba(255,183,112,.09),transparent 62%);border-radius:8px;}
  .gname{margin-top:5px;font-size:10px;font-weight:1000;line-height:1.05;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}.gmeta{margin-top:3px;font-size:7px;color:var(--silver);}.gtag{margin-top:3px;font-size:6px;font-weight:1000;letter-spacing:.08em;color:#FFD24A;min-height:7px;}
  @media(min-width:430px){#guidegrid{grid-template-columns:repeat(4,1fr)}.gcanvas{height:86px}}
'''
one('</style>', guide_css + '\n</style>', "style closing tag")

settings_tail = '''        <div class="setnote">All music is synthesized inside the game, so the HTML still works offline.</div>\n      </div>\n    </div>\n  </div>'''
settings_new = '''        <div class="setnote">All music is synthesized inside the game, so the HTML still works offline.</div>\n      </div>\n      <div class="setgroup">\n        <div class="setlabel">Know your junk</div>\n        <div class="setrow"><button class="setopt setwide" id="junkguide">Junk Hauler's Guide</button></div>\n      </div>\n    </div>\n  </div>'''
one(settings_tail, settings_new, "settings guide button")

guide_html = r'''

  <div id="guidev" aria-hidden="true">
    <div id="guidepanel" role="dialog" aria-label="Junk Hauler's Guide">
      <div class="guidehead"><div><div class="guidetitle">Junk Hauler's Guide</div><div class="guidesub">Know Your Junk</div></div><button id="gclose" aria-label="Close Junk Hauler's Guide">✕</button></div>
      <div id="guidegrid"></div>
    </div>
  </div>
'''
one('<script>\n(function(){', guide_html + '\n<script>\n(function(){', "main script opening")

guide_js = r'''
function renderJunkGuide(){
  var host=document.getElementById("guidegrid");if(!host)return;host.innerHTML="";
  var order=["fridge","oven","micro","tv","couch","loveseat","recliner","twin","mattress","dresser","coffee","washer","dryer","trash","lamp","shed"];
  for(var gi=0;gi<order.length;gi++){
    var key=order[gi],d=DEFS[key];if(!d)continue;
    var card=document.createElement("div");card.className="gcard";
    var cvg=document.createElement("canvas");cvg.className="gcanvas";cvg.width=260;cvg.height=150;card.appendChild(cvg);
    var cg=safeCtx(cvg.getContext("2d")),dm=dims(d.mask),unit=Math.min(220/dm.w,108/dm.h),pw=dm.w*unit,ph=dm.h*unit,x=(260-pw)/2,y=(122-ph)/2+5;
    cg.clearRect(0,0,260,150);cg.save();cg.globalAlpha=.28;cg.fillStyle=key==="shed"?"#A8794A":matColor({key:key,def:d});rr(cg,x,y,pw,ph,Math.min(5,unit*.12));cg.fill();cg.restore();
    drawArt(cg,d.art,x,y,pw,ph,0,false);
    var nm=document.createElement("div");nm.className="gname";nm.textContent=d.name;card.appendChild(nm);
    var mt=document.createElement("div");mt.className="gmeta";mt.textContent=dm.w+" × "+dm.h+" · "+d.wt+" lb";card.appendChild(mt);
    var tg=document.createElement("div");tg.className="gtag";
    if(key==="shed")tg.textContent="VERY RARE · BIG JOB BONUS";else if(d.frag)tg.textContent="FRAGILE";else if(d.soft)tg.textContent="SOFT";else if(d.wt>=180)tg.textContent="HEAVY";else tg.innerHTML="&nbsp;";
    card.appendChild(tg);host.appendChild(card);
  }
}
function openJunkGuide(){
  var s=document.getElementById("settingsv"),g=document.getElementById("guidev");if(!g)return;
  if(s)s.classList.remove("show");renderJunkGuide();g.classList.add("show");g.setAttribute("aria-hidden","false");
}
function closeJunkGuide(){
  var s=document.getElementById("settingsv"),g=document.getElementById("guidev");if(g){g.classList.remove("show");g.setAttribute("aria-hidden","true");}if(s)s.classList.add("show");
}

'''
one('function sfx(k){', guide_js + 'function sfx(k){', "guide functions insertion")
one('bindBtn("sclose",closeSettings);', 'bindBtn("sclose",closeSettings);\nbindBtn("junkguide",openJunkGuide);\nbindBtn("gclose",closeJunkGuide);', "guide button bindings")

# Sanity checks: final roster has exactly 16 active keys and no Dining Table definition.
for must in ['name:"Shed"', 'art:"recliner"', 'art:"dryer"', 'Junk Hauler\'s Guide', 'BUILD V59 CANDIDATE']:
    if must not in s:
        raise SystemExit(f"V59 patch stopped: missing expected output marker {must}")
if 'name:"Dining Table"' in s:
    raise SystemExit("V59 patch stopped: Dining Table still present")

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(s, encoding="utf-8")
print(f"Built {out_path} from preserved V58 ({len(s):,} chars)")
