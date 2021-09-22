from threading import Thread
import json
from pynput import keyboard
from tkinter import *
import time
import socket


MAP_SIZE = 20
GAME_SPEED = 100
SNAKE_COLOR =  ['#99d98c', '#264653', '#2a9d8f']

SERVER_IP = '127.0.0.1'
SERVER_PORT = 9996


class Game():

    def __init__(self):

        self.socket = socket.socket()
        self.connect_to_server()

        self.root = Tk()
        self.root.geometry('800x800')

        self.canvas = Canvas(self.root, height=800, width=800,  bg='black')
        self.canvas.pack()
        self.canvas.update()

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        self.players = []
        self.food_pos = {}

        self.gameloop()

        self.root.mainloop()


    def gameloop(self):
        self.recv_data()
        self.show_interface()
        self.gameloop()
        self.root.after(GAME_SPEED,self.gameloop)

    def connect_to_server(self):
        self.socket.connect((SERVER_IP, SERVER_PORT))

    def recv_data(self):

        data = self.socket.recv(1024)
        data = data.decode("utf-8")
        print(data)
        data = json.loads(data)
        print(data is dict)
        self.update_data(data)



    def update_data(self,data):
        self.food_pos = data['food_pos']
        for i in range(len(data) - 1):
            try:
                self.players[i] = data[f'player{i}']
            except IndexError:
                self.players.append(data[f'player{i}'])


    def show_interface(self):
        self.canvas.delete('all')
        snake_color = SNAKE_COLOR
        flag = 0
        ##TODO CHANGE SIZING
        for snake in self.players:
            for segment in snake:
                self.canvas.create_rectangle(segment['Y'] * MAP_SIZE, segment['X'] * MAP_SIZE, segment['Y'] * MAP_SIZE + 20, segment['X'] * MAP_SIZE + 20, fill=snake_color[flag])
                flag = 2 if flag == 1 or 0 else 1
        self.canvas.create_rectangle(self.food_pos['Y']*MAP_SIZE, self.food_pos['X']*MAP_SIZE, self.food_pos['Y']*MAP_SIZE + 20, self.food_pos['X']*MAP_SIZE + 20, fill='#d00000')
        SNAKE_COLOR[2], SNAKE_COLOR[1] = SNAKE_COLOR[1], SNAKE_COLOR[2]
        self.canvas.update()

    def on_press(self, key):
        self.socket.send(bytes(str(key), encoding = "utf-8"))



def main():
    game = Game()


if __name__ == "__main__":
    main()