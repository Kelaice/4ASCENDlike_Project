import pygame
from board import *
from background import*

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False

    drawBackGround(screen)

    drawUI(screen)
    turn = checkMouse(screen)
    setPiece(turn)
    drawPiece(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()