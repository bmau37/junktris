from pathlib import Path
import re

# Compatibility wrapper for the first V60 difficulty builder.
# The original builder's replacement string for the per-difficulty high-score
# helpers accidentally emitted literal quote characters between JS functions.
# Patch the builder source before execution; all other guarded V60 rules/audits
# remain unchanged.

builder_path = Path(__file__).with_name("build_v60_difficulty.py")
code = builder_path.read_text(encoding="utf-8")

start = code.find("# Difficulty is independent from game mode. Hard intentionally preserves V59 gameplay.")
end = code.find("\nold_state =", start)
if start < 0 or end < 0:
    raise SystemExit("V60 fixed wrapper stopped: high-score patch block not found")

fixed_block = r'''# Difficulty is independent from game mode. Hard intentionally preserves V59 gameplay.
one(
    'function loadBest(){try{return +localStorage.getItem("junktris_best")||0}catch(e){return 0}}\n'
    'function saveBest(v){try{localStorage.setItem("junktris_best",String(v))}catch(e){}}',
    'function bestKey(d,m){return "junktris_best_"+(d||selectedDifficulty||"easy")+"_"+(m||selectedMode||"line");}\n'
    'function loadBest(d,m){try{d=d||selectedDifficulty||"easy";m=m||selectedMode||"line";var v=localStorage.getItem(bestKey(d,m));if(v!==null)return +v||0;if(d==="hard")return +localStorage.getItem("junktris_best")||0;return 0;}catch(e){return 0}}\n'
    'function saveBest(v,d,m){try{localStorage.setItem(bestKey(d||gameDifficulty,m||gameMode),String(v))}catch(e){}}',
    "difficulty-specific best-score storage",
)
'''

code = code[:start] + fixed_block + code[end:]
exec(compile(code, str(builder_path), "exec"), {"__name__": "__main__", "__file__": str(builder_path)})
