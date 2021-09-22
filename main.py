from pynput import keyboard
from random import randint
import json
from threading import Thread
from tkinter import *
import socket
import time

MAP_SIZE = 20
GAME_SPEED = 100

SNAKE_COLOR = ['#99d98c', '#264653', '#2a9d8f']


# WAS DESIGION OF USE A DICT IS RIGHT?

class Game:

    def __init__(self):

        self.root = Tk()
                                        #network
        self.socket = socket.socket()
        self.socket.bind(('',9996))     #Using 9996 port
        self.socket.listen(1)         #Listen two players, two for test...

        self.players = []

        while len(self.players) < 1:
            print('waiting players:',len(self.players),'/ 1')
            conn, addr = self.socket.accept()
            print('player',conn,addr,'connected')
            self.players.append(Snake(conn,addr))


        th_recv = Thread(target = self.reciv_input())
        th_recv.start()
                                        #

        self.food_pos = {}

        for i in range(len(self.players)):
            self.add_food()

        data = self.get_network_data()
        self.send_data(data)
        time.sleep(1)
        print('am send some important data')
        self.gameloop()

        self.root.mainloop()



    def gameloop(self):

        for snake in self.players:
            snake.direction = snake.next_direction
            snake.move()
            self.check_snakes_collision()

        data = self.get_network_data()
        self.send_data(data)

        self.root.after(GAME_SPEED, self.gameloop)


    def add_food(self):

        x = randint(0, MAP_SIZE - 1)
        y = randint(0, MAP_SIZE - 1)

        snakes_coords = self.get_snake_coord()

        while [x, y] in snakes_coords:
            x = randint(0, MAP_SIZE - 1)
            y = randint(0, MAP_SIZE - 1)

        self.food_pos = {'X': x, 'Y': y}

    ##TODO GET SPECIFIC OF PLAYER SNAKE COORDS LIKE get_snake_coord(player1,player3)
    def get_snake_coord(self):
        cordinates = []
        for snake in self.players:
            for segment in snake.body:
                cordinates.append(list(segment.values()))
        return cordinates

    def get_network_data(self):
        data = {'food_pos': self.food_pos,
                'player0': self.players[0].body}
        return data

    ##TODO COLLISION BETWEEN PLAYERS
    def check_snakes_collision(self):
        for snake in self.players:
            if list(snake.body[0].values()) == list(self.food_pos.values()):
                snake.add_segment()
                self.add_food()


    def send_data(self,data):
        print('...sending data')
        for snake in self.players:
            snake.conn.send(bytes(json.dumps(data), encoding = "utf-8"))


    def reciv_input(self):
        while True:
            key,addr = self.socket.recvfrom(1024)
            key = key.decode("utf-8")
            for snake in self.players:
                if snake.addr == addr:
                    if key == 'Key.left' and snake.direction != 'right':
                        snake.next_direction = 'left'
                    elif key == 'Key.right' and snake.direction != 'left':
                        snake.next_direction = 'right'
                    elif key == 'Key.up' and snake.direction != 'down':
                        snake.next_direction = 'up'
                    elif key == 'Key.down' and snake.direction != 'up':
                        snake.next_direction = 'down'
                    elif key == 'Key.esc':
                        snake.living = False



class Snake:

    def __init__(self,conn,addr):

        self.conn = conn
        self.addr = addr

        self.living = True
        self.score = 0

        self.body = [{'X': 3, 'Y': 3},
                     {"X": 3, "Y": 2},
                     {"X": 3, "Y": 1}, ]

        self.direction = 'up'
        self.next_direction = 'up'


    def move(self):
        # перемещение координат тела змейки
        print(self.body)
        for segment in range(len(self.body) - 1, 0, -1):
            self.body[segment]['X'] = self.body[segment - 1]['X']
            self.body[segment]['Y'] = self.body[segment - 1]['Y']

        if self.direction == 'right':
            if self.body[0]['Y'] == MAP_SIZE - 1:
                self.body[0]['Y'] = 0
            else:
                self.body[0]['Y'] += 1

        elif self.direction == 'left':
            if self.body[0]['Y'] == 0:
                self.body[0]['Y'] = MAP_SIZE - 1
            else:
                self.body[0]['Y'] -= 1
        elif self.direction == 'up':
            if self.body[0]['X'] == 0:
                self.body[0]['X'] = MAP_SIZE - 1
            else:
                self.body[0]['X'] -= 1
        elif self.direction == 'down':
            if self.body[0]['X'] == MAP_SIZE - 1:
                self.body[0]['X'] = 0
            else:
                self.body[0]['X'] += 1
         #### SNAKE CHECK HIS OWN COLLISION? ITS BAD
        for i in range(1, len(self.body)):
            if self.body[0] == self.body[i]:
                self.death()



    def add_segment(self):
        self.score += 10
        print(f'Score is {self.score}')

        new_segment  = {'X': self.body[-1]['X'], 'Y': self.body[-1]['Y']}
        self.body.append(new_segment)


    def death(self):
        self.living = False

        ## TODO END GAME!
        time.sleep(3)



def main():
    game = Game()


if __name__ == "__main__":
    main()
