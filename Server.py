import socket
import threading

class Cliente:
    name = ""
    conn = None
    addr = None

def clientthread(conn, addr):
    # Esta función maneja la comunicación con un cliente específico
    while True:
        #try:
            message = conn.recv(BUFFER_SIZE)
            if message:
                print(f"<{addr[0]}> {message}")
                msg = message.decode('utf-8')#decodificamos el mensaje recibido a 8 # bits
                # Mensajes especiales (comandos)
                if msg.startswith('<name>'):
                    setName(conn, msg.removeprefix('<name>'))
                elif msg.startswith('<get_clients>'):
                    # <list_of_clients> - Envía la lista de clientes conectados
                    client_list = getClients()
                    if client_list:
                        response = f"<get_clients>{client_list}"
                    else:
                        response = "<No hay clientes conectados>"
                    broadcast_only_to(response, conn)
                    
                elif msg.startswith('<only_to>'):
                    # <only_to>Nombre del cliente<text> - Envía un mensaje solo a un cliente específico
                    # Solo me da el nombre del cliente que va dirigido
                    name =  msg.split("<only_to>")[1].split("<text>")[0].strip()
                    # Solo el texto del cliente que va dirigido
                    text = msg.split("<text>")[1].strip()
                    message_to_send = f"<only_to><{getName(conn)}> {text}\n"
                    found = False
                    # Buscamos al cliente por su nombre   
                    for client in list_of_clients:
                        if client.name == name:
                            broadcast_only_to(message_to_send, client.conn)
                            found = True
                            break
                    if not found:
                        # Si no se encuentra el cliente, enviamos un mensaje de error
                        error_message = f"<Error> Cliente '{name}' no encontrado.\n"
                        broadcast_only_to(error_message, conn)
                        
                elif msg.startswith('<conection_ESP32>'):
                    # <conection_ESP32>ESP32<text> comando que hara la ESP32
                    name = msg.split("<conection_ESP32>")[1].split("<text>")[0].strip()
                    text = msg.split("<text>")[1].strip()
                    message_to_send = text + "\n"
                    print(message_to_send)
                    found = False
                    broadcast(message_to_send, conn)
                    
                elif msg.startswith('<group>'):
                    # <group>Nombre del grupo<Integrants>Nombre1,Nombre2,Nombre3
                    # Da el nombre del grupo
                    name_group = msg.split("<group>")[1].split("<Integrants>")[0].strip()
                    # Da los nombres de los integrantes del grupo en un string separados por ','
                    integrants = msg.split("<Integrants>")[1].strip()
                    # Da los nombres de los integrantes del grupo
                    names =  msg.split("<Integrants>")[1].strip().split(',')
                    message_to_send = f'<group>{name_group}<Integrants>{integrants}'
                    
                    found_any = False
                    for name in names:
                        name = name.strip()
                        found = False
                        for client in list_of_clients:
                            if client.name == name:
                                broadcast_only_to(message_to_send, client.conn)
                                found = True
                                found_any = True
                                break
                        if not found:
                            # Cliente no encontrado
                            error_message = f"<Error> Cliente '{name}' no encontrado.\n"
                            broadcast_only_to(error_message, conn)

                    if not found_any:
                        # Ningún cliente válido encontrado
                        error_message = "<Error> Ningún cliente encontrado.\n"
                        broadcast_only_to(error_message, conn)
                    
                elif msg.startswith('<some_people>'):
                    # <some_people>Nombre1,Nombre2<text> - Envía un mensaje a varios clientes específicos"
                    # Da los nombres a quienes van dirigidos
                    names = msg.split("<some_people>")[1].split("<text>")[0].strip().split(',')
                    # El texto a quienes van dirigidos
                    text = msg.split("<text>")[1].strip()
                    message_to_send = f"<some_people><{getName(conn)}> {text}\n"

                    found_any = False
                    for name in names:
                        name = name.strip()
                        found = False
                        for client in list_of_clients:
                            if client.name == name:
                                broadcast_only_to(message_to_send, client.conn)
                                found = True
                                found_any = True
                                break
                        if not found:
                            # Cliente no encontrado
                            error_message = f"<Error> Cliente '{name}' no encontrado.\n"
                            broadcast_only_to(error_message, conn)

                    if not found_any:
                        # Ningún cliente válido encontrado
                        error_message = "<Error> Ningún cliente encontrado.\n"
                        broadcast_only_to(error_message, conn)
                        
                elif msg.startswith('<chess_move>'):
                    # <chess_move>NombreDelRival<text>e2e4
                    try:
                        name = msg.split("<chess_move>")[1].split("<text>")[0].strip()
                        move = msg.split("<text>")[1].strip()
                        sender = getName(conn)
                        message_to_send = f"<chess_move>{move}<from>{sender}"
                        found = False
                        for client in list_of_clients:
                            if client.name == name:
                                broadcast_only_to(message_to_send, client.conn)
                                found = True
                                break
                        if not found:
                            error_message = f"<Error> Cliente '{name}' no encontrado.\n"
                            broadcast_only_to(error_message, conn)
                    except Exception as e:
                        error_message = f"<Error> Fallo al procesar movimiento: {e}\n"
                        broadcast_only_to(error_message, conn)

                elif msg.startswith('<chess_surrender>'):
                    # <chess_surrender>NombreDelRival
                    name = msg.replace("<chess_surrender>", "").strip()
                    message_to_send = f"<chess_surrender>{getName(conn)}"
                    found = False
                    for client in list_of_clients:
                        if client.name == name:
                            broadcast_only_to(message_to_send, client.conn)
                            found = True
                            break
                    if not found:
                        error_message = f"<Error> Cliente '{name}' no encontrado.\n"
                        broadcast_only_to(error_message, conn)

                elif msg.startswith('<chess_invite>'):
                    # <chess_invite>NombreDelRival
                    parts = msg.replace("<chess_invite>", "").split("<from>")
                    to_user = parts[0].strip()
                    from_user = parts[1].strip()
                    message_to_send = f"<chess_invite>{to_user}<from>{from_user}"
                    found = False
                    for client in list_of_clients:
                        if client.name == to_user:#correccion//to_user=name
                            broadcast_only_to(message_to_send, client.conn)
                            found = True
                            break
                    if not found:
                        error_message = f"<Error> Cliente '{to_user}' no encontrado.\n"#to_user=name //correccion
                        broadcast_only_to(error_message, conn)

                elif msg.startswith('<chess_accept>'):
                    # <chess_accept>NombreDelRival
                    name = msg.replace("<chess_accept>", "").strip()
                    message_to_send = f"<chess_accept>{getName(conn)}"
                    found = False
                    for client in list_of_clients:
                        if client.name == name:
                            broadcast_only_to(message_to_send, client.conn)
                            found = True
                            break
                    if not found:
                        error_message = f"<Error> Cliente '{name}' no encontrado.\n"
                        broadcast_only_to(error_message, conn)
                        
                elif msg.startswith('<gato_invite>'):
                    try:
                        # Esperado: <gato_invite>to_user<from>from_user
                        parts = msg.replace("<gato_invite>", "").split("<from>")
                        to_user = parts[0].strip()
                        from_user = parts[1].strip()
                        print(f"[GATO] Invitación de {from_user} a {to_user}")
                        found = False
                        for client in list_of_clients:
                            if client.name == to_user:
                                client.conn.send(message)
                                print(f"[GATO] Invitación enviada a {to_user}")
                                found = True
                                break
                        if not found:
                            error_msg = f"<Error> Cliente '{to_user}' no encontrado para invitación de gato"
                            for client in list_of_clients:
                                if client.name == from_user:
                                    client.conn.send(error_msg.encode('utf-8'))
                                    break
                    except Exception as e:
                        print(f"[GATO] Error procesando invitación: {e}")
                        
                elif msg.startswith('<gato_accept>'):
                    # msg: <gato_accept>nombre_del_retador
                    name = msg.split("<gato_accept>")[1].strip()
                    message_to_send = f"<gato_accept>{getName(conn)}"
                    print(f"[GATO] {getName(conn)} aceptó la invitación. Enviando a {name}")
                    found = False
                    for client in list_of_clients:
                        if client.name == name:
                            broadcast_only_to(message_to_send, client.conn)
                            found = True
                            break
                    if not found:
                        error_message = f"<Error> Cliente '{name}' no encontrado para aceptar invitación.\n"
                        broadcast_only_to(error_message, conn)
                        
                elif msg.startswith('<jugar>'):
                    try:
                        name = msg.split("<jugar>")[1].split("<")[0].strip()
                        found = False
                        for client in list_of_clients:
                            if client.name == name:
                                client.conn.send(message)
                                print(f"[GATO] Enviada jugada a {name}: {msg}")
                                found = True
                                break
                        if not found:
                            error_message = f"<Error> Cliente '{name}' no encontrado para jugada de gato.\n"
                            broadcast_only_to(error_message, conn)
                    except Exception as e:
                        print(f"[GATO] Error procesando jugada: {e}")

                elif msg.startswith('<gato_surrender>'):
                    name = msg.split("<gato_surrender>")[1].strip()
                    message_to_send = f"<gato_surrender>{getName(conn)}"
                    found = False
                    for client in list_of_clients:
                        if client.name == name:
                            broadcast_only_to(message_to_send, client.conn)
                            print(f"[GATO] {getName(conn)} se rindió contra {name}")
                            found = True
                            break
                    if not found:
                        error_message = f"<Error> Cliente '{name}' no encontrado para rendirse.\n"
                        broadcast_only_to(error_message, conn)
                else:
                    message_to_send = f"<all><{getName(conn)}> {msg}\n"
                    broadcast(message_to_send, conn)                      
            else:
                remove(conn)
        #except Exception as e:
            #print(f"[ERROR] Conexión con {addr} cerrada por error: {e}")
            #remove(conn)        

def setName(connection, name:str):
    # Actualiza el nombre del cliente en la lista de clientes
    for client in list_of_clients:
        if client.conn == connection:
            client.name = name
            break

def getName(connection) -> str:
    # Obtiene el nombre del cliente a partir de su conexión
    for client in list_of_clients:
        if client.conn == connection:
            return client.name
    return ""

def getClients()-> str:
    # Devuelve un string con los nombres de todos los clientes conectadoss
    names = [client.name for client in list_of_clients if client.name]
    return ', '.join(names)

def broadcast(message, connection):
    # Envía un mensaje a todos los clientes conectados, excepto al que envió el mensaje
    for client in list_of_clients:
        if client.conn != connection:
            try:
                client.conn.send(bytes(message, 'utf-8'))
            except:
                client.conn.close()
                remove(client)
                
def broadcast_only_to(message, connection):
    # Envía un mensaje solo al cliente especificado
    for client in list_of_clients:
        if client.conn == connection:
            try:
                client.conn.send(bytes(message, 'utf-8'))
            except:
                client.conn.close()
                remove(client)                

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

if __name__ == "__main__":
    #host = socket.gethostname()  # Esta función nos da el nombre de la máquina
    host = "0.0.0.0"
    port = 4004
    BUFFER_SIZE = 1024  # Usamos un número pequeño para tener una respuesta rápida
    # Creamos un socket TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(100)  # Escuchamos hasta 100 clientes
    list_of_clients = []  # Lista de clientes conectados
    print(f"Escuchando conexiones en: {(host, port)}")
    try:
        while True:
            conn, addr = server.accept()
            nuevo_cliente = Cliente()
            nuevo_cliente.conn = conn
            nuevo_cliente.addr = addr
            #list_of_clients.append(conn)  # Agregamos a la lista de clientes
            list_of_clients.append(nuevo_cliente)  # Agregamos a la lista de clientes
            print(f"Cliente conectado: {addr}")
            # Creamos y ejecutamos el hilo para atender al cliente
            threading.Thread(target=clientthread, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        conn.close()
        server.close()   
    print("Conexión terminada.")
    
    