# Repair block evidence bundle

Read first: `../FINAL_REVIEW.md`, then `../stage2-summary.md`.

## Plan and gates
- `../experiment-plan.md`: Entries 1, 1a, 1b, 1c and 2, append-only; every amendment is made before the outputs it affects.
- `../reviews/` holds every gate report:
  - plan (Opus);
  - prompt and renderer (Opus);
  - Stage 1 results (Opus, Sonnet);
  - Stage 2 results (Opus, Sonnet).

## Stage 1
- `prompts/pilot-v2.2/unit_system.txt`: the one revision, v2.1 plus one section. Its hash is in the freeze.
- Code changes:
  - `src/vomi/pilot.py`: `numbered_public_model`, r7 `task_card`, `matched_notes_text`;
  - `src/vomi/unit_schema.py`: `validate_unit_output_v22`;
  - tests: `tests/test_repair_stage1.py`.
- Regression check: `../stage1-regress-*.json` (development, inspected states) and `../stage1-regress-R1-addendum.json`.
- Planning: `../power.md` / `../power.json` (precision simulation; K = 24; limitations).
- Symbolic qualification: `../stage2-qualification.json` (576 fresh-seed states, all pass).
- Freeze: `../stage1-freeze.json` (commit `27c324e`).

## Stage 2
- Note proof: `../stage2-notes-freeze.json`, committed before any policy call. Payloads are in gitignored `data/repair-block/`.
- Pre-declared analysis: `../stage2-results.md` / `.json` (`scripts/report_repair_stage2.py`).
- `episodes-stage2.csv`: 4,032 episodes, one row each.
- `stage2-example-episodes.json`: the 3b and 2b ×4 traces cited in the summary, for the none and reference conditions.
- `stage2-manifest.json`: the run manifest.

## Hashes
- `hashes.json` gives sha256 for every file of this block. The CSV is written with LF line endings.
