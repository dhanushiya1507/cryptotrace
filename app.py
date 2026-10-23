
from flask import Flask, request, redirect, session, render_template_string, url_for
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = __import__("os").environ.get("SECRET_KEY", "cryptotrace-demo-secret-change-for-production")

# Demo-only in-memory data. Restarting the Colab runtime resets this data.
users = {
    "demo": {"password": "demo123", "balance": 2.5000, "name": "Demo Analyst"}
}
contacts = ["Alice Johnson", "Ravi Kumar", "Priya Sharma", "Michael Chen", "Sarah Wilson", "Arun Kumar"]
transactions = [
    {"id": "CT-1004", "date": "2026-10-21 10:30", "type": "Received", "from": "Alice Johnson", "to": "demo", "amount": 0.2500, "status": "Confirmed"},
    {"id": "CT-1003", "date": "2026-10-20 15:12", "type": "Sent", "from": "demo", "to": "Ravi Kumar", "amount": 0.0750, "status": "Confirmed"},
    {"id": "CT-1002", "date": "2026-10-19 09:42", "type": "Received", "from": "Priya Sharma", "to": "demo", "amount": 0.4000, "status": "Confirmed"},
]

BASE = """
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CryptoTrace | Blockchain Intelligence</title>
<style>
:root{--bg:#0a1020;--panel:#111b30;--panel2:#16233b;--line:#263651;--text:#edf3ff;--muted:#93a5c4;--cyan:#4de0d0;--blue:#6b8cff;--green:#39d98a;--red:#ff6b83}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 10% 0%,#18294b 0,transparent 34%),var(--bg);font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--text)}
a{color:inherit;text-decoration:none}.shell{display:flex;min-height:100vh}.sidebar{width:245px;background:rgba(11,18,34,.94);border-right:1px solid var(--line);padding:26px 17px;display:flex;flex-direction:column;gap:26px}
.brand{display:flex;align-items:center;gap:11px;font-size:20px;font-weight:800;letter-spacing:.2px;padding:0 10px}.logo{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,var(--cyan),var(--blue));display:grid;place-items:center;color:#081324;font-weight:900}
.brand small{display:block;color:var(--muted);font-size:10px;letter-spacing:2px;margin-top:3px}.navlabel{color:#667b9e;font-size:10px;letter-spacing:1.7px;padding:0 13px;margin-bottom:-14px}
.nav a{display:flex;gap:12px;align-items:center;padding:12px 13px;border-radius:11px;color:#a8b8d3;margin:3px 0;font-size:14px}.nav a:hover,.nav a.active{background:linear-gradient(90deg,#203653,#172841);color:#fff;border:1px solid #2b4768}.nav .ico{width:20px;text-align:center;color:var(--cyan);font-size:17px}
.sidefoot{margin-top:auto;border:1px solid var(--line);background:#101b2d;border-radius:14px;padding:14px;color:var(--muted);font-size:12px;line-height:1.6}
.main{flex:1;min-width:0;padding:27px clamp(16px,3vw,38px)}.topbar{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-bottom:28px}.eyebrow{color:var(--cyan);font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:700}.page-title{font-size:27px;font-weight:750;margin:7px 0 5px}.sub{color:var(--muted);font-size:13px}.userchip{display:flex;align-items:center;gap:10px;border:1px solid var(--line);background:var(--panel);padding:9px 13px;border-radius:14px;font-size:13px}.avatar{width:34px;height:34px;border-radius:11px;background:linear-gradient(135deg,#4de0d0,#6b8cff);display:grid;place-items:center;color:#081324;font-weight:800}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px}.card{background:linear-gradient(145deg,rgba(20,33,56,.98),rgba(14,24,42,.98));border:1px solid var(--line);border-radius:17px;padding:20px;box-shadow:0 12px 28px #00000014}.metriclabel{font-size:12px;color:var(--muted)}.metric{font-size:25px;font-weight:800;margin:12px 0 8px;letter-spacing:-.5px}.positive{color:var(--green)}.negative{color:var(--red)}.metricfoot{font-size:11px;color:var(--muted)}.cardhead{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:17px}.cardtitle{font-size:15px;font-weight:700}.pill{font-size:10px;border:1px solid #2d5261;background:#122e3a;color:var(--cyan);padding:5px 8px;border-radius:20px}
.contentgrid{display:grid;grid-template-columns:1.5fr 1fr;gap:16px;margin-top:16px}.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:12px}th{text-align:left;color:#7f93b4;font-weight:600;padding:12px 10px;border-bottom:1px solid var(--line);white-space:nowrap}td{padding:14px 10px;border-bottom:1px solid #202f48;white-space:nowrap}tr:last-child td{border-bottom:0}.status{padding:5px 8px;border-radius:20px;font-size:10px;color:var(--green);background:#14352f}.status.pending{color:#ffce78;background:#3a2e19}
.btn{border:0;cursor:pointer;border-radius:10px;padding:11px 15px;font-weight:700;font-size:12px;background:linear-gradient(135deg,var(--cyan),#73a1ff);color:#071425;display:inline-block}.btn.secondary{background:#1b2a43;border:1px solid #30435f;color:#eaf1ff}.btn.danger{background:#402337;color:#ffb5c1;border:1px solid #66364b}
.formgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.field{display:flex;flex-direction:column;gap:7px;margin-bottom:15px}.field label{font-size:12px;color:#9aacc8}.field input,.field select,.field textarea{width:100%;padding:12px 13px;border:1px solid #30415d;background:#0b1527;color:var(--text);border-radius:10px;outline:none}.field input:focus,.field select:focus{border-color:var(--cyan)}.notice{border:1px solid #37505e;background:#112a35;color:#b8f5e8;padding:12px 14px;border-radius:11px;font-size:12px;margin-bottom:16px}.empty{color:var(--muted);text-align:center;padding:26px}.contact{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-bottom:1px solid var(--line)}.contact:last-child{border-bottom:0}.contactname{font-size:13px;font-weight:650}.contactmeta{font-size:11px;color:var(--muted);margin-top:4px}
.authwrap{min-height:100vh;display:grid;grid-template-columns:1.1fr .9fr;background:var(--bg)}.authhero{padding:8vw;display:flex;flex-direction:column;justify-content:center;background:radial-gradient(circle at 20% 20%,#24496a,transparent 42%),linear-gradient(145deg,#101c34,#0a1020)}.authhero h1{font-size:clamp(35px,5vw,62px);line-height:1.08;margin:24px 0 15px}.authhero p{color:#a9bad6;max-width:500px;line-height:1.8}.authfeatures{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}.feature{padding:9px 12px;border:1px solid #2c405d;border-radius:30px;font-size:11px;color:#c3d4ee}.authformside{display:grid;place-items:center;padding:25px}.authbox{width:min(100%,390px)}.authbox h2{font-size:27px;margin-bottom:8px}.authbox>p{color:var(--muted);font-size:13px;margin-bottom:25px}.authbox .field{margin-bottom:16px}.authbox .btn{width:100%;margin-top:6px}.authlinks{display:flex;justify-content:space-between;font-size:12px;color:var(--cyan);margin-top:17px}.authnote{font-size:11px;color:#7589a9;line-height:1.7;margin-top:22px}
.chartbars{height:170px;display:flex;align-items:end;gap:13px;padding:12px 4px 0;border-bottom:1px solid var(--line)}.barpair{height:100%;display:flex;align-items:end;gap:4px;flex:1;justify-content:center}.bar{width:13px;border-radius:5px 5px 0 0;background:linear-gradient(180deg,var(--cyan),#317f99);min-height:5px}.bar.sent{background:linear-gradient(180deg,#8b9bff,#5361a9)}.chartlabels{display:flex;justify-content:space-around;color:var(--muted);font-size:10px;margin-top:9px}.legend{display:flex;gap:15px;color:var(--muted);font-size:11px}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--cyan);margin-right:5px}.dot.blue{background:#8b9bff}
.network{display:flex;justify-content:center;align-items:center;min-height:260px;background:radial-gradient(circle,#1a3450,#0c1729 65%);border-radius:13px;position:relative;overflow:hidden}.node{padding:14px;border-radius:14px;border:1px solid #3c7181;background:#13313e;text-align:center;font-size:12px;z-index:1}.node.mainnode{background:#1e3157;border-color:#718aff;box-shadow:0 0 30px #536cff40}.networkline{color:#6b8cff;font-size:22px;padding:0 9px}
.footer{color:#647b9d;font-size:10px;margin-top:22px;text-align:center}
@media(max-width:1000px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.contentgrid{grid-template-columns:1fr}.sidebar{width:205px}}
@media(max-width:680px){.shell{display:block}.sidebar{width:100%;padding:15px;gap:13px}.nav{display:flex;overflow:auto;gap:5px}.nav a{white-space:nowrap;padding:9px}.navlabel,.sidefoot{display:none}.main{padding:20px 14px}.grid{grid-template-columns:1fr 1fr}.metric{font-size:20px}.authwrap{grid-template-columns:1fr}.authhero{padding:30px}.authhero h1{font-size:36px}.authformside{padding:28px 20px}.formgrid{grid-template-columns:1fr}}
</style></head><body>
{% if not session.get('user') %}
<div class="authwrap"><section class="authhero"><div class="brand"><div class="logo">CT</div><div>CryptoTrace<small>BLOCKCHAIN INTELLIGENCE</small></div></div>
<h1>Clarity for every<br><span style="color:var(--cyan)">transaction.</span></h1><p>A professional simulated blockchain investigation workspace to explore wallet activity, trace transfers, and review transaction patterns — safely, without real cryptocurrency.</p>
<div class="authfeatures"><span class="feature">◈ Wallet analytics</span><span class="feature">⌁ Transaction tracking</span><span class="feature">◎ Network view</span></div></section>
<section class="authformside"><div class="authbox">{{ auth_content|safe }}</div></section></div>
{% else %}
<div class="shell"><aside class="sidebar"><div class="brand"><div class="logo">CT</div><div>CryptoTrace<small>BLOCKCHAIN INTELLIGENCE</small></div></div>
<div class="navlabel">WORKSPACE</div><nav class="nav">
<a class="{{'active' if page=='dashboard' else ''}}" href="/dashboard"><span class="ico">▦</span>Dashboard</a>
<a class="{{'active' if page=='transactions' else ''}}" href="/transactions"><span class="ico">↔</span>Transaction History</a>
<a class="{{'active' if page=='send' else ''}}" href="/send"><span class="ico">↗</span>Send BTC</a>
<a class="{{'active' if page=='receive' else ''}}" href="/receive"><span class="ico">↙</span>Receive BTC</a>
<a class="{{'active' if page=='analysis' else ''}}" href="/analysis"><span class="ico">⌕</span>Wallet Analysis</a>
<a class="{{'active' if page=='network' else ''}}" href="/network"><span class="ico">◎</span>Transaction Network</a>
<a class="{{'active' if page=='contacts' else ''}}" href="/contacts"><span class="ico">♧</span>Contacts</a>
<a class="{{'active' if page=='settings' else ''}}" href="/settings"><span class="ico">⚙</span>Settings</a>
</nav><div class="sidefoot"><b style="color:#dceaff">DEMO ENVIRONMENT</b><br>Simulated BTC only<br>No blockchain connection<br>No real funds are transferred.</div></aside>
<main class="main"><header class="topbar"><div><div class="eyebrow">Blockchain intelligence platform</div><div class="page-title">{{ title }}</div><div class="sub">{{ subtitle }}</div></div><div class="userchip"><div class="avatar">{{ session.user[0]|upper }}</div><div><b>{{ users[session.user].name }}</b><div style="color:var(--muted);font-size:11px">Demo analyst</div></div></div></header>
{% if flash %}<div class="notice">{{ flash }}</div>{% endif %}{{ content|safe }}<div class="footer">CRYPTOTRACE • SIMULATION MODE • EDUCATIONAL DEMO ONLY</div></main></div>
{% endif %}
</body></html>
"""

def page(title, subtitle, content, flash=""):
    return render_template_string(BASE, title=title, subtitle=subtitle, content=content,
                                  page=request.path.strip("/").split("/")[0] or "dashboard",
                                  flash=flash, users=users)

def auth_page(content):
    return render_template_string(BASE, auth_content=content, users=users)

LOGIN = """<div class="eyebrow">WELCOME BACK</div><h2>Sign in to CryptoTrace</h2><p>Access your simulated blockchain intelligence dashboard.</p>
<form method="post" action="/login"><div class="field"><label>USERNAME</label><input name="username" placeholder="Enter username" required autocomplete="username"></div>
<div class="field"><label>PASSWORD</label><input id="pw" name="password" type="password" placeholder="Enter password" required autocomplete="current-password"></div>
<label style="font-size:12px;color:#9aacc8"><input type="checkbox" onclick="document.getElementById('pw').type=this.checked?'text':'password'"> Show password</label>
<button class="btn" type="submit">Sign in securely →</button></form>
<div class="authlinks"><a href="/register">Create an account</a><a href="/help">Login help</a></div>
<div class="authnote">Demo credentials: <b style="color:#cbd9ef">demo</b> / <b style="color:#cbd9ef">demo123</b><br>Never enter a real wallet seed phrase or private key.</div>"""
REGISTER = """<div class="eyebrow">GET STARTED</div><h2>Create your account</h2><p>Register a local demo account to explore the interface.</p>
<form method="post" action="/register"><div class="field"><label>DISPLAY NAME</label><input name="display_name" placeholder="Your name" required></div>
<div class="field"><label>USERNAME</label><input name="username" placeholder="Choose username" required></div>
<div class="field"><label>PASSWORD</label><input name="password" type="password" minlength="4" placeholder="Choose password (4+ characters)" required></div>
<button class="btn">Create account →</button></form><div class="authlinks"><a href="/">← Back to login</a></div>
<div class="authnote">This prototype stores accounts in temporary memory and is not suitable for real user credentials.</div>"""

@app.route("/")
def login():
    if session.get("user"): return redirect("/dashboard")
    return auth_page(LOGIN)

@app.route("/login", methods=["POST"])
def do_login():
    u, p = request.form.get("username","").strip(), request.form.get("password","")
    if u in users and users[u]["password"] == p:
        session["user"] = u
        return redirect("/dashboard")
    return auth_page('<div class="eyebrow">SIGN IN</div><h2>Login unsuccessful</h2><p style="color:#ff8b9c">Username or password is incorrect.</p>'+LOGIN)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form.get("display_name","").strip()
        u = request.form.get("username","").strip()
        p = request.form.get("password","")
        if not u or not p or u in users:
            return auth_page('<div class="eyebrow">CREATE ACCOUNT</div><h2>Try another username</h2><p style="color:#ff8b9c">Username already exists or details are missing.</p>'+REGISTER)
        users[u] = {"password":p, "balance":1.0, "name":name or u}
        session.clear()
        return auth_page('<div class="notice">Account created. Please log in using your new credentials.</div>'+LOGIN)
    return auth_page(REGISTER)

def require_login():
    return not bool(session.get("user"))

def tx_table(items):
    if not items: return '<div class="empty">No transactions match this view yet.</div>'
    rows = ""
    for t in items:
        rows += f"""<tr><td><b>{t['id']}</b><br><span style="color:#7186a7;font-size:10px">{t['date']}</span></td><td>{t['type']}</td><td>{t['from']} → {t['to']}</td><td>{t['amount']:.4f} BTC</td><td><span class="status">{t['status']}</span></td></tr>"""
    return '<div class="tablewrap"><table><thead><tr><th>TX ID / DATE</th><th>TYPE</th><th>TRANSFER</th><th>AMOUNT</th><th>STATUS</th></tr></thead><tbody>'+rows+'</tbody></table></div>'

@app.route("/dashboard")
def dashboard():
    u = session.get("user")
    if not u or u not in users:
        session.clear()
        return redirect('/')
    bal = users[u]["balance"]
    received=sum(t["amount"] for t in transactions if t["to"]==u or (t["type"]=="Received" and t["to"]=="demo"))
    sent=sum(t["amount"] for t in transactions if t["from"]==u)
    recent=tx_table(transactions[:5])
    content=f"""
    <div class="grid">
    <div class="card"><div class="metriclabel">WALLET BALANCE</div><div class="metric">{bal:.4f} <span style="font-size:12px;color:var(--cyan)">BTC</span></div><div class="metricfoot">Simulated demo funds</div></div>
    <div class="card"><div class="metriclabel">TOTAL TRANSACTIONS</div><div class="metric">{len(transactions):02d}</div><div class="metricfoot">Recorded in this session</div></div>
    <div class="card"><div class="metriclabel">RECEIVED VOLUME</div><div class="metric positive">+{received:.4f}</div><div class="metricfoot">BTC in demo records</div></div>
    <div class="card"><div class="metriclabel">SENT VOLUME</div><div class="metric negative">-{sent:.4f}</div><div class="metricfoot">BTC in demo records</div></div></div>
    <div class="contentgrid"><section class="card"><div class="cardhead"><div class="cardtitle">Recent transactions</div><a class="pill" href="/transactions">View all →</a></div>{recent}</section>
    <section class="card"><div class="cardhead"><div class="cardtitle">Wallet health</div><span class="pill">DEMO</span></div>
    <div style="font-size:13px;margin:12px 0">Simulation status <b style="float:right;color:var(--green)">Operational</b></div><div style="height:7px;background:#263650;border-radius:10px"><div style="width:100%;height:100%;background:linear-gradient(90deg,var(--cyan),var(--blue));border-radius:10px"></div></div>
    <p class="sub" style="line-height:1.8;margin-top:18px">Explore simulated transfers, transaction records, and wallet relationships. No live blockchain data is queried.</p><a class="btn" href="/send">Create a transfer</a></section></div>"""
    return page("Overview","Monitor your simulated wallet and activity.",content)

@app.route("/transactions")
def transaction_history():
    if require_login(): return redirect("/")
    content='<section class="card"><div class="cardhead"><div class="cardtitle">All transactions</div><span class="pill">SIMULATED LEDGER</span></div>'+tx_table(transactions)+'</section>'
    return page("Transaction History","Review transfer IDs, parties, amounts, timestamps and status.",content)

@app.route("/send", methods=["GET","POST"])
def send():
    if require_login(): return redirect("/")
    u=session["user"]; flash=""
    if request.method=="POST":
        recipient=request.form.get("recipient","").strip()
        try: amount=float(request.form.get("amount","0"))
        except: amount=0
        if not recipient or amount<=0:
            flash="Enter a recipient and an amount greater than zero."
        elif amount>users[u]["balance"]:
            flash="Insufficient simulated BTC balance."
        else:
            users[u]["balance"]=round(users[u]["balance"]-amount,8)
            tid="CT-"+secrets.token_hex(3).upper()
            transactions.insert(0,{"id":tid,"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"type":"Sent","from":u,"to":recipient,"amount":amount,"status":"Confirmed"})
            flash=f"Simulated transfer recorded successfully. Transaction ID: {tid}"
    content=f"""<div class="contentgrid"><section class="card"><div class="cardhead"><div class="cardtitle">New simulated transfer</div><span class="pill">NO REAL BTC</span></div>
    <div class="notice">This action only updates the local demo ledger. It does not connect to Bitcoin or send real funds.</div>
    <form method="post"><div class="field"><label>RECIPIENT NAME OR WALLET LABEL</label><input name="recipient" placeholder="e.g. Alice Johnson" required></div>
    <div class="field"><label>AMOUNT (BTC)</label><input name="amount" type="number" min="0.0001" step="0.0001" max="{users[u]['balance']}" placeholder="0.0100" required></div>
    <button class="btn">Confirm simulated transfer →</button></form></section>
    <section class="card"><div class="cardtitle">Available balance</div><div class="metric">{users[u]['balance']:.4f} BTC</div><p class="sub">Your current demo balance.</p><hr style="border-color:var(--line);margin:20px 0"><div class="cardtitle">How it works</div><p class="sub" style="line-height:1.9">1. Enter a recipient label.<br>2. Enter an amount within your balance.<br>3. Confirm to add a record to transaction history.</p></section></div>"""
    return page("Send BTC","Create a clearly labelled simulated transfer.",content,flash)

@app.route("/receive")
def receive():
    if require_login(): return redirect("/")
    u=session["user"]
    content=f"""<div class="contentgrid"><section class="card"><div class="cardhead"><div class="cardtitle">Receive simulated BTC</div><span class="pill">DEMO ONLY</span></div>
    <p class="sub" style="line-height:1.8">Use this demo wallet label to represent an incoming transfer during your presentation. This is not a real blockchain address.</p>
    <div style="background:#0a1425;border:1px dashed #3a607b;padding:22px;border-radius:12px;text-align:center;margin:20px 0"><div class="eyebrow">WALLET LABEL</div><div style="font-size:20px;font-weight:800;margin-top:10px;word-break:break-all">{u.upper()}-DEMO-WALLET</div></div>
    <button class="btn secondary" onclick="navigator.clipboard.writeText('{u.upper()}-DEMO-WALLET')">Copy wallet label</button></section>
    <section class="card"><div class="cardtitle">Demo balance</div><div class="metric">{users[u]['balance']:.4f} BTC</div><p class="sub">Incoming transfers can be shown in the sample history. No funds are actually received.</p></section></div>"""
    return page("Receive BTC","Demo wallet label and incoming-transfer information.",content)

@app.route("/analysis", methods=["GET","POST"])
def analysis():
    if require_login(): return redirect("/")
    q=request.values.get("wallet","demo").strip()
    related=[t for t in transactions if q.lower() in str(t["from"]).lower() or q.lower() in str(t["to"]).lower() or q.lower() in t["id"].lower()]
    content=f"""<section class="card"><div class="cardhead"><div class="cardtitle">Wallet / transaction lookup</div><span class="pill">LOCAL DATA</span></div>
    <form method="get" class="formgrid"><div class="field"><label>SEARCH LABEL OR TRANSACTION ID</label><input name="wallet" value="{q}" placeholder="demo, Alice, CT-1004"></div><div style="display:flex;align-items:end;padding-bottom:15px"><button class="btn">Analyze records</button></div></form>
    <div class="grid" style="grid-template-columns:repeat(3,minmax(0,1fr));margin:10px 0 18px"><div class="card"><div class="metriclabel">MATCHES</div><div class="metric">{len(related)}</div></div><div class="card"><div class="metriclabel">DATA SOURCE</div><div class="metric" style="font-size:18px">Local</div></div><div class="card"><div class="metriclabel">LIVE CHAIN</div><div class="metric" style="font-size:18px">Off</div></div></div>
    {tx_table(related)}<p class="sub" style="margin-top:16px">This is a basic lookup of demo records, not a real-world attribution or forensic conclusion.</p></section>"""
    return page("Wallet Analysis","Search the local demo ledger for related records.",content)

@app.route("/network")
def network():
    if require_login(): return redirect("/")
    content="""<section class="card"><div class="cardhead"><div class="cardtitle">Transaction relationship view</div><span class="pill">ILLUSTRATIVE</span></div>
    <p class="sub" style="margin-bottom:18px">A visual concept showing how a wallet may connect to other labels in the simulated ledger.</p>
    <div class="network"><div class="node">Alice<br><span style="color:var(--muted)">Sender</span></div><div class="networkline">⟷</div><div class="node mainnode">DEMO WALLET<br><span style="color:var(--cyan)">CryptoTrace</span></div><div class="networkline">⟷</div><div class="node">Ravi<br><span style="color:var(--muted)">Recipient</span></div></div>
    <div class="legend" style="margin-top:15px"><span><i class="dot"></i>Incoming relation</span><span><i class="dot blue"></i>Outgoing relation</span></div></section>"""
    return page("Transaction Network","Explore an illustrative wallet relationship diagram.",content)

@app.route("/contacts", methods=["GET","POST"])
def contact_page():
    if require_login(): return redirect("/")
    flash=""
    if request.method=="POST":
        name=request.form.get("name","").strip()
        if name and name not in contacts:
            contacts.append(name); flash=f"{name} added to contacts."
        else: flash="Enter a new contact name."
    rows=""
    for i,name in enumerate(contacts):
        rows+=f'<div class="contact"><div><div class="contactname">{name}</div><div class="contactmeta">Saved demo contact</div></div><span class="pill">CONTACT {i+1:02d}</span></div>'
    content=f"""<div class="contentgrid"><section class="card"><div class="cardhead"><div class="cardtitle">Your contacts</div><span class="pill">{len(contacts)} SAVED</span></div>{rows}</section>
    <section class="card"><div class="cardtitle">Add a contact</div><p class="sub" style="margin:10px 0 18px">Add names to use as recipient labels in simulated transfers.</p><form method="post"><div class="field"><label>CONTACT NAME</label><input name="name" placeholder="Enter a name" required></div><button class="btn">Add contact +</button></form></section></div>"""
    return page("Contacts","Manage the names used in your demo transfers.",content,flash)

@app.route("/settings", methods=["GET","POST"])
def settings():
    if require_login(): return redirect("/")
    u=session["user"]; flash=""
    if request.method=="POST":
        name=request.form.get("name","").strip()
        if name:
            users[u]["name"]=name; flash="Display name updated."
    content=f"""<div class="contentgrid"><section class="card"><div class="cardtitle">Display settings</div><p class="sub" style="margin:9px 0 20px">Personalize your demo profile.</p>
    <form method="post"><div class="field"><label>DISPLAY NAME</label><input name="name" value="{users[u]['name']}" required></div><button class="btn">Save settings</button></form></section>
    <section class="card"><div class="cardtitle">Security & demo status</div><div class="contact"><span class="sub">Environment</span><b>Simulation only</b></div><div class="contact"><span class="sub">Live blockchain</span><b class="negative">Disabled</b></div><div class="contact"><span class="sub">Private keys stored</span><b>No</b></div><p class="sub" style="line-height:1.8;margin-top:16px">Do not enter real passwords, seed phrases, or private keys into this educational prototype.</p><a class="btn secondary" href="/logout">Sign out</a></section></div>"""
    return page("Settings","Profile preferences and demo security information.",content,flash)

@app.route("/help")
def help_page():
    return auth_page('<div class="eyebrow">HELP CENTRE</div><h2>Demo login help</h2><p>Use username <b>demo</b> and password <b>demo123</b>. Or create a local demo account.</p><a class="btn" href="/">Back to login</a>')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
