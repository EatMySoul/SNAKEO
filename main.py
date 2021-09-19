from pynput import keyboard
from random import randint
from tkinter import *
import time

MAP_SIZE = 20
GAME_SPEED = 100


class Game():

    def __init__(self):

        self.players = []
        self.food_pos = []
        new_snake = Snake()
        self.players.append(new_snake)
        self.map = [[0] *  MAP_SIZE for i in range(MAP_SIZE)]

        self.root = Tk()
        self.root.geometry('800x800')

        self.canvas = Canvas(self.root,height=800,width=800,bg='black')
        self.canvas.pack()
####    dont like this V V V V
        for snake in self.players:
            for i in snake.body:
                self.map[ i['X'] ][ i['Y'] ] = 1
 ####
        self.add_food()
        self.gameloop()

        self.root.mainloop()


    def show_interface_map(self):

        self.canvas.delete('all')

        for x in range(MAP_SIZE):
            for y in range(MAP_SIZE):
                if self.map[x][y] == 1:
                    self.canvas.create_rectangle(y*MAP_SIZE,x*MAP_SIZE,y*MAP_SIZE+20,x*MAP_SIZE+20,fill='green')
                elif self.map[x][y] == 2:
                    self.canvas.create_rectangle(y*MAP_SIZE,x*MAP_SIZE,y*MAP_SIZE+20,x*MAP_SIZE+20,fill='red')
                elif self.map[x][y] == 3:
                    pass

                ######## SOME DEBUG TO SEE MATRIX MAP
 #       for i in range(MAP_SIZE):
 #          for j in range(MAP_SIZE):
 #              print(self.map[i][j],end = ' ')
 #          print()
 #       print('\n')


    def gameloop(self):
        for snake in self.players:
            snake.direction = snake.next_direction
            snake.move()
            self.check_snakes_collision()
            #### CLEANING MATRIX MAP
            for i in range(MAP_SIZE):
                for j in range(MAP_SIZE):
                    if self.map[i][j] == 1:
                        self.map[i][j] = 0
            ####
#################################################### LOOOK AT ME AM HERE!
            for i in snake.body:
                self.map[i['X'] ][ i['Y'] ] = 1
            #####


        self.show_interface_map()
        self.root.after(GAME_SPEED,self.gameloop)


    def add_food(self):
        x = randint(0, MAP_SIZE - 1)
        y = randint(0, MAP_SIZE - 1)

        while self.map[x][y] == 1:
            x = randint(0, MAP_SIZE - 1)
            y = randint(0, MAP_SIZE - 1)

        self.food_pos = {'X': x, 'Y': y}
        self.map[x][y] = 2


    def check_snakes_collision(self):
        for snake in self.players:
            if list(snake.body[0].values()) == list(self.food_pos.values()):
                snake.add_segment()
                self.add_food()



class Snake():

    def __init__(self):
        self.living = True
        self.score = 0

        self.body = [{'X':3,'Y':3},
                     {"X":3,"Y":2},
                     {"X":3,"Y":1},]

        self.direction = 'up'
        self.next_direction = 'up'

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

    def move(self):
        # перемещение координат тела змейки
   #     for i in range(len(self.body), 1, -1):
   #         j = i - 1
   #         self.body[j]['X'] = self.body[j - 1]['X']
   #         self.body[j]['Y'] = self.body[j - 1]['Y']
   #     #
        print(self.body)
        for segment in range(len(self.body) - 1,-1,-1):
            print(self.body[segment])
##### WHATS WRONG?????????
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
         #### SNAKE CHECK HIS OWN COLLISION?
        for i in range(1, len(self.body)):
            if self.body[0] == self.body[i]:
                self.death()


    def on_press(self, key):
        if key == keyboard.Key.left and self.direction != 'right':
            self.next_direction = 'left'
        elif key == keyboard.Key.right and self.direction != 'left':
            self.next_direction = 'right'
        elif key == keyboard.Key.up and self.direction != 'down':
            self.next_direction = 'up'
        elif key == keyboard.Key.down and self.direction != 'up':
            self.next_direction = 'down'
        elif key == keyboard.Key.esc:
            self.living = False



    def add_segment(self):
        self.score += 10
        print(f'Score is {self.score}')

        ## FIX start position of new segment
        new_segment  = self.body[-1]
        self.body.append(new_segment)


    def death(self):
        print('snake is dead ;(')
        self.living = False

        ## TODO END GAME!
        time.sleep(3)


def main():
    game = Game()


if __name__ == "__main__":
    main()

"""
MATRIX MAP LOOKS LIKE

1 - snake body

2 - apple

0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 


"""
