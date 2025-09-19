import pygame
import numpy as np
import threading
import random
from board import Board
from title_page import drawWelcome
from menu_page import drawMenuPage, mouseJudge, menu_animation, gameJudge
from game_core import FourAscendGame, StupidFourAscendPlayer

# -------------------------------------------Initialize-----------------------------------------------
TITLE = 0
MENU = 1
PVP = 2
PVE = 3
TEACH = 4

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("resource\\background_music.mp3")


class MyThread(threading.Thread):
    def run(self):
        pygame.mixer.music.play(-1)


screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

background_image = pygame.image.load("resource\\background.png")
titleBackground_image = pygame.image.load("resource\\titleBackground.png")

board = Board()
game = FourAscendGame()
board.set_game_reference(game)
game_state = game.getInitBoard()
player = 1
# 鼠标锁
lock = 0

# 添加动画状态变量
battle_animation_started = False
pending_game_state = None
pending_player = None


thread = MyThread()
thread.start()
thread.run()

state = TITLE

click_cooldown = 0
CLICK_COOLDOWN_TIME = 100  # 毫秒
ai_thinking_time = 0


# -------------------------------------------Reset Function-----------------------------------------------
def reset_game(board_size=9, hp1=6, hp2=6, init_player=1):
    """
    重置游戏状态的通用函数
    board_size: 棋盘大小
    hp1: 玩家1初始血量
    hp2: 玩家2初始血量
    init_player: 先手玩家（1或-1）
    """
    global \
        game, \
        game_state, \
        player, \
        lock, \
        battle_animation_started, \
        pending_game_state, \
        pending_player

    # 创建新的游戏实例
    game = FourAscendGame(board_size=board_size, hp1=hp1, hp2=hp2)
    game_state = game.getInitBoard()
    player = init_player

    # 设置棋盘引用
    board.set_game_reference(game)
    board.syncFromPieces(game_state)
    board.start_time = pygame.time.get_ticks()

    # 重置动画状态
    battle_animation_started = False
    pending_game_state = None
    pending_player = None
    board.reset_battle_animation()
    board.place_animations = []

    # 重置锁和血量记录
    lock = 0
    board.last_hp1 = None
    board.last_hp2 = None

    # 重置AI相关状态（如果存在）
    if "ai_thinking_time" in globals():
        globals()["ai_thinking_time"] = 0

    menu_animation.reset()

    # 重置游戏结束状态
    board.end_time = None
    board.end_animation_scale = 0


reset_game()

# -------------------------------------------Main Loop-----------------------------------------------
while running:
    if click_cooldown > 0:
        click_cooldown -= clock.get_time()

    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    match state:
        case 0:  # TITLE
            continue_title = drawWelcome(screen, titleBackground_image, events)
            if not continue_title:
                state = MENU
                menu_animation.reset()

        case 1:  # MENU
            # 检查菜单动画是否完成
            menu_animation_finished = menu_animation.update()

            if not menu_animation_finished:
                # 显示菜单动画
                menu_animation.draw(screen, background_image)
            else:
                # 动画完成后才处理交互
                # 更新鼠标悬停状态
                mouseJudge(screen, mouse_pos)
                drawMenuPage(screen, background_image)

                # 处理点击
                for event in events:
                    if (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                        and click_cooldown <= 0
                    ):
                        new_state = gameJudge(mouse_pos)
                        if new_state != state:
                            state = new_state
                            click_cooldown = CLICK_COOLDOWN_TIME
                            lock = 0  # 重置锁状态
                            if state == PVE:
                                reset_game(9, 4, 8, random.choice([1, -1]))

                pygame.display.flip()

        case 2:  # PVP
            # 游戏主界面
            screen.fill(0xFFFFFF)
            screen.blit(background_image, (0, 0))

            pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = game_state

            delta_time = clock.get_time()

            board.drawUI(
                screen, game.hp1, game.hp2, game.max_hp1, game.max_hp2, delta_time
            )

            # 检查战斗动画是否结束
            if battle_animation_started and not board.is_battle_animation_active():
                if pending_game_state is not None and pending_player is not None:
                    game_state = pending_game_state
                    player = pending_player
                    board.syncFromPieces(game_state)  # 动画结束后同步棋盘状态
                    pending_game_state = None
                    pending_player = None
                    # 补充魔法植物
                    if np.sum(magic_plants) < 8:
                        game.spawn_magic_plants(game_state[0], game_state[1], 2)
                battle_animation_started = False
                lock = 0
            elif battle_animation_started:
                # 显示下一步的棋盘状态（但不包括魔法植物生成）
                if pending_game_state is not None:
                    board.syncFromPieces(pending_game_state)
                    # 绘制棋盘和棋子，但不显示下子指示
                    board.drawBoard(screen)
                    board.drawPiece(screen)
                    board.drawMagicPlants(screen)
                # 更新和绘制战斗动画
                board.update_battle_animation(delta_time)
                board.draw_battle_animation(screen)
            else:
                # 正常游戏逻辑
                # 检查鼠标位置并显示下子指示
                valid = board.checkMouse(screen, player)

                # 检查鼠标点击落子
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if (
                            board.check_menu_button_click(mouse_pos)
                            and click_cooldown <= 0
                        ):
                            reset_game()
                            state = MENU
                            click_cooldown = CLICK_COOLDOWN_TIME
                        elif valid and not lock and click_cooldown <= 0:
                            if (
                                board.check_menu_button_click(mouse_pos)
                                and click_cooldown <= 0
                            ):
                                reset_game()
                                state = MENU
                                click_cooldown = CLICK_COOLDOWN_TIME

                            pixel_pos = board.findPos()
                            row, col = board.pixel_to_board_index(pixel_pos)
                            action = row * board.game.board_size + col
                            valid_moves = game.getValidMoves(game_state, player)

                            if 0 <= action < len(valid_moves) and valid_moves[action]:
                                # 检查是否处于防御阶段
                                is_defense_turn = np.any(ascend_state == 1)

                                if is_defense_turn:
                                    # 记录下一个游戏状态，但不立即更新
                                    pending_game_state, pending_player = (
                                        game.getNextState(game_state, player, action)
                                    )
                                    battle_animation_started = True

                                    # 开始战斗动画
                                    attacking_player = -player  # 攻击方是另一个玩家

                                    # player=-player

                                    board.start_battle_animation(
                                        game_state, action, attacking_player, player
                                    )

                                else:
                                    # 正常落子，没有战斗动画
                                    board.add_place_animation(row, col, player)
                                    game_state, player = game.getNextState(
                                        game_state, player, action
                                    )
                                    board.syncFromPieces(game_state)

                                click_cooldown = CLICK_COOLDOWN_TIME
                            # 鼠标上锁
                            lock = 1
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        # 鼠标松开后解锁
                        lock = 0

                board.drawAscendAnimation(screen, -player)

                # 绘制棋子和魔法植物
                board.drawPiece(screen)
                board.drawMagicPlants(screen)
                # 绘制菜单按钮
                board.draw_menu_button(screen, mouse_pos)

            result = game.getGameEnded(game_state, player)
            if result is not None:
                if board.end_time is None:
                    board.set_game_end()
                total_time = (
                    (board.end_time - board.start_time) / 1000
                    if board.start_time
                    else 0
                )
                if board.drawEndBoard(
                    screen,
                    result,
                    state,
                    game.hp1,
                    game.hp2,
                    game.max_hp1,
                    game.max_hp2,
                    total_time,
                    events,
                ):
                    reset_game()

            pygame.display.flip()

        case 3:  # PVE - 添加AI对战逻辑
            # 游戏主界面
            screen.fill(0xFFFFFF)
            screen.blit(background_image, (0, 0))

            pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = game_state

            delta_time = clock.get_time()

            board.drawUI(
                screen, game.hp1, game.hp2, game.max_hp1, game.max_hp2, delta_time
            )

            # 检查战斗动画是否结束
            if battle_animation_started and not board.is_battle_animation_active():
                if pending_game_state is not None and pending_player is not None:
                    game_state = pending_game_state
                    player = pending_player
                    board.syncFromPieces(game_state)  # 动画结束后同步棋盘状态
                    pending_game_state = None
                    pending_player = None
                    # 补充魔法植物
                    if np.sum(magic_plants) < 8:
                        game.spawn_magic_plants(game_state[0], game_state[1], 2)
                battle_animation_started = False
                lock = 0
            elif battle_animation_started:
                # 显示下一步的棋盘状态（但不包括魔法植物生成）
                if pending_game_state is not None:
                    board.syncFromPieces(pending_game_state)
                    # 绘制棋盘和棋子，但不显示下子指示
                    board.drawBoard(screen)
                    board.drawPiece(screen)
                    board.drawMagicPlants(screen)
                # 更新和绘制战斗动画
                board.update_battle_animation(delta_time)
                board.draw_battle_animation(screen)
            else:
                # 正常游戏逻辑
                if player == 1:  # 玩家回合
                    # 检查鼠标位置并显示下子指示
                    valid = board.checkMouse(screen, player)

                    # 检查鼠标点击落子
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if (
                                board.check_menu_button_click(mouse_pos)
                                and click_cooldown <= 0
                            ):
                                reset_game()
                                state = MENU
                                menu_animation.reset()
                                click_cooldown = CLICK_COOLDOWN_TIME
                            elif valid and not lock and click_cooldown <= 0:
                                pixel_pos = board.findPos()
                                row, col = board.pixel_to_board_index(pixel_pos)
                                action = row * board.game.board_size + col
                                valid_moves = game.getValidMoves(game_state, player)

                                if (
                                    0 <= action < len(valid_moves)
                                    and valid_moves[action]
                                ):
                                    # 检查是否处于防御阶段
                                    is_defense_turn = np.any(ascend_state == 1)

                                    if is_defense_turn:
                                        # 记录下一个游戏状态，但不立即更新
                                        pending_game_state, pending_player = (
                                            game.getNextState(
                                                game_state, player, action
                                            )
                                        )
                                        battle_animation_started = True

                                        # 开始战斗动画
                                        attacking_player = -player  # 攻击方是另一个玩家

                                        board.start_battle_animation(
                                            game_state, action, attacking_player, player
                                        )
                                    else:
                                        # 正常落子，没有战斗动画
                                        board.add_place_animation(row, col, player)
                                        game_state, player = game.getNextState(
                                            game_state, player, action
                                        )
                                        board.syncFromPieces(game_state)

                                    click_cooldown = CLICK_COOLDOWN_TIME
                                # 鼠标上锁
                                lock = 1
                        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                            # 鼠标松开后解锁
                            lock = 0
                else:  # AI回合
                    if "ai_thinking_time" not in globals():
                        globals()["ai_thinking_time"] = random.randint(0, 500)
                    ai_thinking_time += delta_time

                    if ai_thinking_time >= 800:
                        if "ai_player" not in globals():
                            globals()["ai_player"] = StupidFourAscendPlayer(game)

                        action = ai_player.play(game_state)
                        row, col = (
                            action // board.game.board_size,
                            action % board.game.board_size,
                        )

                        is_defense_turn = np.any(ascend_state == 1)

                        if is_defense_turn:
                            pending_game_state, pending_player = game.getNextState(
                                game_state, player, action
                            )
                            battle_animation_started = True

                            attacking_player = -player
                            board.start_battle_animation(
                                game_state, action, attacking_player, player
                            )
                        else:
                            # 正常落子，没有战斗动画
                            board.add_place_animation(row, col, player)
                            game_state, player = game.getNextState(
                                game_state, player, action
                            )
                            board.syncFromPieces(game_state)

                        # 重置AI思考计时器
                        ai_thinking_time = random.randint(0, 500)
                        lock = 0
                    else:
                        font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                        thinking_text = font.render(
                            "Thinking...", True, (100, 100, 100)
                        )
                        screen.blit(thinking_text, (900, 100))
                        lock = 1

                board.drawAscendAnimation(screen, -player)

                # 绘制棋子和魔法植物
                board.drawPiece(screen)
                board.drawMagicPlants(screen)
                # 绘制菜单按钮
                board.draw_menu_button(screen, mouse_pos)

            result = game.getGameEnded(game_state, player)
            if result is not None:
                if board.end_time is None:
                    board.set_game_end()
                total_time = (
                    (board.end_time - board.start_time) / 1000
                    if board.start_time
                    else 0
                )
                if board.drawEndBoard(
                    screen,
                    result if player == -1 else -result,
                    state,
                    game.hp1,
                    game.hp2,
                    game.max_hp1,
                    game.max_hp2,
                    total_time,
                    events,
                ):
                    reset_game(9, 4, 8)

            pygame.display.flip()

        case 4:  # TEACH - 教学模式
            # 初始化教学数据（如果不存在）
            if "teaching_step" not in globals():
                globals()["teaching_step"] = 0
                # 创建教学用的游戏对象
                if "teaching_game" not in globals():
                    globals()["teaching_game"] = FourAscendGame()
                # 创建教学用的棋盘对象
                if "teaching_board" not in globals():
                    globals()["teaching_board"] = Board()
                    teaching_board.set_game_reference(teaching_game)

                # 初始化教学动画相关变量
                if "teaching_anim_playing" not in globals():
                    globals()["teaching_anim_playing"] = False
                if "teaching_anim_timer" not in globals():
                    globals()["teaching_anim_timer"] = 0
                if "teaching_animation_triggered" not in globals():
                    globals()["teaching_animation_triggered"] = {}
                # 添加动画准备阶段标记
                if "teaching_anim_preparing" not in globals():
                    globals()["teaching_anim_preparing"] = False

            # 获取当前步骤
            step = teaching_step
            game = teaching_game
            #board = teaching_board

            # 清除屏幕并绘制背景
            screen.fill(0xFFFFFF)
            screen.blit(background_image, (0, 0))

            # 绘制UI元素
            board.drawUI(screen, game.hp1, game.hp2, game.max_hp1, game.max_hp2)

            # 更新动画
            delta_time = clock.get_time()
            board.update_place_animations(delta_time)
            board.update_battle_animation(delta_time)

            # 更新动画计时器
            if teaching_anim_preparing:
                teaching_anim_timer += delta_time
                # 500ms延迟后开始播放动画
                if teaching_anim_timer > 500:
                    teaching_anim_preparing = False
                    teaching_anim_playing = True
                    teaching_anim_timer = 0
                    # 根据当前步骤触发相应的动画
                    if step == 2:
                        # 攻击动画
                        board.start_battle_animation(
                            teaching_state, 4 * board.game.board_size + 4, 1, 2
                        )
                    elif step == 3:
                        # 防御动画
                        board.start_battle_animation(
                            teaching_state, 4 * board.game.board_size + 5, -1, 1
                        )
            elif teaching_anim_playing:
                teaching_anim_timer += delta_time
                # 检查动画是否完成
                if (
                    not board.is_battle_animation_active()
                    and teaching_anim_timer > 1000
                ):
                    teaching_anim_playing = False

            # 绘制当前棋盘状态（棋子和魔法植物）
            # 在动画播放时不绘制正常棋盘，以避免重叠
            if not teaching_anim_playing:
                board.drawPiece(screen)
                board.drawMagicPlants(screen)

            # 绘制动画
            board.draw_place_animations(screen)
            board.draw_battle_animation(screen)

            # 根据动画状态和步骤绘制提示
            if step < 6 and not teaching_anim_playing and not teaching_anim_preparing:
                # 绘制下一步提示
                hint_font = pygame.font.Font("resource\\pixelfont.ttf", 24)
                hint_text = hint_font.render("点击屏幕继续...", True, (100, 100, 100))
                screen.blit(hint_text, (560, 660))
            # 绘制返回菜单按钮
            board.draw_menu_button(screen, mouse_pos)

            # 根据当前步骤设置教学内容
            if step == 0:
                # 步骤0：游戏简介
                title_font = pygame.font.Font("resource\\pixelfont.ttf", 48)
                title = title_font.render(
                    "欢迎来到4ASCEND!", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(title, (400, 50))

                content_font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                text1 = content_font.render(
                    "这是一款融合了四子棋与策略元素的对战游戏",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text2 = content_font.render(
                    "你的目标是将对手的血量降至0", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(text1, (250, 150))
                screen.blit(text2, (330, 200))

            elif step == 1:
                # 步骤1：基本规则 - 棋盘和落子
                title_font = pygame.font.Font("resource\\pixelfont.ttf", 48)
                title = title_font.render(
                    "游戏棋盘与落子", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(title, (430, 50))

                content_font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                text1 = content_font.render(
                    "• 游戏在9x9的棋盘上进行", True, (0, 0, 0), (255, 255, 255)
                )
                text2 = content_font.render(
                    "• 玩家轮流在空位上放置自己的棋子", True, (0, 0, 0), (255, 255, 255)
                )
                text3 = content_font.render(
                    "• 黑方先行，白方后行", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(text1, (250, 150))
                screen.blit(text2, (250, 200))
                screen.blit(text3, (250, 250))

                # 设置棋盘状态，显示几个示例棋子
                pieces = np.zeros((9, 9), dtype=np.int8)
                pieces[4, 4] = 1  # 中央黑棋
                pieces[3, 3] = 1  # 黑棋
                pieces[5, 5] = -1  # 白棋
                pieces[4, 5] = -1  # 白棋
                magic_plants = np.zeros((9, 9), dtype=np.int8)
                ascend_state = np.zeros((9, 9), dtype=np.bool_)
                teaching_state = (
                    pieces,
                    magic_plants,
                    ascend_state,
                    game.hp1,
                    game.hp2,
                    0,
                )
                board.syncFromPieces(teaching_state)

            elif step == 2:
                # 步骤2：攻击阶段
                title_font = pygame.font.Font("resource\\pixelfont.ttf", 48)
                title = title_font.render("攻击阶段", True, (0, 0, 0), (255, 255, 255))
                screen.blit(title, (500, 50))

                content_font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                text1 = content_font.render(
                    "• 当你放置棋子形成4个或更多连续棋子时",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text2 = content_font.render(
                    "• 这些棋子会被消除并进入'ASCEND'状态",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text3 = content_font.render(
                    "• ASCEND 状态的棋子会在下一轮发动攻击",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text4 = content_font.render(
                    "• 多个方向的连子会同时触发", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(text1, (250, 150))
                screen.blit(text2, (250, 200))
                screen.blit(text3, (250, 250))
                screen.blit(text4, (250, 300))

                # 设置棋盘状态，显示攻击示例
                pieces = np.zeros((9, 9), dtype=np.int8)
                magic_plants = np.zeros((9, 9), dtype=np.int8)
                ascend_state = np.zeros((9, 9), dtype=np.bool_)
                # 放置多个方向的连子，表示多方向连击
                for i in range(4):  # 横向4连
                    pieces[4, 2 + i] = 1
                    ascend_state[4, 2 + i] = True
                for i in range(4):  # 纵向4连
                    pieces[2 + i, 4] = 1
                    ascend_state[2 + i, 4] = True
                teaching_state = (
                    pieces,
                    magic_plants,
                    ascend_state,
                    game.hp1,
                    game.hp2,
                    0,
                )
                board.syncFromPieces(teaching_state)

                # 绘制升华动画（在动画未播放时显示）
                if not teaching_anim_playing:
                    board.drawAscendAnimation(screen, 1)  # 1表示攻击方

                # 触发攻击动画准备阶段（只触发一次）
                if (
                    step not in teaching_animation_triggered
                    and not teaching_anim_playing
                    and not teaching_anim_preparing
                ):
                    teaching_animation_triggered[step] = True
                    teaching_anim_preparing = True
                    teaching_anim_timer = 0

            elif step == 3:
                # 步骤3：防御阶段
                title_font = pygame.font.Font("resource\\pixelfont.ttf", 48)
                title = title_font.render("防御阶段", True, (0, 0, 0), (255, 255, 255))
                screen.blit(title, (500, 50))

                content_font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                text1 = content_font.render(
                    "• 当一方发动攻击后，另一方就会进入防御阶段",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text2 = content_font.render(
                    "• 防御方同样可以触发四连，获得防御力",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text3 = content_font.render(
                    "• 防御力与防御方连子数量成正比", True, (0, 0, 0), (255, 255, 255)
                )
                text4 = content_font.render(
                    "• 特殊规则：", True, (0, 0, 0), (255, 255, 255)
                )
                text5 = content_font.render(
                    "• 防御方可以在上一轮消除的棋子处放置自己的棋子",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text6 = content_font.render(
                    "• 此时这个位置的攻击将会无效化", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(text1, (250, 150))
                screen.blit(text2, (250, 200))
                screen.blit(text3, (250, 250))
                screen.blit(text4, (200, 350))
                screen.blit(text5, (200, 400))
                screen.blit(text6, (200, 450))

                # 设置棋盘状态，显示防御示例
                pieces = np.zeros((9, 9), dtype=np.int8)
                magic_plants = np.zeros((9, 9), dtype=np.int8)
                ascend_state = np.zeros((9, 9), dtype=np.bool_)
                # 白棋有升华棋子（防御方）
                for i in range(4):
                    pieces[3, 3 + i] = -1
                    ascend_state[3, 3 + i] = True
                # 黑棋在附近防御
                pieces[4, 5] = 1
                teaching_state = (
                    pieces,
                    magic_plants,
                    ascend_state,
                    game.hp1,
                    game.hp2,
                    0,
                )
                board.syncFromPieces(teaching_state)

                # 绘制升华动画（在动画未播放时显示）
                if not teaching_anim_playing:
                    board.drawAscendAnimation(screen, -1)  # -1表示防御方

                # 触发防御动画准备阶段（只触发一次）
                if (
                    step not in teaching_animation_triggered
                    and not teaching_anim_playing
                    and not teaching_anim_preparing
                ):
                    teaching_animation_triggered[step] = True
                    teaching_anim_preparing = True
                    teaching_anim_timer = 0

            elif step == 4:
                # 步骤4：魔法植物系统
                title_font = pygame.font.Font("resource\\pixelfont.ttf", 48)
                title = title_font.render("魔法植物", True, (0, 0, 0), (255, 255, 255))
                screen.blit(title, (500, 50))

                content_font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                text1 = content_font.render(
                    "• 棋盘上会随机生成黄色的魔法植物", True, (0, 0, 0), (255, 255, 255)
                )
                text2 = content_font.render(
                    "• 魔法植物可以增强棋子的攻击力或防御力",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text3 = content_font.render(
                    "• 每回合可能生成新的魔法植物", True, (0, 0, 0), (255, 255, 255)
                )
                text4 = content_font.render(
                    "• 占领魔法植物的棋子会获得特殊标记",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                screen.blit(text1, (250, 150))
                screen.blit(text2, (250, 200))
                screen.blit(text3, (250, 250))
                screen.blit(text4, (250, 300))

                # 设置棋盘状态，显示魔法植物
                pieces = np.zeros((9, 9), dtype=np.int8)
                magic_plants = np.zeros((9, 9), dtype=np.int8)
                ascend_state = np.zeros((9, 9), dtype=np.bool_)
                # 放置一些棋子和魔法植物
                pieces[4, 4] = 1
                pieces[4, 5] = 1  # 魔法植物上的棋子
                magic_plants[4, 5] = 1  # 魔法植物
                magic_plants[5, 4] = 1  # 魔法植物
                magic_plants[5, 5] = 1  # 魔法植物
                teaching_state = (
                    pieces,
                    magic_plants,
                    ascend_state,
                    game.hp1,
                    game.hp2,
                    0,
                )
                board.syncFromPieces(teaching_state)

            elif step == 5:
                # 步骤5：血量与胜利条件
                title_font = pygame.font.Font("resource\\pixelfont.ttf", 48)
                title = title_font.render(
                    "血量与胜利", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(title, (480, 50))

                content_font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                text1 = content_font.render(
                    "• 双方初始有6点血量", True, (0, 0, 0), (255, 255, 255)
                )
                text2 = content_font.render(
                    "• 当攻击超过防御时，对手会受到伤害",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text3 = content_font.render(
                    "• 伤害值 = 攻击力 - 防御力", True, (0, 0, 0), (255, 255, 255)
                )
                text4 = content_font.render(
                    "• 将对手血量降至0即可获胜！", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(text1, (250, 150))
                screen.blit(text2, (250, 200))
                screen.blit(text3, (250, 250))
                screen.blit(text4, (250, 300))

            elif step == 6:
                # 步骤6：结束教学
                title_font = pygame.font.Font("resource\\pixelfont.ttf", 48)
                title = title_font.render(
                    "教学完成！", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(title, (500, 50))

                content_font = pygame.font.Font("resource\\pixelfont.ttf", 36)
                text1 = content_font.render(
                    "现在你已经了解了4ASCEND的基本规则",
                    True,
                    (0, 0, 0),
                    (255, 255, 255),
                )
                text2 = content_font.render(
                    "点击MENU返回主菜单开始游戏吧！", True, (0, 0, 0), (255, 255, 255)
                )
                screen.blit(text1, (250, 150))
                screen.blit(text2, (250, 200))
                game.hp1 = 6
                game.hp2 = 6
            # 处理事件
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if board.check_menu_button_click(mouse_pos):
                        reset_game()
                        state = MENU
                    else:
                        # 切换到下一步教学
                        if (
                            step < 6
                            and not teaching_anim_playing
                            and not teaching_anim_preparing
                        ):
                            teaching_step += 1
                            # 重置动画状态，为下一步准备
                            teaching_anim_playing = False
                            teaching_anim_preparing = False
                            teaching_anim_timer = 0
                            board.reset_battle_animation()
                            # 清除已触发的动画标记，允许在新步骤中触发动画
                            if "teaching_animation_triggered" in globals():
                                teaching_animation_triggered = {}

            pygame.display.flip()

    clock.tick(60)

pygame.quit()
