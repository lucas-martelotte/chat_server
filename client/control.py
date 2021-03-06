from components.user_list_screen import UserListScreen
from components.string_buffer import StringBuffer
from network.receiver import Receiver
from network.sender import Sender
from network.network import Network
import socket
import curses
import random
import json
import os

class Control():
    '''
        ToDo
    '''

    # The width (in characters) that the bar containing
    # the usernames will have.
    USER_AREA_WIDTH = 32

    # Enumerators to help handling the state
    STATE_OFFLINE = 0
    STATE_IDLE = 1
    STATE_CHAT = 2

    # The address of the client machine
    RECEIVER_IP = "0.0.0.0" # CLIENT IP HERE

    # The address of the main server
    SERVER_IP = "0.0.0.0" # SERVER IP HERE
    SERVER_PORT = 1240 # SERVER PORT HERE


    def __init__(self,stdscr):

        self.sender   = Sender()
        self.receiver = Receiver()
        self.chat_sender = None

        self.stdscr = stdscr
        self.rows, self.cols = self.stdscr.getmaxyx()
        self.cursor_pos = [1, self.rows-3]
        # Bar separating the chat and the users
        self.separating_bar = self.cols - Control.USER_AREA_WIDTH

        self.user_list = UserListScreen(self.separating_bar+1, 1,
            self.cols-self.separating_bar-1, self.rows-4)

        self.string_buffer = StringBuffer(1, 1, self.separating_bar-1, self.rows-4)
        self.string_buffer.append('Bem vindo ao ZAP dos cria 🤡🤡🗡️')
        self.string_buffer.append('Digite \"\help\" para ver os comandos.')

        self.current_message = ''
        self.state = Control.STATE_OFFLINE

        self.command_dict = {
            '\\help' :   self.command_help,
            '\\clear':   self.command_clear,
            '\\login':   self.command_login,
            '\\logoff':  self.command_logoff,
            '\\update':  self.command_update,
            '\\u':       self.command_update,
            '\\close':   self.command_close,
            '\\chat' :   self.command_chat,
            '\\endchat': self.command_endchat
        }

#==================================================================================================#
#=========================================== MAIN LOOP ============================================#
#==================================================================================================#

    def main_loop(self):
        '''
            ToDo
        '''

        while True:

            #=================#
            #==== UPDATES ====#
            #=================#
            self.receiver.get_new_messages()

            if self.state == Control.STATE_CHAT:
                try:
                    username = self.sender.chatting_with
                    if username in self.receiver.message_dict:
                        message_queue = self.receiver.message_dict[username]
                        while not message_queue.empty():
                            new_msg = message_queue.get()
                            self.string_buffer.append(username + ':' + ' '*max(1, 9-len(username)) + new_msg)
                except Exception as e:
                    self.string_buffer.append("Algo deu errado ao tentar recuperar as mensagens.")
                    self.string_buffer.append(str(e))

            #=================#
            #=== Rendering ===#
            #=================#
            self.clear_screen_and_draw_lines()
            self.string_buffer.render(self.stdscr)
            self.user_list.render(self.stdscr, self.receiver.message_dict)
            self.stdscr.addstr(self.rows-3, 1, ' '*(self.separating_bar-1))
            self.stdscr.addstr(self.rows-3, 1, self.current_message)
            self.stdscr.move(self.cursor_pos[1], self.cursor_pos[0])
            self.stdscr.refresh()

            #==================#
            #=== User Input ===#
            #==================#
            key = self.stdscr.getkey()

            if key == '\n':
                self.finish_message()
            elif key in ('KEY_BACKSPACE', '\b', '\x7f'):
                if self.cursor_pos[0] > 1:
                    self.current_message = self.current_message[:-1]
                    self.cursor_pos = [self.cursor_pos[0]-1, self.cursor_pos[1]]
            else:
                if self.cursor_pos[0] < self.separating_bar-1:
                    self.current_message += key
                    self.cursor_pos = [self.cursor_pos[0]+1, self.cursor_pos[1]]

#==================================================================================================#
#============================================ DRAWING =============================================#
#==================================================================================================#

    def clear_screen_and_draw_lines(self):
        '''
            Clears the screen and draws the borders that
            separate the user area from the chat.
        '''

        # Clear screen
        self.stdscr.clear()
        rows, cols = self.stdscr.getmaxyx()

        self.stdscr.addstr(0,0,'╔' + '═'*(cols-2) + '╗')
        for i in range(1,rows-2,1):
            self.stdscr.addstr(i,0,'║')
            self.stdscr.addstr(i,cols-1,'║')
        self.stdscr.addstr(rows-2, 0,'╚' + '═'*(cols-2) + '╝')

        self.stdscr.addstr(0,self.separating_bar,'╦')
        for i in range(1, rows-2, 1):
            self.stdscr.addstr(i, self.separating_bar,'║')
        self.stdscr.addstr(rows-2,self.separating_bar,'╩')

#==================================================================================================#
#============================================ COMMANDS ============================================#
#==================================================================================================#

    def finish_message(self):
        '''
            Handles the sending of a message. This function is called when the user presses
            the \n key on the keyboard. It checks if the user typed a specific command or
            simply typed a message and executes the correponding treatment.
        '''

        if len(self.current_message) == 0:
            # Empty message
            return

        sb = self.string_buffer
        parts = self.current_message.split(' ')
        command = parts[0]
        inputs = parts[1:]

        if command[0] == '\\':
            # In this case, the user typed a command
            if command in self.command_dict:
                self.command_dict[command](inputs)
            else:
                sb.append('ERRO: Comando inválido.')
        else:
            # In this case, the user typed a message.
            if self.state != Control.STATE_CHAT:
                sb.append('ERRO: Não há como enviar mensagens pois nenhuma conversa foi iniciada.')
            else:
                try:
                    self.sender.send_chat_message(self.current_message)
                    username = self.sender.username
                    sb.append(str(username) + ':' + ' '*max(1, 9-len(username)) + self.current_message)
                except Exception as e:
                    #sb.append(str(e))
                    sb.append('Falha ao enviar mensagem. Encerrando conversa.')
                    self.command_endchat([])

        self.current_message = ''
        self.cursor_pos = [1, self.rows-3]

    def command_help(self, inputs):
        '''
            This function handles the command '\\help'.
            It prints on the chat screen all the commands available.
        '''

        sb = self.string_buffer
        sb.append('')
        sb.append('\\help : O programa imprime a lista de comandos para o usuário.')
        sb.append('\\clear : Limpa da tela de chat.')
        sb.append('\\login <username> <ip> <porta> : Entra no ZAP.')
        sb.append('\\logoff <username> : Sai do ZAP.')
        sb.append('\\update : Atualiza a lista de usuários online.')
        sb.append('\\close : Encerra a aplicação. Caso esteja conectado, desloga.')
        sb.append('\\chat <usuário> : O usuário inicializa uma conversa com um outro usuário.')
        sb.append('\\endchat : O usuário encerra uma conversa com um outro usuário.')

    def command_clear(self, inputs):
        '''
            This function handles the command '\\clear'.
            It clears the chat screen.
        '''

        self.string_buffer.clear()

    def command_login(self, inputs):
        '''
            This function handles the command '\\login'.
            It tries to connect to the server. If the connection is
            successful, it updates the user_list.
        '''

        sb = self.string_buffer

        if not len(inputs) in [1,2] :
            sb.append('')
            sb.append('ERRO: O comando \"\\login\" só deve ter 2 entradas: <usuário> <porta>.')
            return

        if len(inputs) == 1:
            sb.append('')
            port = random.randint(1000,2000)
            sb.append(f'AVISO: Porta não fornecida. Porta aleatória gerada: {port}.')
        else:
            port = int(inputs[1])

        username = inputs[0]
        ip       = Control.RECEIVER_IP

        status_1 = self.receiver.start(ip, port)
        if status_1 == Network.STATUS_FAILED:
            sb.append('')
            sb.append('ERRO: Falha ao tentar criar o servidor de recepção de mensagens.')
            return
        else:
            sb.append('')
            sb.append('Servidor de mensagens criado com sucesso.')
            sb.append(f'Esperando conexões no ip {ip} e porta {port}.')

        status_2 = self.sender.login(username, port, Control.SERVER_IP, Control.SERVER_PORT)

        if status_2 == Network.STATUS_FAILED:
            sb.append('')
            sb.append('ERRO: Falha no login.')
        elif status_2 == Network.STATUS_SUCCESS:
            sb.append('')
            sb.append(f'Sucesso no login (porta {port})! Bem vindo {username}!')
            self.command_update([])
        else:
            sb.append('')
            sb.append(f'Resposta inesperada do servidor ({status}).')

    def command_logoff(self, inputs):
        '''
            This function handles the command '\\logoff'.
            If the user is connected to the server, it disconnects it.
        '''

        sb = self.string_buffer
        status_1 = self.sender.logoff()
        status_2 = self.receiver.close()
        status   = status_1

        if status == 400:
            sb.append('')
            sb.append('ERRO: Falha no logoff.')
        elif status == 200:
            sb.append('')
            sb.append('Desconectado do servidor com sucesso! Até a próxima!')
            self.receiver.close()
            self.user_list.set_user_list([])
            self.state = Control.STATE_OFFLINE
        else:
            sb.append('')
            sb.append(f'Resposta inesperada do servidor ({status}).')

    def command_update(self, inputs):
        '''
            This function handles the command '\\update'.
            If the user is connected to the server, it updates the user_list.
        '''

        if not self.sender.connected:
            self.string_buffer.append('ERRO: Não foi possível atualizar a lista de usuários pois '+\
                                      'não foi estabelecida uma conexão com o servidor.')
            return

        sb = self.string_buffer
        status = self.sender.get_user_dict()

        if status == 400:
            sb.append('')
            sb.append('ERRO: Falha ao obter lista.')
        elif status == 200:
            sb.append('')
            sb.append('Sucesso ao obter lista!')
            self.user_list.set_user_list([key for key in self.sender.user_dict.keys()])
        else:
            sb.append('')
            sb.append(f'Resposta inesperada do servidor ({status}).')

    def command_close(self, inputs):
        '''
            This function handles the command '\\close'.
            If the user is connected to the server, it disconnects it.
            After that, it closes the application.
        '''

        self.sender.logoff()
        curses.endwin()
        exit()

    def command_chat(self, inputs):

        sb = self.string_buffer

        if len(inputs) != 1:
            sb.append('')
            sb.append('ERRO: O comando \"\\chat\" só deve ter 1 entrada: <usuário>.')
            return

        username = inputs[0]

        if not username in self.sender.user_dict:
            sb.append('')
            sb.append(f'ERRO: O usuário {username} não consta na lista de usuários.')
            return

        if username == self.sender.username:
            sb.append('')
            sb.append(f'ERRO: Não seja antissocial! Inicie uma conversa com alguém que não seja você mesmo!')
            return

        sb.append(f'Tentando estabelecer conexão com {[v for v in self.sender.user_dict[username].values()]}.')
        try:
            status = self.sender.set_chatting_with(username)
        except:
            return
        if status == Network.STATUS_SUCCESS:
            self.state = Control.STATE_CHAT
            sb.clear()
            sb.append(f'Conversa iniciada com {username}.')
            sb.append('')
        else:
            sb.append('')
            sb.append(f'ERRO: Falha ao tentar estabelecer conexão com {username}.')

    def command_endchat(self, inputs):

        sb = self.string_buffer

        if self.state != Control.STATE_CHAT:
            sb.append('')
            sb.append(f'ERRO: Não foi possível encerrar uma conversa ' +\
                       'pois você não está em nennhuma.')
            return

        status = self.sender.end_chat()
        if status == Network.STATUS_SUCCESS:
            self.state = Control.STATE_IDLE
            sb.append('Conversa encerrada.')
        else:
            sb.append('')
            sb.append(f'ERRO: Falha ao tentar encerrar conversa.')
