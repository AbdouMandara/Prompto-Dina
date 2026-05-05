# Prompto-Dina

Projet de démonstration d’un Prompt Builder intelligent.

## Architecture

- `front_end/` : interface Vue 3 avec un wizard de création de prompt.
- `back_end/` : API FastAPI modulaire.
  - `back_end/core/` : configuration et paramètres d’environnement.
  - `back_end/services/` : services métier pour la génération de prompt, providers IA et schémas.
  - `back_end/.env` : token API et paramètres secrets.

## Démarrage

1. Backend :
   - activez l’environnement Python dans `back_end/.venv`
   - installez `fastapi`, `uvicorn`, `pydantic` et `httpx`
   - définissez `HF_TOKEN` dans `back_end/.env`
   - lancez `fastapi dev main.py --port 8000`

2. Frontend :
   - lancez `npm run dev`
   - installez les dépendances dans `front_end/`
   - lancez `npm run dev`

Le frontend communique avec le backend via `/generate_prompt`, `/test_prompt` et `/refine_prompt`.
