from random import randint
import pickle
import socket

MAP_SIZE = 800
SEGMENT_SIZE = 20
GAME_SPEED = 100
MAX_PLAYERS = 2

PLAYERS_START_POS = ([[60,60],[60,40],[60,20]],
                    [[740,780],[740,760],[740,740]],
                    [[100,740],[80,740],[60,740]],
                    [[740,60],[760,40],[780,20]],
                    [[60,400],[40,400],[20,400]],
                    [[740,400],[760,400],[780,400]])
PLAYER_START_DIR = ('down','up','right','left','right','left')



class Game:

    def __init__(self):

                                        #network
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind(('',9996))     #Using 9996 port
        self.server.listen(MAX_PLAYERS)
        self.players = []


        while len(self.players) < MAX_PLAYERS:
            print('* waiting players:',len(self.players),'/',MAX_PLAYERS)
            conn, addr = self.server.accept()
            name = conn.recv(1024).decode('utf-8')
            print('[!] player',name,'connected')
            self.players.append(Snake(conn, name, addr, len(self.players)))
            
            for snake in self.players:
                if snake.name != name:
                    snake.conn.send(bytes(name,encoding = 'utf-8'))

        self.live_players = len(self.players)


        self.food_pos = []
        for i in range(len(self.players)):
            self.add_food()

        init_data = [self.food_pos]
        for snake in self.players:
            snake.conn.send(bytes('runing', encoding = "utf-8"))
            init_data.append({'name': snake.name,'body': snake.body, 'color': snake.color,'score': snake.score,'living': True})
        self.send_data(init_data)


        while self.live_players > 0:
            self.gameloop()

        self.send_data('stop')
        print('[!] Game Over')



    def gameloop(self):

        self.recv_input()

        for snake in self.players:
            if snake.living:
                snake.direction = snake.next_direction
                snake.move()
        self.check_snakes_collision()
                
        data = self.get_network_data()
        self.send_data(data)


    def add_food(self):

        x = randint(0, MAP_SIZE/SEGMENT_SIZE - 1) * SEGMENT_SIZE
        y = randint(0, MAP_SIZE/SEGMENT_SIZE - 1) * SEGMENT_SIZE

        snakes_coords = self.get_snake_coord()

        while [x, y] in snakes_coords:
            x = randint(0, MAP_SIZE/SEGMENT_SIZE) * SEGMENT_SIZE
            y = randint(0, MAP_SIZE/SEGMENT_SIZE) * SEGMENT_SIZE

        self.food_pos.append([x, y])




    def get_snake_coord(self,except_snake = None):
        cordinates = []
        for snake in self.players:
            if snake.living:
                for segment in snake.body:
                    cordinates.append(segment)
        if except_snake:
            cordinates.remove(except_snake.body[0])
        return cordinates



    def check_snakes_collision(self):
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

    def get_network_data(self):
        data = [self.food_pos]
        for i in range(len(self.players)):
            data.append({'body': self.players[i].body,'score': self.players[i].score , 'living': self.players[i].living})
        return data


    def send_data(self,data):
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




    def recv_input(self):  
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
## TODO NEED TO SET UNIQ COORDS FOR EACH SNAKE
        #self.body = [[ 3*player_count * SEGMENT_SIZE, 3 * SEGMENT_SIZE],
        #             [ 3*player_count * SEGMENT_SIZE, 2 * SEGMENT_SIZE],
        #             [ 3*player_count * SEGMENT_SIZE, 1 * SEGMENT_SIZE]]
        self.body = PLAYERS_START_POS[player_count]

        self.color = ('green','blue','pink','dust','underground','candy')[player_count]
        self.direction = PLAYER_START_DIR[player_count]
        self.next_direction = PLAYER_START_DIR[player_count]


    def move(self):
        # перемещение координат тела змейки
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
    


    def add_segment(self):
        self.score += 10

        new_segment  = [self.body[-1][0],  self.body[-1][1]]
        self.body.append(new_segment)


    def death(self):

        self.living = False
        print(f'[!] {self.name}, is dead')


def main():
    game = Game()


if __name__ == "__main__":
    MAX_PLAYERS = int(input("max players: "))
    main()

