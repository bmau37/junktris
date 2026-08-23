from pathlib import Path
import subprocess, sys

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v59_launch_gate.py SOURCE_HTML OUTPUT_HTML")

# Compatibility shim: the launch-gate experiment is intentionally retired.
# Build the polished/audio-probe candidate directly so players always land on the
# real Junktris landing page. The installed PWA path handles zero-touch audio.
src = Path(sys.argv[1])
out = Path(sys.argv[2])
base = Path(__file__).with_name("build_v59_audio_probe.py")
subprocess.run([sys.executable, str(base), str(src), str(out)], check=True)
print("V59 launch gate retired; direct landing-page candidate built")
