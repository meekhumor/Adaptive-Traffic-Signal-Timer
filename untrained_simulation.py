import random
import time
import threading
import pygame

# Default signal times (fixed for standardized timing)
defaultRed = 55
defaultYellow = 5
defaultGreen = 20

signals = []
noOfSignals = 4
simTime = 300  # Simulation time in "ticks"
timeElapsed = 0

currentGreen = 0
nextGreen = (currentGreen + 1) % noOfSignals
currentYellow = 0

# Doubled vehicle speeds for faster movement
speeds = {'car': 6.75, 'bus': 5.4, 'truck': 5.4, 'rickshaw': 6.0, 'bike': 7.5}

x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'rickshaw', 4: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]
vehicleCountTexts = ["0", "0", "0", "0"]

stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580, 580, 580], 'down': [320, 320, 320], 'left': [810, 810, 810], 'up': [545, 545, 545]}

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = "20"

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.currentImage = pygame.image.load(path)
        
        if direction == 'right':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][self.index - 1].currentImage.get_rect().width - 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + 15
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction == 'left':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][self.index - 1].currentImage.get_rect().width + 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + 15
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif direction == 'down':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][self.index - 1].currentImage.get_rect().height - 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + 15
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction == 'up':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][self.index - 1].currentImage.get_rect().height + 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + 15
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.currentImage.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.x + self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or (currentGreen == 0 and currentYellow == 0)) and \
               (self.index == 0 or self.x + self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index - 1].x - 15)):
                self.x += self.speed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.currentImage.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.y + self.currentImage.get_rect().height <= self.stop or self.crossed == 1 or (currentGreen == 1 and currentYellow == 0)) and \
               (self.index == 0 or self.y + self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index - 1].y - 15)):
                self.y += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and \
               (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().width + 15)):
                self.x -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if (self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and \
               (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().height + 15)):
                self.y -= self.speed

def getVehiclesInDirection(direction):
    count = 0
    for lane in range(3):
        for vehicle in vehicles[direction][lane]:
            if vehicle.crossed == 0:
                count += 1
    return count

def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.green + ts1.yellow, defaultYellow, defaultGreen)
    signals.append(ts2)
    ts3 = TrafficSignal(ts2.red + ts2.green + ts2.yellow, defaultYellow, defaultGreen)
    signals.append(ts3)
    ts4 = TrafficSignal(ts3.red + ts3.green + ts3.yellow, defaultYellow, defaultGreen)
    signals.append(ts4)
    for _ in range(8):
        vehicle_type = random.randint(0, 4)
        lane_number = 0 if vehicle_type == 4 else random.randint(1, 2)
        direction_number = random.randint(0, 3)
        will_turn = random.randint(0, 1) if lane_number == 2 else 0
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
    repeat()

def repeat():
    global currentGreen, currentYellow, nextGreen
    while True:
        if signals[currentGreen].green > 0:
            updateValues()
        elif signals[currentGreen].yellow > 0:
            if currentYellow == 0:
                currentYellow = 1
                vehicleCountTexts[currentGreen] = "0"
                for i in range(3):
                    stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
                    for vehicle in vehicles[directionNumbers[currentGreen]][i]:
                        vehicle.stop = defaultStop[directionNumbers[currentGreen]]
            updateValues()
        else:
            currentYellow = 0
            signals[currentGreen].green = defaultGreen
            signals[currentGreen].yellow = defaultYellow
            signals[currentGreen].red = defaultRed
            currentGreen = nextGreen
            nextGreen = (currentGreen + 1) % noOfSignals
            signals[nextGreen].red = signals[currentGreen].green + signals[currentGreen].yellow + defaultRed - (defaultGreen + defaultYellow)
        return  # Let main loop control timing

def updateValues():
    for i in range(noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    while True:
        vehicle_type = random.randint(0, 4)
        lane_number = 0 if vehicle_type == 4 else random.randint(1, 2)
        will_turn = random.randint(0, 1) if lane_number == 2 else 0
        direction_number = random.randint(0, 3)
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(1)

def simulationTime():
    global timeElapsed
    while True:
        timeElapsed += 1
        if timeElapsed >= simTime:
            totalVehicles = sum(vehicles[directionNumbers[i]]['crossed'] for i in range(noOfSignals))
            print(f"Total vehicles passed: {totalVehicles}")
            print(f"Total time passed: {timeElapsed} ticks ({timeElapsed * 0.75:.1f} real seconds)")
            print(f"Vehicles per unit time: {totalVehicles / timeElapsed:.2f}")
            pygame.quit()
        time.sleep(0.75)  # Sync with signal update rate

class Main:
    thread4 = threading.Thread(target=simulationTime)
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(target=initialize)
    thread2.daemon = True
    thread2.start()

    black = (0, 0, 0)
    white = (255, 255, 255)

    screenWidth = 1400
    screenHeight = 800
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption("SIMULATION (Standardized Timing - 20s Green = 15s Real)")

    background = pygame.image.load('images/mod_int.png')
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread3 = threading.Thread(target=generateVehicles)
    thread3.daemon = True
    thread3.start()

    clock = pygame.time.Clock()
    FPS = 60  # Frames per second for smooth visuals
    signal_update_interval = 750  # Signal updates every 750ms (0.75s)
    last_signal_update = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_time = pygame.time.get_ticks()
        if current_time - last_signal_update >= signal_update_interval:
            repeat()  # Update signals every 750ms
            last_signal_update = current_time

        screen.blit(background, (0, 0))
        for i in range(noOfSignals):
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = "STOP" if signals[i].yellow == 0 else str(signals[i].yellow)
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = "SLOW" if signals[i].green == 0 else str(signals[i].green)
                    screen.blit(greenSignal, signalCoods[i])
            else:
                signals[i].signalText = "GO" if signals[i].red == 0 else (str(signals[i].red) if signals[i].red <= 10 else "---")
                screen.blit(redSignal, signalCoods[i])

        for i in range(noOfSignals):
            signalTexts = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts, signalTimerCoods[i])
            displayText = getVehiclesInDirection(directionNumbers[i])
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

        timeElapsedText = font.render(f"Time Elapsed: {timeElapsed} ticks ({timeElapsed * 0.75:.1f}s)", True, black, white)
        screen.blit(timeElapsedText, (1100, 50))

        for vehicle in simulation:
            vehicle.render(screen)
            vehicle.move()
        pygame.display.update()
        clock.tick(FPS)  # Cap at 60 FPS for smooth visuals

Main()