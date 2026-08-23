
## Amendment — 2026-08-21 — timestamp handling in the Arm B join

Protocol section 3 specified a join key rounded to the second. Notebook 02 showed
the original release records timestamps at MINUTE resolution on a 12-hour clock
with no AM/PM marker. Changes, fixed before any label comparison was computed:

- join key uses minute resolution (the finest the original supports)
- parsed hours 1-7 in the original interpreted as PM (+12h): 1,248,917 rows
- clock fix applied to improved: 0 rows
- constant shift applied to original clock: -6h
  (selected by match-count peak on Monday; full search in match_calibration.json)

These are data-format corrections, not analysis choices; the label comparison had
not been run when they were fixed.

## Amendment — 2026-08-21 — Arm B join key

Protocol section 3 specified a directed 5-tuple key rounded to the second.
Diagnostics on the real data (03b) established three format facts, all fixed
before any label comparison was computed:

1. The original release MIXES timestamp formats across its own files (some
   files carry seconds, some do not). Whole-column format inference in pandas
   therefore silently voided entire files — 18.72% NaT, exactly Monday's share
   of the corpus — until per-element parsing (format='mixed') was used. It also
   records timestamps at MINUTE resolution in several files, on a 12-hour clock
   with no AM/PM marker; hours 1-7 were repaired to PM
   (1,471,716 rows).
2. The improved release's clock runs +3h
   relative to the original (minute-sets overlap perfectly at that shift;
   original is Atlantic local time, the regenerated release is consistent with
   UTC). The shift was found by search and applied to the original.
3. The original's flow direction is inconsistent (server->client rows exist;
   8,239 distinct Monday src IPs vs 90 in the improved). The key therefore uses
   canonically ordered endpoints, matching flows regardless of direction.

Join key: (sorted endpoint pair, protocol, minute). Ambiguous keys (repeated
within a version) are dropped and the retention reported.
