
from .network import Network
import socket
import select
import curses
from queue import Queue

class Receiver(Network):
    '''
        This class implements the client component that receives messages
        according to the system architecture. Its function is to receive
        messages sent by other users. It has a dictionary that stores a
        queue of messages by user and a method to check for new messages.
    '''

    def __init__(self):
        self.sock = None
        self.inputs = []
        self.message_dict = {}

#==================================================================================================#
#=========================================== START/CLOSE ==========================================#
#==================================================================================================#


    def start(self, host, port):
        '''
            Input:  host - the ip of the server to be started
                    port - the port of the server to be started
            Output: If the server is started successfully, it returns
                    STATUS_SUCCESS, if it fails it returns STATUS_FAILED.

            Description: This method initializes the receiver's socket
                         to be able to receive new connections and messages.
        '''

        # Starting the server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((host, port))
            self.sock.listen(6)
            self.sock.setblocking(False) # Non-blocking mode
            self.inputs = [self.sock] # Adding the server to the I/O list
            return Network.STATUS_SUCCESS
        except:
            return Network.STATUS_FAILED

    def close(self):
        '''
            Input:  --
            Output: If the server is closed successfully, it returns
                    STATUS_SUCCESS, if it fails it returns STATUS_FAILED.

            Description: This method closes the receiver's socket.
        '''

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.sock = None
            return Network.STATUS_SUCCESS
        except:
            return Network.STATUS_FAILED

#==================================================================================================#
#======================================== HANDLE CONNECTIONS ======================================#
#==================================================================================================#

    def get_new_messages(self):
        '''
            Input:  --
            Output: --

            Description: This method checks new connections with the
                         select method and updates the message_dict.
                         If the server is not yet started, the method
                         will do nothing and just return.
        '''

        # If the server is not yet started, we'll simply return
        if self.sock is None:
            return

        # Get new inputs
        reading, writing, exception = select.select(self.inputs, [], [], 0)

        for s in reading:
            # In this case, it is a new connection to the server
            if s is self.sock:
                client, address = self.sock.accept()
                self.inputs.append(client)
                continue
            # In this case, there is data to be received and we will read it
            data = Network.recv(s)

            if data is None:
                # If there is no data, that means the connection is over
                try:
                    self.inputs.remove(s)
                except:
                    pass
                continue

            # Handling the message
            if 'username' in data and 'mensagem' in data:
                username = data['username']
                message  = data['mensagem']

                if not username in self.message_dict:
                    self.message_dict[username] = Queue()

                self.message_dict[username].put(message)
            else:
                curses.endwin()
                print(data)

