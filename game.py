import pygame
import math
from pygame.locals import *
import random

import winsound
from pygame import mixer

mixer.pre_init(44100, -16, 2, 512)
mixer.init()
mixer.music.load('data/bensound-clearday.mp3')
mixer.music.play(-1)
#Credits to https://www.bensound.com/ for the music


''' Configurable variables '''
WIDTH = 1024
HEIGHT = 768

characterMovementAmount = 2
bgMovementAmount = characterMovementAmount 

cX = int(WIDTH/2)
cY = 100
fishSize = 20
fishSpeed = 5
hungerSpeed = 0.02

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

# graphics
startScreen = pygame.image.load("data/bg_menu.png").convert_alpha()
loseScreen = pygame.image.load("data/lose.png").convert_alpha()
winScreen = pygame.image.load("data/win.png").convert_alpha()
heart = pygame.image.load("data/heart_icon.png").convert_alpha()
seaweed = pygame.image.load("data/seaweed.png").convert_alpha()

# sounds effects all public domain
eatsound = pygame.mixer.Sound("data/bloop_x.wav")
damagesound = pygame.mixer.Sound("data/ouch.wav")
losesound = pygame.mixer.Sound("data/buzzer_x.wav")
winsound = pygame.mixer.Sound("data/applause2_x.wav")

class Bubble(pygame.sprite.DirtySprite):
    def __init__(self, pos):
        super(Bubble, self).__init__()

        self.image = pygame.image.load("data/bubble.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.x = pos[0]
        self.y = pos[1]
        self.wiggle = 1

    def update(self, bgViewPort):
        currentPos = (self.x, self.y)        

        if currentPos[1] > 0:
            newX = currentPos[0]

            self.wiggle = not self.wiggle
            newY = currentPos[1] - 1
            self.rect = self.image.get_rect(center=(newX, newY - bgViewPort))
            self.x = newX
            self.y = newY
        else:
            self.kill()

class Player(pygame.sprite.DirtySprite):
    
    def __init__(self, pos):
        super(Player, self).__init__()
        self.direction = 1
        self.state = 1 # swimming
        self.index = 16
        self.size = 0
        self.alpha = 255


        self.image = pygame.Surface((80, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.spritesheet = pygame.image.load("data/player.png").convert_alpha()
        self.blitImage(self.index)

        self.prevx = pos[0]
        self.prevy = pos[1]
        self.mask = pygame.mask.from_surface(self.image)
        self.animSpeed = 2
        self.animSpeedCounter = self.animSpeed
        self.eatingTimes = 1
        self.eatingCounter = self.eatingTimes
        self.skip = 1
        
    def damage(self, fish):
        enemyPos = fish.rect.center
        playerPos = self.rect.center

        newX = playerPos[0]
        newY = playerPos[1]

        if enemyPos[1] < playerPos[1]:
            newY += 50

        if enemyPos[1] >= playerPos[1]:
            newY -= 50

        self.updatePlayer((newX, newY))
        return (newX, newY)

    def grow(self):
        self.size += 1
        self.blitImage(self.index)

    def eating(self):
        self.state = 3 
        self.index = 24
        self.blitImage(self.index)
        self.animSpeedCounter = self.animSpeed
        self.eatingCounter = self.eatingTimes

    def blitImage(self, index):        
        y = int(index / 8)
        x = index % 8

        self.image = pygame.Surface((80, 50), pygame.SRCALPHA)
        self.image.blit(self.spritesheet, (0,0), (80 * x, 50 * y, 80, 50))
        self.image = pygame.transform.smoothscale(self.image, (80+self.size, 50+self.size))
        self.image.set_alpha(self.alpha)

        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        if self.direction == 0:
            self.image = pygame.transform.flip(self.image, True, False)       

    def update(self):
        if self.animSpeedCounter <= 0:
            self.index += 1

            if self.state == 1 and self.index > 23:
                self.index = 16

            if self.state == 3 and self.index > 27:
                if self.eatingCounter < 0:
                    self.state = 1
                    self.index = 16
                else:
                    self.index = 24
                    self.eatingCounter -= 1

            if self.state == 2 and self.index > 7:
                self.index = 0

            self.blitImage(self.index)
            self.animSpeedCounter = self.animSpeed

        self.animSpeedCounter -= 1

    def updatePlayer(self, pos):
        if self.state != 3:
            if pos[0] == self.prevx and pos[1] == self.prevy:
                if self.state != 2:
                    # change to idle state
                    self.state =2 
                    self.index = 0
                    self.blitImage(self.index)
            else:
                if self.state != 1:
                    self.state = 1
                    self.index = 16
                    self.blitImage(self.index)

        newdirection = self.direction
        if pos[0] < self.prevx:
            newdirection = 1

        if pos[0] > self.prevx:
            newdirection = 0

        if newdirection != self.direction:
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = newdirection

        self.rect = self.image.get_rect(center=pos)
        self.prevx = pos[0]
        self.prevy = pos[1]

    def getSize(self):
        return self.size

class Seaweed(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Seaweed, self).__init__()

        self.image = pygame.Surface((25, 128), pygame.SRCALPHA)

        self.spritesheet = pygame.image.load("data/seaweed.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.x = pos[0]
        self.y = pos[1]
        self.animSpeed = 20
        self.animSpeedCounter = self.animSpeed
        self.index = 0
        self.blitImage(self.index)

    def blitImage(self, index):     
        self.image.fill(0)   
        self.image.blit(self.spritesheet, (0,0), (index * 25, 0, 25,128))

    def update(self, bgViewPort):
        if self.animSpeedCounter <= 0:
            self.index += 1

            if self.index > 3:
                self.index = 0

            self.blitImage(self.index)
            self.animSpeedCounter = self.animSpeed

        self.animSpeedCounter -= 1

        self.rect = self.image.get_rect(center=(self.x,self.y - bgViewPort))


class Fish(pygame.sprite.Sprite):
    
    def __init__(self, pos, size, direction):
        super(Fish, self).__init__()
        self.state = 1 # swimming
        self.index = 8
        self.size = size
        self.direction = direction

        self.image = pygame.Surface((80, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        fishtype = random.randint(1, 7)
        self.spritesheet = pygame.image.load("data/enemy" + str(fishtype)+ ".png").convert_alpha()
        self.blitImage(self.index)

        self.prevx = pos[0]
        self.prevy = pos[1]
        self.mask = pygame.mask.from_surface(self.image)
        self.animSpeed = 2
        self.animSpeedCounter = self.animSpeed

        self.bgViewPort = 0
        self.realPosX = pos[0]
        self.realPosY = pos[1]
        self.dieing = 10
        
    def blitImage(self, index):        
        y = int(index / 8)
        x = index % 8

        self.image = pygame.Surface((80, 50), pygame.SRCALPHA)
        self.image.blit(self.spritesheet, (0,0), (80 * x, 50 * y, 80, 50))
        self.image = pygame.transform.smoothscale(self.image, (80+self.size, 50+self.size))

        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        if self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)       


    def update(self, bgViewPort, spritelist):
        if random.randint(0, 20) == 1:
            rect = self.image.get_rect(center=(self.realPosX, self.realPosY))

            if self.direction < 0:
                newBubble = Bubble(rect.topleft)
            else:
                newBubble = Bubble(rect.topright)

            spritelist.add(newBubble)


        if self.animSpeedCounter <= 0:
            self.index += 1

            if self.index > 15:
                self.index = 8

            self.blitImage(self.index)
            self.animSpeedCounter = self.animSpeed

        self.animSpeedCounter -= 1


        #fishpos = self.rect.center
        # move fish
        fishx = self.realPosX + (characterMovementAmount+2)
        amplitude = 1
        newx = self.realPosX
        newy = self.realPosY
        newy += int(2* math.sin(self.realPosX/5) * (math.pi*amplitude))
        newx += (characterMovementAmount+2) * (self.direction)

        if newx < -50 or newx > (WIDTH + 50):
            self.direction *= -1
       
        self.realPosX = newx
        self.realPosY = newy
        self.rect = self.image.get_rect(center=(newx,newy - bgViewPort))
   
    def getSize(self):
        return self.size

bg = pygame.image.load("data/bg.png")
OCEANWIDTH = bg.get_width()
OCEANDEPTH = bg.get_height()

# counters
loop = 1
bgViewPort = 0
speedCounter = 0
hungerMeter = 100
health = 5

pygame.key.set_repeat(10)

spawnedFish = []

spawnTimer = 20

player = Player((cX, cY))

all_sprites = pygame.sprite.Group()
bubble_list = pygame.sprite.Group()
playersprite = pygame.sprite.Group()
playersprite.add(player)

gameState = 0
gameEndCount = 0

while loop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = 0
            continue

        if event.type == pygame.KEYDOWN and gameState == 0:
            if event.key == K_ESCAPE:
                loop = 0
                continue

            if event.key == K_SPACE:
                gameState = 1
                # counters
                bgViewPort = 0
                speedCounter = 0
                hungerMeter = 100
                health = 5
                pygame.key.set_repeat(10)
                spawnedFish = []
                
                spawnTimer = 20
                player = Player((cX, cY))
                all_sprites = pygame.sprite.Group()
                playersprite = pygame.sprite.Group()
                bubble_list = pygame.sprite.Group()
                playersprite.add(player)

                newSeaweed = Seaweed((100,OCEANDEPTH-64))
                bubble_list.add(newSeaweed)
                newSeaweed = Seaweed((75,OCEANDEPTH-64))
                bubble_list.add(newSeaweed)
                newSeaweed = Seaweed((50,OCEANDEPTH-0))
                bubble_list.add(newSeaweed)
                newSeaweed = Seaweed((125,OCEANDEPTH-20))
                bubble_list.add(newSeaweed)
                newSeaweed = Seaweed((150,OCEANDEPTH-10))
                bubble_list.add(newSeaweed)


    if gameState == 0: # start screen
        # spawn some fishies
        spawnTimer -= 1
        if spawnTimer <= 0:
            spawnTimer = 120

            direction = random.randint(0,1)
            if direction == 1:
                newFish = Fish((WIDTH + 50, random.randint(50, HEIGHT-50)), random.randint(0,4)*10, -1)
            else:
                newFish = Fish((-50, random.randint(50, HEIGHT-50)), random.randint(0,4)*10, 1)

            all_sprites.add(newFish)

    if gameState == 1: # playing game
        keys_down = pygame.key.get_pressed()
        if keys_down[K_DOWN]:
            if cY > HEIGHT - 100 and bgViewPort < OCEANDEPTH - HEIGHT:
                bgViewPort += bgMovementAmount
                print(bgViewPort)
            else:
                if cY < HEIGHT - 20:
                    cY += characterMovementAmount


        if keys_down[K_UP]:
            if cY < 100:
                if bgViewPort > 0:
                    bgViewPort -= bgMovementAmount
            else:
                cY -= characterMovementAmount

        if keys_down[K_LEFT]:
            cX -= characterMovementAmount
        if keys_down[K_RIGHT]:
            cX += characterMovementAmount


    if gameState == 1:
        if hungerMeter < 0:
            print("losing health - hungry!")
            health -= 1

        if health <= 0:
            pygame.mixer.Sound.play(losesound)
            gameState = 3
            gameEndCount = 0

        if player.size >= 50:
            gameState = 2
            gameEndCount = 0
            pygame.mixer.Sound.play(winsound)



        if speedCounter > fishSpeed:
            speedCounter = 0
            all_sprites.update(bgViewPort, bubble_list)
            playersprite.update()

        speedCounter += 1

        UP, DOWN, LEFT, RIGHT = 0, 0, 0, 0

        hungerMeter -= hungerSpeed

        spawnTimer -= 1

        if spawnTimer <= 0:
            spawnTimer = 120

            direction = random.randint(0,1)
            if direction == 1:
                newFish = Fish((WIDTH + 50, random.randint(100, OCEANDEPTH)), random.randint(0,4)*10, -1)
            else:
                newFish = Fish((-50, random.randint(100, OCEANDEPTH-100)), random.randint(0,4)*10, 1)

            all_sprites.add(newFish)

        # check for collision
        collidedFish = pygame.sprite.spritecollide(player, all_sprites, False, pygame.sprite.collide_mask)
            
        if len(collidedFish) > 0:
            for fish in collidedFish:
                print("Collision: " + str(fish.getSize()) + str(player.getSize()))
                
                if player.getSize() >= fish.getSize():
                    player.eating()
                    pygame.mixer.Sound.play(eatsound)
                    hungerMeter += 5
                    player.grow()
                    all_sprites.remove(fish)
                else:
                    pygame.mixer.Sound.play(damagesound)
                    health -= 1
                    (cX, cY) = player.damage(fish)

        player.updatePlayer((cX, cY))
        bubble_list.update(bgViewPort)

        # render screen
        screen.fill((0,0,0))
        screen.blit(bg, (0, 0), area = (0, bgViewPort,WIDTH,HEIGHT))

        bubble_list.draw(screen)
        all_sprites.draw(screen)
        playersprite.draw(screen)

        # hunger
        screen.fill((100, 0, 0), (10,10, 100, 20))
        screen.fill((0, 255, 0), (10,10, int(hungerMeter), 20))

        # foodchain
        screen.fill((255, 209, 94), (200,10, 100, 20))
        screen.fill((0, 0, 255), (200,10, int(player.size)*2, 20))

        # health
        for x in range(health):
            #pygame.draw.circle(screen, (250, 0, 0), (WIDTH - (5 * 20) + (x * 20),20), 10)
            screen.blit(heart, (WIDTH - 20 - (5 * 20) + (x * 20),20) )


    if gameState == 0: # menu
        screen.blit(startScreen, (0,0))

        if speedCounter > fishSpeed:
            speedCounter = 0
            all_sprites.update(0, bubble_list)

        speedCounter += 1

        bubble_list.update(0)

        bubble_list.draw(screen)
        all_sprites.draw(screen)

    if gameState == 2: # end of game - Win
        screen.blit(winScreen, (0,0))

    if gameState == 3: # end of game - Lose
        screen.blit(loseScreen, (0,0))

    if gameState == 2 or gameState == 3:
        gameEndCount += 1
        if gameEndCount > 120:
            gameState = 0

            all_sprites = pygame.sprite.Group()
            playersprite = pygame.sprite.Group()
            bubble_list = pygame.sprite.Group()

            newSeaweed = Seaweed((100,HEIGHT-64))
            bubble_list.add(newSeaweed)
            newSeaweed = Seaweed((75,HEIGHT-64))
            bubble_list.add(newSeaweed)
            newSeaweed = Seaweed((50,HEIGHT-0))
            bubble_list.add(newSeaweed)
            newSeaweed = Seaweed((125,HEIGHT-20))
            bubble_list.add(newSeaweed)
            newSeaweed = Seaweed((150,HEIGHT-10))
            bubble_list.add(newSeaweed)


    clock.tick(60)
    pygame.display.update()

pygame.quit()