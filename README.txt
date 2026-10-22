CRYPTOTRACE — PROFESSIONAL SIMULATED WEBSITE

WHAT THIS PACKAGE CONTAINS
- app.py: Flask backend + page routes and demo data
- requirements.txt: Python dependencies
- Procfile / render.yaml: deployment configuration for Render

FEATURES
- Professional dark dashboard
- Login and create-account page (registration returns to login)
- Dashboard metrics and recent transactions
- Transaction history
- Simulated send BTC form with balance validation
- Receive/demo wallet label
- Wallet/transaction lookup
- Transaction relationship visualization
- Addable contacts
- Profile/display settings and logout

RUN LOCALLY (Windows)
1. Install Python 3.10 or newer from python.org if it is not installed.
2. Extract this ZIP folder. Open Command Prompt inside the extracted folder.
3. Run: py -m pip install -r requirements.txt
4. Run: py app.py
5. Open http://127.0.0.1:5000 in Chrome.
6. Login: username demo  |  password demo123

HOST AS A WEBSITE LINK (RENDER)
1. Upload app.py, requirements.txt, Procfile, and render.yaml to a new GitHub repository.
2. Sign in to Render and choose New > Web Service; connect that repository.
3. Build command: pip install -r requirements.txt
4. Start command: gunicorn app:app
5. Deploy and open the URL Render gives you.

IMPORTANT DEMO LIMITATIONS
This is an educational simulation only. No real Bitcoin, wallet keys, or live blockchain APIs are used. Demo data is stored in memory and may reset when the app restarts. Do not use real credentials or real funds. The prototype is not production-ready.
