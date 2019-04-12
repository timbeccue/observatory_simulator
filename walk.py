
import random
import time

# Print in colors: print(CRED+'string'+CEND)
CRED = '\033[91m'
CEND = '\033[0m'

class Walk:

    # Customizable parameters
    default_char = '.'
    walking_chars = [':', '!']
    size = 75 # length of the line 
    fps = 20 
    pause_on_collision_time = 0.1 # seconds
    

    def __init__(self):
        """
        Create line of given length. 
        Assign random starting spot.
        Run the program loop.
        """

        self.sleep_time = 1 / self.fps
        self.line = [self.default_char for i in range(self.size)]
        self.population = len(self.walking_chars)
        self.spots = []
        for i in range(self.population):
            self.spots.append(random.randint(0,self.size-1))
            self.line[self.spots[i]] = self.walking_chars[i]
        self.run()

    def update(self):
        """
        Remove walker from its spot in line.
        Update spot (randomly +/- 1). 
        Add walker to spot in line.
        """

        # Update all the entities
        for i in range(self.population):
            self.line[self.spots[i]] = self.default_char
            self.spots[i] = (self.spots[i] + 1) % self.size
            if random.getrandbits(1):
                self.spots[i] = (self.spots[i] - 2) % self.size
            self.line[self.spots[i]] = self.walking_chars[i]

        # print a red X if all characters occupy the same spot
        if self.detect_collision(): 
            self.line[self.spots[0]] = CRED+'X'+CEND

    def display(self):
        """
        Print the line with the walker.
        Replace last line (end="/r"), so it animates.
        """
        print(*self.line, sep="", end="\r")
        
    def detect_collision(self):
        """
        Check for case where all entities on the same tile.
        1. Make sure there are multiple entities.
        2. Check if all positions are the same.
        """
        if self.population > 1:
            if len(set(self.spots)) == 1:
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
