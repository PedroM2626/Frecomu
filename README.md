# Frecomu


**Frecomu** é um aplicativo de chat em tempo real feito em Flask + Socket.IO + SQLite.  
Permite que seus usuários:

- 🔐 Criem conta e façam login com autenticação segura  
- 💬 Enviem e recebam mensagens em salas públicas ou privadas  
- ❤️ Reajam a qualquer mensagem com emojis  
- 🎥 Compartilhem vídeos diretamente no chat  
- 🛡️ Gerenciem permissões de acesso às salas  

---

## 📦 Tecnologias

- **Backend**: Python 3.10, Flask, Flask-Login, Flask-SocketIO  
- **Banco de Dados**: SQLite (via SQLAlchemy)  
- **Realtime**: Flask-SocketIO (WebSockets)  
- **Frontend**: HTML5, CSS3, JavaScript (ES6)  
- **Armazenamento de mídia**: pasta `uploads/` local  

---

## 🚀 Pré-requisitos

- Python 3.10+  
- Git  
- (Opcional) Virtualenv ou Conda  

---

## 🔧 Instalação

# 1. Clone o repositório
git clone https://github.com/PedroM2626/frecomu.git
cd frecomu

# 2. Crie e ative um virtualenv
python3 -m venv .venv
source .venv/bin/activate    # Linux/macOS
.\.venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install --upgrade pip
pip install -r requirements.txt
⚙️ Configuração
Renomeie .env.example para .env e preencha:

ini
Copy
Edit
SECRET_KEY=<uma string aleatória e segura>
DATABASE_URL=sqlite:///frecomu.db
UPLOAD_FOLDER=./uploads
SECRET_KEY: usado pelo Flask para sessões

DATABASE_URL: string de conexão SQLAlchemy

UPLOAD_FOLDER: pasta onde vídeos enviados serão guardados

▶️ Como rodar
bash
Copy
Edit
# 1. (Opcional) inicialize o banco de dados vazio
flask db upgrade

# 2. Inicie o servidor Flask
export FLASK_APP=main.py       # Linux/macOS
set FLASK_APP=main.py          # Windows

flask run
# ou, para WebSockets:
python main.py
O app ficará disponível em http://localhost:5000.

📋 Estrutura de Pastas
csharp
Copy
Edit
frecomu/
├── main.py            # entrypoint: cria app e SocketIO
├── requirements.txt
├── .env.example
├── models.py          # definições de User, Room, Message, Reaction
├── routes.py          # rotas HTTP (login, registro, páginas)
├── socket_handlers.py # eventos Socket.IO (join, message, react)
├── templates/         # HTML Jinja2
│   ├── base.html
│   ├── login.html
│   ├── chat.html
│   └── ...
├── static/            # CSS, JS, assets
│   ├── css/
│   └── js/
├── uploads/           # vídeos enviados
└── migrations/        # arquivos de migração Alembic
📱 Funcionalidades em Detalhe
Autenticação

Registro e login com Flask-Login

Senhas armazenadas com hashing seguro (Werkzeug)

Salas de Chat

Públicas: qualquer usuário logado pode entrar

Privadas: somente usuários convidados ou com link de convite

Mensagens & Reações

Cada mensagem tem um ID único

Usuários podem reagir com emojis; contado em tempo real

Envio de Vídeos

Formatos permitidos: .mp4, .webm

Tamanho máximo configurável em UPLOAD_FOLDER

WebSockets em Tempo Real

join_room / leave_room

Broadcast de novas mensagens e reações

🤝 Contribuições
Fork este repositório

Crie uma branch feature:

bash
Copy
Edit
git checkout -b feature/nova-funcionalidade
Commit suas mudanças e envie:

bash
Copy
Edit
git commit -m "Adiciona recurso X"
git push origin feature/nova-funcionalidade
Abra um Pull Request no GitHub

📝 Licença
Este projeto está licenciado sob a MIT License.

<p align="center">🎉 Obrigado por usar o Frecomu! 🎉</p>
