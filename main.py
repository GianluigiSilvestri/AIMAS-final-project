import json
import pygame as pg
import numpy as np
from numpy.linalg import norm
import time
from shapely import geometry

class Repeater():

    def __init__(self, pos):
        self.position = pos
        self.velocity = np.array((0, 0), dtype=float)

        self.error_prev = np.array((0, 0))

    def control(self, pos_desired, repeaters = [], obstacles = []):
        """
        PD controller to provide a control signal / acceleration
        :param pos_desired: Desired position to go towards
        :return: Control signal u
        """


        kr = 2 # Repulsive gain
        S = 10 # completely randomly set. todo: pick a good value.
        R = 2 # radius of repeater (obstacle)

        repulsive = np.array((0.0, 0.0))

        # Compute repulsive forces from repeaters
        if len(repeaters) > 1: # If more repeaters than this one
            for repeater in repeaters: # Look at all repeaters except for this one. Assign indices? d == 0?
                d = norm(repeater.position - self.position)

                # If repeater is far away, don't account for it at all
                if d > S or d == 0: # todo: do something smarter to avoid checking himself?
                    continue

                # Direction from repeater to self, normalized
                direction = (repeater.position - self.position) / d

                # If very close, large repulsive force
                if d >= R:
                    repulsive += direction * 1000 # todo: not a good idea

                else:
                    repulsive += ((S - d) / (S - R)) * direction


        # Proportional and differential gains # Todo: do these values make sense?
        kp = 10; kd = 10

        # PD controller
        error = pos_desired - self.position
        d_error = (error - self.error_prev) / dt
        u = kp * error + kd * d_error - kr * repulsive # todo: plus?

        self.error_prev = error

        return u

    def move(self, pos_desired, repeaters = []):
        """
        Update the position, velocity and acceleration
        :param pos_desired:
        :return:
        """

        # Get the control signal (acceleration)
        u = self.control(pos_desired, repeaters)

        # Make sure it's not too large
        if norm(u) > a_max:
            u = u / norm(u) * a_max

        # Update velocity
        self.velocity += u * dt

        # Make sure it's not too large
        if norm(self.velocity) > v_max:
            self.velocity = self.velocity / norm(self.velocity) * v_max

        # Update position
        self.position += self.velocity






def discretize(min_x,max_x,min_y,max_y,n_squares):
    squares=[]
    xs=[min_x]
    ys=[min_y]
    x=min_x
    y=min_y
    x_side=(max_x-min_x)/n_squares
    while x<max_x:
        x+=x_side
        xs.append(x)
    while y<max_y:
        y+=x_side
        ys.append(y)

    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            square=geometry.Polygon([(xs[i],ys[j]),(xs[i],ys[j+1]),(xs[i+1],ys[j+1]),(xs[i+1],ys[j])])
            squares.append({'square':square,'center':np.array(square.centroid)})
            a=0
    return squares

def list_to_pygame(list_of_points):
    pg_list_of_points=[]
    for point in list_of_points:
        pg_list_of_points.append(to_pygame(point))
    return  pg_list_of_points

def to_pygame(coords):
    '''Convert coordinates into pygame coordinates'''
    return (int(coords[0] * 5 + width / 2 - 150), int(coords[1] * -5 + height / 2 + 200))


def set_bg(repeaters,not_seen):
    '''set initial and final position'''
    screen.fill((255, 255, 255))
    '''for i in range(len(robots.locations)):
        pg_pos = to_pygame(robots.locations[i])
        pg.draw.circle(screen, robots.colors[i], (pg_pos[0], pg_pos[1]), 3, 0)
        if len(robots.all_locations)>1:
            for p in range(1,len(robots.all_locations)):
                pg.draw.line(screen,robots.colors[i],to_pygame(robots.all_locations[p-1][i]),to_pygame(robots.all_locations[p][i]))'''
    for i in range(1,len(traj_pos)):
        pg.draw.line(screen,(0,0,0),to_pygame(traj_pos[i-1]),to_pygame(traj_pos[i]))
    pg.draw.polygon(screen, (0, 0, 0), pg_bounding_polygon, 1)
    '''for pos in vs.desired_pos:
        pg_pos = to_pygame(pos)
        pg.draw.circle(screen, (0, 0, 255), (pg_pos[0], pg_pos[1]), 3, 1)'''
    pg.draw.line(screen,(255,0,0),to_pygame(traj_pos[time_step]+np.array([1,1])),to_pygame(traj_pos[time_step]+np.array([-1,-1])),4)
    pg.draw.line(screen, (255, 0, 0), to_pygame(traj_pos[time_step] + np.array([-1, 1])),
                 to_pygame(traj_pos[time_step] + np.array([1, -1])),4)
    pg.draw.circle(screen,(255,0,0),to_pygame(traj_pos[time_step]),scanning_range*5,1)
    pg.draw.circle(screen,(0,153,0),to_pygame(ground_station),5)
    pg.draw.circle(screen,(0,153,0),to_pygame(ground_station),sensor_range*5,1)
    pg.draw.circle(screen, (0, 255, 0), to_pygame(ground_station), desired_range * 5, 1)
    if repeaters:
        for repeater in repeaters:
            pg.draw.line(screen, (0, 0, 255), to_pygame(repeater.position + np.array([0.8, 0.8])),
                     to_pygame(repeater.position+ np.array([-0.8, -0.8])), 3)
            pg.draw.line(screen, (0, 0, 255), to_pygame(repeater.position + np.array([-0.8, 0.8])),
                     to_pygame(repeater.position + np.array([0.8, -0.8])), 3)
    s=pg.Surface((infoObject.current_w, infoObject.current_h),pg.SRCALPHA)
    if not_seen:
        for square in not_seen:
            pg.draw.polygon(s,(100,100,100,128),list_to_pygame(list(np.array(square['square'].exterior.coords)[:-1])))

    screen.blit(s, (0, 0))
# PyGame parameters
pg.init()
infoObject = pg.display.Info()
screen = pg.display.set_mode((infoObject.current_w, infoObject.current_h))
width = infoObject.current_w
height = infoObject.current_h
background_colour = (255, 255, 255)
screen.fill(background_colour)


data = json.load(open('P25_X.json'))
traj=json.load(open('P25_26_traj.json'))
bounding_polygon = data["bounding_polygon"]
ground_station=np.array(data["ground_station"],dtype=float)
sensor_range=data["sensor_range"]
desired_range=data["desired_range"]
scanning_range=data["scanning_range"]

a_max = data["vehicle_a_max"]
v_max = data["vehicle_v_max"]


traj_t=traj["t"]
traj_theta=traj["theta"]
traj_x=traj["x"]
traj_y=traj["y"]
traj_pos=np.array(list(zip(traj_x,traj_y)))
traj_pos-=traj_pos[0]

dt=0.1

pg_bounding_polygon = []
for point in bounding_polygon:
    pg_bounding_polygon.append(to_pygame(point))

sh_bounding_polygon=geometry.Polygon(bounding_polygon)
min_x,min_y,max_x,max_y=sh_bounding_polygon.bounds
not_seen=discretize(min_x,max_x,min_y,max_y,30)

repeaters=[]

time_step=0
start = False
done = False

while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
    if not start:
        t0 = time.time()
        t1 = 0
        while (t1 - t0 < 1):
            t1 = time.time()
        start = True

    ## check if we see some square
    for square in not_seen:
        if norm(traj_pos[time_step]-square['center'])<scanning_range:
            seen=True
            for vertex in list(np.array(square['square'].exterior.coords))[:-1]:
                if norm(traj_pos[time_step]-square['center'])>=scanning_range:
                    seen=False
            if seen:
                not_seen.remove(square)


    if repeaters:
        # if we have repeaters we move them
        if norm(repeaters[-1].position-ground_station)>=desired_range:
            #if the last added repeater is going out of rage from the ground station we add a new one
            repeaters.append(Repeater(ground_station.copy()))
        for r in range(len(repeaters)):
            #for all the repeaters, if is the one following the payload we move towards it,
            # otherwise we move towards the next repeater in the chain
            if r==0:
                repeaters[r].move(traj_pos[time_step], repeaters)#todo: go to the boss
            else:
                repeaters[r].move(repeaters[r-1].position, repeaters)#todo: go to the previous repeater


    else:
    #if there are no repeaters, we check if the payload is on range.
    # if not, we add a repeater
        if norm(traj_pos[time_step]-ground_station)>=desired_range:
            repeaters.append(Repeater(ground_station.copy()))




    time_step += 1

    if time_step%10==0:
        set_bg(repeaters,not_seen)
        pg.display.flip()