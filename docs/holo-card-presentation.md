# Holo card presentation (team API)

Optional fields for Three.js holographic cards on `/equipo`.

## Request (`POST /api/team`)

| Field | Required | Notes |
|-------|----------|--------|
| `pokemon_sprite` | no | Existing sprite URL (kept) |
| `pokemon_artwork` | no | Official artwork URL; preferred for card face |
| `pokemon_types` | no | Now persisted on `user_pokemon` |

Same optional fields apply to saved-team members (`PokemonTeamMemberCreate`).

## Response extras

- `pokemon_artwork`, `pokemon_types` (nullable on legacy rows)
- `sprites` — legacy mirrored dict (unchanged shape)
- `card_presentation`:
  - `sprite_url`, `artwork_url`, `types`, `foil` (`holo` default; `shiny` if name/URL contains `shiny`)

## Existing databases

There is no Alembic in this repo (`create_all` only). Existing SQLite/MySQL DBs need:

```sql
ALTER TABLE user_pokemon ADD COLUMN pokemon_artwork VARCHAR(500);
ALTER TABLE user_pokemon ADD COLUMN pokemon_types JSON;
ALTER TABLE pokemon_team_members ADD COLUMN pokemon_artwork VARCHAR(500);
```

Or call `app.utils.schema_compat.ensure_holo_presentation_columns(engine)` in a controlled local/dev setup. Do not run against production without an explicit ops step.
