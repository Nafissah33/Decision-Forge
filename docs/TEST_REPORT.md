# Test Report

Run with `pytest` from the repo root (Python 3.14, pytest 9.1.1, Streamlit 1.60).
**Result: 28 passed, 0 failed, about 0.3 s.**

| Test file | Tests | Result | What it verifies |
|---|---|---|---|
| `tests/test_commute_logic.py` | 14 | all passed | Normal cases, boundary cases, invalid inputs, changed inputs, graph/adjacency consistency |
| `tests/test_login_and_views.py` | 8 | all passed | Login rule on all combinations, truth table, traversals, De Morgan equivalence |
| `tests/test_campus_route_diagrams.py` (Nia) | 4 | all passed | Decision-tree and knowledge-graph output, adjacency match, changed priority |
| `tests/test_exhaustive.py` | 2 | all passed | Engines vs. an independent re-statement of the rules (below) |
| `tests/test_login_backend.py` (Mya) | 0 | n/a | A demo/print script with no assertions; its functions are covered in `test_login_and_views.py` |

## Measured results

- **Randomized comparison (commute):** 3,000 generated scenarios (seed 208), each with random
  deadline, budget, weather, priority and three options. In **3,000 of 3,000** cases the engine's
  eligible set and recommended option matched the independent reference implementation (0 mismatches).
- **Exhaustive (login):** all 2^3 = 8 combinations of P, V, L. `AccessGranted` is true in exactly 1
  of 8 rows (P = V = L = true), matching `P ∧ V ∧ L`.
- **Equivalence:** De Morgan's law `¬(P∧V∧L) ≡ ¬P∨¬V∨¬L` holds in all 8 rows (3 variables) and all
  16 rows (4 variables, S F D W).

## Boundary cases tested

| Case | Expected | Result |
|---|---|---|
| Arrival exactly at the deadline (08:30 vs 08:30) | not eligible (must be strictly before) | pass |
| Arrival 1 minute earlier | eligible | pass |
| Fare exactly equal to budget ($6 vs $6) | eligible | pass |
| Fare 1 cent over budget | not eligible | pass |
| Walking exactly at the limit (10 vs 10) | acceptable | pass |
| Walking 1 minute over | not acceptable | pass |
| Snow weather | walking never acceptable, no recommendation | pass |
| Bad time format, negative budget, unknown weather or priority | rejected with an error | pass |

## Changing one input changes the result

| Change | Before | After |
|---|---|---|
| Train service cancelled | train | bus |
| Priority earliest → cheapest | train | bus |
| Budget $10 → $4 | train | bus |
| Budget $4 → $2 | bus | no option |
| Login: lock account (L false) | Access Granted | Access Denied, contact support |

## Limitations

- The reference implementation restates the same written rules, so these tests show that the code
  follows the rules. They do not show that the rules themselves model real commutes correctly.
- No accuracy or performance claims are made beyond the numbers above.
- Streamlit screens were exercised in automated runs only; no formal user testing was done.
- Code-coverage percentage was not measured.
