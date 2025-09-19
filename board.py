# 负责棋盘显示
import pygame
import math
from battle_animation import BattleAnimation
from game_core import FourAscendGame

white_Chess_Image = pygame.image.load("resource\\white_Chess.png")
black_Chess_Image = pygame.image.load("resource\\black_Chess.png")
white_Chess_Plant_Image = pygame.image.load("resource\\white_Chess_Plant.png")
black_Chess_Plant_Image = pygame.image.load("resource\\black_Chess_Plant.png")
HP_Image = pygame.image.load("resource\\HP_Image.png")
Game_End_Image = pygame.image.load("resource\\Game_End_Image.png")


class Board:
    def __init__(self):
        self.Board_x_move = 20
        self.Board_y_move = 10

        self.XtoXstart = 220 + self.Board_x_move
        self.YtoXstart = 150 + self.Board_y_move
        self.XtoYstart = 180 + self.Board_x_move
        self.YtoYstart = 180 + self.Board_y_move

        self.Rowlenth = 490
        self.Collenth = 470
        self.Distance = 50
        self.Line_color = 0x838383

        self.CheckRadius = 24
        self.PieceRadius = 15
        self.All_Piece = []
        self.Piece_Color = 0

        self.Magic_plants = []
        self.Magic_plant_Color = 0xFFECA1

        self.LeftUP_Point = (461 - self.Board_x_move, 210 - self.Board_y_move)
        self.RightDown_Point = (871 - self.Board_x_move, 621 - self.Board_y_move)

        self.PlayerHead_Pos = (150, 70)
        self.EnemyHead_Pos = (1100, 70)

        self.Lock = 0
        self.ascend_state = None
        self.animation_time = 0

        self.place_animations = []

        # 受伤动画相关属性
        self.player1_hurt_animation = {
            "active": False,
            "duration": 0,
            "max_duration": 500,  # 动画持续时间(毫秒)
            "shake_amplitude": 8,  # 增加抖动幅度
            "red_alpha": 0,  # 红色遮罩透明度
        }
        self.player2_hurt_animation = {
            "active": False,
            "duration": 0,
            "max_duration": 500,
            "shake_amplitude": 8,  # 增加抖动幅度
            "red_alpha": 0,
        }

        self.last_hp1 = None
        self.last_hp2 = None

        self.menu_button_rect = pygame.Rect(20, 660, 120, 50)
        self.menu_button_hovered = False

        self.battle_animation = BattleAnimation(self)
        self.battle_animation_active = False
        self.game = None

        # 游戏结束相关属性
        self.end_time = None
        self.end_animation_scale = 0
        self.start_time = None
        self.restart_hovered = False

    def set_game_reference(self, game: FourAscendGame):
        self.game = game

    def start_battle_animation(
        self, game_state, defending_action, attacking_player, defending_player
    ):
        self.battle_animation_active = True
        self.battle_animation.start(
            game_state, defending_action, attacking_player, defending_player
        )

    def update_battle_animation(self, delta_time):
        if self.battle_animation_active:
            if not self.battle_animation.update(delta_time):
                self.battle_animation_active = False

    def draw_battle_animation(self, screen):
        if self.battle_animation_active:
            self.battle_animation.draw(screen)

    def is_battle_animation_active(self):
        return self.battle_animation_active

    def reset_battle_animation(self):
        self.battle_animation_active = False
        # 重置战斗动画内部状态
        if hasattr(self.battle_animation, "active"):
            self.battle_animation.active = False

    def add_place_animation(self, row, col, player):
        animation = {
            "row": row,
            "col": col,
            "player": player,
            "time": 0,
            "duration": 100,
        }
        self.place_animations.append(animation)

    def update_place_animations(self, delta_time):
        updated_animations = []
        for anim in self.place_animations:
            anim["time"] += delta_time
            if anim["time"] < anim["duration"]:
                updated_animations.append(anim)
        self.place_animations = updated_animations

    def draw_place_animations(self, screen):
        for anim in self.place_animations:
            progress = anim["time"] / anim["duration"]

            alpha = int(255 * min(1.0, progress * 2))
            scale = 1.2 - 0.2 * min(1.0, progress * 1.5)

            if anim["player"] == 1:
                chess_image = black_Chess_Image
            else:
                chess_image = white_Chess_Image

            original_size = chess_image.get_size()
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            scaled_image = pygame.transform.scale(chess_image, new_size)

            temp_surface = pygame.Surface(new_size, pygame.SRCALPHA)
            temp_surface.blit(scaled_image, (0, 0))
            temp_surface.set_alpha(alpha)

            pos_x = (
                self.LeftUP_Point[0] + anim["col"] * self.Distance - new_size[0] // 2
            )
            pos_y = (
                self.LeftUP_Point[1] + anim["row"] * self.Distance - new_size[1] // 2
            )

            screen.blit(temp_surface, (pos_x, pos_y))

    def draw_menu_button(self, screen, mouse_pos):
        self.menu_button_hovered = self.menu_button_rect.collidepoint(mouse_pos)

        if self.menu_button_hovered:
            button_color = (100, 100, 100)
        else:
            button_color = (70, 70, 70)

        pygame.draw.rect(screen, button_color, self.menu_button_rect)
        pygame.draw.rect(screen, (40, 40, 40), self.menu_button_rect, 2)

        font = pygame.font.Font("resource\\pixelfont.ttf", 36)
        text = font.render("MENU", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.menu_button_rect.center)
        screen.blit(text, text_rect)

    def check_menu_button_click(self, mouse_pos):
        return self.menu_button_rect.collidepoint(mouse_pos)

    def update_hurt_animations(self, delta_time, current_hp1, current_hp2):
        """更新受伤动画状态"""
        if self.last_hp1 is not None and current_hp1 < self.last_hp1:
            self.trigger_hurt_animation(1)

        if self.last_hp2 is not None and current_hp2 < self.last_hp2:
            self.trigger_hurt_animation(2)

        # 更新记录的血量
        self.last_hp1 = current_hp1
        self.last_hp2 = current_hp2

        # 更新动画状态
        for animation in [self.player1_hurt_animation, self.player2_hurt_animation]:
            if animation["active"]:
                animation["duration"] += delta_time

                # 计算动画进度 (0.0 到 1.0)
                progress = animation["duration"] / animation["max_duration"]

                if progress >= 1.0:
                    # 动画结束
                    animation["active"] = False
                    animation["duration"] = 0
                    animation["red_alpha"] = 0
                else:
                    # 计算红色遮罩透明度 (从高到低渐变)
                    animation["red_alpha"] = int(128 * (1.0 - progress))

    def trigger_hurt_animation(self, player):
        """触发指定玩家的受伤动画"""
        if player == 1:
            self.player1_hurt_animation["active"] = True
            self.player1_hurt_animation["duration"] = 0
            self.player1_hurt_animation["red_alpha"] = 128
        elif player == 2:
            self.player2_hurt_animation["active"] = True
            self.player2_hurt_animation["duration"] = 0
            self.player2_hurt_animation["red_alpha"] = 128

    def get_shake_offset(self, animation):
        """计算抖动偏移量"""
        if not animation["active"]:
            return 0, 0

        progress = animation["duration"] / animation["max_duration"]
        # 抖动在动画前30%时间内最强烈，然后快速衰减
        if progress < 0.3:
            shake_intensity = 1.0 - (progress / 0.3) * 0.5  # 从1.0衰减到0.5
        elif progress < 0.6:
            shake_intensity = 0.5 - ((progress - 0.3) / 0.3) * 0.5  # 从0.5衰减到0
        else:
            shake_intensity = 0

        if shake_intensity > 0:
            import random

            # 使用更大的随机范围，并增加频率
            amplitude = animation["shake_amplitude"]
            offset_x = random.randint(-amplitude, amplitude) * shake_intensity
            offset_y = random.randint(-amplitude, amplitude) * shake_intensity
            return int(offset_x), int(offset_y)
        return 0, 0

    def create_hurt_overlay(self, original_image, alpha_value):
        """创建只在非透明像素上显示的红色遮罩"""
        # 创建与原图像相同大小的Surface，支持alpha
        overlay = pygame.Surface(original_image.get_size(), pygame.SRCALPHA)

        # 遍历原图像的每个像素
        for x in range(original_image.get_width()):
            for y in range(original_image.get_height()):
                # 获取原图像在该位置的颜色和alpha值
                original_color = original_image.get_at((x, y))
                if original_color[3] > 0:  # 如果不是完全透明
                    # 在该位置设置红色，alpha值基于原图和受伤强度
                    red_alpha = min(255, int(alpha_value * (original_color[3] / 255.0)))
                    overlay.set_at((x, y), (255, 0, 0, red_alpha))

        return overlay

    def drawUI(self, screen, hp1=6, hp2=6, initial_hp1=6, initial_hp2=6, delta_time=16):
        """绘制棋盘及玩家状态"""
        self.update_hurt_animations(delta_time, hp1, hp2)
        self.update_place_animations(delta_time)

        self.drawState(screen, hp1, hp2, initial_hp1, initial_hp2)
        self.drawBoard(screen)

    def drawBoard(self, screen):
        # 绘制棋盘
        origin = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        xfirstLine_start = origin - pygame.Vector2(
            self.XtoXstart, self.YtoXstart
        )  # 横向绘制起点
        yfirstLine_start = origin - pygame.Vector2(
            self.XtoYstart, self.YtoYstart
        )  # 纵向绘制起点
        xlineLenth = pygame.Vector2(self.Rowlenth, 0)
        ylineLenth = pygame.Vector2(0, self.Collenth)

        for i in range(self.game.board_size):  # 横向棋盘线
            cur_start = xfirstLine_start + pygame.Vector2(0, self.Distance * i)
            pygame.draw.line(
                screen, self.Line_color, cur_start, cur_start + xlineLenth, 4
            )
        for i in range(self.game.board_size):  # 纵向棋盘线
            cur_start = yfirstLine_start + pygame.Vector2(self.Distance * i, 0)
            pygame.draw.line(
                screen, self.Line_color, cur_start, cur_start + ylineLenth, 4
            )

    def drawState(self, screen, hp1=6, hp2=6, initial_hp1=6, initial_hp2=6):
        # 玩家头像
        player_image = pygame.image.load("resource\\player.png")
        enemy_image = pygame.image.load("resource\\enemy.png")

        # 获取抖动偏移
        player1_shake_x, player1_shake_y = self.get_shake_offset(
            self.player1_hurt_animation
        )
        player2_shake_x, player2_shake_y = self.get_shake_offset(
            self.player2_hurt_animation
        )

        # 应用抖动偏移绘制头像
        player1_pos = (
            self.PlayerHead_Pos[0] + player1_shake_x,
            self.PlayerHead_Pos[1] + player1_shake_y,
        )
        player2_pos = (
            self.EnemyHead_Pos[0] + player2_shake_x,
            self.EnemyHead_Pos[1] + player2_shake_y,
        )

        screen.blit(player_image, player1_pos)
        screen.blit(enemy_image, player2_pos)

        if (
            self.player1_hurt_animation["active"]
            and self.player1_hurt_animation["red_alpha"] > 0
        ):
            hurt_overlay = self.create_hurt_overlay(
                player_image, self.player1_hurt_animation["red_alpha"]
            )
            screen.blit(hurt_overlay, player1_pos)

        if (
            self.player2_hurt_animation["active"]
            and self.player2_hurt_animation["red_alpha"] > 0
        ):
            hurt_overlay = self.create_hurt_overlay(
                enemy_image, self.player2_hurt_animation["red_alpha"]
            )
            screen.blit(hurt_overlay, player2_pos)

        # 玩家1血量条（头像下方）
        avatar_size_height = 50
        player1_x, player1_y = player1_pos
        bar_x = player1_x + 15
        bar_y = player1_y + avatar_size_height + 20
        screen.blit(HP_Image, (bar_x, bar_y))

        f = pygame.font.Font("resource\\pixelfont.ttf", 40)

        hp_text = f.render(f"{hp1}/{initial_hp1}", True, (0, 0, 0))
        text_rect = hp_text.get_rect(center=(player1_x + 35, bar_y + 60))
        screen.blit(hp_text, text_rect)

        # 玩家2血量条（头像下方）
        player2_x, player2_y = player2_pos
        bar_x2 = player2_x + 15
        bar_y2 = player2_y + avatar_size_height + 20
        screen.blit(HP_Image, (bar_x2, bar_y2))

        hp_text2 = f.render(f"{hp2}/{initial_hp2}", True, (0, 0, 0))
        text_rect2 = hp_text2.get_rect(center=(player2_x + 35, bar_y2 + 60))
        screen.blit(hp_text2, text_rect2)
        # 图片资源留空，未来可替换血条为图片

    def findPos(self):
        """定位到棋盘节点"""
        mousePos = pygame.mouse.get_pos()

        for i in range(
            self.LeftUP_Point[0], self.RightDown_Point[0] + 5, self.Distance
        ):
            for j in range(
                self.LeftUP_Point[1], self.RightDown_Point[1] + 5, self.Distance
            ):
                L = i - self.CheckRadius
                R = i + self.CheckRadius
                U = j + self.CheckRadius
                D = j - self.CheckRadius
                if (
                    mousePos[0] > L
                    and mousePos[0] < R
                    and mousePos[1] > D
                    and mousePos[1] < U
                ):
                    return pygame.Vector2(i, j)
        return pygame.Vector2(0, 0)

    def checkMouse(self, screen, player):
        """检查鼠标位置是否合法"""
        piecePos = self.findPos()
        if piecePos[0] != 0 and self.checkPiece(piecePos):
            if player == 1:
                pygame.draw.circle(screen, 0xE4080A, [piecePos[0], piecePos[1]], 20, 2)
            else:
                pygame.draw.circle(screen, 0x5697FF, [piecePos[0], piecePos[1]], 20, 2)
            return True
        return False

    def checkPiece(self, p: pygame.Vector2):
        """检查当前位置是否已经有棋子"""
        for i in self.All_Piece:
            piece_center_x = i[0][0] + 20
            piece_center_y = i[0][1] + 20
            if piece_center_x == p[0] and piece_center_y == p[1]:
                return False
        return True

    def drawPiece(self, screen):
        """绘制棋盘上的所有棋子"""
        animating_positions = set()
        for anim in self.place_animations:
            pos_x = self.LeftUP_Point[0] + anim["col"] * self.Distance - 20
            pos_y = self.LeftUP_Point[1] + anim["row"] * self.Distance - 20
            animating_positions.add((pos_x, pos_y))

        for i in self.All_Piece:
            piece_pos = (i[0][0], i[0][1])
            if piece_pos not in animating_positions:
                screen.blit(i[1], i[0])

        self.draw_place_animations(screen)

    def drawMagicPlants(self, screen):
        """绘制棋盘上的所有魔法植物"""
        if not self.Magic_plants:
            return

        # 更新动画时间，与 ascend 动画相同
        self.animation_time += 1

        for i in self.Magic_plants:
            # 计算缩放因子，与 ascend 动画相同
            scale_factor = 0.7 + 0.6 * abs(math.sin(self.animation_time / 24))

            # 创建原始矩形 Surface
            original_size = (10, 10)
            temp_surface = pygame.Surface(original_size)
            pygame.draw.rect(temp_surface, self.Magic_plant_Color, [0, 0, 10, 10])

            # 缩放 Surface
            new_size = (
                int(original_size[0] * scale_factor),
                int(original_size[1] * scale_factor),
            )
            scaled_surface = pygame.transform.scale(temp_surface, new_size)

            # 计算绘制位置（居中）
            pos_x = i[0] - new_size[0] // 2
            pos_y = i[1] - new_size[1] // 2

            # 绘制到屏幕，不改变透明度
            screen.blit(scaled_surface, (pos_x, pos_y))

    def pixel_to_board_index(self, pixel_pos):
        """将像素坐标转换为棋盘格坐标(row, col)"""
        x0, y0 = self.LeftUP_Point
        distance = self.Distance
        x, y = int(pixel_pos[0]), int(pixel_pos[1])
        col = round((x - x0) / distance)
        row = round((y - y0) / distance)
        return row, col

    def syncFromPieces(self, state):
        """根据核心数据pieces同步棋盘显示数据All_Piece"""
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = state
        self.All_Piece = []
        self.Magic_plants = []

        # 检查ascend状态是否发生变化，如果有新的ascend状态，重置动画时间
        import numpy as np

        if self.ascend_state is None or not np.array_equal(
            self.ascend_state, ascend_state
        ):
            if np.any(ascend_state == 1):  # 如果有新的ascend状态
                self.animation_time = 0  # 重置动画时间

        self.magic_plants = magic_plants
        self.ascend_state = ascend_state

        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                if pieces[row][col] == 1:
                    if magic_plants[row][col] == 1:
                        self.All_Piece.append(
                            [
                                [
                                    self.LeftUP_Point[0] + col * self.Distance - 20,
                                    self.LeftUP_Point[1] + row * self.Distance - 20,
                                ],
                                black_Chess_Plant_Image,
                            ]
                        )
                    else:
                        self.All_Piece.append(
                            [
                                [
                                    self.LeftUP_Point[0] + col * self.Distance - 20,
                                    self.LeftUP_Point[1] + row * self.Distance - 20,
                                ],
                                black_Chess_Image,
                            ]
                        )
                elif pieces[row][col] == -1:
                    if magic_plants[row][col] == 1:
                        self.All_Piece.append(
                            [
                                [
                                    self.LeftUP_Point[0] + col * self.Distance - 20,
                                    self.LeftUP_Point[1] + row * self.Distance - 20,
                                ],
                                white_Chess_Plant_Image,
                            ]
                        )
                    else:
                        self.All_Piece.append(
                            [
                                [
                                    self.LeftUP_Point[0] + col * self.Distance - 20,
                                    self.LeftUP_Point[1] + row * self.Distance - 20,
                                ],
                                white_Chess_Image,
                            ]
                        )

                if magic_plants[row][col] == 1 and pieces[row][col] == 0:
                    self.Magic_plants.append(
                        [
                            self.LeftUP_Point[0] + col * self.Distance,
                            self.LeftUP_Point[1] + row * self.Distance,
                        ]
                    )

    def drawAscendAnimation(self, screen, attacking_player):
        """绘制ascend状态的弹跳动画棋子"""
        if self.ascend_state is None:
            return

        # 更新动画时间
        self.animation_time += 1

        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                if self.ascend_state[row][col]:
                    # 根据攻击方决定棋子颜色
                    if attacking_player == 1:
                        chess_image = black_Chess_Image
                        if self.magic_plants[row][col] == 1:
                            chess_image = black_Chess_Plant_Image
                    else:
                        chess_image = white_Chess_Image
                        if self.magic_plants[row][col] == 1:
                            chess_image = white_Chess_Plant_Image

                    scale_factor = 0.9 + 0.1 * abs(math.sin(self.animation_time / 24))

                    # 缩放棋子图像
                    original_size = chess_image.get_size()
                    new_size = (
                        int(original_size[0] * scale_factor),
                        int(original_size[1] * scale_factor),
                    )
                    scaled_image = pygame.transform.scale(chess_image, new_size)

                    temp_surface = pygame.Surface(new_size, pygame.SRCALPHA)
                    temp_surface.blit(scaled_image, (0, 0))
                    temp_surface.set_alpha(
                        int(128 - scale_factor * 10)
                    )  # 设置透明度为0.5 (128/255)

                    pos_x = (
                        self.LeftUP_Point[0] + col * self.Distance - new_size[0] // 2
                    )
                    pos_y = (
                        self.LeftUP_Point[1] + row * self.Distance - new_size[1] // 2
                    )

                    screen.blit(temp_surface, (pos_x, pos_y))

    def drawEndBoard(
        self,
        screen,
        result,
        state,
        hp1,
        hp2,
        initial_hp1,
        initial_hp2,
        total_time,
        events,
    ):
        if self.end_time is None:
            return False

        current_time = pygame.time.get_ticks()
        if current_time - self.end_time < 1000:
            return False

        # 更新动画缩放
        self.end_animation_scale = min(1.0, self.end_animation_scale + 0.05)

        # 创建临时 Surface 来绘制所有内容，支持透明度
        temp_surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        temp_surface.blit(Game_End_Image, (0, 0))

        f = pygame.font.Font("resource\\pixelfont.ttf", 60)
        font = pygame.font.Font("resource\\pixelfont.ttf", 40)
        small_font = pygame.font.Font("resource\\pixelfont.ttf", 30)

        # 确定标题
        if state == 3:
            if result == 1:
                title_text = "AI Win!"
                title_color = (255, 0, 0)
            else:
                title_text = "Human Win!"
                title_color = (0, 0, 255)
        else:
            if result == 1:
                title_text = "Player 1 Win!"
                title_color = (0, 0, 255)
            else:
                title_text = "Player 2 Win!"
                title_color = (255, 0, 0)

        # 绘制标题
        title_font = f.render(title_text, True, title_color)
        title_rect = title_font.get_rect(center=(640, 150))
        temp_surface.blit(title_font, title_rect)

        # 绘制血量信息
        hp1_text = small_font.render(
            f"Player 1 HP: {hp1}/{initial_hp1}", True, (255, 255, 255)
        )
        hp1_rect = hp1_text.get_rect(center=(640, 250))
        temp_surface.blit(hp1_text, hp1_rect)

        hp2_text = small_font.render(
            f"Player 2 HP: {hp2}/{initial_hp2}", True, (255, 255, 255)
        )
        hp2_rect = hp2_text.get_rect(center=(640, 300))
        temp_surface.blit(hp2_text, hp2_rect)

        # 绘制总用时
        time_text = small_font.render(
            f"Total Time: {total_time:.1f} seconds", True, (255, 255, 255)
        )
        time_rect = time_text.get_rect(center=(640, 350))
        temp_surface.blit(time_text, time_rect)

        # 绘制重启按钮

        if self.restart_hovered:
            button_color = (100, 100, 100)
        else:
            button_color = (30, 30, 30)

        RESTART = font.render("RESTART", True, button_color)
        RESTART_rect = RESTART.get_rect(center=(640, 600))
        temp_surface.blit(RESTART, RESTART_rect)

        # 缩放并绘制到屏幕
        if self.end_animation_scale < 1.0:
            scaled_size = (
                int(1280 * self.end_animation_scale),
                int(720 * self.end_animation_scale),
            )
            scaled_surface = pygame.transform.scale(temp_surface, scaled_size)
            pos_x = (1280 - scaled_size[0]) // 2
            pos_y = (720 - scaled_size[1]) // 2
            screen.blit(scaled_surface, (pos_x, pos_y))
        else:
            screen.blit(temp_surface, (0, 0))

        # 检查鼠标点击事件
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.end_animation_scale < 1.0:
                    # 计算缩放后的按钮区域
                    scale = self.end_animation_scale
                    scaled_button_rect = (
                        int(RESTART_rect[0] * scale) + (1280 - int(1280 * scale)) // 2,
                        int(RESTART_rect[1] * scale) + (720 - int(720 * scale)) // 2,
                        int(RESTART_rect[2] * scale),
                        int(RESTART_rect[3] * scale),
                    )

                    if pygame.Rect(scaled_button_rect).collidepoint(event.pos):
                        return True
                else:
                    # 正常大小的按钮检测
                    if RESTART_rect.collidepoint(event.pos):
                        return True
            elif event.type == pygame.MOUSEMOTION:
                # 检查鼠标是否悬停在按钮上
                self.restart_hovered = RESTART_rect.collidepoint(event.pos)

        return False

    def set_game_end(self):
        self.end_time = pygame.time.get_ticks()
