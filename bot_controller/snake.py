import random
import copy

class Snake:

    def __init__(self, width, height, state_path):

        # the size of the word
        self.width = width
        self.height = height
        self.state_path = state_path

        # some parameters -> position = [y,x]
        self.high_score = None
        self.snake = None
        self.food = None
        self.direction = None

    # starting the game
    def start_game(self, load_from_state = False):

        # print
        print('Game started')

        # retrieve high score from file
        score = 0
        try:
            file = open('score.txt', 'r')
            score = int(file.read())
            file.close()
        except:
            print('No score file found.')

        if load_from_state:
            self.load_state()
        else:
            self.reset_game()

        # returns high score
        self.high_score = score
        return score

    # load from a previous state
    def load_state(self):

        # load file
        try:
            file = open(self.state_path, 'r')
        except:
            print('Unable to load file')
            return False

        # FIXME: block size load better
        world_size = file.readline()

        # high score
        high_score = file.readline()

        # direction
        self.direction = int(file.readline())

        # food
        food = file.readline().split(',')
        self.food = [int(food[1]), int(food[0])]

        # snake
        self.snake = []
        snake = file.readline().split(';')
        for s in snake:

            # position
            p = s.split(',')
            p = [int(p[1]), int(p[0])]

            # add position
            self.snake.append(p)

        # close file and return
        file.close()
        print('load complete')
        return True

    # ends game
    def end_game(self):

        # print
        print('Game ended, score:', self.score())

        # save score
        file = open('score.txt', 'w')
        file.write(str(self.high_score))
        file.close()

        self.reset_game()

    # reset the game -> after a loss
    def reset_game(self):

        # print
        print('Game reset')

        # reset objects
        self.snake = [self.random_pos()]
        self.spawn_food()
        self.direction = 0

    # return a random position 
    def random_pos(self):
        return [random.randint(0, self.height-1), random.randint(0, self.width-1)]

    # gets the score
    def score(self):
        return len(self.snake)-1

    # turn left
    def left(self):
        self.turn(-1)

    # turn right
    def right(self):
        self.turn(1)

    # move | only moves the head at the moment
    def move(self):

        # moving the head
        head = self.snake[0]
        prev = copy.copy(head)  # copy the head
        if self.direction == 0:
            head[0] -=1
        elif self.direction == 1:
            head[1] +=1
        elif self.direction == 2:
            head[0] +=1
        elif self.direction == 3:
            head[1] -=1

        # move the rest of the body
        if len(self.snake) > 0:
            for i in range(1, len(self.snake)):
                aux = copy.copy(self.snake[i])  # copy the current position
                self.snake[i] = prev  # current position to previous
                prev = aux  # set previous position to current

        # check for collisions
        self.collision()

    # collision detection
    def collision(self):
        head = self.snake[0]
        snake_length = len(self.snake)

        # if collided with frame
        if head[0] < 0 or head[1] < 0 or head[0] >= self.height or head[1] >= self.width:
            self.end_game()
            return

        # check if collided with food
        if self.pos_eval(self.food, head):

            # increase snake size and spawn new food
            self.increase_size()
            self.spawn_food()

        # check if collided with snake [only if snake length > 2]
        if snake_length > 2:
            for i in range(2, snake_length):

                # check if collided with body
                if self.pos_eval(self.snake[i], head):

                    # end_game
                    self.end_game()
                    break

    # turn head
    def turn(self, direction):
        self.direction += direction
        if self.direction == 4:
            self.direction = 0
        if self.direction == -1:
            self.direction = 3

    # spawns food -> random position
    # then checks if collides with anything
    # if it does, random position again
    def spawn_food(self):
        found = True
        rand = []
        while found:
            rand = self.random_pos()
            if self.food is None or (not self.pos_eval(rand, self.food)):
                found = False
                for x in self.snake:
                    if self.pos_eval(x, rand):
                        found = True
                        break
        self.food = rand

    # returns if two positions are the same
    def pos_eval(self, l1, l2):
        return l1[0] == l2[0] and l1[1] == l2[1]

    # increase snake's size
    def increase_size(self):

        # if current score > high score, then set the high score as score
        if self.score() > self.high_score:
            self.high_score = self.score()

        tail = copy.copy(self.snake[-1])
        self.snake.append(tail)

    # create state
    def save_state(self):

        # create snake state
        s_state = ''
        snake_length = len(self.snake)
        for i in range(snake_length):
            block = self.snake[i]

            # x,y
            s_state += str(block[1]) + ',' + str(block[0])

            # if not tail add ;
            if i != snake_length-1:
                s_state += ';'

        # save state to file
        file = open(self.state_path, 'w')
        file.write(str(self.width) + '\n' + str(self.high_score) + '\n' + str(self.direction) + '\n' + str(self.food[1]) + ',' + str(self.food[0]) + '\n' + s_state)
        file.close()

        print('State created')

    # a simple world render to console
    def console_render(self):

        # create world
        world = []
        for y in range(self.height):
            x_ = []
            for x in range(self.width):
                x_.append('.')
            world.append(x_)

        # draw food
        world[self.food[0]][self.food[1]] = 'o'

        # draw snake
        for x in self.snake:
            world[x[0]][x[1]] = 'x'

        # draw world
        for y in world:
            x_ = ''
            for x in y:
                x_ += x
            print(x_)
