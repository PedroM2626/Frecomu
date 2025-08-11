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

# 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto com:
```
SECRET_KEY=sua_chave_secreta_muito_dificil_e_segura_para_producao
DATABASE_URL=sqlite:///frecomu.db
UPLOAD_FOLDER=./uploads
FLASK_APP=app.py
FLASK_ENV=development
```

# 5. Inicialize o banco de dados
python init_db.py

# 6. Execute o aplicativo
python app.py

# O app ficará disponível em http://127.0.0.1:5000

# 7. Para testar se está funcionando (em outro terminal):
python test_app.py

📋 Estrutura de Pastas

```
frecomu/
├── app.py             # Aplicação principal Flask + SocketIO
├── config.py          # Configurações do projeto
├── init_db.py         # Script para inicializar banco de dados
├── requirements.txt   # Dependências Python
├── .env               # Variáveis de ambiente (não commitado)
├── .env.example       # Exemplo de variáveis de ambiente
├── test_app.py        # Script de teste da aplicação
├── templates/         # Templates HTML Jinja2
│   ├── login.html     # Página de login
│   ├── register.html  # Página de registro
│   ├── chat.html      # Interface do chat
│   ├── profile.html   # Perfil do usuário
│   └── index.html     # Página principal com salas
├── static/            # Arquivos estáticos (CSS, JS, imagens)
├── uploads/           # Pasta para arquivos enviados
├── config/            # Configurações do Firebase
│   └── firebase-adminsdk.json
└── instance/          # Banco de dados SQLite
```
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
