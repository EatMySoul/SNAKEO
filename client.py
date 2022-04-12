import pickle
from pynput import keyboard
from tkinter import *
import socket


MAP_SIZE = 800
SEGMENT_SIZE = 20
GAME_SPEED  = 100
SNAKE_COLOR = {'green':['#99d98c', '#264653', '#2a9d8f'],
               'blue': ['#4cc9f0', '#3f37c9', '#4361ee'],
               'pink': ['#ffccd5', '#ff8fa3', '#ffb3c1'],
               'dust': ['#f3d5b5', '#a47148', '#d4a276'],
               'underground': ['#a6808c', '#565264', '#706677'],
               'candy': ['#eff7f6','#f7d6e0', '#b2f7ef'],
               'dead': ['#dee2e6', '#adb5bd', '#ced4da']}

SERVER_IP_PORT = ('127.0.0.1',9996)


class Game():

    def __init__(self):


        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

        name = input('Your name: ')


        self.client.connect(SERVER_IP_PORT)

        self.client.send(bytes(name, encoding='utf-8'))

        self.game_status = 'stop'
        self.direction ='None'
        self.players = []
        self.food_pos = []

        while self.game_status == 'stop':
            data = self.client.recv(6)
            if data.decode('utf-8') == 'runing':
                self.game_status = 'runing'
            else:
                print(data.decode('utf-8'),'connected')
        init_data = pickle.loads(self.client.recv(1024))
        self.food_pos = init_data[0]
        self.players = init_data[1:]

        self.root = Tk()
        self.root.geometry(f'{MAP_SIZE + 300}x{MAP_SIZE}')

        self.canvas = Canvas(self.root, height=MAP_SIZE, width=MAP_SIZE + 300,  bg='black')
        self.canvas.pack()
        self.canvas.update()


        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()


        self.gameloop()

        self.root.mainloop()


    def gameloop(self):
        if self.game_status == 'runing':
            self.send_data()
            self.recv_data()

            self.show_interface()
            self.root.after(GAME_SPEED,self.gameloop)
        else:                                                                   #TODO game stop
            print('GG')

    def send_data(self):
        self.client.send(bytes(self.direction,encoding = 'utf-8'))
        self.direction = 'None'

        


    def recv_data(self):

        data = self.client.recv(1024)
        data = pickle.loads(data)
        if data != 'stop':
            self.update_data(data)
        else:
            print('get stop signal')
            self.game_status = 'stop'


    def update_data(self,data):
        self.food_pos = data[0]
        for i in range(0,len(self.players)):
            self.players[i]['body']  = data[i + 1]['body']
            self.players[i]['score'] = data[i + 1]['score']
            self.players[i]['living'] = data[i + 1]['living']


    def show_interface(self):
        self.canvas.delete('all')
        snake_color = SNAKE_COLOR


        for snake in self.players:
            color_num = 0
            if not snake['living']:
                for segment in snake['body']:
                    self.canvas.create_rectangle(segment[1], segment[0], segment[1] + SEGMENT_SIZE, segment[0]  + SEGMENT_SIZE, fill=snake_color['dead'][color_num])
                    color_num = 2 if color_num == 1 or 0 else 1

        for snake in self.players:
            color_num = 0
            if snake['living']:
                for segment in snake['body']:
                    self.canvas.create_rectangle(segment[1], segment[0], segment[1] + SEGMENT_SIZE, segment[0]  + SEGMENT_SIZE, fill=snake_color[snake['color']][color_num])
                    color_num = 2 if color_num == 1 or 0 else 1
                #SNAKE_COLOR[snake['color']][2], SNAKE_COLOR[snake['color']][1] = SNAKE_COLOR[snake['color']][1], SNAKE_COLOR[snake['color']][2]
    

            ##### SCORE TAB ##########             
        self.canvas.create_text(MAP_SIZE + 100, 50, text = 'SCORE:',font=("Purisa", 18), fill='white')
            #WOW LOOKS UNREADBLE
        for i in range(len(self.players)):
            output = self.players[i]['name'] +': '+ str(self.players[i]['score'])
            self.canvas.create_rectangle(MAP_SIZE,100 - SEGMENT_SIZE/2 + i*30, MAP_SIZE + SEGMENT_SIZE, 100 - SEGMENT_SIZE/2 + i* 30 + SEGMENT_SIZE,fill = snake_color[self.players[i]['color']][0])
            self.canvas.create_text(MAP_SIZE + 100, 100 + i*30, text = output,font=("Purisa", 12), fill='white')


        for food in self.food_pos:
            self.canvas.create_rectangle(food[1], food[0], food[1] + SEGMENT_SIZE, food[0] + SEGMENT_SIZE, fill='#d00000')
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