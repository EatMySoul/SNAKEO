from pynput import keyboard
from random import randint
from tkinter import *
import time

MAP_SIZE = 20
GAME_SPEED = 100

SNAKE_COLOR = ['#99d98c','#264653','#2a9d8f']


#WAS DESIGION OF USE A DICT IS RIGHT?

class Game():

    def __init__(self):

        self.players = []
        self.food_pos = {}

        new_snake = Snake()
        self.players.append(new_snake)

        self.root = Tk()
        self.root.geometry('800x800')

        self.canvas = Canvas(self.root,height=800,width=800,bg='black')
        self.canvas.pack()

        self.add_food()
        self.gameloop()

        self.root.mainloop()


    def show_interface_map(self):

        self.canvas.delete('all')

        snake_color = SNAKE_COLOR
        flag = 0
        ##TODO CHANGE SIZING
        for snake in self.players:
            for segment in snake.body:
                self.canvas.create_rectangle(segment['Y'] * MAP_SIZE , segment['X'] * MAP_SIZE,segment['Y'] * MAP_SIZE + 20 , segment['X'] * MAP_SIZE + 20, fill=snake_color[flag])
                flag = 2 if flag == 1 or 0 else 1
        self.canvas.create_rectangle(self.food_pos['Y']*MAP_SIZE, self.food_pos['X']*MAP_SIZE,self.food_pos['Y']*MAP_SIZE + 20, self.food_pos['X']*MAP_SIZE + 20,fill='#d00000')
        SNAKE_COLOR[2],SNAKE_COLOR[1] = SNAKE_COLOR[1],SNAKE_COLOR[2]


    def gameloop(self):

        for snake in self.players:
            snake.direction = snake.next_direction
            snake.move()
            self.check_snakes_collision()

        self.show_interface_map()
        self.root.after(GAME_SPEED,self.gameloop)


    def add_food(self):
        x = randint(0, MAP_SIZE - 1)
        y = randint(0, MAP_SIZE - 1)

        snakes_coords = self.get_snake_coord()

        while [x,y] in snakes_coords:
            x = randint(0, MAP_SIZE - 1)
            y = randint(0, MAP_SIZE - 1)

        self.food_pos = {'X': x, 'Y': y}

    ##TODO GET SPECIFIC OF PLAYER SNAKE COORDS LIKE get_snake_coord(player1,player3)
    def get_snake_coord(self,):
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
        print(self.body)
        for segment in range(len(self.body) - 1,0,-1):
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

        new_segment  = {'X': self.body[-1]['X'],'Y':self.body[-1]['Y']}
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
