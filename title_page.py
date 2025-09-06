import pygame

def drawTitlePage(screen):
    global TITLE_FLAG
    screen.fill(0xd2d2d2)
    pos=pygame.Vector2(640,360)
    radius=600  #300
    color=(210,210,210)
    width=3
    r=0;g=0;b=0

    while(radius>=300):
        tempr=radius
        color=tuple();color+=(210,210,210)
        while(tempr<750):
            pygame.draw.circle(screen,color,pos,tempr,width)
            r=color[0]-1;g=color[0]-1;b=color[0]-1
            color=tuple()
            color+=(r,g,b)
            tempr+=width
        pygame.display.flip()
        radius-=4+int((radius-300)*0.0266)
        pygame.time.wait(50)
    pygame.display.flip()

    f = pygame.font.Font('resource\\ProggyTinySZ-4.ttf',200)
    text = f.render("4 A S C E N D",True,(0,0,0))
    textRect =text.get_rect()
    textRect.center = (640,200)
    screen.blit(text,textRect)
    pygame.display.update(textRect)

    return False

def drawWelcome(screen,titleBackground_image,WEL_FLAG):
    f = pygame.font.Font('resource\\ProggyTinySZ-4.ttf',50)
    text = f.render("press   Any   key   to   continue",True,(100,100,100))
    textRect =text.get_rect()
    textRect.center = (640,600)
    if WEL_FLAG:
        screen.blit(text,textRect)
    else:
        screen.blit(titleBackground_image, (0, 0))
    pygame.display.update(textRect)
    pygame.time.wait(1000)
    return not WEL_FLAG

#废案
# import pygame

# def drawBackGround(screen):
#     screen.fill(0xffffff)
#     pos=pygame.Vector2(640,360)
#     radius=300  #300
#     color=(255,255,255)
#     width=3
#     r=0;g=0;b=0

#     while(radius<750):
#         pygame.draw.circle(screen,color,pos,radius,width)
#         r=color[0]-1;g=color[0]-1;b=color[0]-1
#         color=tuple()
#         color+=(r,g,b)
#         radius+=width
#         pygame.display.update()
#     pygame.display.flip()



# import pygame

# def drawBackGround(screen):
#     screen.fill(0xffffff)
#     pos=pygame.Vector2(640,360)
#     radius=800  #300
#     color=(120,120,120)
#     width=6
#     r=0;g=0;b=0

#     while(radius>300):
#         pygame.draw.circle(screen,color,pos,radius,width)
#         r=color[0]+1;g=color[0]+1;b=color[0]+1
#         color=tuple()
#         color+=(r,g,b)
#         radius-=3+int((radius-300)*0.006)
#         pygame.display.update()
#     pygame.display.flip()