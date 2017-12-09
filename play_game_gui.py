import pygame as pyg
import sys
#import pong_continuous

# Frame per second that we set up and use in the GUI
FPS = 30
# Color setting
WHITE = [255, 255, 255]
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Viedo output setting
ZERO = 0
VIEW_HEIGHT = 480
VIEW_WIDTH = 640
MIDDLE = (int(VIEW_WIDTH/2), int(VIEW_HEIGHT/2))
WHOLE_WINDOW = ((ZERO, ZERO), (VIEW_WIDTH, VIEW_HEIGHT))

# Detail of the paddle
PAD_THICK = 5
# Detail of the ping-pong table
COURT_LINE = 2
RADIUS = 5
# init the screen
pyg.init()
SCREEN = pyg.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
pyg.display.set_caption("Single Player Pong")

def showPaddle(paddle_area, position):
    """ Function used to draw the paddle """

    paddle_area.x, paddle_area.y = position
    pyg.draw.rect(SCREEN, BLACK, paddle_area)


def showTable():
    """ Function used to draw the game table """
    # Fill in the background
    SCREEN.fill(WHITE)
    # Draw the boundary line
    pyg.draw.rect(SCREEN, BLUE, WHOLE_WINDOW, COURT_LINE)
    pyg.display.update()


def showBall(postion):
    """ Function used to draw the ball on table """
    pyg.draw.circle(SCREEN, RED, postion, RADIUS)
    pyg.display.update()


def getUpdateValue(state):
    # Unpackin the state tuple
    ball_x, ball_y, velocity_x, velocity_y, right_pad_y, left_pad_y = state
    new_ball_x = (VIEW_WIDTH - RADIUS - 2*PAD_THICK - COURT_LINE) * ball_x
    new_ball_y = (VIEW_HEIGHT - RADIUS - COURT_LINE) * ball_y
    new_right_pad = right_pad_y * VIEW_HEIGHT
    new_left_pad = left_pad_y * VIEW_HEIGHT

    return new_ball_x, new_ball_y, new_right_pad, new_left_pad


def displayState(state, ball, l_pad, r_pad, round):
    ball_x, ball_y, right_pad, left_pad = getUpdateValue(state)
    # Start re-drawing the court
    showTable()
    showPaddle(l_pad, (l_pad.x, left_pad))
    showPaddle(r_pad, (r_pad.x, right_pad))
    showBall((ball_x, ball_y))


clock = pyg.time.clock()

right_pad_x = WINDOWWIDTH - BOUNDTHICKNESS - LINETHICKNESS
right_pad_y = (WINDOWHEIGHT - RPADDLESIZE) / 2
LPaddlePosition_X = BOUNDTHICKNESS

LPaddlePosition_Y = (WINDOWHEIGHT - LPADDLESIZE) / 2
