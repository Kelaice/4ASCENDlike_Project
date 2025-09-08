import pygame
from board import *
from title_page import*
from menu_page import*

#-------------------------------------------Initialize-----------------------------------------------
TITLE=0;MENU=1;PVP=2;PVE=3;TEACH=4

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

background_image = pygame.image.load('resource\\background.png')
titleBackground_image = pygame.image.load('resource\\titleBackground.png')




state=TITLE
TITLE_FLAG=True;WEL_FLAG=True
MENU_FLAG=True



while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False

    match state:
        case 0:
            if TITLE_FLAG:
                TITLE_FLAG=drawTitlePage(screen)
            WEL_FLAG=drawWelcome(screen,titleBackground_image,WEL_FLAG)
            for event in pygame.event.get():
                if event.type==pygame.MOUSEBUTTONDOWN:
                    state = MENU
        case 1:
            if MENU_FLAG:
                MENU_FLAG = MenuAnimation(screen,background_image)
            drawMenuPage(screen,background_image)
            x1=0;y1=0
            if event.type == pygame.MOUSEMOTION:
                x1,y1=event.pos
            mouseJudge(screen,x1,y1)
            # screen.fill(0xffffff)
            # screen.blit(background_image, (0, 0))
            # drawUI(screen)
            # turn = checkMouse(screen)
            # setPiece(turn)
            # drawPiece(screen)


            pygame.display.flip()

    clock.tick(60)

pygame.quit()