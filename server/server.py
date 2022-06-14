import multiprocessing
import select
import socket
import json

HOST = '0.0.0.0' # SERVER IP HERE
PORT = 1240 # SERVER PORT HERE
MAX_USERS = 50

STATUS_SUCCESS = 200
STATUS_FAILED = 400

#======================================#
#============= VARIABLES ==============#
#======================================#

user_dict = {}  # {user   : (ip, port)}
ip_dict   = {}  # {socket : ip}

#======================================#
#============= FUNCTIONS ==============#
#======================================#
def decode_message(msg):
    # Assuming the message is a json in uft8 format
    # The size of the message has already been read in the server/client loop
    msg_string = json.loads(msg, encoding='utf8')
    return msg_string

def encode_message(msg_dict):
    msg_json = json.dumps(msg_dict)
    msg_json = str.encode(msg_json, 'utf8')
    msg_size = len(msg_json)
    msg_size = msg_size.to_bytes(2, byteorder='big')

    full_msg = bytearray(b'')
    full_msg.extend(msg_size)
    full_msg.extend(msg_json)

    return full_msg


def handle_operation_login(client, msg_dict):
    if not ('username' in msg_dict and 'porta' in msg_dict):
        error_msg = encode_message({'operacao': 'login',
                                    'status': STATUS_FAILED,
                                    'mensagem': 'Requisição de Login mal formada.'})
        client.sendall(error_msg)
        return

    if msg_dict['username'] in user_dict:
        error_msg = encode_message({'operacao': 'login',
                                    'status': STATUS_FAILED,
                                    'mensagem': 'Username em Uso.'})
        client.sendall(error_msg)
        return

    # Login efetuado com sucesso!
    user_dict[msg_dict['username']] = {'Endereco': ip_dict[client],
                                       'Porta': msg_dict['porta']}

    success_msg = encode_message({'operacao': 'login',
                                  'status': STATUS_SUCCESS,
                                  'mensagem': 'Login com sucesso.'})
    client.sendall(success_msg)

    print(f'Cliente {client} logado no sistema!')
    print('Lista atual de usuários:')
    print(user_dict)

    return



def handle_operation_logoff(client, msg_dict):
    if not 'username' in msg_dict:
        error_msg = encode_message({'operacao': 'login',
                                    'status': STATUS_FAILED,
                                    'mensagem': 'Requisição de Logoff mal formada.'})
        print(0)
        client.sendall(error_msg)
        return

    if not msg_dict['username'] in user_dict:
        error_msg = encode_message({'operacao': 'login',
                                'status': STATUS_FAILED,
                                'mensagem': 'Tentando deslogar uma conta que não está logada.'})
        print(1)
        client.sendall(error_msg)
        return

    # Logoff efetuado com sucesso!
    addr_dict = user_dict.pop(msg_dict['username'], None)
    ip_dict.pop(client, None)
    inputs.remove(client)

    success_msg = encode_message({'operacao': 'logoff',
                              'status': STATUS_SUCCESS,
                              'mensagem': 'Logoff com sucesso.'})
    client.sendall(success_msg)


    print(f'Cliente {client} deslogado no sistema!')
    print('Lista atual de usuários:')
    print(user_dict)

    return

def handle_operation_get_lista(client, msg_dict):

    print(f'Pedido de get_lista do cliente {client}')

    success_msg = encode_message({'operacao': 'get_lista',
                              'status': STATUS_SUCCESS,
                              'clientes': user_dict})
    client.sendall(success_msg)
    return

operation_dict = {
    'login' :  handle_operation_login,
    'logoff':   handle_operation_logoff,
    'get_lista':   handle_operation_get_lista
}

#======================================#
#============== SERVER ================#
#======================================#

if __name__=='__main__':
    # Starting the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(6)
    server.setblocking(False) # Non-blocking mode
    inputs = [server] # Adding the server to the I/O list
    print(f'Server started. Listening to connections on port {PORT}.')

    while True:
        # espera por qualquer entrada de interesse
        reading, writing, exception = select.select(inputs, [], [])

        for s in reading:
            # In this case, it is a new connection to the server
            if s is server:
                client, address = server.accept()
                inputs.append(client)
                ip_dict[client] = address[0]
                print (f'Connected to client {client} with aFddress {address}.')
                continue

            # In this case, there is data to be received and we will read it
            try:
                msg_size = int.from_bytes(s.recv(2), byteorder='big')
                msg_dict = decode_message(s.recv(msg_size))
            except:
                msg_dict = None

            if msg_dict is None or msg_dict == {}:
                # If there is no data, that means the connection is over
                inputs.remove(s)
                print(f'Socket disconnected: {s.getsockname()}.')
            else:
                # Handling the message
                if 'operacao' in msg_dict:
                    print(f'Novo comando de {s}')
                    print(msg_dict)
                    if msg_dict['operacao'] in operation_dict:
                        operation_dict[msg_dict['operacao']](s, msg_dict)
                else:
                    print(f'Comando inválido de {s}')


