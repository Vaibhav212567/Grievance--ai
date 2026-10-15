from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, re
app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///grievances.db").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Grievance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default="Submitted", nullable=False)
    department = db.Column(db.String(100), default="General Administration")
    location = db.Column(db.String(160), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def json(self):
        return {"id": f"GRV-{self.id:04d}", "title": self.title, "description": self.description,
                "category": self.category, "priority": self.priority, "status": self.status,
                "department": self.department, "location": self.location,
                "created_at": self.created_at.isoformat() + "Z"}

def classify(text):
    t = text.lower()
    rules = [
        (r"water|drain|garbage|sewage|sanitation|waste|washroom", "Water & Sanitation"),
        (r"school|college|teacher|classroom|student|exam|education", "Education"),
        (r"hospital|doctor|medicine|health|clinic|ambulance", "Healthcare"),
        (r"electric|power cut|transformer|voltage|street light|road|pothole|bridge|footpath|traffic", "Public Infrastructure"),
        (r"pension|certificate|document|application|official|permit|identity", "Administration")
    ]
    category = next((name for pattern,name in rules if re.search(pattern,t)), "Other")
    priority = "High" if re.search(r"urgent|emergency|danger|unsafe|accident|fire|life.?threat|contaminat|severe|exposed wire",t) else ("Medium" if re.search(r"delay|broken|not working|overflow|failure|leak|outage|blocked|repeated",t) else "Low")
    return category, priority

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.get("/api/grievances")
def list_grievances():
    rows = Grievance.query.order_by(Grievance.created_at.desc()).all()
    return jsonify([r.json() for r in rows])

@app.post("/api/grievances")
def create_grievance():
    data = request.get_json(silent=True) or {}
    title, desc = (data.get("title") or "").strip(), (data.get("description") or "").strip()
    if not title or not desc:
        return jsonify({"error":"Title and description are required."}), 400
    category, priority = classify(title + " " + desc)
    requested = (data.get("department") or "Auto-detect with AI").strip()
    department = category if requested == "Auto-detect with AI" else requested
    row = Grievance(title=title[:160], description=desc[:5000], category=category if requested == "Auto-detect with AI" else requested,
                    priority=priority, department=department, location=(data.get("location") or "")[:160])
    db.session.add(row); db.session.commit()
    return jsonify(row.json()), 201

@app.patch("/api/grievances/<int:case_id>")
def update_grievance(case_id):
    row = db.session.get(Grievance, case_id)
    if not row: return jsonify({"error":"Grievance not found."}), 404
    data = request.get_json(silent=True) or {}
    if data.get("status") in ["Submitted","Under Review","In Progress","Resolved"]:
        row.status = data["status"]
    if data.get("department"): row.department = str(data["department"])[:100]
    db.session.commit()
    return jsonify(row.json())

@app.get("/api/stats")
def stats():
    rows = Grievance.query.all()
    return jsonify({"total":len(rows),"pending":sum(x.status in ("Submitted","Under Review") for x in rows),
                    "urgent":sum(x.priority=="High" and x.status!="Resolved" for x in rows),
                    "resolved":sum(x.status=="Resolved" for x in rows)})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
