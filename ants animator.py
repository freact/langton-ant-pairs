import keyboard
import random
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib import colormaps

width = 5000
height = 5000

view_width = 160 * 2
view_height = 90 * 2
view_x = width // 2
view_y = height // 2
move_speed = 0.1
frame = 0
paused = False
rewind = False
frame_skip = 4

headstart =  0

num_ants = 2
x = [random.randint(-20, 20) for _ in range(num_ants - 1)]
y = [random.randint(-20, 20) for _ in range(num_ants - 1)]
r = [random.randint(0, 3) for _ in range(num_ants - 1)]

## use this line to set ant2's position or comment it out to have it set randomly
x,y,r = ([9], [-10], [1])

x_start = int(height/2)
y_start = int(width/2)

ants = {}
ants[num_ants] = [x_start, y_start, 0]

tag = '\n'
for i in range(num_ants - 1):
    tag += '(' + str(x[i]) + ',' + str(y[i]) + ',' + str(r[i]) + ')\n'
    ants[i + 1] = [x_start + x[i], y_start + y[i], r[i]]
print(tag)

u = np.zeros((height, width), dtype=np.int8)

def move(x):
    if x[2] == 0:
        x[0] += 1
    elif x[2] == 1:
        x[1] += 1
    elif x[2] == 2:
        x[0] -= 1
    else:
        x[1] -= 1
    return

def reverseMove(x):
    if x[2] == 0:
        x[0] -= 1
    elif x[2] == 1:
        x[1] -= 1
    elif x[2] == 2:
        x[0] += 1
    else:
        x[1] += 1
    return

def reverseStep():
    global ants, frame
    frame -= 1
    paint = {}
    rem = []
    for i in ants:
        ant = ants[i]
        reverseMove(ant)
        if u[ant[1], ant[0]] == 0:
            ant[2] = (ant[2] + 1) % 4
        else:
            ant[2] = (ant[2] - 1) % 4
        paint[(ant[0], ant[1])] = i
        if ant[0] < 0 or ant[1] < 0 or ant[0] >= width or ant[1] >= height:
            rem.append(i)
    for r in rem:
        ants.pop(r)        
    for p in paint:
        if u[p[1], p[0]] != 0:
            u[p[1], p[0]] = 0
        else:
            u[p[1], p[0]] = paint[p]
    return

def step():
    global ants, frame
    frame += 1
    paint = {}
    rem = []
    for i in ants:
        ant = ants[i]
        if u[ant[1], ant[0]] == 0:
            ant[2] = (ant[2] + 1) % 4
        else:
            ant[2] = (ant[2] - 1) % 4
        paint[(ant[0], ant[1])] = i
        move(ant)
        if ant[0] < 0 or ant[1] < 0 or ant[0] >= width or ant[1] >= height:
            rem.append(i)
    for r in rem:
        ants.pop(r)
    for p in paint:
        if u[p[1], p[0]] != 0:
            u[p[1], p[0]] = 0
        else:
            u[p[1], p[0]] = paint[p]
    return

def animate(i):
    if not paused:
        for s in range(frame_skip):
            if frame % 1000 == 0:
                print('frame: ', str(frame)) 
            if rewind:
                reverseStep()
            else:
                step()
    return [plt.imshow(u[view_y-view_height//2:view_y+view_height//2, view_x-view_width//2:view_x+view_width//2], interpolation='none', cmap=c_map, vmax=num_ants, vmin=0.1)]

for h in range(headstart):
    step()
    if frame % 100000 == 0:
        print('frame: ', str(frame))

fig = plt.figure()
fig.set_facecolor('k')
c_map = colormaps['hsv']
c_map.set_under('dimgrey')

anim = animation.FuncAnimation(fig, animate, interval=50, blit=True, save_count=0)

def controls_setup():
    def follow1(e):
        global view_x, view_y
        if 1 not in ants:
            return
        view_x = max(min(ants[1][0], width - view_width // 2), view_width // 2)
        view_y = max(min(ants[1][1], height - view_height // 2), view_height // 2)

    keyboard.on_press_key('1', follow1)

    def follow2(e):
        global view_x, view_y
        if 2 not in ants:
            return
        if e.name == 'down':
            return
        view_x = max(min(ants[2][0], width - view_width // 2), view_width // 2)
        view_y = max(min(ants[2][1], height - view_height // 2), view_height // 2)
        

    keyboard.on_press_key('2', follow2)
    
    def follow3(e):
        global view_x, view_y
        if 3 not in ants:
            return
        view_x = max(min(ants[3][0], width - view_width // 2), view_width // 2)
        view_y = max(min(ants[3][1], height - view_height // 2), view_height // 2)

    keyboard.on_press_key('3', follow3)

    def follow4(e):
        global view_x, view_y
        if 4 not in ants:
            return
        if e.name == 'left':
            return
        view_x = max(min(ants[4][0], width - view_width // 2), view_width // 2)
        view_y = max(min(ants[4][1], height - view_height // 2), view_height // 2)

    keyboard.on_press_key('4', follow4)

    def follow5(e):
        global view_x, view_y
        if 5 not in ants:
            return
        view_x = max(min(ants[5][0], width - view_width // 2), view_width // 2)
        view_y = max(min(ants[5][1], height - view_height // 2), view_height // 2)

    keyboard.on_press_key('5', follow5)

    def followhome(e):
        global view_x, view_y
        view_x = width // 2
        view_y = height //2

    keyboard.on_press_key('0', followhome)

    def play_pause(e):
        global paused
        if paused:
            paused = False
        else:
            paused = True
        print('View coords: ' + str(view_x) + ', ' + str(view_y))

    keyboard.on_press_key("w", play_pause)

    def play_rewind(e):
        global rewind
        if rewind:
            rewind = False
        else:
            rewind = True

    keyboard.on_press_key("r", play_rewind)  

    def zoom_in(x):
        global view_width, view_height
        view_width = int(view_width * 0.8)
        view_height = int(view_height * 0.8)

    keyboard.on_press_key("t", zoom_in)

    def zoom_out(x):
        global view_width, view_height
        view_width = int(view_width * 1.25)
        view_height = int(view_height * 1.25)

    keyboard.on_press_key("g", zoom_out)

    def inc(x):
        global frame_skip
        frame_skip *= 2

    keyboard.on_press_key("e", inc)

    def dec(x):
        global frame_skip
        frame_skip = max(1, int(frame_skip / 2))

    keyboard.on_press_key("d", dec)

    def view_down(x):
        global view_x, view_y
        view_y = min(height - view_height // 2, view_y + int(view_height * move_speed))

    keyboard.on_press_key("down", view_down)

    def view_up(x):
        global view_x, view_y
        view_y = max(view_height // 2, view_y - int(view_height * move_speed))

    keyboard.on_press_key("up", view_up)

    def view_right(x):
        global view_x, view_y
        view_x = min(width - view_width // 2, view_x + int(view_width * move_speed))

    keyboard.on_press_key("right", view_right)

    def view_left(x):
        global view_x, view_y
        view_x = max(view_width // 2, view_x - int(view_width * move_speed))

    keyboard.on_press_key("left", view_left)
controls_setup()

plt.rcParams['keymap.grid'] = []
plt.rcParams['keymap.grid_minor'] = []
plt.rcParams['keymap.fullscreen'] = []
plt.rcParams['keymap.save'] = []
plt.axis('off')
plt.get_current_fig_manager().window.state('zoomed')
plt.show()