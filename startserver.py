from random import randint
import pickle
import socket

MAP_SIZE = 700
SEGMENT_SIZE = 20
GAME_SPEED = 100
MAX_PLAYERS = 2

PLAYERS_START_POS = ([[60,60],[60,40],[60,20]],
                    [[640,680],[640,660],[640,640]],
                    [[100,640],[80,640],[60,640]],
                    [[640,60],[660,40],[680,20]],
                    [[60,300],[40,300],[20,300]],
                    [[640,300],[660,300],[680,300]])
PLAYER_START_DIR = ('down','up','right','left','right','left')



class Game:

    def __init__(self):

        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) # Creaating a socket
        self.server.bind(('',9996))     #Using 9996 port

        self.server.listen(MAX_PLAYERS)
        self.players = []
        self.food_pos = []

        while len(self.players) < MAX_PLAYERS: # Waiting while all players to connect
            print('* waiting players:',len(self.players),'/',MAX_PLAYERS)
            conn, addr = self.server.accept()
            name = conn.recv(1024).decode('utf-8')
            print('[!] player',name,'connected')
            self.players.append(Snake(conn, name, addr, len(self.players))) # add player's snake
            
        self.live_players = len(self.players)


        for _ in range(len(self.players)):
            self.add_food()

        self.send_data(self.get_init_network_data())

        while self.live_players > 0:  # Gameloop
            self.gameloop()

        self.send_data('stop') #Sending stop massage
        print('[!] Game Over')



    def gameloop(self) -> None:
        """starting gameloop of the game"""

        self.recv_input()

        for snake in self.players:
            if snake.living:
                snake.direction = snake.next_direction
                snake.move()
        self.check_snakes_collision()
                
        data = self.get_network_data()
        self.send_data(data)


    def add_food(self) -> None:
        """add food to the game field"""

        x = randint(0, int(MAP_SIZE/SEGMENT_SIZE) - 1) * SEGMENT_SIZE
        y = randint(0, int(MAP_SIZE/SEGMENT_SIZE) - 1) * SEGMENT_SIZE

        snakes_coords = self.get_snake_coord()

        while [x, y] in snakes_coords:
            x = randint(0, int(MAP_SIZE/SEGMENT_SIZE)) * SEGMENT_SIZE
            y = randint(0, int(MAP_SIZE/SEGMENT_SIZE)) * SEGMENT_SIZE

        self.food_pos.append([x, y])




    def get_snake_coord(self,except_snake = None) -> list:
        """getting list of coordinates of each snake segment"""
        cordinates = []
        for snake in self.players:
            if snake.living:
                for segment in snake.body:
                    cordinates.append(segment)
        if except_snake:
            cordinates.remove(except_snake.body[0])
        return cordinates



    def check_snakes_collision(self) -> None:
        for snake in self.players:
            if snake.living:
                for food in self.food_pos:
                    if snake.body[0] == food:
                        snake.add_segment()
                        self.food_pos.remove(food)
                        self.add_food()
                if snake.body[0] in self.get_snake_coord(except_snake = snake):
                    snake.death()
                    self.live_players -= 1

     ############################NETWORK################################           
    def get_init_network_data(self) -> list:
        """return init network data"""


        init_data = [self.food_pos]
        for snake in self.players:
            init_data.append({'name': snake.name,
                              'body': snake.body,
                              'color': snake.color,
                              'score': snake.score,
                              'living': True})
        return init_data



    def get_network_data(self) -> list:
        """get player inputs from the connection"""
        data = [self.food_pos]
        for i in range(len(self.players)):
            data.append({'body': self.players[i].body,
                         'score': self.players[i].score,
                         'living': self.players[i].living})
        return data


    def send_data(self,data) -> None:
        """send network data to playres"""
        data = pickle.dumps(data)
        for snake in self.players:
            if snake.conn:
                try:
                    snake.conn.send(data) 
                except (ConnectionResetError,BrokenPipeError):
                    print(f'[!] {snake.name}  disconnected')
                    snake.conn = None
                    if snake.living:
                        snake.death()
                        self.live_players -= 1
                    continue




    def recv_input(self) -> None:  
        """recive players input"""
        for snake in self.players:
            if snake.living:
                try:
                    direction = snake.conn.recv(1024)
                except ConnectionResetError:
                    print(f'[!] {snake.name}  disconnected')
                    snake.conn = None
                    snake.death()
                    self.live_players -= 1
                    continue

                direction = direction.decode("utf-8")
                if direction == 'left' and snake.direction != 'right':
                    snake.next_direction = 'left'
                elif direction == 'right' and snake.direction != 'left':
                    snake.next_direction = 'right'
                elif direction == 'up' and snake.direction != 'down':
                    snake.next_direction = 'up'
                elif direction == 'down' and snake.direction != 'up':
                    snake.next_direction = 'down'



class Snake:

    def __init__(self,conn,name,addr,player_count):

        self.name = name
        self.addr = addr
        self.conn = conn

        self.living = True
        self.score = 0
        self.body = PLAYERS_START_POS[player_count]

        self.color = ('green','blue','pink','dust','underground','candy')[player_count]
        self.direction = PLAYER_START_DIR[player_count]
        self.next_direction = PLAYER_START_DIR[player_count]


    def move(self) -> None:
        """moveing snake in game field"""
        if self.living:
            for segment in range(len(self.body) - 1, 0, -1):
                self.body[segment][0] = self.body[segment - 1][0]
                self.body[segment][1] = self.body[segment - 1][1]
    
            if self.direction == 'right':
                if self.body[0][1] == MAP_SIZE - SEGMENT_SIZE:
                    self.body[0][1] = 0
                else:
                    self.body[0][1] += SEGMENT_SIZE
    
            elif self.direction == 'left':
                if self.body[0][1] == 0:
                    self.body[0][1] = MAP_SIZE - SEGMENT_SIZE
                else:
                    self.body[0][1] -= SEGMENT_SIZE
            elif self.direction == 'up':
                if self.body[0][0] == 0:
                    self.body[0][0] = MAP_SIZE - SEGMENT_SIZE
                else:
                    self.body[0][0] -= SEGMENT_SIZE
            elif self.direction == 'down':
                if self.body[0][0] == MAP_SIZE - SEGMENT_SIZE:
                    self.body[0][0] = 0
                else:
                    self.body[0][0] += SEGMENT_SIZE
    


    def add_segment(self) -> None:
        """add segment to the snake"""
        print(f"* {self.name} eats an apple")
        self.score += 10

        new_segment  = [self.body[-1][0],  self.body[-1][1]]
        self.body.append(new_segment)


    def death(self):
        """kill the snake"""

        self.living = False
        print(f'[!] {self.name}, is dead')


def main():
    game = Game()


if __name__ == "__main__":
    MAX_PLAYERS = int(input("max players: "))
    main()

