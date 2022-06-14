import multiprocessing
import socket
import curses
import json


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


class Network():

    SERVER_IP = "localhost"
    SERVER_PORT = 1239

    def __init__(self):
        self.connected = False
        self.username = None
        self.port = None
        self.user_dict = None

        self.client = None

    def recv(self):
        size_of_res = int.from_bytes(self.client.recv(2), byteorder='big')
        res = decode_message(self.client.recv(size_of_res))
        return res

    def send(self, message):
        if not self.connected:
            return {'status' : 400}

        encoded_message = encode_message(message)
        self.client.send(encoded_message)
        res = self.recv()

        return res


    def login(self, username, port):
        '''
            Se conecta ao servidor com usuário "username" e porta "port".
            Se funcionar, retorna código 200, se falhar, retorna código 400.
        '''

        self.client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect((Network.SERVER_IP, Network.SERVER_PORT))
        except:
            self.client.close()
            return 400

        message = {"operacao": "login",
                   "username": str(username),
                   "porta": int(port)}


        self.connected = True
        res = self.send(message)

        if res['status'] != 200:
            self.client.close()
            self.connected = False
            return res['status']

        self.username = username
        self.port = port

        return res['status']

    def logoff(self):
        '''
            Se desconecta do servidor caso esteja conectado.
        '''

        message = {"operacao": "logoff",
                   "username": self.username}
        res = self.send(message)

        if res['status'] == 200:
            self.connected = False
            self.username = None
            self.port = None
            self.user_dict = None
            self.client.close()

        return res['status']

    def get_user_dict(self):
        '''
            Caso o usuário esteja conectado ao servidor, retorna um dicionario
            {username : (ip, port)} e um status de 200. Caso não esteja, ou algo
            falhe, retorna None e um status 400.
        '''

        message = { "operacao": "get_lista" }
        res = self.send(message)

        if res['status'] == 200:
            self.user_dict = res['clientes']

        return res['status']