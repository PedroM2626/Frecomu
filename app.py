import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "sua_chave_secreta_muito_dificil"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///frecomu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Pasta para salvar uploads
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
migrate = Migrate(app, db)

# Armazenamento simples das salas em memória
rooms = {}
# Exemplo:
# rooms = {
#     "geral": {"private": False, "password": None, "owner": "nome@exemplo.com"},
#     "amigos": {"private": True, "password": "123456", "owner": "nome2@exemplo.com"}
# }

# Modelo de Mensagem atualizado (suporta arquivos)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    msg = db.Column(db.Text, nullable=True)  # Pode ser vazio para mensagens de áudio
    file_url = db.Column(db.String(255), nullable=True)  # URL do arquivo (áudio, vídeo, documento)
    file_type = db.Column(db.String(50), nullable=True)  # 'audio', 'video', 'document'
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reply_to = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    parent = db.relationship('Message', remote_side=[id], uselist=False)
    reactions = db.relationship('Reaction', backref='message', lazy=True)

# Modelo de Reação permanece o mesmo
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Rota para servir arquivos enviados (uploads)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rotas de autenticação (login e register) devem existir
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

# Rota unificada para criar/entrar em salas
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    room_param = request.args.get("room")
    
    if request.method == "POST":
        if room_param:
            # Modo "entrar" na sala (username preenchido via Firebase)
            username = request.form.get("username", "").strip()
            room_name = room_param
            entered_password = request.form.get("password", "").strip()
            if room_name not in rooms:
                error = "Sala não existe."
            else:
                room_info = rooms[room_name]
                if room_info["private"]:
                    if not entered_password:
                        error = "Senha é obrigatória para entrar nessa sala."
                    elif entered_password != room_info["password"]:
                        error = "Senha incorreta."
                if not username:
                    error = "Você deve inserir seu nome."
                if not error:
                    session["username"] = username
                    session["room"] = room_name
                    return redirect(url_for("chat"))
        else:
            # Modo "criar" sala
            room_name = request.form.get("room_name", "").strip()
            is_private = request.form.get("is_private") == "on"
            password = request.form.get("password", "").strip() if is_private else None
            if not room_name:
                error = "O nome da sala é obrigatório."
            elif room_name in rooms:
                error = "Essa sala já existe."
            else:
                # Armazena o usuário que criou a sala como owner
                rooms[room_name] = {"private": is_private, "password": password, "owner": session.get("username")}
                return redirect(url_for("index", room=room_name))
    
    return render_template("index.html", rooms=rooms, error=error, room=room_param, current_user=session.get("username"))

# Rota do chat
@app.route("/chat")
def chat():
    username = session.get("username")
    room = session.get("room")
    if not username or not room:
        return redirect(url_for("index"))
    messages = Message.query.filter_by(room=room).order_by(Message.timestamp).all()
    return render_template("chat.html", username=username, room=room, messages=messages)

# Rota para upload de arquivos
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

@app.route('/profile')
def profile():
    return render_template("profile.html")


# Rota para editar o nome da sala (apenas para o owner)
@app.route("/edit_room", methods=["POST"])
def edit_room():
    old_room = request.form.get("old_room")
    new_room = request.form.get("new_room", "").strip()
    if old_room not in rooms:
        return jsonify({"error": "Sala não existe."}), 400
    if rooms[old_room]["owner"] != session.get("username"):
        return jsonify({"error": "Você não é o criador desta sala."}), 403
    if new_room in rooms:
        return jsonify({"error": "O novo nome já está em uso."}), 400
    # Atualiza a sala: copia o conteúdo para a nova chave e remove a antiga
    room_info = rooms.pop(old_room)
    rooms[new_room] = room_info
    if session.get("room") == old_room:
        session["room"] = new_room
    return jsonify({"new_room": new_room}), 200

# Rota para excluir a sala (apenas para o owner)
@app.route("/delete_room", methods=["POST"])
def delete_room():
    room = request.form.get("room")
    if room not in rooms:
        return jsonify({"error": "Sala não existe."}), 400
    if rooms[room]["owner"] != session.get("username"):
        return jsonify({"error": "Você não é o criador desta sala."}), 403
    rooms.pop(room)
    if session.get("room") == room:
        session.pop("room", None)
    return jsonify({"deleted_room": room}), 200

# SocketIO – Eventos para chat e reações
@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    system_msg = f"{username} entrou na sala."
    system_message = Message(username="Sistema", room=room, msg=system_msg)
    db.session.add(system_message)
    db.session.commit()
    emit("message", {"id": system_message.id, "username": "Sistema", "msg": system_msg, "reply_to": None}, room=room)

@socketio.on("message")
def handle_message(data):
    room = data["room"]
    username = data["username"]
    msg_text = data.get("msg")  # pode ser None se for arquivo
    reply_to = data.get("reply_to")
    file_url = data.get("file_url")
    file_type = data.get("file_type")
    message = Message(username=username, room=room, msg=msg_text, reply_to=reply_to, file_url=file_url, file_type=file_type)
    db.session.add(message)
    db.session.commit()
    emit("message", {"id": message.id, "username": username, "msg": msg_text, "reply_to": reply_to, "file_url": file_url, "file_type": file_type}, room=room)

@socketio.on("edit_message")
def handle_edit_message(data):
    message_id = data["id"]
    new_msg = data["msg"]
    username = data["username"]
    room = data["room"]
    message = Message.query.get(message_id)
    if message:
        if message.username == username:
            message.msg = new_msg
            db.session.commit()
            emit("edit_message", {"id": message_id, "username": username, "msg": new_msg}, room=room)
        else:
            emit("error", {"msg": "Você não pode editar mensagens de outros usuários."})
    else:
        emit("error", {"msg": "Mensagem não encontrada."})

@socketio.on("delete_message")
def handle_delete_message(data):
    message_id = data["id"]
    username = data["username"]
    room = data["room"]
    message = Message.query.get(message_id)
    if message:
        if message.username == username:
            db.session.delete(message)
            db.session.commit()
            emit("delete_message", {"id": message_id}, room=room)
        else:
            emit("error", {"msg": "Você não pode excluir mensagens de outros usuários."})
    else:
        emit("error", {"msg": "Mensagem não encontrada."})

@socketio.on("leave")
def on_leave(data):
    username = data["username"]
    room = data["room"]
    leave_room(room)
    system_msg = f"{username} saiu da sala."
    system_message = Message(username="Sistema", room=room, msg=system_msg)
    db.session.add(system_message)
    db.session.commit()
    emit("message", {"id": system_message.id, "username": "Sistema", "msg": system_msg, "reply_to": None}, room=room)

@socketio.on("react_message")
def handle_react_message(data):
    message_id = data.get("message_id")
    emoji = data.get("emoji")
    username = data.get("username")
    room = data.get("room")
    existing = Reaction.query.filter_by(message_id=message_id, username=username, emoji=emoji).first()
    if existing:
        db.session.delete(existing)
    else:
        new_reaction = Reaction(message_id=message_id, username=username, emoji=emoji)
        db.session.add(new_reaction)
    db.session.commit()
    reactions = db.session.query(Reaction.emoji, db.func.count(Reaction.id))\
                    .filter_by(message_id=message_id)\
                    .group_by(Reaction.emoji).all()
    reaction_data = {emoji: count for emoji, count in reactions}
    emit("reaction_update", {"message_id": message_id, "reactions": reaction_data}, room=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)
