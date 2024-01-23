import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from time import time

WIDTH = 5000
HEIGHT = 5000

RIGHT = 0
DOWN = 1
LEFT = 2
UP = 3

ants = {}

initial_ants = {}
glider = {}
bridges = {}
double_bridge = {}
follow_bridge = {}
spiral = {}

universe = np.zeros((1, 1), dtype=np.int8) 
num_nonempty_cells = 0
frame = 0
min_xy_visited = [0, 0]
max_xy_visited = [0, 0]

loop_data = np.zeros((100,100))
bridge_data = np.zeros((100,100))
glider_data = np.zeros((100,100))

def moveAnt(ant):
    if ant[2] == RIGHT:
        ant[0] += 1
    elif ant[2] == DOWN:
        ant[1] += 1
    elif ant[2] == LEFT:
        ant[0] -= 1
    else:
        ant[1] -= 1

def moveAntReverse(ant):
    if ant[2] == RIGHT:
        ant[0] -= 1
    elif ant[2] == DOWN:
        ant[1] -= 1
    elif ant[2] == LEFT:
        ant[0] += 1
    else:
        ant[1] += 1

def turnAnt(ant, read_symbol):
    if read_symbol == 0:
        ant[2] = (ant[2] + 1) % 4
    else:
        ant[2] = (ant[2] - 1) % 4

def isAntEscaped(ant):
    return ant[0] < 0 or ant[1] < 0 or ant[0] >= WIDTH or ant[1] >= HEIGHT

def reverseStep():
    global num_nonempty_cells, frame

    frame -= 1

    paintCells = {}
    escaped_ant_ids = []
    for ant_id, ant in ants.items():
        if isAntEscaped(ant):
            escaped_ant_ids.append(ant_id)
            continue
        moveAntReverse(ant)
        turnAnt(ant, universe[ant[1], ant[0]])
        paintCells[(ant[0], ant[1])] = ant_id

    for x, y in paintCells:
        if universe[y, x] == 0:
            universe[y, x] = paintCells[x, y]
            num_nonempty_cells += 1
        else:
            universe[y, x] = 0
            num_nonempty_cells -= 1

    for ant_id in escaped_ant_ids:
        ants.pop(ant_id)  

def step():
    global num_nonempty_cells, frame

    frame += 1

    paintCells = {}
    escaped_ant_ids = []
    for ant_id, ant in ants.items():
        if isAntEscaped(ant):
            escaped_ant_ids.append(ant_id)
            continue
        paintCells[(ant[0], ant[1])] = ant_id
        turnAnt(ant, universe[ant[1], ant[0]])
        moveAnt(ant)

    for x, y in paintCells:
        if universe[y, x] == 0:
            universe[y, x] = paintCells[x, y]
            num_nonempty_cells += 1
        else:
            universe[y, x] = 0
            num_nonempty_cells -= 1

    for ant_id in escaped_ant_ids:
        ants.pop(ant_id)        

def isLoop():
    if num_nonempty_cells != 0:
        return False
    for id in ants:
        if ants[id][0] != initial_ants[id][0]:
            return False
        if ants[id][1] != initial_ants[id][1]:
            return False
        if ants[id][2] != initial_ants[id][2]:
            return False
    return True

MARGIN_OF_ERROR = 10
def isEscaping(ant):
    if ant[0] > min_xy_visited[0] - MARGIN_OF_ERROR and ant[0] < max_xy_visited[0] + MARGIN_OF_ERROR:
        return False
    if ant[1] > min_xy_visited[1] - MARGIN_OF_ERROR and ant[1] < max_xy_visited[1] + MARGIN_OF_ERROR:
        return False
    return True

GLIDER_CONFIRM = 10
def isGliderEscaping():
    if len(ants) < 2:
        return False
    if glider['iterations'] >= GLIDER_CONFIRM and isEscaping(ants[1]) and isEscaping(ants[2]):
        return True
    if frame % 10 != 0:
        return False
    
    ant1_direction = (ants[1][0] - glider['ant1x'], ants[1][1] - glider['ant1y'])
    ant2_direction = (ants[2][0] - glider['ant2x'], ants[2][1] - glider['ant2y'])
    if abs(ant1_direction[0]) == 1 and abs(ant1_direction[1]) == 1 and ant1_direction == ant2_direction:
        glider['iterations'] += 1
    else:
        glider['iterations'] = 0

    glider['ant1x'] = ants[1][0]
    glider['ant1y'] = ants[1][1]
    glider['ant2x'] = ants[2][0]
    glider['ant2y'] = ants[2][1]

    return False

BRIDGE_CONFIRM = 4
def isAllBridgeEscaping():
    if frame % 104 != 0:
        return False
    
    for id, ant in ants.items():
        if abs(ant[0] - bridges[id]['x']) == 2 and abs(ant[1] - bridges[id]['y']) == 2:
            bridges[id]['iterations'] += 1
        else:
            bridges[id]['iterations'] = 0

        bridges[id]['x'] = ant[0]
        bridges[id]['y'] = ant[1]

    if bridges[1]['iterations'] >= BRIDGE_CONFIRM and bridges[2]['iterations'] >= BRIDGE_CONFIRM and all([isEscaping(ant) for ant in ants.values()]):
        return True
    
    return False

DOUBLE_BRIDGE_CONFIRM = 4
def isDoubleBridgeEscaping():
    if len(ants) < 2:
        return False
    if double_bridge['iterations'] >= DOUBLE_BRIDGE_CONFIRM and isEscaping(ants[1]) and isEscaping(ants[2]):
        return True
    if frame % 102 != 0:
        return False
    
    ant1_direction = (abs(ants[1][0] - double_bridge['ant1x']), abs(ants[1][1] - double_bridge['ant1y']))
    ant2_direction = (abs(ants[2][0] - double_bridge['ant2x']), abs(ants[2][1] - double_bridge['ant2y']))
    if ant1_direction == ant2_direction and ((abs(ant1_direction[0]) == 3 and abs(ant1_direction[1]) == 5) or (abs(ant1_direction[0]) == 5 and abs(ant1_direction[1]) == 3)):
        double_bridge['iterations'] += 1
    else:
        double_bridge['iterations'] = 0
    
    double_bridge['ant1x'] = ants[1][0]
    double_bridge['ant1y'] = ants[1][1]
    double_bridge['ant2x'] = ants[2][0]
    double_bridge['ant2y'] = ants[2][1]

    return False

SPIRAL_CONFIRM = 80
SPIRAL_VARIANCE = 3
MIN_SPIRAL_RADIUS = 55
def isSpiral():
    if frame % 10 != 0:
        return False
    if len(ants) < 2:
        return False
    if spiral['iterations'] >= SPIRAL_CONFIRM and num_nonempty_cells / (abs(min_xy_visited[0] - max_xy_visited[0]) + abs(min_xy_visited[1] - max_xy_visited[1])) < 6:
        return True
    
    for id in ants:
        dist = abs(ants[id][0] - WIDTH/2) + abs(ants[id][1] - HEIGHT/2)
        if abs(dist - spiral['radius'][id]) > SPIRAL_VARIANCE: 
            spiral['radius'][id] = dist
            spiral['iterations'] = 0

    if spiral['radius'][1] > MIN_SPIRAL_RADIUS and spiral['radius'][2] > MIN_SPIRAL_RADIUS and np.sign(ants[1][0] - WIDTH/2) == -np.sign(ants[2][0] - WIDTH/2) and np.sign(ants[1][1] - HEIGHT/2) == -np.sign(ants[2][1] - HEIGHT/2):
        spiral['iterations'] += 1

    return False

FOLLOW_BRIDGE_CONFIRM = 4
def isFollowBridgeEscaping():
    if frame % 108 != 0:
        return False
    if len(ants) < 2:
        return False
    if bridges[1]['iterations'] >= BRIDGE_CONFIRM:
        follower_id = 2
    elif bridges[2]['iterations'] >= BRIDGE_CONFIRM:
        follower_id = 1
    else:
        return False
    if follow_bridge['iterations'] >= FOLLOW_BRIDGE_CONFIRM and isEscaping(ants[1]) and isEscaping(ants[2]):
        return True
    
    if abs(ants[follower_id][0] - follow_bridge['x']) == 2 and abs(ants[follower_id][1] - follow_bridge['y']) == 2:
        follow_bridge['iterations'] += 1
    else:
        follow_bridge['iterations'] = 0

    follow_bridge['x'] = ants[follower_id][0]
    follow_bridge['y'] = ants[follower_id][1]

    return False    

def updateMinMax():
    if glider['iterations'] >= GLIDER_CONFIRM or double_bridge['iterations'] >= DOUBLE_BRIDGE_CONFIRM or follow_bridge['iterations'] >= FOLLOW_BRIDGE_CONFIRM:
        return
    
    for id in ants:
        if bridges[id]['iterations'] < BRIDGE_CONFIRM:
            if ants[id][0] < min_xy_visited[0]:
                min_xy_visited[0] = ants[id][0]
            elif ants[id][0] > max_xy_visited[0]:
                max_xy_visited[0] = ants[id][0]
            if ants[id][1] < min_xy_visited[1]:
                min_xy_visited[1] = ants[id][1]
            elif ants[id][1] > max_xy_visited[1]:
                max_xy_visited[1] = ants[id][1]

def noCollision(x, y, r):
    if r == 0:
        if x > 44 and y < x - 16:
            return True
        if x < -44 and y > x + 16:
            return True
        if y < -48 and x > y + 77:
            return True
        if y > 48 and x < y - 77:
            return True
    elif r == 2:
        if x > 44:
            return True
        if x < -44 and y > x + 30:
            return True
        if y > 58:
            return True
        if y < -38 and x > y + 62:
            return True
    return False

def patternFollowed(ant1_pattern, ant2_pattern):
    if ants[1][2] != ant1_pattern[0]:
        return False
    if ants[2][2] != ant2_pattern[0]:
        return False
    if universe[ants[1][1], ants[1][0]] != ant1_pattern[1]:
        return False
    if universe[ants[2][1], ants[2][0]] != ant2_pattern[1]:
        return False
    return True

def plot_single(ant2x, ant2y, ant2r, is_saved, is_shown):
    global ants, initial_ants, universe, num_nonempty_cells, min_xy_visited, max_xy_visited, glider, bridges, double_bridge, follow_bridge, spiral, frame

    print('Plotting ', ant2x, ' ', ant2y, ' ', ant2r, '...')

    if noCollision(ant2x, ant2y, ant2r):
        print('Smart Skipped - No Collision')
        return ('bridge', 9984)
        
    time_start = time()

    ants = {1:[WIDTH // 2 + ant2x, HEIGHT // 2 + ant2y, ant2r], 2:[WIDTH // 2, HEIGHT // 2, 0]}
    initial_ants = {1:ants[1].copy(), 2:ants[2].copy()}
    min_xy_visited = [min(ants[1][0], ants[2][0]), min(ants[1][1], ants[2][1])]
    max_xy_visited = [max(ants[1][0], ants[2][0]), max(ants[1][1], ants[2][1])]

    glider = {'iterations': 0, 'ant1x': ants[1][0], 'ant1y': ants[1][1], 'ant2x': ants[2][0], 'ant2y': ants[2][1]}
    bridges = {1: {'iterations': 0, 'x': ants[1][0], 'y': ants[1][1]}, 2: {'iterations': 0, 'x': ants[2][0], 'y': ants[2][1]}}
    double_bridge = {'iterations': 0, 'ant1x': ants[1][0], 'ant1y': ants[1][1], 'ant2x': ants[2][0], 'ant2y': ants[2][1]}
    follow_bridge = {'iterations': 0, 'x': 0, 'y': 0}
    spiral = {'iterations': 0, 'radius': {1: 0, 2: 0}}

    universe = np.zeros((HEIGHT, WIDTH), dtype=np.int8)
    num_nonempty_cells = 0
    frame = 0

    tag = ''
    step()
    while True:
        if len(ants) == 0:
            tag = 'unknown'
            break
        if isLoop():
            tag = 'loop'
            break
        if isGliderEscaping():
            tag = 'glider'
            frame -= 10 * glider['iterations']
            break
        if isAllBridgeEscaping():
            tag = 'bridge'
            #store the bridge sequence while rewinding
            bridge_pattern = {1:[], 2:[]}
            for _ in range(104):
                for id, ant in ants.items():
                    bridge_pattern[id].append((ant[2], universe[ant[1], ant[0]]))
                reverseStep()
            pattern_index = 0
            while patternFollowed(bridge_pattern[1][pattern_index], bridge_pattern[2][pattern_index]):
                reverseStep()
                pattern_index = (pattern_index + 1) % 104
            break
        if isDoubleBridgeEscaping():
            tag = 'double bridge'
            for _ in range(4 * 102):
                step()
            frame -= 102 * (4 + double_bridge['iterations'])
            break
        if isFollowBridgeEscaping():
            tag = 'follow bridge'
            for _ in range(4 * 108):
                step()
            frame -= 108 * (4 + follow_bridge['iterations'])
            break
        if isSpiral():
            tag = 'spiral'
            break

        updateMinMax()
        step()
    
    print('Frame: ', frame, ' ', tag)
    print(int((time() - time_start) * 100) / 100, ' s')

    if is_saved or is_shown:
        plt.axis('off')
        c_map = colors.ListedColormap(['dimgrey', 'b', 'r'])
        margin = 10
        plt.imshow(universe[max(0, min_xy_visited[1] - margin):min(HEIGHT, max_xy_visited[1] + margin), max(0, min_xy_visited[0] - margin):min(WIDTH, max_xy_visited[0] + margin)], cmap=c_map, interpolation='none')
    if is_saved:
        plt.savefig('( ' + str(ant2x) + ',' + str(ant2y) + ',' + str(ant2r) +') frame ' + str(frame) + ' ' + tag + '.png')
    if is_shown:
        plt.show()
    plt.clf()
    return (tag, frame)

def log_data(type, frame, x, y):
    if type == 'bridge':
        bridge_data[y + int((bridge_data.shape[0] - 1) / 2), x + int((bridge_data.shape[1] - 1) / 2)] = frame
    elif type == 'loop':
        loop_data[y + int((loop_data.shape[0] - 1) / 2), x + int((loop_data.shape[1] - 1) / 2)] = frame
    elif type == 'glider':
        glider_data[y + int((glider_data.shape[0] - 1) / 2), x + int((glider_data.shape[1] - 1) / 2)] = frame

def plot_ring(size, r, save, log):
    time_start = time()
    if size == 0:
        t,f = plot_single(0,0,r,save,False)
        if log:
            log_data(t, f, 0, 0)
    elif r == 0:
        for i in range(-size, size + 1):
            t,f = plot_single(size, i, r, save, False)
            if log:
                log_data(t, f, size, i)
                log_data(t, f, -size, -i)
        for i in range(0, size):
            t,f = plot_single(i, size, r, save, False)
            if log:
                log_data(t, f, i, size)
                log_data(t, f, -i, -size)
            if i > 0:
                t,f = plot_single(i, -size, r, save, False)
                if log:
                    log_data(t, f, i, -size)
                    log_data(t, f, -i, size)
    else:
        for i in range(-size, size + 1):
            t,f = plot_single(size, i, r, save, False)
            if log:
                log_data(t, f, size, i)
            t,f = plot_single(-size, i, r, save, False)
            if log:
                log_data(t, f, -size, i)
        for i in range(-(size-1), size):
            t,f = plot_single(i, size, r, save, False)
            if log:
                log_data(t, f, i, size)
            t,f = plot_single(i, -size, r, save, False)
            if log:
                log_data(t, f, i, -size)
    print('\nTotal time: ', int((time() - time_start) * 100) / 100, ' s')

def data_run(start_size, end_size, r):
    global bridge_data, loop_data, glider_data
    bridge_data = np.loadtxt('bridge data r = ' + str(r) + '.txt')
    loop_data = np.loadtxt('loop data r = ' + str(r) + '.txt')
    glider_data = np.loadtxt('glider data r = ' + str(r) + '.txt')
    if int((bridge_data.shape[0] - 1) / 2) < end_size:
        bridge_data = np.pad(bridge_data, end_size - int((bridge_data.shape[0] - 1) / 2))
    if int((loop_data.shape[0] - 1) / 2) < end_size:
        loop_data = np.pad(loop_data, end_size - int((loop_data.shape[0] - 1) / 2))
    if int((glider_data.shape[0] - 1) / 2) < end_size:
        glider_data = np.pad(glider_data, end_size - int((glider_data.shape[0] - 1) / 2))
    #bridge_data = np.zeros((end_size*2 + 1, end_size*2 + 1))
    #loop_data = np.zeros((end_size*2 + 1, end_size*2 + 1))
    #glider_data = np.zeros((end_size*2 + 1, end_size*2 + 1))
    for i in range(start_size, end_size + 1):
        plot_ring(i, r, False, True)
    np.savetxt('bridge data r = ' + str(r) + '.txt', bridge_data, fmt = '%i', delimiter = '\t')
    np.savetxt('loop data r = ' + str(r) + '.txt', loop_data, fmt = '%i', delimiter = '\t')
    np.savetxt('data r = ' + str(r) + '.txt', glider_data, fmt = '%i', delimiter = '\t')

t,f = plot_single(-3, 11, 1, True, True)
#plot_ring(2, 0, True, True)
#data_run(0, 5, 2)