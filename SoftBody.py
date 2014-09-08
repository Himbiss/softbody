'''
Soft Body Simulation
Created on Sep 5, 2014

@author: himbiss

Controls:
A      -  Show/Hide Springs
SPACE  -  Perform 'Jump'
LM     -  Drag the balls towards the mouse location
RM     -  Spawn a new ball
ESC    -  Exit
'''

import pygame, sys, math
from pygame.locals import *

NUMP = 10       # number of mass points
BALLRADIUS = 80 # ballradius
SCRSIZEX, SCRSIZEY = 640,480   # screen size
GY = 9.81       # gravity
Pressure = 10   # pressure
DT = .1         # delta time
JUMPSPEED = -180
SHOWSPRINGS = False # show springs?
MOUSEDOWN = False

class CPoint2d(object):

    def __init__(self):
        self.x, self.y = float(0),float(0)   # position
        self.vx, self.vy = float(0),float(0) # velocity
        self.fx, self.fy = float(0),float(0) # force accumulator
    
    # returns a tupel containing the position of this masspoint
    def posTupel(self):
        return (self.x,self.y)

        
class CSpring(object):

    def __init__(self):
        self.i, self.j = int(0),int(0)       # point indexes
        self.length = float(0),float(0)      # rest length
        self.nx, self.ny = float(0),float(0) # normal vector

class Object(object):
    # is initialized with a list of mass points
    def __init__(self,myPoints):
        self.myPoints = myPoints   # holds all points
        
    # returns a list of all point tupels
    def pointList(self):
        pointList = []
        for point in self.myPoints:
            pointList.append(point.posTupel())
        return pointList
    
    # renders a polygon using the points of this object
    def renderPoly(self,surfaceObj,color):
        pygame.draw.polygon(surfaceObj, color, self.pointList())
        
    def calcCentroid(self):
        signedArea = 0.
        centroidX,centroidY = 0.,0.
        for idx, pt in enumerate(self.myPoints):
            nxt = self.myPoints[(idx+1)%len(self.myPoints)]
            a = pt.x*nxt.y-pt.y*nxt.x
            signedArea += a
            centroidX += (pt.x+nxt.x)*a
            centroidY += (pt.y+nxt.y)*a
        signedArea *= .5
        return (int(centroidX/(6.*signedArea)),int(centroidY/(6.*signedArea)))
        
    # returns the bounding box as a rectangle    
    def boundingBox(self):
        p = self.myPoints[0]
        minP, maxP = p.posTupel(),p.posTupel()
        for p in self.myPoints:
            minP = (min(minP[0],p.x),min(minP[1],p.y))
            maxP = (max(maxP[0],p.x),max(maxP[1],p.y))
        dim = (maxP[0]-minP[0],maxP[1]-minP[1])
        return Rect(minP,dim)
    
    # render boundingbox
    def renderBoundingBox(self,surfaceObj):
        pygame.draw.rect(surfaceObj, blueColor, self.boundingBox(),1)
    
class DeformableObject(Object):
    
    def __init__(self,myPoints,mass,final_pressure,ks,kd):
        super(DeformableObject,self).__init__(myPoints)
        self.mySprings = []         # holds all springs
        self.final_pressure = final_pressure     # max pressure
        self.ks,self.kd = ks,kd     # elasticity(ks) and damping(kd)
        self.mass = mass            # mass of a mass point
        # add springs
        for i in range(0,NUMP):
            for j in range(0,i):
                if j != i:
                    self.addSpring(j,i)
    
    def renderPoly(self,surfaceObj):
        super(DeformableObject,self).renderPoly(surfaceObj,yellowColor)
        
    # adds a spring between masspoint i and j
    def addSpring(self,i,j):
        s = CSpring()
        s.i,s.j = i,j
        pA,pB = self.myPoints[i],self.myPoints[j]
        s.length = math.sqrt((pA.x - pB.x) * 
                         (pA.x - pB.x) +
                         (pA.y - pB.y) * 
                         (pA.y - pB.y))
        self.mySprings.append(s)
    
    # render springs    
    def renderSprings(self,surfaceObj):
        for spring in self.mySprings:
            p1,p2 = self.myPoints[spring.i],self.myPoints[spring.j]
            pygame.draw.line(surfaceObj, redColor, (p1.x,p1.y), (p2.x,p2.y), 2)
    
    # override physics, makes object deformable
    def updatePhysics(self):
        # calculate gravity force
        for p in self.myPoints:
            p.fx = 0
            p.fy = self.mass * GY * (abs(Pressure - self.final_pressure))
        
        # calculate spring force
        # loop over all springs
        for s in self.mySprings:
            # get positions of spring start & end points
            p1,p2 = self.myPoints[s.i],self.myPoints[s.j]
            x1,y1,x2,y2 = p1.x,p1.y,p2.x,p2.y
        
            # calculate sqr(distance)
            r12d = math.sqrt((x1-x2) * (x1-x2) + (y1-y2) * (y1-y2))
            
            # start = end?
            if r12d != 0:
                # get velocities of start & end points
                vx12 = p1.vx - p2.vx
                vy12 = p1.vy - p2.vy
            
            # calculate force value
            f = (r12d - s.length) * self.ks + ((vx12 * (x1-x2) + vy12 * (y1-y2)) * self.kd) / r12d
            
            # force vector
            Fx = ((x1-x2) / r12d) * f;
            Fy = ((y1-y2) / r12d) * f;
            
            # accumulate force for starting point
            p1.fx -= Fx
            p1.fy -= Fy
            
            # accumulate force for end point
            p2.fx += Fx
            p2.fy += Fy
            
            # calculate normal vectors to springs
            s.nx = (y1-y2) / r12d
            s.ny = -(x1-x2) / r12d
            
        # pressure force
        for s in self.mySprings:
            # get positions of spring start & end points
            p1,p2 = self.myPoints[s.i],self.myPoints[s.j]
            x1,y1,x2,y2 = p1.x,p1.y,p2.x,p2.y
            
            # calculate sqr(distance)
            r12d = math.sqrt((x1-x2) * (x1-x2) + (y1-y2) * (y1-y2))
            
            pressurev = r12d * Pressure * (float(1.)/self.calcVolume())
                
            p1.fx += s.nx * pressurev
            p1.fy += s.ny * pressurev
            p2.fx += s.nx * pressurev
            p2.fy += s.ny * pressurev
        
        # integrate euler
        for p in self.myPoints:
            # x
            p.vx += (p.fx / self.mass) * DT
            p.x += p.vx * DT
            
            # boundaries y
            if p.x > SCRSIZEX:
                p.x = SCRSIZEX
                p.vx = -p.vx
                    
            # y
            p.vy += (p.fy / self.mass) * DT
            p.y += p.vy * DT
            
            # boundaries y
            if p.y > SCRSIZEY:
                p.y = SCRSIZEY
                p.vy = -p.vy
    
    def calcVolume(self):
        self.volume = 0
        # calculate volume of the object (gauss theorem)
        for s in self.mySprings:
            # get positions of spring start & end points
            p1,p2 = self.myPoints[s.i],self.myPoints[s.j]
            x1,y1,x2,y2 = p1.x,p1.y,p2.x,p2.y
        
            # calculate sqr(distance)
            r12d = math.sqrt((x1-x2) * (x1-x2) + (y1-y2) * (y1-y2))
        
            self.volume += .5 * abs(x1-x2) * abs(s.nx) * r12d
        return self.volume
        
class Ball(DeformableObject):
    
    def __init__(self,x,y,nump):
        self.x,self.y = x,y
        # init ball points
        points = []
        for i in range(0,nump):
            p = CPoint2d()
            p.x = BALLRADIUS * math.sin(i * (2.0 * math.pi) / nump) + x
            p.y = BALLRADIUS * math.cos(i * (2.0 * math.pi) / nump) + y
            points.append(p)
        super(Ball,self).__init__(points,1,3,4,.5)
    
        


pygame.init()

fpsClock = pygame.time.Clock()

windowSurfaceObj = pygame.display.set_mode((SCRSIZEX,SCRSIZEY))
pygame.display.set_caption('Soft Body Simulation')

redColor = pygame.Color(255, 0, 0)
greenColor = pygame.Color(0, 255, 0)
blueColor = pygame.Color(0, 0, 255)
yellowColor = pygame.Color(255,255,0)
whiteColor = pygame.Color(255, 255, 255)
mousex, mousey = 0, 0

fontObj = pygame.font.Font('freesansbold.ttf', 16)
msg = 'Soft Body Test'

balls = []

while True:
    windowSurfaceObj.fill(whiteColor)

    if MOUSEDOWN:
        for ball in balls:
                    ptA = ball.myPoints[1]
                    ptB = ball.myPoints[0]
                    ptC = ball.myPoints[2]
                    dx = mousex-ptA.x
                    dy = mousey-ptA.y
                    ptA.vx,ptA.vy =  dx,dy
                    ptB.vy,ptC.vy,ptB.vx,ptC.vx = dy/2,dy/2,dx/2,dx/2
    # Draw an arc as part of an ellipse. 
    # Use radians to determine what angle to draw.
    pi = math.pi
    for ball in balls:    
        # update physics
        ball.updatePhysics()
        
        ball.renderPoly(windowSurfaceObj)
        if SHOWSPRINGS:
            ball.renderSprings(windowSurfaceObj)
        ball.renderBoundingBox(windowSurfaceObj)    
        
        # draw centroid
        pygame.draw.circle(windowSurfaceObj, blueColor, ball.calcCentroid(), 5, 3)
   
    msg = 'Rendering '+str(len(balls))+' Objects' 
    # draw message
    msgSurfaceObj = fontObj.render(msg, False, blueColor)
    msgRectobj = msgSurfaceObj.get_rect()
    msgRectobj.topleft = (10, 20)
    windowSurfaceObj.blit(msgSurfaceObj, msgRectobj)
   
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            if event.button == 3: # left mouse click
                balls.append(Ball(mousex, mousey, NUMP))
            if event.button == 1: # right mouse click
                MOUSEDOWN = False
        elif event.type == MOUSEBUTTONDOWN:
            mousex, mousey = event.pos
            if event.button == 1: # right mouse click
                MOUSEDOWN = True
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                XDIR = int(-1)
            if event.key == K_RIGHT:
                XDIR = int(1)
            if event.key == K_SPACE:
                for ball in balls:
                    for p in ball.myPoints:
                        p.vy += JUMPSPEED
            if event.key == K_a:
                SHOWSPRINGS = not SHOWSPRINGS
                XDIR = int(0)
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
        
    pygame.display.update()
    fpsClock.tick(30)