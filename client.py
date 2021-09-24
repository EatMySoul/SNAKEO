from threading import Thread
import json
from pynput import keyboard
from tkinter import *
import time
import socket


MAP_SIZE = 800
SEGMENT_SIZE = 20
GAME_SPEED  = 100
SNAKE_COLOR = [ ['#99d98c', '#264653', '#2a9d8f'], ['#4cc9f0', '#3f37c9', '#4361ee'] , ['#ffccd5', '#ff4d6d', '#ffb3c1'] , ['#f3d5b5', '#a47148', '#d4a276']]

SERVER_IP_PORT = ('127.0.0.1',9996)


class Game():

    def __init__(self):


        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        name = input('Your name :')

        self.client.sendto(bytes(name, encoding='utf-8'),SERVER_IP_PORT)


        self.game_status = 'stop'
        while self.game_status == 'stop':
            self.game_status = self.client.recv(1024)
            self.game_status = self.game_status.decode('utf-8')




        self.root = Tk()
        self.root.geometry(f'{MAP_SIZE}x{MAP_SIZE}')

        self.canvas = Canvas(self.root, height=MAP_SIZE, width=MAP_SIZE,  bg='black')
        self.canvas.pack()
        self.canvas.update()

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        self.direction ='None'
        self.players = []
        self.food_pos = {}

        self.gameloop()

        self.root.mainloop()
        print('YOU ARE DEAD ;(')


    def gameloop(self):
      #  print(self.players)
        if self.game_status == 'runing':
            self.send_data()
            self.recv_data()
    
    
            self.show_interface()
            self.root.after(GAME_SPEED,self.gameloop)
        

    def send_data(self):
        self.client.sendto(bytes(self.direction,encoding = 'utf-8'),SERVER_IP_PORT)
        self.direction = 'None'

        


    def recv_data(self):

        data,serv_addr = self.client.recvfrom(1024)
     #   print(data)

        data = data.decode("utf-8")
        if data == 'stop':

            self.game_status = 'stop'
        else:

            data = json.loads(data)
            self.update_data(data)



    def update_data(self,data):
        self.food_pos = data['food_pos']
        coord_data = []
        for i in range(len(data) - 1):
            coord_data.append(data[f'player{i}'])
        self.players = coord_data


    def show_interface(self):
        self.canvas.delete('all')

        color_num = 0
        snake_num = 0
        snake_color = SNAKE_COLOR

        ##TODO CHANGE SIZING
        for snake in self.players:
            for segment in snake:
                self.canvas.create_rectangle(segment['Y'], segment['X'], segment['Y'] + SEGMENT_SIZE, segment['X']  + SEGMENT_SIZE, fill=snake_color[snake_num][color_num])
                color_num = 2 if color_num == 1 or 0 else 1
            color_num = 0
            snake_num += 1

        for food in self.food_pos:
            self.canvas.create_rectangle(food['Y'], food['X'], food['Y'] + SEGMENT_SIZE, food['X'] + SEGMENT_SIZE, fill='#d00000')
   #     SNAKE_COLOR[2], SNAKE_COLOR[1] = SNAKE_COLOR[1], SNAKE_COLOR[2]
        self.canvas.update()

    def on_press(self, key):
        if key == keyboard.Key.left:
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