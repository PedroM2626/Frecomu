from app import app, db, Room, Message

def update_message_room_ids():
    print("Iniciando atualização de room_id nas mensagens existentes...")
    
    # Usar o contexto da aplicação Flask
    with app.app_context():
        # Buscar todas as mensagens que não têm room_id definido
        messages_without_room_id = Message.query.filter(Message.room_id.is_(None)).all()
        print(f"Encontradas {len(messages_without_room_id)} mensagens sem room_id.")
        
        # Atualizar cada mensagem
        updated_count = 0
        for message in messages_without_room_id:
            # Buscar a sala pelo nome
            room = Room.query.filter_by(name=message.room).first()
            if room:
                message.room_id = room.id
                updated_count += 1
            else:
                print(f"Sala '{message.room}' não encontrada para a mensagem {message.id}")
        
        # Salvar as alterações no banco de dados
        if updated_count > 0:
            db.session.commit()
            print(f"Atualizadas {updated_count} mensagens com room_id.")
        else:
            print("Nenhuma mensagem foi atualizada.")

if __name__ == "__main__":
    update_message_room_ids()