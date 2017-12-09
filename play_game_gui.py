import pygame as pyg
import sys
import pong_continuous as pc
# Parameters used for training
TRAIN_TRAIL = 1000000
Q_Dict = dict()
Action_Dict = dict()

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
L_PAD_LEN = VIEW_HEIGHT * pc.LP_HEIGHT
R_PAD_LEN = VIEW_HEIGHT * pc.RP_HEIGHT

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


def displayState(state, l_pad, r_pad, round_count):
    ball_x, ball_y, right_pad, left_pad = getUpdateValue(state)
    # Start re-drawing the court
    showTable()
    showPaddle(l_pad, (l_pad.x, left_pad))
    showPaddle(r_pad, (r_pad.x, right_pad))
    showBall((ball_x, ball_y))
    # Display game status
    text = pyg.font.Font('None', 15)
    surface = text.render("Round #: {}", format(round_count), BLACK)
    textbox = surface.get_rect()
    textbox.topleft = (VIEW_WIDTH / 2, 28)
    SCREEN.blit(surface, textbox)


clock = pyg.time.Clock()
# Right paddle sizing
right_pad_x = VIEW_WIDTH - COURT_LINE - PAD_THICK
right_pad_y = (VIEW_HEIGHT - R_PAD_LEN) / 2
# Start getting drawing unit for the right paddle
r_pad = pyg.Rect(right_pad_x, right_pad_y, PAD_THICK, R_PAD_LEN)

# Left paddle sizing
left_pad_x = COURT_LINE
left_pad_y = (VIEW_HEIGHT - L_PAD_LEN) / 2
l_pad = pyg.Rect(left_pad_x, left_pad_y, PAD_THICK, L_PAD_LEN)

# Start Training
print("Start the training session, current set training trails: ", TRAIN_TRAIL, " times")
pc.simulated_training(TRAIN_TRAIL, Q_Dict, Action_Dict)

# Set up the initial state after the training to start testing
print("The training session has been completed.")
round_count = 1
init_state = (0.5, 0.5, 0.03, 0.01, 0.5 - (pc.RP_HEIGHT / 2), 0.5 - (pc.LP_HEIGHT / 2))
discrete_init = pc.to_discrete(init_state)

displayState(init_state, l_pad, r_pad, round_count)

right_action = max(Q_Dict[discrete_init], key=Q_Dict[discrete_init].get)
left_action = pc.l_paddle_action(init_state)
action = (right_action, left_action)
state = pc.action_state(init_state, action)
prev_state = init_state

flag = True

# Start looping this game
while flag:
    # Make sure that the user doesn't want to quit
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            pyg.quit()
            sys.exit(status=None)

    # Update the display
    displayState(state, l_pad, r_pad, round_count)

    bounce_count = 0

    state, prev_state, right_action = pc.update_pos(prev_state, right_action, state, Q_Dict, Action_Dict)

    # Check if the AI lose the game
    if right_action == "END":
        prev_state = init_state
        displayState(prev_state, l_pad, r_pad, round_count)
        round_count += 1
        right_action = max(Q_Dict[discrete_init], key=Q_Dict[discrete_init].get)
        left_action = pc.l_paddle_action(prev_state)
        action = (right_action, left_action)
        curr_state = pc.action_state(prev_state, action)
        bounce_count = 0
    if pc.is_bounced(prev_state, curr_state) and curr_state[3] < 0:
        bounce_count += 1
        print("Paddle bounces the ball %s", format(bounce_count), " times")

    pyg.display.update()
    clock.tick(FPS)
