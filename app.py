import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SECRET_KEY"] = "sua_chave_secreta_muito_dificil"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///frecomu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
migrate = Migrate(app, db)

# Armazenamento simples das salas em memória
rooms = {}
# Exemplo:
# rooms = {
#     "geral": {"private": False, "password": None},
#     "amigos": {"private": True, "password": "123456"}
# }

# Modelo de Mensagem com campo opcional "reply_to"
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    msg = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reply_to = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    # Relacionamento para a mensagem original (pai)
    parent = db.relationship('Message', remote_side=[id], uselist=False)
    # Relacionamento com as reações:
    reactions = db.relationship('Reaction', backref='message', lazy=True)

# Modelo de Reação
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Rota de login (template login.html deve existir)
@app.route("/login")
def login():
    return render_template("login.html")

# Rota de registro (template register.html deve existir)
@app.route("/register")
def register():
    return render_template("register.html")

# Rota unificada para criar ou entrar em salas
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    # Se há o parâmetro "room" na query string, estamos no modo "entrar"
    room_param = request.args.get("room")
    
    if request.method == "POST":
        if room_param:
            # Formulário de entrada (join)
            username = request.form.get("username", "").strip()
            room_name = room_param  # já definido na URL
            entered_password = request.form.get("password", "").strip()
            if room_name not in rooms:
                error = "Sala não existe."
            else:
                room = rooms[room_name]
                if room["private"]:
                    if not entered_password:
                        error = "Senha é obrigatória para entrar nessa sala."
                    elif entered_password != room["password"]:
                        error = "Senha incorreta."
                if not username:
                    error = "Você deve inserir seu nome."
                if not error:
                    session["username"] = username
                    session["room"] = room_name
                    return redirect(url_for("chat"))
        else:
            # Formulário de criação de sala
            room_name = request.form.get("room_name", "").strip()
            is_private = request.form.get("is_private") == "on"
            password = request.form.get("password", "").strip() if is_private else None
            if not room_name:
                error = "O nome da sala é obrigatório."
            elif room_name in rooms:
                error = "Essa sala já existe."
            else:
                rooms[room_name] = {"private": is_private, "password": password}
                # Após criar, redireciona para a mesma página com ?room=nome_da_sala para que o usuário possa entrar
                return redirect(url_for("index", room=room_name))
    
    # Renderiza o template unificado: se room_param estiver definido, exibe o formulário de entrada; senão, exibe o formulário de criação e a lista de salas
    return render_template("index.html", rooms=rooms, error=error, room=room_param)

# Rota do chat
@app.route("/chat")
def chat():
    username = session.get("username")
    room = session.get("room")
    if not username or not room:
        return redirect(url_for("index"))
    messages = Message.query.filter_by(room=room).order_by(Message.timestamp).all()
    return render_template("chat.html", username=username, room=room, messages=messages)

# SocketIO – Eventos permanecem inalterados

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
    msg_text = data["msg"]
    reply_to = data.get("reply_to")  # Pode ser None se não for resposta
    message = Message(username=username, room=room, msg=msg_text, reply_to=reply_to)
    db.session.add(message)
    db.session.commit()
    emit("message", {"id": message.id, "username": username, "msg": msg_text, "reply_to": reply_to}, room=room)

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
