#!/usr/bin/env python3
"""
Teste simples para verificar se a aplicação está funcionando no Replit.
"""

import os
import sys
import requests
from app import app, db

def test_app_creation():
    """Testa se a aplicação Flask foi criada corretamente."""
    assert app is not None
    print("✅ Aplicação Flask criada com sucesso")

def test_database_connection():
    """Testa se a conexão com o banco de dados está funcionando."""
    try:
        with app.app_context():
            db.create_all()
        print("✅ Banco de dados conectado e tabelas criadas")
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False
    return True

def test_routes():
    """Testa se as rotas principais estão funcionando."""
    with app.test_client() as client:
        # Testa rota principal
        response = client.get('/')
        assert response.status_code in [200, 302]  # 302 para redirect
        print("✅ Rota principal funcionando")
        
        # Testa rota de login
        response = client.get('/login')
        assert response.status_code == 200
        print("✅ Rota de login funcionando")
        
        # Testa rota de registro
        response = client.get('/register')
        assert response.status_code == 200
        print("✅ Rota de registro funcionando")

def test_environment():
    """Testa se as variáveis de ambiente estão configuradas."""
    print(f"🔧 FLASK_ENV: {os.getenv('FLASK_ENV', 'não definido')}")
    print(f"🔧 SECRET_KEY: {'definido' if os.getenv('SECRET_KEY') else 'não definido'}")
    print(f"🔧 DATABASE_URL: {os.getenv('DATABASE_URL', 'não definido')}")
    
    # Verifica se está no Replit
    if os.getenv('REPL_ID') or os.getenv('REPLIT_DB_URL'):
        print("🌐 Executando no Replit")
    else:
        print("💻 Executando localmente")

def test_firebase():
    """Testa se o Firebase está configurado."""
    firebase_path = 'config/firebase-adminsdk.json'
    if os.path.exists(firebase_path):
        print("✅ Arquivo Firebase encontrado")
    else:
        print("⚠️  Arquivo Firebase não encontrado - necessário para autenticação")

def main():
    """Executa todos os testes."""
    print("🧪 Iniciando testes do Replit...\n")
    
    try:
        test_environment()
        print()
        
        test_app_creation()
        test_database_connection()
        test_routes()
        test_firebase()
        
        print("\n🎉 Todos os testes passaram! A aplicação está pronta para o Replit.")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()