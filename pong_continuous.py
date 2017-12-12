import math
import random

# state = (ball_x, ball_y, velocity_x, velocity_y, l_paddle_y, r_paddle_y)
# action = ([l_up, l_down, l_stay], [r_up, r_down, r_stay])

HEIGHT = 12
WIDTH = 12
LP_HEIGHT = 1
LP_STEP = 0
# Since there is jut a single paddle, we initialize this one as if it is a wall
RP_HEIGHT = 0.2
RP_STEP = 0.04
LEFT_BOUND = 0
RIGHT_BOUND = 1
DIS_V_X = 1
DIS_V_Y = 1
V_Y_UP_BOUND = 0.015

# helper function to detect bounce
def is_bounced(prev_state, curr_state):
    # check if the ball is already bounced back
    not_bounced = True
    if prev_state[2] < 0:
        not_bounced = False
    # check if it will be bounced
    if not_bounced:
        if curr_state[2] < 0:
            return True
    else:
        if curr_state[2] > 0:
            return True
    return False



# declare reward state
def reward_state(prev_state, curr_state):
    # get curr state info
    ball_x, ball_y, velocity_x, velocity_y, l_paddle_y, r_paddle_y = curr_state
    # initialize reward value
    reward = 0
    # if the ball is already bounced, reward = 1
    if is_bounced(prev_state, curr_state) and velocity_x < 0:
        reward = 1
    else:
        # else we lose but there are two cases
        # if ball x position is already out of bound
        if ball_x > 1:
            # and check if the ball y position is in the fit of paddle
            if r_paddle_y > ball_y or ball_y > r_paddle_y + RP_HEIGHT:
                # this means the ball is outside our range
                reward = -1
        # for the left paddle, this is the same condition
        if ball_x < 0:
            if l_paddle_y > ball_y or ball_y > l_paddle_y + LP_HEIGHT:
                reward = 0

    return reward


# declare action state
def action_state(curr_state, action):
    # get curr state info
    ball_x, ball_y, velocity_x, velocity_y, l_paddle_y, r_paddle_y = curr_state
    # get action command
    l_action, r_action = action

    # update left paddle position
    if l_action == 'Up':
        l_paddle_y_new = max(0, l_paddle_y - LP_STEP)
    elif l_action == 'Down':
        l_paddle_y_new = min(1 - LP_HEIGHT, l_paddle_y + LP_STEP)
    elif l_action == 'Nothing':
        l_paddle_y_new = l_paddle_y
    else:
        l_paddle_y_new = 0

    # update right paddle position
    if r_action == 'Up':
        r_paddle_y_new = max(0, r_paddle_y - RP_STEP)
    elif r_action == 'Down':
        r_paddle_y_new = min(1 - RP_HEIGHT, r_paddle_y + RP_STEP)
    elif r_action == 'Nothing':
        r_paddle_y_new = r_paddle_y
    else:
        r_paddle_y_new = 0
    # update new position
    ball_x_new = ball_x + velocity_x
    ball_y_new = ball_y + velocity_y

    # we need to discretize the ball position in order to prevent out-of-bound situation
    dis_ball_x = math.floor(ball_x_new * WIDTH) / WIDTH

    # lets bounce now!
    # reverse the direction and velocity if touch the bound
    if ball_y_new > 1:
        ball_y_new = 2 - ball_y_new
        velocity_y = -velocity_y
    if ball_y_new < 0:
        ball_y_new = -ball_y_new
        velocity_y = -velocity_y
    # check x position with discretized value
    if dis_ball_x > RIGHT_BOUND:
        U = random.uniform(-0.015, 0.015)
        V = random.uniform(-0.03, 0.03)
        if r_paddle_y_new <= ball_y_new and ball_y_new <= (r_paddle_y_new + RP_HEIGHT):
            ball_x_new = 2 * RIGHT_BOUND - ball_x_new
            # make sure x speed won't exceed 0.03
            velocity_x = min(-0.03, -velocity_x + U)
            velocity_y += V
    # for the left paddle
    if dis_ball_x < LEFT_BOUND:
        if l_paddle_y_new <= ball_y_new and ball_y_new <= (l_paddle_y_new + LP_HEIGHT):
            ball_x_new = -ball_x_new
            velocity_x = max(0.03, -velocity_x)
            velocity_y = velocity_y

    return (ball_x_new, ball_y_new, velocity_x, velocity_y, l_paddle_y_new, r_paddle_y_new)


def terminate_state(state):
    """terminate_state.
    Function used to chekc if the state is terminated
    """
    # Upacking each element from the state tuple
    ball_x, ball_y, velocity_x, velocity_y, l_paddle_y, r_paddle_y = state

    # For the first player:
    #   if the ball has pass the right bound and it is going right
    if ball_x > RIGHT_BOUND and velocity_x > 0:
        return True
    if ball_x < LEFT_BOUND and velocity_x < 0:
        return True
    return False


# we need to convert the continuous game state into discrete
def to_discrete(curr_state):
    ball_x, ball_y, velocity_x, velocity_y, l_paddle_y, r_paddle_y = curr_state
    ball_x = math.floor(WIDTH * ball_x) /WIDTH
    ball_y = math.floor(HEIGHT * ball_y) /HEIGHT
    # set the speed to discretized speed
    vx_new = DIS_V_X
    vy_new = DIS_V_Y
    # discretize ball speed
    # change x speed direction
    if velocity_x < 0:
        vx_new = -DIS_V_X
    # change y speed direction to 0 if in bound
    if abs(velocity_y) < V_Y_UP_BOUND:
        vy_new = 0
    elif velocity_y < 0:
        vy_new = -DIS_V_Y
    # discretize paddle
    r_paddle_y_new = math.floor(r_paddle_y*HEIGHT/(1-RP_HEIGHT)) * ((1-RP_HEIGHT)/HEIGHT)
    # for part 1
    if LP_HEIGHT == 1:
        l_paddle_y_new = l_paddle_y
    else:
        l_paddle_y_new = math.floor(l_paddle_y*HEIGHT/(1-LP_HEIGHT)) / HEIGHT

    return (ball_x, ball_y, vx_new, vy_new, l_paddle_y_new, r_paddle_y_new)


def random_speed():
    offset_x = random.uniform(-0.015, 0.015)
    offset_y = random.uniform(-0.03, 0.03)
    if offset_x > 0:
        u = 0.03 + offset_x
    else:
        u = -0.03 + offset_x

    return u, offset_y


def Qlearning(QLearn_Dict, action_counter, state, prev_state, prev_action):
    Q_state = to_discrete(state)
    Q_prev_state = to_discrete(prev_state)

    if terminate_state(Q_prev_state):
        Q_prev_state = 'End State'
        QLearn_Dict[Q_prev_state] = -1
        best_action = 'End'
    else:
        action_counter[Q_prev_state][prev_action] += 1
        c = 25
        alpha = c / (c + action_counter[Q_prev_state][prev_action])
        gamma = 0.95

        if Q_state not in QLearn_Dict:
            QLearn_Dict[Q_state] = {'Up': 0, 'Nothing': 0, 'Down': 0}
            action_counter[Q_state] = {'Up': 0, 'Nothing': 0, 'Down': 0}

        Q_prev_val = QLearn_Dict[Q_prev_state][prev_action]
        QLearn_Dict[Q_prev_state][prev_action] = (1 - alpha) * Q_prev_val + alpha * (
            reward_state(Q_prev_state, Q_state) + gamma * getMaxUtil(QLearn_Dict, Q_state))
        best_action = exploration(QLearn_Dict[Q_state], action_counter[Q_state])
    return best_action


# Exploration function uses the modified strategy discussed in the lecture slides
def exploration(Q_action_set, counter_set):
    threshold = 50
    action = min(counter_set, key=counter_set.get)
    if counter_set[action] > threshold:
        return max(Q_action_set, key=Q_action_set.get)
    else:
        return min(counter_set, key=counter_set.get)


def getMaxUtil(QLearn_Dict, Q_state):
    if terminate_state(Q_state):
        return -1
    Utilval = (QLearn_Dict[Q_state]['Up'], QLearn_Dict[Q_state]['Nothing'], QLearn_Dict[Q_state]['Down'])
    return max(Utilval)


def simulated_training(trainsession, Qlearn_Dict, action_counter):
    ### Initialize game
    u, v = random_speed()
    ini_state = (0.5, 0.5, u, v, 0.5 - 0.5 * LP_HEIGHT, 0.5 - 0.5 * RP_HEIGHT)
    # print(ini_state)
    Q_ini_state = to_discrete(ini_state)
    # print(Q_ini_state)

    prev_state = ini_state
    Qlearn_Dict[Q_ini_state] = {'Up': 0, 'Nothing': 0, 'Down': 0}
    action_counter[Q_ini_state] = {'Up': 0, 'Nothing': 0, 'Down': 0}

    R_action = 'Up'
    L_action = 'Nothing'
    action = (L_action, R_action)
    state = action_state(prev_state, action)

    sum_bounce = 0
    print('Initiated')
    for i in range(trainsession):
        averageBounce = 0
        while True:
            R_action = Qlearning(Qlearn_Dict, action_counter, state, prev_state, R_action)
            if R_action == 'End':
                sum_bounce += averageBounce
                break

            prev_state = state
            action = (L_action, R_action)
            state = action_state(state, action)

            if is_bounced(prev_state, state) and state[2] < 0:
                averageBounce += 1

        #print('Round %d: ' % i)
        #print(averageBounce)
        #print('\n')
        if (i+1) % 10000 == 0:

            print("\nAverage bounces (per 10000) after %d trails: " % i, sum_bounce/10000)
            sum_bounce = 0

        u, v = random_speed()
        ini_state = (0.5, 0.5, u, v, 0.5 - 0.5 * LP_HEIGHT, 0.5 - 0.5 * RP_HEIGHT)
        Q_ini_state = to_discrete(ini_state)
        if Q_ini_state not in Qlearn_Dict:
            Qlearn_Dict[Q_ini_state] = {'Up': 0, 'Nothing': 0, 'Down': 0}
            action_counter[Q_ini_state] = {'Up': 0, 'Nothing': 0, 'Down': 0}

        prev_state = ini_state
        R_action = exploration(Qlearn_Dict[Q_ini_state], action_counter[Q_ini_state])
        L_action = l_paddle_action(prev_state)
        action = (L_action, R_action)
        state = action_state(prev_state, action)

    return 'Done'

# define the movement of left paddle
def l_paddle_action(curr_state):
    action = 'Up'
    return action


# return position to the game window for update
def update_pos(prev_state, prev_action, state, Qlearning_dict, action_counter):
    r_action = Qlearning(Qlearning_dict, action_counter, state, prev_state, prev_action)
    if r_action == 'End':
        return 0, 0, 'End'
    new_action = (l_paddle_action(state), r_action)
    return (action_state(state, new_action), state, r_action)
