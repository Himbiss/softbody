'''
Soft Body Simulation Example
Created on Sep 5, 2014

@author: himbiss

Controls:
A      -  Show/Hide Springs
SPACE  -  Perform 'Jump'
LM     -  Drag the balls towards the mouse location
RM     -  Spawn a new ball
ESC    -  Exit
'''

import pygame, sys, SoftBody
from pygame.locals import *

SHOWSPRINGS = False # show springs?
MOUSEDOWN = False
SCRSIZEX, SCRSIZEY = 640,480   # screen size
NUMP = 10       # number of mass points
JUMPSPEED = -180

blueColor = pygame.Color(0, 0, 255)
whiteColor = pygame.Color(255, 255, 255)

pygame.init()

fpsClock = pygame.time.Clock()

windowSurfaceObj = pygame.display.set_mode((SCRSIZEX,SCRSIZEY))
pygame.display.set_caption('Soft Body Simulation')

mousex, mousey = 0, 0

fontObj = pygame.font.Font('freesansbold.ttf', 16)
msg = 'Soft Body Example'

balls = []

while True:
    windowSurfaceObj.fill(whiteColor)

    # applies force on the first three masspoints,
    # directed to the mouse pointer  
    if MOUSEDOWN:
        for ball in balls:
                    ptA = ball.myPoints[1]
                    ptB = ball.myPoints[0]
                    ptC = ball.myPoints[2]
                    dx = mousex-ptA.x
                    dy = mousey-ptA.y
                    ptA.vx,ptA.vy =  dx,dy
                    ptB.vy,ptC.vy,ptB.vx,ptC.vx = dy/2,dy/2,dx/2,dx/2
                    
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
   
    # check for events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONUP:
            mousex, mousey = event.pos
            if event.button == 3: # left mouse click
                balls.append(SoftBody.Ball(mousex, mousey, NUMP))
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
