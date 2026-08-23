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
