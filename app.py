from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid
import datetime

def init_db():
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        text TEXT,
        category TEXT,
        priority TEXT,
        department TEXT,
        solution TEXT,
        status TEXT,
        location TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()
app = Flask(__name__)
CORS(app)

# ================= DB =================
def init_db():
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT,
        text TEXT,
        category TEXT,
        priority TEXT,
        department TEXT,
        solution TEXT,
        status TEXT,
        location TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= AI =================
def classify(text):
    t = text.lower()
    if "road" in t: return "Road Issue"
    if "water" in t: return "Water Issue"
    if "garbage" in t: return "Sanitation Issue"
    if "light" in t: return "Streetlight Issue"
    return "General Issue"

def priority(text):
    return "High" if "urgent" in text else "Normal"

def dept(cat):
    return {
        "Road Issue":"PWD",
        "Water Issue":"Water Board",
        "Sanitation Issue":"Municipality",
        "Streetlight Issue":"Electricity"
    }.get(cat,"City Office")

# ================= SUBMIT =================
@app.route('/submit', methods=['POST'])
@app.route('/submit', methods=['POST'])
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    text = data.get("text")
    location = data.get("location")

    cid = str(uuid.uuid4())[:8]

    if "road" in text.lower():
        category = "Road Issue"
        solution = "Road team assigned"
    elif "water" in text.lower():
        category = "Water Issue"
        solution = "Water board notified"
    elif "garbage" in text.lower():
        category = "Sanitation Issue"
        solution = "Cleaning team assigned"
    else:
        category = "General Issue"
        solution = "Forwarded to authority"

    priority = "High" if "urgent" in text.lower() else "Normal"
    status = "Pending"
    time = str(datetime.datetime.now())

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO complaints VALUES (?,?,?,?,?,?,?,?,?)
    """, (cid, text, category, priority, "City Dept", solution, status, location, time))

    conn.commit()
    conn.close()

    return jsonify({"id": cid})
@app.route('/track/<cid>')
def track(cid):
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("SELECT * FROM complaints WHERE id=?", (cid,))
    row = c.fetchone()

    conn.close()

    if not row:
        return jsonify({"error": "not found"})

    return jsonify({
        "id": row[0],
        "text": row[1],
        "category": row[2],
        "priority": row[3],
        "department": row[4],
        "solution": row[5],
        "status": row[6],
        "location": row[7],
        "time": row[8],

        "map": f"https://www.google.com/maps?q={row[7]}&output=embed"
    })
# ================= ALL COMPLAINTS =================
@app.route('/complaints')
def complaints():
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()
    c.execute("SELECT * FROM complaints")
    data = c.fetchall()
    conn.close()
    return jsonify(data)

# ================= STATS =================
@app.route('/stats')
def stats():

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM complaints")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
    resolved = c.fetchone()[0]

    c.execute("""
    SELECT location, COUNT(*) 
    FROM complaints 
    GROUP BY location 
    ORDER BY COUNT(*) DESC 
    LIMIT 1
    """)

    top = c.fetchone()

    conn.close()

    return jsonify({
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "top_area": top[0] if top else "N/A"
    })
@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("message", "").lower()

    if "road" in msg:
        reply = "🚧 Road issues are handled by PWD department"
    elif "water" in msg:
        reply = "💧 Water issue has been forwarded"
    elif "garbage" in msg:
        reply = "🚮 Sanitation team assigned"
    else:
        reply = "🤖 Ask about road, water, garbage or complaint tracking"

    return jsonify({"reply": reply})
if __name__ == "__main__":
    app.run(debug=True)