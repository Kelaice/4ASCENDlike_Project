import pygame

def drawBackGround(screen):
    screen.fill(0xffffff)
    pos=pygame.Vector2(640,360)
    color=(255,255,255)
    radius=300
    width=5
    r=0;g=0;b=0
    while(radius<750):
        pygame.draw.circle(screen,color,pos,radius,width)
        r=color[0]-2;g=color[0]-2;b=color[0]-2
        color=tuple()
        color+=(r,g,b)
        radius+=width
