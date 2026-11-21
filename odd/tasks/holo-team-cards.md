# Holo Team Cards — Backend presentation payload

Objective: Enrich team Pokemon API so the Angular `/equipo` Three.js holo card can render artwork, types, and foil metadata without inventing URLs client-side when the backend already has them.
Branch: `feature/holo-team-cards`
Delivery: ask-on-risk
Test runner: `pytest`

## Specs

- S1: "utilizar la librería threejs para mejorar el apartado de /equipo cuando salga la figura del pokemon que pueda ser una carta holo y en 3D"
- S2: "mejora la calidad de codigo y la interaccion"
- S3: Team responses should expose a stable presentation payload for holo cards (artwork URL, sprite URL, types, optional foil/rarity hint) without breaking existing clients that only read `pokemon_sprite` / `sprites`.
- S4: Prefer official artwork URL when the client sends it on add-to-team; persist and return it; keep backward compatibility with legacy single-sprite rows.
- S5: No database writes against production; migrations/schema changes only in code + local tests.

## Tasks

| ID | Specs | Route | Status | Evidence |
|----|-------|-------|--------|----------|
| T1 | S3,S4,S2 | delegated backend-lead | done | `pytest tests/test_holo_card_presentation.py -q` → 4 passed; fields `pokemon_artwork`, `pokemon_types`, `card_presentation` on POST/GET `/api/pokemon/team` |
| T2 | S2 | delegated backend-lead | done | DRY helper `app/utils/card_presentation.py`; removed duplicated `__init__` sprite blocks; schema_compat for nullable columns |

## Log

- L1: Con backend-lead y frontend-lead: threejs carta holo 3D en /equipo + calidad de código e interacción. Backend must support presentation fields for the card face.
- L2: 2026-11-21 — Implemented presentation payload. Added nullable `pokemon_artwork` + `pokemon_types` on `user_pokemon`, `pokemon_artwork` on `pokemon_team_members`. No Alembic; `ensure_holo_presentation_columns` for local/test SQLite. Existing DBs need ALTER (documented in `docs/holo-card-presentation.md`). Verification: `pytest tests/test_holo_card_presentation.py -q` → 4 passed. No production DB writes. Commit deferred (user did not request).
