from .network import Network
import socket

class Sender(Network):
    '''
        This class implements the client component that sends messages
        according to the system architecture. Its function is to send
        messages to other users and receive their response. It has a
        dictionary that stores usernames, ips and ports.
    '''

    def __init__(self):
        self.connected   = False
        self.username    = None
        self.port        = None
        self.client      = None

        # The chat_socket will connect to the user that is chatting at the moment
        # The chatting_with will store the username of that user
        self.chat_socket = None
        self.chatting_with = None
        self.user_dict  = {}

    def recv(self):
        res = Network.recv(self.client)
        return res

    def send(self, message, no_recv=False):
        if not self.connected:
            return {'status' : 400}

        res = Network.send(self.client, message, no_recv=no_recv)
        return res

#==================================================================================================#
#============================================= CHATTING ===========================================#
#==================================================================================================#

    def set_chatting_with(self, username):
        '''
            Input:  username - the username of the user we want to connect with
            Output: If the connection is done successfully, it returns
                    STATUS_SUCCESS, if it fails it returns STATUS_FAILED.

            Description: This method initialized a chat with another user.
                         It creates a new socket and tries to connect to the
                         user's receiver object. If the user's username is
                         not yet in the user_dict, the method fails.
        '''

        if username in self.user_dict:
            #try:
            chat_ip   = self.user_dict[username]['Endereco']
            chat_port = int(self.user_dict[username]['Porta'])
            self.chat_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_socket.connect((chat_ip, chat_port))
            #except:
            #    return Network.STATUS_FAILED

            self.chatting_with = username
            return Network.STATUS_SUCCESS

        return Network.STATUS_FAILED

    def end_chat(self):
        '''
            Input:  --
            Output: If the chat is terminated successfully, it returns
                    STATUS_SUCCESS, if it fails it returns STATUS_FAILED.

            Description: This method terminates the connection established
                         with another user if it exists closing the chat_socket.
                         If a connection was not yet established the method fails.
        '''

        if self.chat_socket is None:
            return Network.STATUS_FAILED

        self.chat_socket.close()
        self.chatting_with = None
        return Network.STATUS_SUCCESS

    def send_chat_message(self, message):
        '''
            Input:  message - the message to be sent (a string)
            Output: If the chat is message was sent successfully, it returns
                    STATUS_SUCCESS, if it fails it returns STATUS_FAILED.

            Description: This method sends a message to the user chatting a the
                         moment. If there is none, the method fails.
        '''

        if self.chatting_with is None or (not self.connected):
            return Network.STATUS_FAILED
        Network.send(self.chat_socket, {'username':self.username, 'mensagem':message}, no_recv=True)
        return Network.STATUS_SUCCESS

#==================================================================================================#
#========================================== OTHER COMMANDS ========================================#
#==================================================================================================#

    def login(self, username, port, server_ip, server_port):
        '''
            Se conecta ao servidor com usuário "username" e porta "port".
            Se funcionar, retorna código 200, se falhar, retorna código 400.
        '''
        if self.connected:
            return Network.STATUS_FAILED

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((server_ip, server_port))
        except:
            return Network.STATUS_FAILED

        message = {"operacao": "login",
                   "username": str(username),
                   "porta": int(port)}

        self.connected = True
        res = self.send(message)

        if res['status'] != Network.STATUS_SUCCESS:
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

        if res['status'] == Network.STATUS_SUCCESS:
            self.connected = False
            self.username = None
            self.port = None
            self.user_dict = {}
            self.client.close()

        if not(self.chatting_with is None):
            self.end_chat()

        return res['status']

    def get_user_dict(self):
        '''
            Caso o usuário esteja conectado ao servidor, retorna um dicionario
            {username : (ip, port)} e um status de 200. Caso não esteja, ou algo
            falhe, retorna None e um status 400.
        '''

        message = { "operacao": "get_lista" }
        res = self.send(message)

        if res['status'] == Network.STATUS_SUCCESS:
            self.user_dict = res['clientes']

        return res['status']
