#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do Frecomu
"""

from app import app, db

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Banco de dados inicializado com sucesso!")
            print("📊 Tabelas criadas:")
            
            # Listar tabelas criadas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            for table in tables:
                print(f"   - {table}")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Inicializando banco de dados do Frecomu...")
    success = init_database()
    
    if success:
        print("\n🎉 Banco de dados pronto para uso!")
        print("💡 Execute 'python app.py' para iniciar o servidor")
    else:
        print("\n💥 Falha ao inicializar banco de dados")
        exit(1)
