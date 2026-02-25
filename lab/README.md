# Lab Sandbox

Use this folder for quick experiments and prototypes (e.g., notebooks or scratch scripts) before wiring changes into the main app.

## How to run notebooks
1. Activate the project venv: `./venv/Scripts/activate`
2. Install deps (adds Jupyter/ipykernel): `pip install -r requirements.txt`
3. Launch VS Code and open the notebook you want to run (e.g., `lab/brochure_playground.ipynb`).
4. Select the venv kernel (`projects1` or the venv path) in the VS Code notebook UI.

## Environment
The notebook uses the same `.env` values as the app. If you want to exercise the Gemini LLM, ensure `APP_GOOGLE_API_KEY` and `APP_GEMINI_MODEL` are set. Without a key, the LLM step will be skipped.

## Safety
Keep experiments isolated here. When code graduates from the lab, move it into the `app/` or `routes/` packages and add tests.
