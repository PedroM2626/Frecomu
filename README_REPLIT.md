# Deploy no Replit - Frecomu

Este guia explica como fazer o deploy do projeto Frecomu no Replit.

## 📋 Pré-requisitos

1. Conta no [Replit](https://replit.com)
2. Arquivo `firebase-adminsdk.json` (credenciais do Firebase)

## 🚀 Passos para Deploy

### 1. Importar o Projeto

1. Acesse [Replit](https://replit.com)
2. Clique em "Create Repl"
3. Selecione "Import from GitHub" ou "Upload files"
4. Faça upload dos arquivos do projeto

### 2. Configurar Variáveis de Ambiente

No painel do Replit, vá em "Secrets" (ícone de cadeado) e adicione:

```
SECRET_KEY=sua_chave_secreta_muito_segura
FLASK_ENV=production
DATABASE_URL=sqlite:///frecomu.db
UPLOAD_FOLDER=/tmp/uploads
```

### 3. Configurar Firebase

1. Crie uma pasta `config/` no seu Repl
2. Faça upload do arquivo `firebase-adminsdk.json` para a pasta `config/`
3. Certifique-se de que o caminho está correto: `config/firebase-adminsdk.json`

### 4. Instalar Dependências

O Replit instalará automaticamente as dependências do `pyproject.toml`. Se necessário, você pode executar:

```bash
pip install -r requirements.txt
```

### 5. Executar o Projeto

Clique no botão "Run" ou execute:

```bash
python main.py
```

## 🔧 Configurações Específicas do Replit

O projeto foi configurado para detectar automaticamente o ambiente Replit através das variáveis:
- `REPL_ID`
- `REPLIT_DB_URL`

Quando detectado, usa a configuração `ReplitConfig` que:
- Define `DEBUG = False`
- Usa `/tmp/uploads` para arquivos temporários
- Configura o host como `0.0.0.0`
- Usa a porta fornecida pelo Replit

## 📁 Arquivos Específicos do Replit

- `main.py` - Ponto de entrada principal
- `.replit` - Configuração do ambiente Replit
- `replit.nix` - Definição do ambiente Nix
- `pyproject.toml` - Gerenciamento de dependências

## 🌐 Acesso à Aplicação

Após o deploy, sua aplicação estará disponível em:
```
https://seu-repl-name.seu-username.repl.co
```

## 🔒 Segurança

1. **Nunca** commite o arquivo `firebase-adminsdk.json` no repositório
2. Use variáveis de ambiente para informações sensíveis
3. Mantenha a `SECRET_KEY` segura

## 🐛 Troubleshooting

### Erro de Firebase
- Verifique se o arquivo `firebase-adminsdk.json` está na pasta `config/`
- Confirme se as permissões do Firebase estão corretas

### Erro de Porta
- O Replit define automaticamente a porta via variável `PORT`
- Não é necessário configurar manualmente

### Erro de Banco de Dados
- O SQLite será criado automaticamente
- Para dados persistentes, considere usar Replit Database

### Arquivos de Upload
- Arquivos são salvos em `/tmp/uploads` (temporário)
- Para persistência, configure um serviço de armazenamento externo

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no console do Replit
2. Confirme se todas as variáveis de ambiente estão configuradas
3. Teste localmente primeiro

---

✅ **Projeto configurado com sucesso para Replit!**