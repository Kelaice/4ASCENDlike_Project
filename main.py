import pygame
import random
from board import Board
from title_page import drawTitlePage, drawWelcome
from game_core import FourAscendGame

#-------------------------------------------Initialize-----------------------------------------------
TITLE=0;MENU=1;PVP=2;PVE=3;TEACH=4

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

background_image = pygame.image.load('resource\\background.png')
titleBackground_image = pygame.image.load('resource\\titleBackground.png')


# 游戏状态初始化
state=TITLE
TITLE_FLAG=True;WEL_FLAG=True

board = Board()
game = FourAscendGame()
game_state = game.getInitBoard()
player = 1
#鼠标锁
lock = 0


# 主循环
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False

    match state:
        case 0:
            # 标题页和欢迎页
            if TITLE_FLAG:
                TITLE_FLAG=drawTitlePage(screen)
            WEL_FLAG=drawWelcome(screen,titleBackground_image,WEL_FLAG)
            for event in pygame.event.get():
                if event.type==pygame.MOUSEBUTTONDOWN:
                    state = MENU
        case 1:
            # 游戏主界面
            screen.fill(0xffffff)
            screen.blit(background_image, (0, 0))

            pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = game_state
            board.drawUI(screen, hp1, hp2, game.hp1, game.hp2)

            valid = board.checkMouse(screen)
            pressed = pygame.mouse.get_pressed()
            # 鼠标点击落子
            if valid and pressed[0] and not lock:
                pixel_pos = board.findPos()
                row, col = board.pixel_to_board_index(pixel_pos)
                action = row * board.Boardsize + col
                valid_moves = game.getValidMoves(game_state, player)

                if 0 <= action < len(valid_moves) and valid_moves[action]:
                    game_state, player = game.getNextState(game_state, player, action)
                    board.syncFromPieces(game_state[0], game_state[1])
                #鼠标上锁    
                lock = 1
            # 鼠标松开后解锁
            if not pressed[0]:
                lock = 0
            # 绘制棋子和魔法植物    
            board.drawPiece(screen)
            board.drawMagicPlants(screen)

            result = game.getGameEnded(game_state, player)
            if result is not None:
                print("Game Over:", result)
                running = False
            
                
            pygame.display.flip()
    clock.tick(60)

pygame.quit()