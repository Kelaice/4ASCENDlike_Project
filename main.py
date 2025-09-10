import pygame
from board import *
from title_page import *
from menu_page import *
from game_core import *
#-------------------------------------------Initialize-----------------------------------------------
TITLE=0;MENU=1;PVP=2;PVE=3;TEACH=4

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

background_image = pygame.image.load('resource\\background.png')
titleBackground_image = pygame.image.load('resource\\titleBackground.png')

board = Board()
game = FourAscendGame()
game_state = game.getInitBoard()
player = 1
#鼠标锁
lock = 0



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
            pygame.display.flip()
            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
            # if event.type == pygame.MOUSEBUTTONDOWN:
                x1,y1=event.pos
                state = gameJudge(x1,y1)
                lock=1
            if not pressed[0]:
                lock=0

        case 2:
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