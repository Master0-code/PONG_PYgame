""" Pong, Local 2 player game. made with Python and pygame
    Controls : Player 1 ; W to move the slider UP and S to move the slider DOWN
    Controls : Player 2 ; /\ to move the slider UP and \/ to move the slider DOWN
    Controls : Mouse to pause or start the game after scoring """

import pygame
import math
import array
import random
import sys

#--- starting the PYGAME ---
#pygame.inti() starts up all of pygame's internal subsystems
#(Display, sound, fonts, etc). You must call this before using any of them.
pygame.init()

#--- constants ---
width, height = 640, 400
paddle_width, paddle_height = 12, 80
paddle_speed = 6
ball_size = 12
win_score = 7
fps = 60

#colors
black = (0,0,0)
white = (244,241,234)
p1_color = (82,227,194)
p2_color = (227,82,105)
line_color = (42,47,51)

# --- window setup--- (the thing for sizing the game window)

screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("PONG - Local - 2 Players")

# thing to lock the game to a fixed FRAME RATE later.
clock = pygame.time.Clock()

score_font = pygame.font.SysFont("couriernew", 48, bold=True)
msg_font = pygame.font.SysFont("couriernew", 28, bold=True)
hint_font = pygame.font.SysFont("couriernew", 16, bold=False)

# Sound generation using math lib and array lib

def make_beep(frequency=440, duration_ms=80, volume=0.4):
    sample_rate = 44100 # samples per seconds (CD QUALITY, IDK about the quality)
    n_samples = int(sample_rate * duration_ms / 1000)

    # 'h' means 16 bit integers - the format pygame's mixer expects. for some reason. but yeah.
    buf = array.array("h")

    for i in range(n_samples):
        t = i / sample_rate  # t is for time, current time in seconds.
        # A sine wave oscillates between -1 to 1. we scale it up
        # range of a 16 bit int (-3k to 3k something) and its apply volume somehow.
        sample = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
        buf.append(sample) #left channel
        buf.append(sample) #right channel. 
        #this something same like stereo, same vaulue is mono sound

    return pygame.mixer.Sound(buffer=buf)
    






#two different pitches so you can tell paddle hit from wall bounces/scores.
#here
paddle_hit_sound = make_beep(frequency=520, duration_ms=60)
score_sound = make_beep(frequency=200, duration_ms=200)

# game state
# now values which change while playing.
paddle1_y = height / 2 - paddle_height / 2
paddle2_y = height / 2 - paddle_height / 2

ball_x = width / 2
ball_y = height / 2
ball_speed_x = 4
ball_speed_y = 3

score1 = 0
score2 = 0

paused = True #click to start
game_over = False
win_message = ""


def reset_ball(direction):
    #telling the game to set the ball where it need to be
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    ball_x = width / 2
    ball_y = height / 2
    ball_speed_x = 4 * direction
    ball_speed_y = random.choice([-1, 1]) * 3


def reset_game():
    #everything back to reset. scores, paddle positions. game unpaused ready.
    global score1, score2, paddle1_y, paddle2_y, game_over, paused 
    score1 = 0
    score2 = 0
    paddle1_y = height / 2 - paddle_height / 2
    paddle2_y = height / 2 - paddle_height / 2
    reset_ball(random.choice([-1, 1]))
    game_over = False
    paused = True 
        # wait for a click before the next game starts moving

# main game loop things
# everything below runs once per frame, forever, until the window is closed (game is closed)
running = True 
while running:
    # 1 : handle events like input
    # pygame.event.get() returns a list of everything that happened since
    # last frame: key presses, mouse clicks, window closed, etc.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                reset_game()
            else:
                paused = not paused # this makes it use mouse for start the game, start new game after ending, pause and unpause. 
        """ if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                reset_game()
            else:
                paused = False #click to resume, because of this game only starts, not toggle between toggle off or on"""
        #if added below is used to resize the window below. you dont want everyting small on your 60 inch monitor. 
        if event.type == pygame.VIDEORESIZE:
            width = event.w
            height = event.h
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            ball_x = width / 2 #this two lines are added because if you resize the window, ball will not be centered. 
            ball_y = height / 2 
            #this below centers the bars
            paddle1_y = height / 2 - paddle_height / 2
            paddle2_y = height / 2 - paddle_height / 2

    # 2 : read the held down keys
    #unlike the single "keydown" events this tells us which keys are held. (EX : hold E)
    # Right now, every frame needed for smooth continuous paddle movement
    
    
    keys = pygame.key.get_pressed()
    
    if not paused and not game_over:
        if keys[pygame.K_w]:
            paddle1_y -= paddle_speed
        if keys[pygame.K_s]:
            paddle1_y += paddle_speed
        if keys[pygame.K_UP]:
            paddle2_y -= paddle_speed
        if keys[pygame.K_DOWN]:
            paddle2_y += paddle_speed
        
        #clamp the sliders or paddles to stay fully on screen
        paddle1_y = max(0, min(height - paddle_height, paddle1_y))
        paddle2_y = max(0, min(height - paddle_height, paddle2_y))

        # 3 move the ball know the ball

        ball_x += ball_speed_x
        ball_y += ball_speed_y

        if ball_y <=0 or ball_y + ball_size >= height:
            ball_speed_y *= -1
        
        # 4 collisions. hit it to move it
        # player 1 paddle (on left side) check the ball is at the right X
        # positions AND overlapping the paddle's Y-range.

        if (
            ball_x <= paddle_width
            and ball_y + ball_size >= paddle1_y
            and ball_y <= paddle1_y + paddle_height
        ):
            ball_speed_x *= -1.05
            ball_x = paddle_width
            paddle_hit_sound.play()

        #player 2 paddle setting so he/she dont blame the game
        if ( 
            ball_x + ball_size >= width - paddle_width
            and ball_y + ball_size >= paddle2_y
            and ball_y <= paddle2_y + paddle_height
        ):
            ball_speed_x *= -1.05
            ball_x = width - paddle_width - ball_size
            paddle_hit_sound.play()

        if ball_x < 0:
            score2 += 1
            score_sound.play()
            if score2 >= win_score:
                game_over = True
                win_message = "Player 2 WINS" #player 1 sucks
            else:
                reset_ball(-1)
                paused = True #pause after each point very important

        if ball_x > width:
            score1 += 1
            score_sound.play()
            if score1 >= win_score:
                game_over = True
                win_message = "Player 1 WINS"
            else: 
                reset_ball(1)
                paused = True
    #6. draws everying black        
    screen.fill(black)
    #center dashed line. to part player 1 and 2
    for y in range(0, height, 20):
         pygame.draw.rect(screen, line_color,(width // 2 - 1, y, 2, 10))

    # paddles and the balls drawing
    pygame.draw.rect(screen, p1_color, (0, paddle1_y, paddle_width,paddle_height))
    pygame.draw.rect(screen,p2_color, (width - paddle_width, paddle2_y, paddle_width, paddle_height))
    pygame.draw.rect(screen,white,(ball_x,ball_y,ball_size,ball_size))

    

    #scoreboard text
    score_text = score_font.render(f"{score1}   {score2}", True, white)
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, 20))

    hint1 = hint_font.render("W / S", True, p1_color)
    hint2 = hint_font.render("UP / DOWN", True, p2_color)
    screen.blit(hint1, (20, height - 30))
    screen.blit(hint2, (width - hint2.get_width() - 20, height - 30))

    #pause or win overlay MSG
    if game_over:

        msg = msg_font.render(win_message, True, white)
        sub = hint_font.render("Click to play again", True, white)
        screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 30))
        screen.blit(sub, (width // 2 - sub.get_width() // 2, height // 2 + 20))
    elif paused:
         msg = msg_font.render("Click to play" , True, white)
         screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 15))



# 7 :   flip the display
# everyting drawn above happens on a hidden "back buffer"
# flip() swaps it to the screen all at once. Avoiding the flicker.
# we use pygame.display.flip()
    pygame.display.flip()

#8 :    Locking the frame rate

#pauses just long enought to keep the loop running at -60 FPS
#no matter how fast the computer is.
    clock.tick(fps)

pygame.quit()
sys.exit()