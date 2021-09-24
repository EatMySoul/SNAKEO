from pynput import keyboard
from random import randint
import json
from tkinter import *
import socket
import time

MAP_SIZE = 20
GAME_SPEED = 100

MAX_PLAYERS = 2

SNAKE_COLOR = ['#99d98c', '#264653', '#2a9d8f']


# WAS DESIGION OF USE A DICT IS RIGHT?

class Game:

    def __init__(self):

                                        #network
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.server.bind(('127.0.0.1',9996))     #Using 9996 port

        self.players = []
        #### PLAYERS CONNECT
        while len(self.players) < MAX_PLAYERS:
            print('waiting players:',len(self.players),'/',MAX_PLAYERS)
            name,addr = self.server.recvfrom(1024)
            self.players.append(Snake(name,addr,len(self.players) + 1))
            print(name.decode('utf-8'),'connected')

        for snake in self.players:
            self.server.sendto(bytes('runing', encoding = "utf-8"),snake.addr)



        self.food_pos = {}

        for i in range(len(self.players)):
            self.add_food()

        data = self.get_network_data()
        self.send_data(data)

        print('am send some important data')
        self.gameloop()



    def gameloop(self):

        self.recv_input()

        for snake in self.players:
            snake.direction = snake.next_direction
            snake.move()
            self.check_snakes_collision()

        data = self.get_network_data()
        self.send_data(data)

        time.sleep(GAME_SPEED/1000)
        self.gameloop()


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



    ##TODO COLLISION BETWEEN PLAYERS
    def check_snakes_collision(self):
        for snake in self.players:
            if list(snake.body[0].values()) == list(self.food_pos.values()):
                snake.add_segment()
                self.add_food()

     ############################NETWORK################################           

    def get_network_data(self):
        data = {'food_pos': self.food_pos,
                'player0': self.players[0].body,
                'player1':self.players[1].body}
        return data


    def send_data(self,data):
        print('...sending data')
        for snake in self.players:
            self.server.sendto(bytes(json.dumps(data), encoding = "utf-8"),snake.addr)


    def recv_input(self):

        direction,addr = self.server.recvfrom(1024)
        direction = direction.decode("utf-8")
        for snake in self.players:
            if snake.addr == addr:
                if direction == 'left' and snake.direction != 'right':
                    snake.next_direction = 'left'
                elif direction == 'right' and snake.direction != 'left':
                    snake.next_direction = 'right'
                elif direction == 'up' and snake.direction != 'down':
                    snake.next_direction = 'up'
                elif direction == 'down' and snake.direction != 'up':
                    snake.next_direction = 'down'
                elif direction == 'esc':
                    snake.living = False



class Snake:

    def __init__(self,name,addr,player_count):

        self.name = name
        self.addr = addr

        self.living = True
        self.score = 0
## TODO NEED TO SET UNIQ COORDS FOR EACH SNAKE
        self.body = [{'X': 3*player_count, 'Y': 3},
                     {"X": 3*player_count, "Y": 2},
                     {"X": 3*player_count, "Y": 1}, ]

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

