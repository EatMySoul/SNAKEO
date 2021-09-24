from threading import Thread
import json
from pynput import keyboard
from tkinter import *
import time
import socket


MAP_SIZE = 20
GAME_SPEED = 100
SNAKE_COLOR =  ['#99d98c', '#264653', '#2a9d8f']

SERVER_IP_PORT = ('127.0.0.1',9996)


class Game():

    def __init__(self):


        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        name = input('Your name :')

        self.client.sendto(bytes(name, encoding='utf-8'),SERVER_IP_PORT)


        game_status = 'stop'
        while game_status == 'stop':
            game_status = self.client.recv(1024)
            game_status = game_status.decode('utf-8')

        self.root = Tk()
        self.root.geometry('800x800')

        self.canvas = Canvas(self.root, height=800, width=800,  bg='black')
        self.canvas.pack()
        self.canvas.update()

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        self.direction ='None'
        self.players = []
        self.food_pos = {}

        self.gameloop()

        self.root.mainloop()


    def gameloop(self):
        self.send_data()
        self.recv_data()


        self.show_interface()
        self.root.after(GAME_SPEED,self.gameloop)
        

    def send_data(self):
        self.client.sendto(bytes(self.direction,encoding = 'utf-8'),SERVER_IP_PORT)
        self.direction = 'None'

        


    def recv_data(self):

        data,serv_addr = self.client.recvfrom(1024)
        print(data)

        data = data.decode("utf-8")
        data = json.loads(data)

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
            flag = 0
        self.canvas.create_rectangle(self.food_pos['Y']*MAP_SIZE, self.food_pos['X']*MAP_SIZE, self.food_pos['Y']*MAP_SIZE + 20, self.food_pos['X']*MAP_SIZE + 20, fill='#d00000')
        SNAKE_COLOR[2], SNAKE_COLOR[1] = SNAKE_COLOR[1], SNAKE_COLOR[2]
        self.canvas.update()

    def on_press(self, key):
        if key == keyboard.Key.left :
            self.direction = 'left'
        elif key == keyboard.Key.right :
            self.direction = 'right'
        elif key == keyboard.Key.up:
            self.direction = 'up'
        elif key == keyboard.Key.down :
            self.direction = 'down'




def main():
    game = Game()


if __name__ == "__main__":
    main()