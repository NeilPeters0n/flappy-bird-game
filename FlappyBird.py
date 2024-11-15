import pygame
import sys
from pygame.locals import *
import random

pygame.init()
clock= pygame.time.Clock ()
fps= 60

#window
SCREEN_WIDTH = 864
SCREEN_HEIGHT = 936
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

#define font
font= pygame.font.SysFont("Bauhaus 93", 85)

#define colors
white= (255, 255, 255)

#define game variables
ground_scroll= 0
scroll_speed= 4
flying = False
game_over= False
pipe_gap= 150
pipefrequency= 1500
lastpipe= pygame.time.get_ticks() - pipefrequency
score= 0 
pass_pipe= False

running = True

#backgrounds
bg = pygame.image.load("images/bg.png")
ground_img = pygame.image.load("images/ground.png")
button_img= pygame.image.load("images/restart.png")

def draw_text(text, font, text_col, x, y):
    img= font.render(text, True, text_col)
    screen.blit(img, (x, y))

#reset the game
def reset_game():
    pipegroup.empty()
    flappy.rect.x= 100
    flappy.rect.y= int(SCREEN_HEIGHT / 2)
    flappy.vel= 0
    score= 0
    return score
    

#bird
class bird (pygame.sprite.Sprite):
    def __init__ (self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images= []
        self.index= 0
        self.counter= 0
        for num in range(1, 4):
            img=pygame.image.load(f"images/bird{num}.png")
            self.images.append(img)
        self.image= self.images [self.index]
        self.rect= self.image.get_rect ()
        self.rect.center= [x, y]
        self.vel= 0
        self.clicked= False
        
        
    def update(self):
        
        #gravity
        if flying == True:
            self.vel += .425
            if self.vel > 9:
                self.vel= 9
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
        if game_over == False: 
            #jump
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] == True and self.clicked == False:
                self.clicked= True
                self.vel = -9
            if keys[pygame.K_SPACE] == False:
                self.clicked= False
                
            
            #handle the animation
            if flying == True:
                self.counter += 1
                flap_cooldown=5
                
                if self.counter > flap_cooldown:
                    self.counter= 0
                    self.index += 1
                    if self.index >= len(self.images):
                        self.index= 0
                self.image= self.images[self.index]
            
            #rotation
            self.image= pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image= pygame.transform.rotate(self.images[self.index], -45)

class pipe(pygame.sprite.Sprite):
    def __init__ (self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image= pygame.image.load("images/pipe.png")
        self.rect= self.image.get_rect()
        #position 1 is form the top, -1 from the bottom
        if position == 1:
            self.image= pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft= [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft= [x, y + int(pipe_gap / 2)]
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
        
class Button():
    def __init__(self, x, y, image):
        self.image= image
        self.rect= self.image.get_rect()
        self.rect.topleft= (x, y)
    def draw(self):
        action= False
        #get mouse position
        pos= pygame.mouse.get_pos()
        
        #check if mouse is over the button and pressed
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[1] or pygame.mouse.get_pressed()[0] == 1:
                action = True
                
        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action
        



birdgroup= pygame.sprite.Group ()
pipegroup= pygame.sprite.Group ()

flappy= bird(100, int(SCREEN_HEIGHT / 2))

birdgroup.add(flappy)

#create restart button instance
button= Button(SCREEN_WIDTH // 2 -50, SCREEN_HEIGHT // 2 -100, button_img)


#main loop
while running:
    clock.tick(fps)
    
    #background
    screen.blit(bg, (0,0))
    
    birdgroup.draw(screen)
    birdgroup.update()
    pipegroup.draw(screen)
    
    #check the score
    if len(pipegroup) > 0:
        if birdgroup.sprites()[0].rect.left > pipegroup.sprites()[0].rect.left\
            and birdgroup.sprites()[0].rect.right < pipegroup.sprites()[0].rect.right\
            and pass_pipe == False:
                pass_pipe = True
        if pass_pipe == True:
            if birdgroup.sprites()[0].rect.left > pipegroup.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, white, int(SCREEN_WIDTH / 2), 30)
    
    if flying == True:
        screen.blit(ground_img, (ground_scroll,768))
        
    else:
        ground_scroll= 0
        screen.blit(ground_img, (ground_scroll,768))
    
    if pygame.sprite.groupcollide(birdgroup, pipegroup, False, False) or flappy.rect.top< 0:
        game_over= True
        
        
    #check if bird has hit the ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False
        
    if game_over == False:
        
        #generate pipes
        time_now = pygame.time.get_ticks()
        if time_now - lastpipe > pipefrequency and flying == True:
            pipeheight= random.randint(-175, 100)
            btm_pipe= pipe (SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipeheight, -1)
            top_pipe= pipe (SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipeheight, 1)
            pipegroup.add(btm_pipe)
            pipegroup.add(top_pipe)
            lastpipe= time_now
        
        #ground and scroll
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll=0
        pipegroup.update()
    
    #check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score= reset_game()
            
    #exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and flying == False and game_over == False:
            if event.key == pygame.K_SPACE:
                flying= True
    pygame.display.update()

pygame.quit()