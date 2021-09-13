from pynput import keyboard
from random import randint
import os

MAP_SIZE = 40
GAME_SPEED = 70


class Game():

    def __init__(self):
        self.map = [[' '] * MAP_SIZE for i in range(MAP_SIZE)]
        self.tick_time = GAME_SPEED / 1000
        self.snake = Snake()
        self.add_food()
        while self.snake.living == True:
            self.tick()
        print(f'Score: {self.snake.score}')


    def idk(self):
        for i in range(len(self.snake.body)):
            if self.map[self.snake.body[i][0]][self.snake.body[i][1]] == '*':
                self.snake.add_segment()
                self.add_food()
            self.map[self.snake.body[i][0]][self.snake.body[i][1]] = '#'

    def show_map(self):
        print(' ', '__' * MAP_SIZE, sep='')
        for i in range(MAP_SIZE):
            print('|', end='')
            for j in range(MAP_SIZE):
                print(self.map[i][j], '', end='')
            print('|')
        print(' ', '--' * MAP_SIZE, sep='')
        print(self.snake.score)

    def add_food(self):
        x = randint(0, MAP_SIZE - 1)
        y = randint(0, MAP_SIZE - 1)
        for i in range(len(self.snake.body)):
            while x == self.snake.body[i][0]:
                x = randint(0, MAP_SIZE - 1)
            while y == self.snake.body[i][1]:
                y = randint(0, MAP_SIZE - 1)
        self.map[x][y] = '*'

    def tick(self):
        os.system('clear')
        self.snake.move()
        self.show_map()
        os.system(f'sleep {self.tick_time}')


class Snake():

    def __init__(self):
        self.living = True
        self.score = 0
        self.body = [[0] * 2 for i in range(3)]
        self.body[0][0] = 3
        self.body[0][1] = 3
        self.body[1][0] = 3
        self.body[1][1] = 2
        self.body[2][0] = 3
        self.body[2][1] = 1
        self.direction = 'up'
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

    def move(self):

        for i in range(len(self.body), 1, -1):
            j = i - 1
            self.body[j][0] = self.body[j - 1][0]
            self.body[j][1] = self.body[j - 1][1]

        if self.direction == 'right':
            if self.body[0][1] == MAP_SIZE - 1:
                self.body[0][1] = 0
            else:
                self.body[0][1] += 1

        elif self.direction == 'left':
            if self.body[0][1] == 0:
                self.body[0][1] = MAP_SIZE - 1
            else:
                self.body[0][1] -= 1
        elif self.direction == 'up':
            if self.body[0][0] == 0:
                self.body[0][0] = MAP_SIZE - 1
            else:
                self.body[0][0] -= 1
        elif self.direction == 'down':
            if self.body[0][0] == MAP_SIZE - 1:
                self.body[0][0] = 0
            else:
                self.body[0][0] += 1
        for i in range(1, len(self.body)):
            if self.body[0] == self.body[i]:
                self.death()

    def on_press(self, key):
        if key == keyboard.Key.left and self.direction != 'right':
            self.direction = 'left'
        elif key == keyboard.Key.right and self.direction != 'left':
            self.direction = 'right'
        elif key == keyboard.Key.up and self.direction != 'down':
            self.direction = 'up'
        elif key == keyboard.Key.down and self.direction != 'up':
            self.direction = 'down'
        elif key == keyboard.Key.esc:
            self.living = False

    def add_segment(self):
        self.score += 10
        self.body.append([0, 0])
        pass

    def death(self):
        self.living = False


def main():
    game = Game()


if __name__ == "__main__":
    main()