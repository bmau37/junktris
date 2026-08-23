from pathlib import Path
import subprocess, sys

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v59_pwa.py SOURCE_HTML OUTPUT_HTML")

src = Path(sys.argv[1])
out = Path(sys.argv[2])
base = Path(__file__).with_name("build_v59_audio_probe.py")
subprocess.run([sys.executable, str(base), str(src), str(out)], check=True)
s = out.read_text(encoding="utf-8")


def one(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"V59 PWA build stopped: expected one {label}, found {count}")
    s = s.replace(old, new, 1)

# Installable game metadata. Installed/Add-to-Home-Screen Chromium apps are the
# supported route for direct landing-page audible autoplay on Android.
head_add = '''\n<link rel="manifest" href="./junktris.webmanifest">\n<link rel="icon" type="image/png" sizes="192x192" href="./pwa/icon-192.png">\n<link rel="apple-touch-icon" href="./pwa/icon-192.png">'''
one('</head>', head_add + '\n</head>', 'head closing tag')

# Register offline/install support. Keep it silent and invisible in the game UI.
register = r'''
if('serviceWorker' in navigator){
  window.addEventListener('load',function(){
    navigator.serviceWorker.register('./sw.js',{scope:'./'}).catch(function(){});
  });
}
'''
one('window.addEventListener("resize",function(){layout();drawStartArt();});', register + '\nwindow.addEventListener("resize",function(){layout();drawStartArt();});', 'service worker registration anchor')

# If launched as an installed app, make an extra autoplay attempt immediately and
# again on pageshow. The existing media element still carries the autoplay attribute.
pwa_audio = r'''
function isInstalledJunktris(){
  return (window.matchMedia&&window.matchMedia('(display-mode: standalone)').matches) ||
         (window.navigator.standalone===true) || /(?:\?|&)source=pwa(?:&|$)/.test(location.search);
}
if(isInstalledJunktris()){
  setTimeout(tryLandingMusic,0);
  window.addEventListener('pageshow',function(){setTimeout(tryLandingMusic,0);});
}
'''
one('function audioProbeEnabled(){', pwa_audio + '\nfunction audioProbeEnabled(){', 'installed PWA audio hook')

for marker in ['rel="manifest" href="./junktris.webmanifest"', "serviceWorker.register('./sw.js'", 'function isInstalledJunktris()']:
    if marker not in s:
        raise SystemExit(f"V59 PWA audit failed: missing {marker}")

out.write_text(s, encoding='utf-8')
print('V59 PWA BUILD: direct landing page, installable app support, no launch gate')
