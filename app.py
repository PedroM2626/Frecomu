import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase configuration
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate('config/firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {e}")

app = Flask(__name__)

# Load configuration
from config import config
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
migrate = Migrate(app, db)

# Modelo de Sala para persistir no banco de dados
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  # Removido unique=True para permitir salas com o mesmo nome
    private = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=True)
    owner = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    messages = db.relationship('Message', backref='room_obj', lazy=True)

# Modelo de Mensagem atualizado (suporta arquivos)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    msg = db.Column(db.Text, nullable=True)  # Pode ser vazio para mensagens de áudio
    file_url = db.Column(db.String(255), nullable=True)  # URL do arquivo (áudio, vídeo, documento)
    file_type = db.Column(db.String(50), nullable=True)  # 'audio', 'video', 'document'
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reply_to = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    parent = db.relationship('Message', remote_side=[id], uselist=False)
    reactions = db.relationship('Reaction', backref='message', lazy=True)

# Modelo de Reação permanece o mesmo
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Rota para servir arquivos enviados (uploads)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rotas de autenticação (login e register) devem existir
@app.route("/login")
def login():
    # Verifica se o parâmetro no_redirect está presente na URL
    no_redirect = request.args.get('no_redirect', 'false').lower() == 'true'
    
    # Renderiza a página de login sem redirecionamento automático
    # Isso evita loops de redirecionamento entre login e index
    return render_template("login.html", no_redirect=no_redirect)

@app.route("/register")
def register():
    if session.get("username"):
        return redirect(url_for("index"))
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
            
            # Buscar sala no banco de dados
            room = Room.query.filter_by(name=room_name).first()
            if not room:
                error = "Sala não existe."
            else:
                if room.private:
                    if not entered_password:
                        error = "Senha é obrigatória para entrar nessa sala."
                    elif entered_password != room.password:
                        error = "Senha incorreta."
                if not error:
                    session["username"] = username
                    session["room"] = room_name
                    return redirect(url_for("chat"))
        else:
            # Modo "criar" sala
            room_name = request.form.get("room_name", "").strip()
            is_private = request.form.get("is_private") == "on"
            password = request.form.get("password", "").strip() if is_private else None
            username = session.get("username")
            
            if not username:
                error = "Usuário não autenticado."
            elif not room_name:
                error = "O nome da sala é obrigatório."
            else:
                # Não precisamos mais verificar se a sala já existe, pois permitimos salas com o mesmo nome
                # Criar nova sala no banco de dados
                    new_room = Room(
                        name=room_name,
                        private=is_private,
                        password=password,
                        owner=username
                    )
                    db.session.add(new_room)
                    db.session.commit()
                    return redirect(url_for("index", room=room_name))
    
    # Buscar todas as salas do banco de dados
    rooms_data = {}
    for room in Room.query.all():
        rooms_data[room.name] = {
            "private": room.private,
            "password": room.password,
            "owner": room.owner
        }
    
    # Passa o usuário logado como current_user para o template
    return render_template("index.html", rooms=rooms_data, error=error, room=room_param, current_user=session.get("username"))

# Rota do chat
@app.route("/chat")
def chat():
    username = session.get("username")
    room = session.get("room")
    
    if not username or not room:
        return redirect(url_for("index"))
    
    # Buscar o room_id a partir do nome da sala
    room_obj = Room.query.filter_by(name=room).first()
    if room_obj:
        # Usar room_id para filtrar mensagens
        messages = Message.query.filter_by(room_id=room_obj.id).order_by(Message.timestamp).all()
    else:
        # Fallback para o campo room se não encontrar o room_id
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
    
    # Verificar se o usuário está logado
    if not session.get("username"):
        return jsonify({"error": "Usuário não autenticado."}), 401
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({"url": url_for('uploaded_file', filename=filename), "file_type": file.mimetype})

# Rota para o perfil (exibe a página de configurações do perfil)
@app.route('/profile')
def profile():
    username = session.get("username")
    if not username:
        return redirect(url_for("index"))
    return render_template("profile.html", username=username)

# Rota para logout
@app.route('/logout')
def logout():
    # Limpar toda a sessão
    session.clear()
    # Redirecionar para a página de login com parâmetro no_redirect
    return redirect(url_for('login', no_redirect="true"))

# Rota para editar o nome da sala (apenas para o owner)
@app.route("/edit_room", methods=["POST"])
def edit_room():
    if not session.get("username"):
        return jsonify({"error": "Usuário não autenticado."}), 401
    
    old_room = request.form.get("old_room")
    new_room = request.form.get("new_room", "").strip()
    
    if not old_room or not new_room:
        return jsonify({"error": "Dados inválidos."}), 400
    
    # Buscar sala no banco de dados
    room = Room.query.filter_by(name=old_room).first()
    if not room:
        return jsonify({"error": "Sala não existe."}), 400
    
    if room.owner != session.get("username"):
        return jsonify({"error": "Você não é o criador desta sala."}), 403
    
    # Verificar se o novo nome já existe
    existing_room = Room.query.filter_by(name=new_room).first()
    if existing_room:
        return jsonify({"error": "O novo nome já está em uso."}), 400
    
    # Atualizar a sala no banco de dados
    room.name = new_room
    db.session.commit()
    
    # Atualizar mensagens no banco
    Message.query.filter_by(room=old_room).update({"room": new_room})
    db.session.commit()
    
    if session.get("room") == old_room:
        session["room"] = new_room
    
    return jsonify({"new_room": new_room}), 200

# Rota para excluir a sala (apenas para o owner)
@app.route("/delete_room", methods=["POST"])
def delete_room():
    if not session.get("username"):
        return jsonify({"error": "Usuário não autenticado."}), 401
    
    room_name = request.form.get("room")
    if not room_name:
        return jsonify({"error": "Nome da sala não fornecido."}), 400
    
    # Buscar sala no banco de dados
    room = Room.query.filter_by(name=room_name).first()
    if not room:
        return jsonify({"error": "Sala não existe."}), 400
    
    if room.owner != session.get("username"):
        return jsonify({"error": "Você não é o criador desta sala."}), 403
    
    # Remover mensagens associadas primeiro
    Message.query.filter_by(room=room_name).delete()
    
    # Remover a sala do banco de dados
    db.session.delete(room)
    db.session.commit()
    
    if session.get("room") == room_name:
        session.pop("room", None)
    
    return jsonify({"deleted_room": room_name}), 200

# SocketIO – Eventos para chat e reações
@socketio.on("join")
def on_join(data):
    username = data.get("username")
    room = data.get("room")
    
    if not username or not room:
        emit("error", {"msg": "Dados inválidos para entrar na sala."})
        return
    
    join_room(room)
    system_msg = f"{username} entrou na sala."
    
    # Buscar o room_id a partir do nome da sala
    room_obj = Room.query.filter_by(name=room).first()
    room_id = room_obj.id if room_obj else None
    
    system_message = Message(username="Sistema", room=room, room_id=room_id, msg=system_msg)
    db.session.add(system_message)
    db.session.commit()
    emit("message", {"id": system_message.id, "username": "Sistema", "msg": system_msg, "reply_to": None}, room=room)

@socketio.on("message")
def handle_message(data):
    room = data.get("room")
    username = data.get("username")
    msg_text = data.get("msg")  # pode ser None se for arquivo
    reply_to = data.get("reply_to")
    file_url = data.get("file_url")
    file_type = data.get("file_type")
    
    if not room or not username:
        emit("error", {"msg": "Dados inválidos para enviar mensagem."})
        return
    
    # Não armazenamos a foto de perfil no banco; o cliente irá enviar o photoURL
    # Buscar o room_id a partir do nome da sala
    room_obj = Room.query.filter_by(name=room).first()
    room_id = room_obj.id if room_obj else None
    
    message = Message(username=username, room=room, room_id=room_id, msg=msg_text, reply_to=reply_to, file_url=file_url, file_type=file_type)
    db.session.add(message)
    db.session.commit()
    
    # Inclui a foto de perfil (se enviada) na resposta do socket
    photoURL = data.get("photoURL")
    emit("message", {
        "id": message.id,
        "username": username,
        "msg": msg_text,
        "reply_to": reply_to,
        "file_url": file_url,
        "file_type": file_type,
        "photoURL": photoURL
    }, room=room)


@socketio.on("edit_message")
def handle_edit_message(data):
    message_id = data.get("id")
    new_msg = data.get("msg")
    username = data.get("username")
    room = data.get("room")
    
    if not all([message_id, new_msg, username, room]):
        emit("error", {"msg": "Dados inválidos para editar mensagem."})
        return
    
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
    message_id = data.get("id")
    username = data.get("username")
    room = data.get("room")
    
    if not all([message_id, username, room]):
        emit("error", {"msg": "Dados inválidos para excluir mensagem."})
        return
    
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
    username = data.get("username")
    room = data.get("room")
    
    if not username or not room:
        emit("error", {"msg": "Dados inválidos para sair da sala."})
        return
    
    leave_room(room)
    system_msg = f"{username} saiu da sala."
    
    # Buscar o room_id a partir do nome da sala
    room_obj = Room.query.filter_by(name=room).first()
    room_id = room_obj.id if room_obj else None
    
    system_message = Message(username="Sistema", room=room, room_id=room_id, msg=system_msg)
    db.session.add(system_message)
    db.session.commit()
    emit("message", {"id": system_message.id, "username": "Sistema", "msg": system_msg, "reply_to": None}, room=room)

@socketio.on("react_message")
def handle_react_message(data):
    message_id = data.get("message_id")
    emoji = data.get("emoji")
    username = data.get("username")
    room = data.get("room")
    
    if not all([message_id, emoji, username, room]):
        emit("error", {"msg": "Dados inválidos para reagir à mensagem."})
        return
    
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
    # Initialize database if it doesn't exist
    with app.app_context():
        db.create_all()
    # Use threading mode for better Windows compatibility
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
