# Instruções de Deploy para Render.com

Este guia explica como fazer o deploy da aplicação Frecomu no Render.com de forma gratuita.

## Pré-requisitos

1. Uma conta no [GitHub](https://github.com/)
2. Uma conta no [Render.com](https://render.com/)
3. O código do projeto em um repositório GitHub

## Passo a Passo

### 1. Preparar o Repositório

1. Crie um repositório no GitHub (se ainda não tiver um)
2. Faça upload do código para o repositório
3. Certifique-se de que todos os arquivos necessários estão incluídos:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `render.yaml`
   - `setup.sh`
   - `config/firebase-adminsdk.json` (se estiver usando Firebase)

### 2. Configurar o Render.com

1. Acesse o [Painel do Render](https://dashboard.render.com/)
2. Clique em "New +" e selecione "Web Service"
3. Conecte sua conta do GitHub e selecione o repositório

### 3. Configurar o Serviço Web

1. **Nome do Serviço**: `frecomu` (ou o nome que preferir)
2. **Branch**: `main` (ou a branch que deseja fazer deploy)
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn --worker-class eventlet -w 1 app:app`

### 4. Configurar Variáveis de Ambiente

Adicione as seguintes variáveis de ambiente no painel do Render:

- `PYTHON_VERSION`: `3.10.13`
- `FLASK_APP`: `app.py`
- `FLASK_ENV`: `production`
- `SECRET_KEY`: Gere uma chave segura (você pode usar `openssl rand -hex 16` no terminal)
- `DATABASE_URL`: Render irá fornecer automaticamente uma URL de banco de dados PostgreSQL
- `UPLOAD_FOLDER`: `/opt/render/project/src/uploads`
- `FIREBASE_CREDENTIALS`: Cole o conteúdo do seu arquivo `firebase-adminsdk.json` (se estiver usando Firebase)

### 5. Configurar o Banco de Dados

1. No painel do Render, clique em "New +" e selecione "PostgreSQL"
2. Escolha o plano gratuito
3. Após a criação, vá para as configurações do banco de dados e copie a URL de conexão
4. Volte para as configurações do serviço web e atualize a variável `DATABASE_URL` com a URL fornecida

### 6. Inicializar o Banco de Dados

1. No painel do Render, vá para a aba "Shell" do seu serviço web
2. Execute os seguintes comandos:
   ```bash
   python init_db.py
   flask db upgrade
   ```

### 7. Finalizar o Deploy

1. Clique em "Save Changes" e depois em "Deploy"
2. Aguarde o deploy ser concluído (pode levar alguns minutos)
3. Após o deploy, sua aplicação estará disponível na URL fornecida pelo Render

## Solução de Problemas Comuns

- **Erro de Banco de Dados**: Verifique se as migrações foram aplicadas corretamente
- **Arquivos não encontrados**: Certifique-se de que o diretório de uploads tem permissões corretas
- **Erros de Dependência**: Verifique se todas as dependências estão listadas no `requirements.txt`

## Manutenção

- O Render oferece logs em tempo real na aba "Logs" do painel
- Para atualizar a aplicação, basta fazer push para o repositório conectado
- O plano gratuito tem algumas limitações, como tempo de inatividade após 15 minutos sem acesso

## Recursos Adicionais

- [Documentação do Render](https://render.com/docs)
- [Documentação do Flask](https://flask.palletsprojects.com/)
- [Documentação do SQLAlchemy](https://www.sqlalchemy.org/)
