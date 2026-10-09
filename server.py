#!/usr/bin/env python3
"""CampusHire demo backend: Python standard library only."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
import json, secrets, hashlib, os, threading, sqlite3
ROOT=Path(__file__).resolve().parent
DB=ROOT/"campushire.db"
LOCK=threading.Lock()
SEED={
 "users":[
  {"id":"STU001","email":"student@campushire.demo","password":"Student@123","role":"student","name":"Aarav Kumar","regNo":"24BIT1001","department":"IT","cgpa":8.2,"graduationYear":2027,"resume":"https://example.com/aarav-resume.pdf"},
  {"id":"REC001","email":"recruiter@campushire.demo","password":"Recruiter@123","role":"recruiter","name":"Maya Recruiter","companyId":"co_orbit"},
  {"id":"ADM001","email":"admin@campushire.demo","password":"Admin@123","role":"admin","name":"Placement Cell Admin"}
 ],
 "companies":[
  {"id":"co_orbit","name":"Orbit Cloud Systems","industry":"Cloud & Software","description":"Cloud-native tools and developer platforms.","website":"https://example.com","ownerId":"REC001","status":"approved"},
  {"id":"co_pixel","name":"Pixelforge Studio","industry":"Design Technology","description":"Digital product studio building accessible web experiences.","website":"https://example.com","ownerId":"REC001","status":"pending"}
 ],
 "jobs":[
  {"id":"job_orbit","companyId":"co_orbit","title":"Software Development Intern","location":"Bengaluru · Hybrid","type":"Internship · 6 months","pay":"₹35,000/month","description":"Build internal tools and customer-facing dashboards with a mentor.","minCgpa":7.5,"departments":["IT","CSE","AI&DS"],"status":"approved","createdBy":"REC001","deadline":"2026-10-30"},
  {"id":"job_pixel","companyId":"co_pixel","title":"Frontend Developer","location":"Chennai · On-site","type":"Full-time","pay":"₹5–6.5 LPA","description":"Build responsive interfaces from product designs.","minCgpa":7.0,"departments":["IT","CSE"],"status":"pending","createdBy":"REC001","deadline":"2026-11-12"},
  {"id":"job_webintern","companyId":"co_orbit","title":"Web Development Intern","location":"Vellore · Hybrid","type":"Internship · 3 months","pay":"₹15,000/month","description":"Work on responsive web pages, REST API integration and product improvements.","minCgpa":7.0,"departments":["IT","CSE","AI&DS"],"status":"approved","createdBy":"REC001","deadline":"2026-11-15"},
  {"id":"job_helix","companyId":"co_orbit","title":"Network Support Associate","location":"Coimbatore · On-site","type":"Full-time","pay":"₹3.6–4.2 LPA","description":"Monitor networks, troubleshoot issues and document incidents.","minCgpa":8.5,"departments":["ECE","EEE"],"status":"approved","createdBy":"REC001","deadline":"2026-11-20"}
 ],
 "applications":[
  {"id":"app_001","jobId":"job_orbit","studentId":"STU001","status":"Shortlisted","createdAt":"2026-10-08T10:00:00+05:30"}
 ],
 "audit":[{"id":"aud_seed","timestamp":"2026-10-09T09:00:00+05:30","adminId":"SYSTEM","action":"SEED_DATA_CREATED","entityType":"platform","entityId":"seed","details":"Initial demonstration data"}]
}
def _connect():
 conn=sqlite3.connect(DB,timeout=10)
 conn.execute("CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
 return conn
def read_db():
 with LOCK:
  with _connect() as conn:
   row=conn.execute("SELECT payload FROM app_state WHERE id=1").fetchone()
   if row is None:
    conn.execute("INSERT INTO app_state (id,payload) VALUES (1,?)",(json.dumps(SEED),))
    row=(json.dumps(SEED),)
   return json.loads(row[0])
def write_db(d):
 with LOCK:
  with _connect() as conn:
   conn.execute("INSERT INTO app_state (id,payload) VALUES (1,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",(json.dumps(d),))
def now():
 from datetime import datetime, timezone
 return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
SESSIONS={}
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,fmt,*args): print("%s - %s"%(self.address_string(),fmt%args))
 def send_json(self,code,obj):
  raw=json.dumps(obj).encode()
  self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
 def body(self):
  n=int(self.headers.get("Content-Length","0"))
  try: return json.loads(self.rfile.read(n) or b"{}")
  except Exception: return {}
 def current(self):
  token=self.headers.get("Authorization","").replace("Bearer ","")
  return SESSIONS.get(token)
 def require(self,*roles):
  u=self.current()
  if not u: self.send_json(401,{"error":"Please sign in again."}); return None
  if roles and u["role"] not in roles: self.send_json(403,{"error":"Your role is not allowed to perform this action."}); return None
  return u
 def do_GET(self):
  p=urlparse(self.path).path
  if p.startswith("/api/"):
   if p=="/api/health": return self.send_json(200,{"ok":True,"storage":"JSON file","message":"CampusHire API running"})
   u=self.require()
   if not u:return
   d=read_db()
   if p=="/api/me": return self.send_json(200,{"user":{k:v for k,v in u.items() if k!="password"}})
   if p=="/api/dashboard":
    visible=[j for j in d["jobs"] if j["status"]=="approved" and next((c["status"]=="approved" for c in d["companies"] if c["id"]==j["companyId"]),False)]
    if u["role"]=="student":
     apps=[a for a in d["applications"] if a["studentId"]==u["id"]]
     return self.send_json(200,{"user":u,"jobs":visible,"applications":apps,"companies":[c for c in d["companies"] if c["status"]=="approved"]})
    if u["role"]=="recruiter":
     companies=[c for c in d["companies"] if c["ownerId"]==u["id"]]
     ids=[c["id"] for c in companies]
     jobs=[j for j in d["jobs"] if j["companyId"] in ids]
     jobids=[j["id"] for j in jobs]
     apps=[a for a in d["applications"] if a["jobId"] in jobids]
     return self.send_json(200,{"user":u,"companies":companies,"jobs":jobs,"applications":apps,"students":[{k:v for k,v in x.items() if k not in ("password",)} for x in d["users"] if x["role"]=="student"]})
    return self.send_json(200,{"user":u,"companies":d["companies"],"jobs":d["jobs"],"applications":d["applications"],"users":[{k:v for k,v in x.items() if "password" not in k} for x in d["users"]],"audit":d["audit"]})
   return self.send_json(404,{"error":"API route not found"})
  return super().do_GET()
 def do_POST(self):
  p=urlparse(self.path).path; b=self.body()
  if p=="/api/register":
   d=read_db()
   role=str(b.get("role","student")).lower()
   if role not in ("student","recruiter"):
    return self.send_json(400,{"error":"Public registration is available for students and recruiters only."})
   name=str(b.get("name","")).strip()
   email=str(b.get("email","")).strip().lower()
   password=str(b.get("password",""))
   if not name or not email or not password:
    return self.send_json(400,{"error":"Name, email and password are required."})
   if len(password)<8:
    return self.send_json(400,{"error":"Use a password with at least 8 characters."})
   if any(x["email"].lower()==email for x in d["users"]):
    return self.send_json(409,{"error":"An account with this email already exists."})
   uid=("STU" if role=="student" else "REC")+secrets.token_hex(3).upper()
   user={"id":uid,"email":email,"password":password,"role":role,"name":name}
   if role=="student":
    user.update({"regNo":str(b.get("regNo","")).strip(),"department":str(b.get("department","IT")),"cgpa":float(b.get("cgpa",0) or 0),"graduationYear":int(b.get("graduationYear",2027) or 2027),"resume":str(b.get("resume","")).strip()})
    if not user["regNo"]:return self.send_json(400,{"error":"Registration number is required."})
    if not 0<=user["cgpa"]<=10:return self.send_json(400,{"error":"CGPA must be between 0 and 10."})
   d["users"].append(user)
   if role=="recruiter":
    d["audit"].append({"id":"aud_"+secrets.token_hex(4),"timestamp":now(),"adminId":"SYSTEM","action":"RECRUITER_REGISTERED","entityType":"user","entityId":uid,"details":"Recruiter account created; company submissions require approval"})
   write_db(d)
   token=secrets.token_urlsafe(32); SESSIONS[token]=user
   return self.send_json(201,{"token":token,"user":{k:v for k,v in user.items() if k!="password"}})
  if p=="/api/login":
   d=read_db(); user=next((x for x in d["users"] if x["email"].lower()==str(b.get("email","")).lower() and x["password"]==b.get("password")),None)
   if not user:return self.send_json(401,{"error":"Invalid demo email or password."})
   token=secrets.token_urlsafe(32); SESSIONS[token]=user
   return self.send_json(200,{"token":token,"user":{k:v for k,v in user.items() if k!="password"}})
  u=self.require()
  if not u:return
  d=read_db()
  if p=="/api/profile" and u["role"]=="student":
   allowed={"name","regNo","department","cgpa","graduationYear","resume"}
   for k in allowed:
    if k in b:
     if k=="cgpa":
      try: b[k]=float(b[k])
      except: return self.send_json(400,{"error":"CGPA must be a number."})
      if not 0<=b[k]<=10:return self.send_json(400,{"error":"CGPA must be between 0 and 10."})
     if k=="graduationYear":
      try:b[k]=int(b[k])
      except:return self.send_json(400,{"error":"Graduation year must be a number."})
     u[k]=b[k]
   for x in d["users"]:
    if x["id"]==u["id"]:x.update({k:v for k,v in u.items() if k!="password"})
   write_db(d); SESSIONS[self.headers.get("Authorization","").replace("Bearer ","")]=u
   return self.send_json(200,{"user":{k:v for k,v in u.items() if k!="password"}})
  if p=="/api/apply" and u["role"]=="student":
   job=next((j for j in d["jobs"] if j["id"]==b.get("jobId")),None)
   if not job or job["status"]!="approved" or not next((c["status"]=="approved" for c in d["companies"] if c["id"]==job["companyId"]),False):return self.send_json(400,{"error":"This job is not approved and open for applications."})
   reasons=[]
   if float(u.get("cgpa",0))<float(job["minCgpa"]):reasons.append("Your CGPA is below the required "+str(job["minCgpa"])+".")
   if u.get("department") not in job["departments"]:reasons.append("Your department is not permitted for this role.")
   if not u.get("resume"):reasons.append("Add a resume link to your profile before applying.")
   if reasons:return self.send_json(400,{"error":"Not eligible: "+" ".join(reasons)})
   if any(a["jobId"]==job["id"] and a["studentId"]==u["id"] for a in d["applications"]):return self.send_json(409,{"error":"You have already applied to this role."})
   app={"id":"app_"+secrets.token_hex(4),"jobId":job["id"],"studentId":u["id"],"status":"Applied","createdAt":now()}
   d["applications"].append(app);write_db(d);return self.send_json(201,{"application":app})
  if p=="/api/company" and u["role"]=="recruiter":
   name=str(b.get("name","")).strip()
   if not name:return self.send_json(400,{"error":"Company name is required."})
   c={"id":"co_"+secrets.token_hex(4),"name":name,"industry":str(b.get("industry","Technology")),"description":str(b.get("description","")),"website":str(b.get("website","")),"ownerId":u["id"],"status":"pending"}
   d["companies"].append(c);write_db(d);return self.send_json(201,{"company":c})
  if p=="/api/job" and u["role"]=="recruiter":
   c=next((x for x in d["companies"] if x["id"]==b.get("companyId") and x["ownerId"]==u["id"]),None)
   if not c:return self.send_json(400,{"error":"Choose a company you manage."})
   try:cgpa=float(b.get("minCgpa",0))
   except:return self.send_json(400,{"error":"Minimum CGPA must be numeric."})
   depts=b.get("departments",["IT"])
   if not isinstance(depts,list) or not depts:return self.send_json(400,{"error":"Select at least one permitted department."})
   j={"id":"job_"+secrets.token_hex(4),"companyId":c["id"],"title":str(b.get("title","")).strip(),"location":str(b.get("location","")),"type":str(b.get("type","Internship")),"pay":str(b.get("pay","Not specified")),"description":str(b.get("description","")),"minCgpa":cgpa,"departments":depts,"status":"pending","createdBy":u["id"],"deadline":str(b.get("deadline","2026-12-31"))}
   if not j["title"]:return self.send_json(400,{"error":"Job title is required."})
   d["jobs"].append(j);write_db(d);return self.send_json(201,{"job":j})
  return self.send_json(403,{"error":"Unsupported action for this role."})
 def do_PATCH(self):
  p=urlparse(self.path).path;b=self.body();u=self.require()
  if not u:return
  d=read_db()
  if p.startswith("/api/application/") and u["role"]=="recruiter":
   aid=p.rsplit("/",1)[-1]; app=next((a for a in d["applications"] if a["id"]==aid),None)
   job=next((j for j in d["jobs"] if app and j["id"]==app["jobId"]),None)
   if not app or not job or job["createdBy"]!=u["id"]:return self.send_json(404,{"error":"Application not found in your company."})
   status=b.get("status")
   if status not in ["Applied","Under Review","Shortlisted","Interview","Offered","Rejected"]:return self.send_json(400,{"error":"Invalid application status."})
   app["status"]=status;write_db(d);return self.send_json(200,{"application":app})
  if p.startswith("/api/admin/") and u["role"]=="admin":
   parts=p.strip("/").split("/")
   # Expected route /api/admin/company/<id> or /api/admin/job/<id>
   if len(parts)!=4 or parts[0]!="api" or parts[1]!="admin" or parts[2] not in ("company","job"):
    return self.send_json(404,{"error":"Invalid approval route."})
   kind,entity_id=parts[2],parts[3]
   collection="companies" if kind=="company" else "jobs" if kind=="job" else None
   if not collection:return self.send_json(404,{"error":"Unknown entity."})
   item=next((x for x in d[collection] if x["id"]==entity_id),None)
   if not item:return self.send_json(404,{"error":"Item not found."})
   action=b.get("action")
   if action not in ("approved","rejected"):return self.send_json(400,{"error":"Action must be approved or rejected."})
   item["status"]=action
   d["audit"].append({"id":"aud_"+secrets.token_hex(4),"timestamp":now(),"adminId":u["id"],"action":action.upper()+"_"+kind.upper(),"entityType":kind,"entityId":entity_id,"details":item.get("name",item.get("title",""))})
   write_db(d);return self.send_json(200,{"item":item})
  return self.send_json(403,{"error":"Not permitted."})
 def do_DELETE(self):
  if urlparse(self.path).path=="/api/logout":
   token=self.headers.get("Authorization","").replace("Bearer ","");SESSIONS.pop(token,None);return self.send_json(200,{"ok":True})
  self.send_json(404,{"error":"Not found"})
if __name__=="__main__":
 read_db()
 print("CampusHire running at http://127.0.0.1:8000")
 print("Persistent SQLite database:", DB.name)
 print("Demo accounts: student@campushire.demo / Student@123 | recruiter@campushire.demo / Recruiter@123 | admin@campushire.demo / Admin@123")
 ThreadingHTTPServer(("127.0.0.1",8000),Handler).serve_forever()
