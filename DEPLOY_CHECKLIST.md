# ✅ Checklist de Deploy no Replit

Antes de fazer o deploy no Replit, verifique se todos os itens abaixo estão completos:

## 📋 Pré-Deploy

### ✅ Arquivos Necessários
- [ ] `main.py` - Ponto de entrada principal ✅ **Criado**
- [ ] `.replit` - Configuração do ambiente ✅ **Criado**
- [ ] `replit.nix` - Ambiente Nix ✅ **Criado**
- [ ] `pyproject.toml` - Dependências ✅ **Criado**
- [ ] `requirements.txt` - Dependências alternativas ✅ **Existe**
- [ ] `.env.example` - Exemplo de variáveis ✅ **Criado**

### ✅ Configurações
- [ ] `config.py` atualizado com `ReplitConfig` ✅ **Configurado**
- [ ] `app.py` detecta ambiente Replit automaticamente ✅ **Configurado**
- [ ] `.gitignore` inclui arquivos do Replit ✅ **Atualizado**

### ✅ Documentação
- [ ] `README_REPLIT.md` com instruções completas ✅ **Criado**
- [ ] `README.md` atualizado com seção Replit ✅ **Atualizado**
- [ ] `test_replit.py` para verificar funcionamento ✅ **Criado**

## 🚀 No Replit

### 📁 Upload de Arquivos
- [ ] Fazer upload de todos os arquivos do projeto
- [ ] Criar pasta `config/`
- [ ] Fazer upload do `firebase-adminsdk.json` para `config/`

### 🔐 Variáveis de Ambiente (Secrets)
Configure as seguintes variáveis em "Secrets":
- [ ] `SECRET_KEY` - Chave secreta segura
- [ ] `FLASK_ENV` - `production`
- [ ] `DATABASE_URL` - `sqlite:///frecomu.db` (opcional)
- [ ] `UPLOAD_FOLDER` - `/tmp/uploads` (opcional)

### 🧪 Testes
- [ ] Executar `python test_replit.py` para verificar
- [ ] Verificar se não há erros no console
- [ ] Testar acesso às rotas principais

### 🌐 Deploy Final
- [ ] Clicar em "Run" no Replit
- [ ] Verificar se a aplicação inicia sem erros
- [ ] Testar funcionalidades principais:
  - [ ] Registro de usuário
  - [ ] Login
  - [ ] Criação de salas
  - [ ] Envio de mensagens
  - [ ] Upload de arquivos

## 🔧 Troubleshooting

### ❌ Problemas Comuns

**Erro de Firebase:**
- Verifique se `firebase-adminsdk.json` está em `config/`
- Confirme permissões do Firebase

**Erro de Porta:**
- Replit define automaticamente via `PORT`
- Não configure manualmente

**Erro de Dependências:**
- Execute `pip install -r requirements.txt`
- Verifique `pyproject.toml`

**Erro de Banco:**
- SQLite é criado automaticamente
- Verifique permissões de escrita

## 📞 Suporte

Se encontrar problemas:
1. ✅ Verifique este checklist
2. 📖 Consulte `README_REPLIT.md`
3. 🧪 Execute `test_replit.py`
4. 📋 Verifique logs no console do Replit

---

## 🎉 Status do Projeto

**✅ PROJETO TOTALMENTE CONFIGURADO PARA REPLIT!**

Todos os arquivos necessários foram criados e configurados. O projeto está pronto para deploy no Replit seguindo as instruções do `README_REPLIT.md`.

### 📊 Resumo das Modificações:
- ✅ 7 novos arquivos criados
- ✅ 3 arquivos existentes atualizados
- ✅ Configuração automática de ambiente
- ✅ Testes de verificação incluídos
- ✅ Documentação completa

**Próximo passo:** Fazer upload no Replit e seguir o guia de deploy!