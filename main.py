from random import randint
import json
import socket

MAP_SIZE = 800
SEGMENT_SIZE = 20
GAME_SPEED = 100

MAX_PLAYERS = 1

SNAKE_COLOR = ['#99d98c', '#264653', '#2a9d8f']


# WAS DESIGION OF USE A DICT IS RIGHT? IDK

class Game:

    def __init__(self):

                                        #network
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind(('',9996))     #Using 9996 port
        self.server.listen(MAX_PLAYERS)

        self.players = []


        while len(self.players) < MAX_PLAYERS:
            print('waiting players:',len(self.players),'/',MAX_PLAYERS)
            conn, addr = self.server.accept()
            name = conn.recv(1024).decode('utf-8')
            print('player',name,'connected')
            self.players.append(Snake(conn, name, addr, len(self.players) + 1))


        for snake in self.players:
            snake.conn.send(bytes('runing', encoding = "utf-8"))



        self.food_pos = []
        for i in range(len(self.players)):
            self.add_food()


        data = self.get_network_data()
        self.send_data(data)

        self.gameloop()
        print('game over')



    def gameloop(self):

        self.recv_input()

        for snake in self.players:
            if snake.living:
                snake.direction = snake.next_direction
                snake.move()
                self.check_snakes_collision()
            else:
                if len(self.players) > 1:
                    self.players.remove(snake)
                    self.kill_snake(snake)
                else:
                    return 0

        data = self.get_network_data()
        self.send_data(data)


        self.gameloop()


    def add_food(self):

        x = randint(0, MAP_SIZE/SEGMENT_SIZE - 1) * SEGMENT_SIZE
        y = randint(0, MAP_SIZE/SEGMENT_SIZE - 1) * SEGMENT_SIZE

        snakes_coords = self.get_snake_coord()

        while [x, y] in snakes_coords:
            x = randint(0, MAP_SIZE/SEGMENT_SIZE) * SEGMENT_SIZE
            y = randint(0, MAP_SIZE/SEGMENT_SIZE) * SEGMENT_SIZE

        self.food_pos.append({'X': x, 'Y': y})




    def get_snake_coord(self,except_snake = None):
        cordinates = []
        for snake in self.players:
            if snake != except_snake:
                for segment in snake.body:
                    cordinates.append(list(segment.values()))
        return cordinates



    def check_snakes_collision(self):
        for snake in self.players:
            for food in self.food_pos:
                if list(snake.body[0].values()) == list(food.values()):
                    snake.add_segment()
                    self.food_pos.remove(food)
                    self.add_food()
            if list(snake.body[0].values()) in self.get_snake_coord(except_snake = snake):
                snake.death()

     ############################NETWORK################################           

    def get_network_data(self):
        data = {'food_pos': self.food_pos}
        for i in range(len(self.players)):
            data.update({f'player{i}':self.players[i].body})
        return data


    def send_data(self,data):
        for snake in self.players:
            snake.conn.send(bytes(json.dumps(data), encoding = "utf-8"))


    def recv_input(self):
        for snake in self.players:
            direction = snake.conn.recv(1024)
            direction = direction.decode("utf-8")
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


    def kill_snake(self,snake):
        snake.conn.send(bytes('stop',encoding = 'utf-8'))



class Snake:

    def __init__(self,conn,name,addr,player_count):

        self.name = name
        self.addr = addr
        self.conn = conn

        self.living = True
        self.score = 0
## TODO NEED TO SET UNIQ COORDS FOR EACH SNAKE
        self.body = [{'X': 3*player_count * SEGMENT_SIZE, 'Y': 3 * SEGMENT_SIZE},
                     {"X": 3*player_count * SEGMENT_SIZE, "Y": 2 * SEGMENT_SIZE},
                     {"X": 3*player_count * SEGMENT_SIZE, "Y": 1 * SEGMENT_SIZE}, ]

        self.direction = 'up'
        self.next_direction = 'up'


    def move(self):
        # перемещение координат тела змейки
        if self.living:
            for segment in range(len(self.body) - 1, 0, -1):
                self.body[segment]['X'] = self.body[segment - 1]['X']
                self.body[segment]['Y'] = self.body[segment - 1]['Y']
    
            if self.direction == 'right':
                if self.body[0]['Y'] == MAP_SIZE - SEGMENT_SIZE:
                    self.body[0]['Y'] = 0
                else:
                    self.body[0]['Y'] += SEGMENT_SIZE
    
            elif self.direction == 'left':
                if self.body[0]['Y'] == 0:
                    self.body[0]['Y'] = MAP_SIZE - SEGMENT_SIZE
                else:
                    self.body[0]['Y'] -= SEGMENT_SIZE
            elif self.direction == 'up':
                if self.body[0]['X'] == 0:
                    self.body[0]['X'] = MAP_SIZE - SEGMENT_SIZE
                else:
                    self.body[0]['X'] -= SEGMENT_SIZE
            elif self.direction == 'down':
                if self.body[0]['X'] == MAP_SIZE - SEGMENT_SIZE:
                    self.body[0]['X'] = 0
                else:
                    self.body[0]['X'] += SEGMENT_SIZE
             #### SNAKE CHECK HIS OWN COLLISION? ITS BAD
            for i in range(1, len(self.body)):
                if self.body[0] == self.body[i]:
                    self.death()
    


    def add_segment(self):
        self.score += 10

        new_segment  = {'X': self.body[-1]['X'], 'Y': self.body[-1]['Y']}
        self.body.append(new_segment)


    def death(self):
        self.living = False


def main():
    game = Game()


if __name__ == "__main__":
    main()

