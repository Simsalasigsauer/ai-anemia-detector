import base64, certifi, json
import datetime

import bcrypt
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import gridfs

from detect_nails import detect_and_annotate
from predict_hb import predict_hb

app = Flask(__name__)
CORS(app)

uri = 'mongodb+srv://jakobscharf:mIFL16blqCB3O9V1@onlynails.zjtlwkc.mongodb.net/?retryWrites=true&w=majority&appName=OnlyNails'
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["onlynails"]
fs = gridfs.GridFS(db, collection="pictures")

# Key zur Generierung vom Login-Token -- nicht ändern!
SECRET_KEY = "deinemamaistdickeralsmeinemamaaberdasistgarnichtschlimmweilmenschistmenschausserinkendieistkackiundfaul"

'''
Wichtiges To-Do vor Vorstellung: die 'best.pt' und 'model_rf_rgb_avg.pkl' gegen richtig trainierte austauschen

CHECK -- Bilder anonym in DB ablegen für KI-Training Zwecke
CHECK -- Visualisierung HG-Werte
CHECK -- Hb-Werte in DB hinterlegen
CHECK -- API Endpoint für die Auswertung
CHECK -- Profil: Werte direkt bei Aufruf; Meds und Krankheiten werden doppelt eingetragen
CHECK -- Einheitliche Schriftarten
CHECK --  Daily Stuff: In DB hinterlegen + Speicher-Funktion
CHECK -- Passwort Hashing (per bcrypt) -> nur wirklich sicher, wenn Passwort mind. 12 Zeichen und Sonderzeichen etc.
CHECK -- Code dokumentieren und aufräumen
CHECK -- Analyse: Werte, Bilder etc. im sessionStorage speichern
CHECK -- Token Logik implementieren für Security der Endpoints (Enkrypting per HS256 und geheimen Key)
- Erkannte Boxen löschen implementieren (über Nummerierung der Boxen)

Zusatz CHECK: Autologin, wenn username, password noch lokal gespeichert sind
'''

def check_token(auth_header):
    try:
        token = auth_header.split(" ")[1]
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return "success"
    except jwt.ExpiredSignatureError:
        return "Token abgelaufen"
    except jwt.InvalidTokenError:
        return "Token ungültig"

@app.route('/userdata', methods=['GET'])
def get_userdata():
    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":
        collection = db["userdata"]
        user_id = request.args.get("uid")
        user_dok = collection.find_one({"uid": user_id})
        if user_dok:
            user_dok["_id"] = str(user_dok["_id"])
            return jsonify(user_dok), 200
        else:
            collection.insert_one({"uid": user_id})
            return jsonify({"uid": user_id}), 201
    else:
        return jsonify({"error": token_response}), 401

@app.route('/userdata', methods=['POST'])
def update_userdata():
    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":
        collection = db["userdata"]
        if not request.is_json:
            return jsonify({"error": "Missing JSON body"}), 400
        data = request.get_json()
        user_id = data.get("uid")
        try:
            collection.update_one(
                {"uid": user_id},
                {"$set": {
                    "name": data.get("name"),
                    "birthday": data.get("birthday"),
                    "gender": data.get("gender"),
                    "vorerkrankung": data.get("vorerkrankung"),
                    "medikamente": data.get("medikamente")
                }}
            )
            return jsonify({"success": True}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': e}), 401
    else:
        return jsonify({"error": token_response}), 401

@app.route('/login', methods=['POST'])
def login():
    collection = db["onlynails"]
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 415

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    try:
        user_dok = collection.find_one({"username": username})
        if user_dok and bcrypt.checkpw(password.encode(), user_dok["password"].encode('utf-8')):
            payload = {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            user_id = str(user_dok['_id'])
            return jsonify({'success': True, 'id': user_id, 'token': token}), 200
        else:
            return jsonify({'success': False}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': e}), 401

@app.route('/register', methods=['POST'])
def register():
    collection = db["onlynails"]
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 415

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    existing_user = collection.find_one({"username": username})
    if not existing_user:
        try:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_dok = {
                "username": username,
                "password": hashed_pw
            }
            new_user = collection.insert_one(user_dok)
            return jsonify({'success': True, 'id': str(new_user.inserted_id)}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': e}), 401
    else:
        return jsonify({'success': False}), 401

@app.route("/nails/detect", methods=["POST"])
def route_detect_nails():
    """
    Multipart POST (image)
    → YOLO erkennt Fingernägel, gibt Box-Koordinaten & Preview zurück.
    """
    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":
        if "file" not in request.files:
            return jsonify({"error": 'Field "file" missing'}), 400

        img_bytes = request.files["file"].read()

        # Upload des Bildes in DB für Training
        fs.put(img_bytes)

        boxes, jpg_bytes, _ = detect_and_annotate(img_bytes)
        b64 = base64.b64encode(jpg_bytes).decode("ascii")

        return jsonify({
            "bboxes": boxes,                                    # [{id,x1,y1,x2,y2,score}, …]
            "annotated": f"data:image/jpeg;base64,{b64}"
        }), 200
    else:
        return jsonify({"error": token_response}), 401

@app.route("/hb/predict", methods=["POST"])
def route_predict_hb():
    """
    Multipart POST (image)
    → Hb-Schätzung unter Einbeziehung *aller* erkannten Boxen.
    """
    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":

        if "file" not in request.files:
            return jsonify({"error": 'Field "file" missing'}), 400
        elif "uid" not in request.form:
            return jsonify({"error": 'Field "uid" missing'}), 400
        elif "date" not in request.form:
            return jsonify({"error": 'Field "date" missing'}), 400

        try:
            hb_val = predict_hb(request.files["file"].read())
            hb = round(hb_val, 1)

            safe_hb_in_db(hb, request.form.get("uid"), request.form.get("date"))
            return jsonify({"hb": hb}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": token_response}), 401

# anonymously saving the hb value in the db
def safe_hb_in_db(hb, uid, date):
    db["hb_values"].insert_one({
        "uid": uid,
        "date": date,
        "hb": hb,
    })

@app.route("/hb/predict-custom", methods=["POST"])
def predict_hb_custom():
    """
    Multipart POST
      image      : JPEG
      keep_ids   : JSON-Liste (optional) → nur diese Box-IDs verwenden
      drop_ids   : JSON-Liste (optional) → bestimmte Box-IDs ausschließen
    """
    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":

        if "image" not in request.files:
            return jsonify({"error": 'Field "image" missing'}), 400

        keep_ids = drop_ids = None

        if "keep_ids" in request.form:
            keep_ids = json.loads(request.form["keep_ids"])
        elif "drop_ids" in request.form:
            drop_ids = json.loads(request.form["drop_ids"])

        try:
            hb_val = predict_hb(request.files["image"].read(),
                                keep_ids=keep_ids,
                                drop_ids=drop_ids)
            return jsonify({"hb": round(hb_val, 1)}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": token_response}), 401

@app.route("/daily", methods=["POST"])
def post_daily():
    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":

        if not request.is_json:
            return jsonify({"error": "Missing JSON body"}), 400

        data = request.get_json()
        db["daily"].insert_one({
            "uid": data.get("uid"),
            "mood": data.get("mood"),
            "symptoms": data.get("symptoms"),
            "period": data.get("period"),
            "sport": {
                "type": data.get("sport").get("type"),
                "intensity": data.get("sport").get("intensity"),
                "duration": data.get("sport").get("duration"),
                "comment": data.get("sport").get("comment"),
            },
            "date": data.get("date"),
        })
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": token_response}), 401

@app.route("/hb", methods=["GET"])
def get_hb():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "Parameter 'uid' fehlt"}), 400

    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":

        cursor = db["hb_values"].find({"uid": uid})
        matching_values = list(cursor)

        if not matching_values:
            return jsonify({"error": "No values found"}), 404

        data = [{"date": doc["date"], "value": doc["hb"]} for doc in matching_values]
        print(f"Return data {data}")

        return jsonify(data), 200
    else:
        return jsonify({"error": token_response}), 401

@app.route("/last-hb", methods=["GET"])
def get_last_hb():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "Parameter 'uid' fehlt"}), 400

    token_response = check_token(request.headers.get('Authorization'))
    if token_response == "success":
        cursor = db["hb_values"].find({"uid": uid})
        matching_values = list(cursor)

        for doc in matching_values:
            doc["parsed_date"] = datetime.datetime.strptime(doc["date"], "%d.%m.%Y")

        max_date = max(doc["parsed_date"] for doc in matching_values)

        latest_docs = [doc for doc in matching_values if doc["parsed_date"] == max_date]
        latest_doc = latest_docs[0]
        data = {"date": latest_doc["date"], "value": latest_doc["hb"]}

        return jsonify(data), 200
    else:
        return jsonify({"error": token_response}), 401

if __name__ == '__main__':
    app.run(debug=True)