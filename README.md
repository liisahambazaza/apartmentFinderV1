<<<<<<< HEAD
# apartmentFinderV1
=======
# NYC Apartment Recommender — Starter

This is a minimal FastAPI scaffold that demonstrates using NYC area data to produce apartment recommendations based on preselected budget

Quick start (macOS):

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
uvicorn app.main:app --reload --port 8000
```

3. Open http://localhost:8000 in your browser.

Files of interest:
- File: app/main.py (FastAPI app)
- File: app/data.py (data loading + simple recommender)
- File: data/sample_nyc.csv (small sample dataset)
- File: templates/index.html (basic frontend)

>>>>>>> 3958a45 (Initial commit)
