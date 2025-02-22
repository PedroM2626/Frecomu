import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.utils import secure_filename

# ---------------------------
# Configurações do Flask
# ---------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "PedroM2626"  # Substitua por uma chave forte

# Configura a pasta para uploads
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------------------
# Inicializa o Firebase Admin (Firestore)
# ---------------------------
cred = credentials.Certificate("config/firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------------------
# Inicializa o SocketIO
# ---------------------------
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------------------
# Funções de Persistência com Firestore
# ---------------------------

# Usuários
def create_user(username, email, password):
    user_ref = db.collection("users").document(username)
    if user_ref.get().exists:
        raise Exception("Usuário já existe")
    data = {"email": email, "password": password, "created": datetime.datetime.utcnow()}
    user_ref.set(data)
    return username

def get_user(username):
    doc = db.collection("users").document(username).get()
    if doc.exists:
        data = doc.to_dict()
        data["username"] = doc.id
        return data
    return None

def update_user_password(username, new_password):
    user_ref = db.collection("users").document(username)
    if not user_ref.get().exists:
        raise Exception("Usuário não encontrado")
    user_ref.update({"password": new_password})

# Salas
def create_room(room_name, private=False, password=None, owner=None):
    room_ref = db.collection("rooms").document(room_name)
    if room_ref.get().exists:
        return None
    data = {"private": private, "password": password, "owner": owner, "created": datetime.datetime.utcnow()}
    room_ref.set(data)
    return room_name

def get_room(room_name):
    doc = db.collection("rooms").document(room_name).get()
    if doc.exists:
        data = doc.to_dict()
        data["name"] = doc.id
        return data
    return None

def update_room(old_room, new_room):
    old_doc = db.collection("rooms").document(old_room).get()
    if not old_doc.exists:
        return False
    data = old_doc.to_dict()
    db.collection("rooms").document(new_room).set(data)
    db.collection("rooms").document(old_room).delete()
    return True

def delete_room(room_name):
    db.collection("rooms").document(room_name).delete()
    # Exclui mensagens associadas à sala
    messages = db.collection("messages").where("room", "==", room_name).stream()
    for m in messages:
        m.reference.delete()

# Mensagens
def create_message(data):
    msg_ref = db.collection("messages").document()
    data["timestamp"] = datetime.datetime.utcnow()
    msg_ref.set(data)
    return msg_ref.id

def get_messages_for_room(room):
    messages = []
    query = db.collection("messages").where("room", "==", room).order_by("timestamp")
    for doc in query.stream():
        msg = doc.to_dict()
        msg["id"] = doc.id
        messages.append(msg)
    return messages

def delete_message(message_id):
    db.collection("messages").document(message_id).delete()

# ---------------------------
# Rotas de Autenticação
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user(username)
        if not user or user["password"] != password:
            error = "Credenciais inválidas"
        else:
            session["username"] = username
            return redirect(url_for("index"))
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            create_user(username, email, password)
            session["username"] = username
            return redirect(url_for("index"))
        except Exception as e:
            error = str(e)
    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------------------
# Rotas para Salas (Persistentes no Firestore)
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    current_user = session.get("username")
    if not current_user:
        return redirect(url_for("login"))
    
    error = None
    room_param = request.args.get("room")
    
    if request.method == "POST":
        if room_param:
            # Entrar em sala existente
            entered_password = request.form.get("password")
            room = get_room(room_param)
            if not room:
                error = "Sala não existe."
            else:
                if room["private"]:
                    if not entered_password:
                        error = "Senha é obrigatória para entrar nessa sala."
                    elif entered_password != room["password"]:
                        error = "Senha incorreta."
            if not error:
                session["room"] = room_param
                return redirect(url_for("chat"))
        else:
            # Criar nova sala
            room_name = request.form.get("room_name")
            is_private = request.form.get("is_private") == "on"
            password = request.form.get("password") if is_private else None
            if not room_name:
                error = "O nome da sala é obrigatório."
            elif get_room(room_name):
                error = "Essa sala já existe."
            else:
                create_room(room_name, is_private, password, owner=current_user)
                return redirect(url_for("index", room=room_name))
    
    # Lista todas as salas persistentes
    rooms = []
    for doc in db.collection("rooms").stream():
        data = doc.to_dict()
        data["name"] = doc.id
        rooms.append(data)
    return render_template("index.html", rooms=rooms, error=error, room=room_param, current_user=current_user)

# ---------------------------
# Rota do Chat
# ---------------------------
@app.route("/chat")
def chat():
    current_user = session.get("username")
    room = session.get("room")
    if not current_user or not room:
        return redirect(url_for("index"))
    messages = get_messages_for_room(room)
    return render_template("chat.html", username=current_user, room=room, messages=messages)

# ---------------------------
# Rota para Upload de Arquivos
# ---------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400
    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "Nome de arquivo inválido."}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({"url": url_for('uploaded_file', filename=filename), "file_type": file.mimetype})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------------------
# SocketIO – Eventos para Chat (Persistindo mensagens no Firestore)
# ---------------------------
@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    system_msg = f"{username} entrou na sala."
    msg_data = {"username": "Sistema", "room": room, "msg": system_msg}
    create_message(msg_data)
    emit("message", {"username": "Sistema", "msg": system_msg}, room=room)

@socketio.on("message")
def handle_message(data):
    room = data["room"]
    username = data["username"]
    msg_text = data.get("msg")
    reply_to = data.get("reply_to")
    file_url = data.get("file_url")
    file_type = data.get("file_type")
    msg_data = {"username": username, "room": room, "msg": msg_text, "reply_to": reply_to, "file_url": file_url, "file_type": file_type}
    msg_id = create_message(msg_data)
    data["id"] = msg_id
    emit("message", data, room=room)

@socketio.on("leave")
def on_leave(data):
    username = data["username"]
    room = data["room"]
    leave_room(room)
    system_msg = f"{username} saiu da sala."
    msg_data = {"username": "Sistema", "room": room, "msg": system_msg}
    create_message(msg_data)
    emit("message", {"username": "Sistema", "msg": system_msg}, room=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)
