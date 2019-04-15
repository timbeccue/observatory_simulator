
import random
import os
import time

# Print in colors: print(CRED+'string'+CEND)
CRED = '\033[91m'
CEND = '\033[0m'

class Walk:

    # Customizable parameters
    default_char = '.'
    walking_chars = ['M', '!']
    size = 25 # length of the line 
    fps = 2000
    pause_on_collision_time = 0.1 # seconds
    

    def __init__(self):
        """
        Create line of given length. 
        Assign random starting spot.
        Run the program loop.
        """

        #self.blank_line = [[self.default_char for col in range(self.size)] for row in range(self.size)]
        self.sleep_time = 1 / self.fps
        self.line = [[self.default_char for col in range(self.size)] for row in range(self.size)]

        self.population = len(self.walking_chars)
        self.spots = []
        for i in range(self.population):
            self.spots.append([random.randint(0,self.size-1), random.randint(0,self.size-1)])
            self.line[self.spots[i][0]][self.spots[i][1]] = self.walking_chars[i]
        self.run()

    def update(self):
        """
        Remove walker from its spot in line.
        Update spot (randomly +/- 1). 
        Add walker to spot in line.
        """

        # Update all the entities
        for i in range(self.population):

            x = self.spots[i][0]
            y = self.spots[i][1]
            self.line = [[self.default_char for col in range(self.size)] for row in range(self.size)]
 

            x_or_y = random.getrandbits(1)
            self.spots[i][x_or_y] = (self.spots[i][x_or_y] + 1) % self.size
            if random.getrandbits(1):
                self.spots[i][x_or_y] = (self.spots[i][x_or_y] - 2) % self.size


            self.line[x][y] = self.walking_chars[i]

        # print a red X if all characters occupy the same spot
        if self.detect_collision(): 
            self.line[self.spots[0][0]][self.spots[0][1]] = CRED+'X'+CEND

    def display(self):
        """
        Print the line with the walker.
        Replace last line (end="/r"), so it animates.
        """
        os.system('clear')
        for row in range(self.size):
            print(*self.line[row], sep="")#, end='\r')

        
    def detect_collision(self):
        """
        Check for case where all entities on the same tile.
        1. Make sure there are multiple entities.
        2. Check if all positions are the same.
        """
        if self.population > 1:
            x_set = set()
            y_set = set() 
            for i in range(self.population):
                x_set.add(self.spots[i][0])
                y_set.add(self.spots[i][1])
            if len(x_set) == len(y_set) == 1:
                return True
        return False

    def run(self):
        while True:
            self.update()
            self.display()

            # Wait a bit if there is a collision
            if self.detect_collision():
                time.sleep(self.pause_on_collision_time)

            # Sleep to fit desired fps.
            time.sleep(self.sleep_time)


if __name__=="__main__":
    w = Walk()
