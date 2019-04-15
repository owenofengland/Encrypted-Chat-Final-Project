# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import EncryptOE
import tictactoechat as tac

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.peer_key = ()
        self.pub_key = ()
        self.priv_key = ()
        self.waiting = True
        self.board = [['#' for i in range(3)] for j in range(3)]
        self.symbol = ''        #will be using X or O for tic-tac-toe

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def play_with(self, peer):
        msg = M_PLAY + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_PLAY+'ok'):
            self.peer = peer
            self.out_msg += 'You have joined a game with ' + self.peer + '. Have fun!\n'
            self.state = S_PLAYING
            self.out_msg += tac.welcome_banner()
            self.symbol = 'X'
            return True
        elif response == (M_PLAY + 'hey you'):
            self.out_msg += "You can't challenge yourself to a game!\n"
        elif response == (M_PLAY + 'no_user'):
            self.out_msg += 'No such user exists\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return False

    # def play_with(self, peer):
    #     msg = M_PLAY + peer
    #     mysend(self.s, msg)
    #     response = myrecv(self.s)
    #     if response == (M_PLAY+'ok'):
    #         self.peer = peer
    #         self.out_msg += self.peer + ' has accepted your game invite. Have fun!\n'
    #         self.state = S_PLAYING
    #         self.out_msg += tac.welcome_banner()
    #         self.symbol = 'X'
    #         return True
    #     elif response == (M_PLAY + 'hey you'):
    #         self.out_msg += "You can't challenge yourself to a game!\n"
    #     elif response == (M_PLAY + 'no_user'):
    #         self.out_msg += 'No such user exists\n'
    #     else:
    #         self.out_msg += 'User is not online, try again later\n'
    #     return False
    #
    # def game_requested(self, asker):
    #     print('Game request from ' + self.peer + '\n')
    #     play_or_no = input('Would you lke to play a game with ' + self.peer + '?\n> ')
    #     if play_or_no.strip().upper()[0] == 'Y' or play_or_no.strip()[0] == '1':
    #         self.out_msg += 'Ok.\n'
    #         mysend(self.s, M_PLAY+'ok')
    #         self.state = S_PLAYING
    #         self.out_msg += tac.welcome_banner()
    #         self.symbol = 'O'

    def leave_game(self):   #also make a way to remove peer from game
        self.state = S_LOGGEDIN
        return

    def connect_to(self, peer):
        msg = M_CONNECT + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_CONNECT+'ok'):
            self.peer = peer
            return (True)
        elif response == (M_CONNECT + 'busy'):
            self.out_msg += 'User is busy. Please try again later\n'
        elif response == (M_CONNECT + 'hey you'):
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = M_DISCONNECT
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_code, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, M_TIME)
                    time_in = myrecv(self.s)
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, M_LIST)
                    logged_in = myrecv(self.s)
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[:4] == 'play':  #can only invite someone to a game if they're also in S_LOGGEDIN,
                                        #i.e. not chatting
                    peer = my_msg[4:].strip()
                    if self.play_with(peer) == True:
                        self.state = S_PLAYING

                elif my_msg[0] == 'c':
                    peer = my_msg[1:].strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connected to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, M_SEARCH + term)
                    search_rslt = myrecv(self.s)[1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'
                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                self.peer = peer_msg
                if peer_code == M_CONNECT:
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                elif peer_code == M_PLAY:
                    self.game_requested(peer)

        elif self.state == S_PLAYING:
            #print('playing I think...')
            if len(my_msg) > 0:
                if my_msg[:2] == 'bye':
                    self.leave_game()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                elif tac.userin_good(my_msg):
                    row,col = tac.userin_parser(my_msg)
                    if tac.not_taken(self.board,row,col):
                        self.board = tac.make_move(self.board,row,col,self.symbol)
                        if tac.check_board(self.board,self.symbol) == 'win':
                            mysend(self.s, '!'+'I win'+self.board)
                        elif tac.check_board(self.board,self.symbol) == 'draw':
                            mysend(self.s, '!'+'draw'+self.board)
                    else:
                        self.out_msg += "That spot's already been taken!"
                else:
                    self.out_msg += 'Invalid input,there goes your turn.\n'
                    self.out_msg += 'Next time, try entering row and column numbers in the format r,c'
                mysend(self.s, '!' + self.board)

            if len(peer_msg) > 0:
                if peer_msg[:5] == 'I win':
                    self.board = peer_msg[5:]
                    self.out_msg += self.board
                    self.out_msg += 'You lose!\n'
                    self.out_msg += 'Would you like to play again?'
                elif peer_msg[:4] == 'draw':
                    self.board = peer_msg[4:]
                    self.out_msg += self.board
                    self.out_msg += "It's a draw.\n"
                    self.out_msg += 'Would you like to play again?'
                else:   #peer_msg is the game board after they've made their move
                    self.board = peer_msg
                    self.out_msg += self.board

            # elif self.state == S_CHATTING:
            #     if len(my_msg) > 0:     # my stuff going out
            #         mysend(self.s, M_EXCHANGE + "[" + self.me + "] " + my_msg)
            #         if my_msg == 'bye':
            #             self.disconnect()
            #             self.state = S_LOGGEDIN
            #             self.peer = ''
            #
            #     #implemented
            #     if len(peer_msg) > 0:    # peer's stuff, coming in
            #         # when peer_msg is "bye", peer_code will be M_DISCONNECT
            #         if peer_msg == 'bye':
            #             self.peer_code = M_DISCONNECT
            #             self.disconnect()
            #             self.state = S_LOGGEDIN
            #             self.peer = ''
            #         else:
            #             self.out_msg += peer_msg + '\n'

            #if self.waiting == True:
                #get recv
                    #if len(myrecv) > 0:
                #other shit
                #at end, self.waiting = False
            #elif self.waiting == False:
                #send recv

            #can check is_winner on client side, then send info i.e. send 'I win' to server
            #switch is_waiting from True to False or vice versa

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            self.pub_key, self.priv_key = EncryptOE.gen_keys()
            mysend(self.s, M_UNDEF + str(self.pub_key[0]) + ',' + str(self.pub_key[1]))
            self.out_msg += "My public key: "
            self.out_msg += str(self.pub_key) + '\n'
            self.out_msg += "My Private key: "
            self.out_msg += str(self.priv_key) + '\n'

            if len(my_msg) > 0:
                enc_list = EncryptOE.encrypt(self.peer_key, '[' + self.me + ']' + my_msg)
                enc_msg = str(enc_list[0])
                for num in enc_list[1:]:
                    enc_msg += ',' + str(num)
                self.out_msg += enc_msg + '\n'
                mysend(self.s, M_EXCHANGE + enc_msg) #Sending encrypted cipher text string of numbers

                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                    #No longer encrypting chat, reset to generate new keys for next chat

            if len(peer_msg) > 0:   # Peer's stuff, coming in
                # New peer joins
                if peer_code == M_CONNECT:
                    self.out_msg += "(" + peer_msg + " joined)\n"

                elif peer_code == M_UNDEF: #Receiving peer key for encrypting outbound message
                    key = peer_msg.split(',')
                    self.peer_key = int(key[0]), int(key[1])
                    self.out_msg += 'Peer Key: '
                    self.out_msg += str(self.peer_key) +'\n'

                else: #Decrypting inbound messages using private key
                    self.out_msg += peer_msg + '\n'
                    str_list = peer_msg.split(',')
                    dec_list = [int(char) for char in str_list]
                    dec_msg = EncryptOE.decrypt(self.priv_key, dec_list)
                    self.out_msg += dec_msg

            # I got bumped out
            if peer_code == M_DISCONNECT:
                self.state = S_LOGGEDIN

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
