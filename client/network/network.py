import select
from queue import Queue
import json

class Network():
    '''
        This class implements the comunication protocol of the application,
        including recv and send methods and the proper encoding/decoding of
        messages.
    '''

    # Enumerators to help handling status codes
    STATUS_FAILED = 400
    STATUS_SUCCESS = 200

    def __init__(self):
        pass

    @staticmethod
    def recv(sock):
        '''
            Input:  sock - the socket to call the recv method.
            Output: res  - the response properly decoded.

            Description: This method implements the recv functionality
                         with the proper comunication protocol.
        '''
        try:
            size_of_res = int.from_bytes(sock.recv(2), byteorder='big')
            res = Network.decode_message(sock.recv(size_of_res))
        except:
            return None

        return res

    @staticmethod
    def send(sock, message, no_recv=False):
        '''
            Input:  sock - the socket to call the recv method.
                    message - the message to be sent. It must be a dictionary.
                    no_recv - an optional parameter. If set to True, this method
                              will not call a recv after sending the message.
            Output: res  - the response properly decoded.

            Description: This method implements the send functionality with the
                         proper comunication protocol. By default, the method
                         calls a recv after the message is sent. That can be
                         changed according to the parameter "no_recv".
        '''
        encoded_message = Network.encode_message(message)
        sock.send(encoded_message)

        if no_recv:
            return None

        res = Network.recv(sock)
        return res

    @staticmethod
    def decode_message(msg):
        '''
            Input:  msg - the message to be decoded. It is assumed to be a
                    dictionary encoded in ut8 format.
            Output: msg_dict - the message decoded as a dict.

            Description: This method implements the decoding according to
                         the comunication protocol of the application. It
                         assumes all messages will be in the form of a
                         dictionary encoded in uft8 format.
                         The actual messages sent by other users will have
                         the message size at the beginning of the bytearray,
                         however, it is assumed that this part has already
                         been read in the "recv" method.
        '''
        msg_dict = json.loads(msg, encoding='utf8')
        return msg_dict

    @staticmethod
    def encode_message(msg_dict):
        '''
            Input:  msg_dict - the message to be encoded. It is assumed to
                    be a dictionary.
            Output: full_msg - the message encoded.

            Description: This method implements the encoding according to
                         the comunication protocol of the application. It
                         assumes the message is a dictionary. It converts
                         it to utf8 format and inserts two bytes at the
                         beginning indicating the size of the message.
        '''
        msg_json = json.dumps(msg_dict)
        msg_json = str.encode(msg_json, 'utf8')
        msg_size = len(msg_json)
        msg_size = msg_size.to_bytes(2, byteorder='big')

        full_msg = bytearray(b'')
        full_msg.extend(msg_size)
        full_msg.extend(msg_json)

        return full_msg