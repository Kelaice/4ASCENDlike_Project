import pygame
import math
import random
import numpy as np

# 导入游戏资源
white_Chess_Image = pygame.image.load("resource\\white_Chess.png")
black_Chess_Image = pygame.image.load("resource\\black_Chess.png")
white_Chess_Plant_Image = pygame.image.load("resource\\white_Chess_Plant.png")
black_Chess_Plant_Image = pygame.image.load("resource\\black_Chess_Plant.png")


class BattleAnimation:
    def __init__(self, board):
        self.board = board
        self.active = False
        self.phase = "FLYING_OUT"  # 动画阶段：FLYING_OUT, COLLIDING, ATTACKING

        # 存储飞出的棋子
        self.attacking_pieces = []  # 攻击方棋子
        self.defending_pieces = []  # 防御方棋子

        # 当前碰撞对
        self.current_collision_pair = None

        # 物理常量
        self.COLLISION_RADIUS = 24
        self.ATTRACTION_STRENGTH = 200
        self.REPULSION_STRENGTH = 100

        # 跟踪已碰撞的棋子对
        self.collided_pairs = set()

        # 标记是否所有碰撞已完成
        self.collisions_completed = False

        self.target_player = 0
        self.attacking_player = 0

        # 添加飞出阶段计时器
        self.timer = 0
        self.FLYING_DURATION = 300
        self.ATTACKING_DURATION = 100

        # 碰撞动画列表
        self.collision_animations = []

    def start(self, game_state, defending_action, attacking_player, defending_player):
        """开始战斗动画"""
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = game_state
        self.active = True
        self.phase = "FLYING_OUT"
        self.attacking_pieces = []
        self.defending_pieces = []
        self.current_collision_pair = None
        self.collided_pairs = set()
        self.collisions_completed = False
        self.attacking_player = attacking_player

        # 重置飞出阶段计时器
        self.timer = 0

        # 重置碰撞动画列表
        self.collision_animations = []

        # 计算防御方下子位置
        board_size = len(pieces)
        defend_row, defend_col = (
            defending_action // board_size,
            defending_action % board_size,
        )

        # 收集攻击方的ascend棋子（初始的ascend_state=1的全部是攻击方）
        for row in range(board_size):
            for col in range(board_size):
                # 排除防御方下子的位置
                if row == defend_row and col == defend_col:
                    continue

                if ascend_state[row][col]:
                    # 将棋盘坐标转换为像素坐标
                    pixel_x = self.board.LeftUP_Point[0] + col * self.board.Distance
                    pixel_y = self.board.LeftUP_Point[1] + row * self.board.Distance

                    # 确定棋子类型（所有ascend_state=1的都是攻击方）
                    has_plant = magic_plants[row][col] == 1

                    # 计算向两侧的随机初速度
                    angle = (random.random() - 0.5) / 3 * math.pi + (
                        math.pi if attacking_player == 1 else 0
                    )
                    speed = 10 + random.random() * 5
                    vx = math.cos(angle) * speed
                    vy = -math.sin(angle) * speed

                    # 添加棋子到攻击方数组
                    piece = {
                        "x": pixel_x,
                        "y": pixel_y,
                        "vx": vx,
                        "vy": vy,
                        "ax": 0,
                        "ay": 0,
                        "player": attacking_player,
                        "has_plant": has_plant,
                        "alive": True,
                        "original_row": row,
                        "original_col": col,
                    }
                    self.attacking_pieces.append(piece)

        # 处理防御方的连子判断
        # 为了进行连子判断，需要复制游戏状态
        pieces_copy = pieces.copy()
        magic_plants_copy = magic_plants.copy()
        ascend_state_copy = np.zeros_like(ascend_state)

        # 如果board有game引用，使用它的ascend方法进行连子判断
        if hasattr(self.board, "game") and hasattr(self.board.game, "ascend"):
            # 调用ascend方法判断防御方是否成功连子
            defense_power, defense_connected = self.board.game.ascend(
                pieces_copy,
                magic_plants_copy,
                ascend_state_copy,
                defend_row,
                defend_col,
                defending_player,
                set_ascend_value=True,
            )

            # 如果成功连子，收集防御方的ascend棋子
            if defense_connected:
                for row in range(board_size):
                    for col in range(board_size):
                        if ascend_state_copy[row][col]:
                            # 将棋盘坐标转换为像素坐标
                            pixel_x = (
                                self.board.LeftUP_Point[0] + col * self.board.Distance
                            )
                            pixel_y = (
                                self.board.LeftUP_Point[1] + row * self.board.Distance
                            )

                            # 确定棋子类型
                            has_plant = magic_plants_copy[row][col] == 1

                            # 计算向两侧的随机初速度
                            angle = (random.random() - 0.5) / 3 * math.pi + (
                                math.pi if attacking_player != 1 else 0
                            )
                            speed = 10 + random.random() * 5
                            vx = math.cos(angle) * speed
                            vy = -math.sin(angle) * speed  # 向上飞

                            # 添加棋子到防御方数组
                            piece = {
                                "x": pixel_x,
                                "y": pixel_y,
                                "vx": vx,
                                "vy": vy,
                                "ax": 0,
                                "ay": 0,
                                "player": defending_player,
                                "has_plant": has_plant,
                                "alive": True,
                                "original_row": row,
                                "original_col": col,
                            }
                            self.defending_pieces.append(piece)

    def update(self, delta_time):
        """更新动画状态"""
        if not self.active:
            return False

        # 根据当前阶段执行不同的更新逻辑
        if self.phase == "FLYING_OUT":
            self._update_flying_out(delta_time)
        elif self.phase == "COLLIDING":
            self._update_colliding(delta_time)
        elif self.phase == "ATTACKING":
            self._update_attacking(delta_time)

        # 更新碰撞动画
        self._update_collision_animations(delta_time)

        return self.active

    def _update_flying_out(self, delta_time):
        """更新棋子飞出阶段"""
        self.timer += delta_time

        # 计算斥力
        all_pieces = self.attacking_pieces + self.defending_pieces
        for piece in all_pieces:
            if not piece["alive"]:
                continue
            piece["ax"] = 0
            piece["ay"] = 0

        for i in range(len(all_pieces)):
            for j in range(i + 1, len(all_pieces)):
                piece1 = all_pieces[i]
                piece2 = all_pieces[j]
                if not piece1["alive"] or not piece2["alive"]:
                    continue
                dx = piece2["x"] - piece1["x"]
                dy = piece2["y"] - piece1["y"]
                dist = math.sqrt(dx**2 + dy**2) + 1
                force = self.REPULSION_STRENGTH / (dist**2)
                fx = force * dx / dist
                fy = force * dy / dist
                piece1["ax"] -= fx
                piece1["ay"] -= fy
                piece2["ax"] += fx
                piece2["ay"] += fy

        # 更新棋子位置和速度
        for pieces_list in [self.attacking_pieces, self.defending_pieces]:
            for piece in pieces_list:
                if not piece["alive"]:
                    continue

                # 应用斥力加速度
                piece["vx"] += piece["ax"]
                piece["vy"] += piece["ay"]

                piece["vx"] *= 0.9
                piece["vy"] *= 0.9
                piece["x"] += piece["vx"]
                piece["y"] += piece["vy"]

        if self.timer >= self.FLYING_DURATION:
            self.timer = 0
            self.phase = "COLLIDING"
            self._select_next_collision_pair()

    def _update_colliding(self, delta_time):
        """更新棋子碰撞阶段"""
        # 如果没有活跃的碰撞对，尝试选择新的
        if self.current_collision_pair is None:
            if not self._select_next_collision_pair():
                self.timer += delta_time
                # 没有更多可碰撞的棋子对，进入攻击阶段
                if self.timer >= self.ATTACKING_DURATION:
                    self.timer = 0
                    self.phase = "ATTACKING"
                    self._prepare_attacks()
                return
        else:
            # 更新当前碰撞对的物理状态
            piece1, piece2 = self.current_collision_pair

            # 检查两个棋子是否还活着
            if not piece1["alive"] or not piece2["alive"]:
                self.current_collision_pair = None
                return

            # 计算两个棋子之间的距离
            dx = piece2["x"] - piece1["x"]
            dy = piece2["y"] - piece1["y"]
            distance = math.sqrt(dx * dx + dy * dy)

            # 始终应用吸引力，直到碰撞发生
            if distance > 0:
                dir_x = dx / (10 + distance**2)
                dir_y = dy / (10 + distance**2)
            else:
                dir_x, dir_y = 0, 0

            # 应用吸引力
            piece1["ax"] = dir_x * self.ATTRACTION_STRENGTH
            piece2["ax"] = -dir_x * self.ATTRACTION_STRENGTH
            piece1["ay"] = dir_y * self.ATTRACTION_STRENGTH
            piece2["ay"] = -dir_y * self.ATTRACTION_STRENGTH

            # 更新速度和位置 - 添加这部分代码解决静止问题
            piece1["vx"] += piece1["ax"]
            piece1["vy"] += piece1["ay"]
            piece2["vx"] += piece2["ax"]
            piece2["vy"] += piece2["ay"]

            # 更新位置
            piece1["x"] += piece1["vx"]
            piece1["y"] += piece1["vy"]
            piece2["x"] += piece2["vx"]
            piece2["y"] += piece2["vy"]

            # 检测碰撞
            if distance < self.COLLISION_RADIUS * 2:
                self._handle_collision(piece1, piece2)
                self.current_collision_pair = None

        # 更新棋子位置和速度
        for pieces_list in [self.attacking_pieces, self.defending_pieces]:
            for piece in pieces_list:
                if not piece["alive"]:
                    continue

                piece["vx"] *= 0.99
                piece["vy"] *= 0.99
                piece["x"] += piece["vx"]
                piece["y"] += piece["vy"]

    def _update_attacking(self, delta_time):
        """更新棋子攻击头像阶段"""
        # 检查是否还有活跃的棋子
        active_pieces = 0
        for pieces_list in [self.attacking_pieces, self.defending_pieces]:
            active_pieces += sum(1 for p in pieces_list if p["alive"])

        if active_pieces == 0 and len(self.collision_animations) == 0:
            # 所有攻击都已完成，结束动画
            self.active = False
            return

        # 分别处理攻击方和防御方的棋子，确保加速度按索引逐渐增加
        for pieces_list in [self.attacking_pieces, self.defending_pieces]:
            for i, piece in enumerate(pieces_list):
                if not piece["alive"]:
                    continue

                # 确定攻击目标（对方头像）
                if piece["player"] == 1:  # 攻击方是玩家1，攻击玩家2的头像
                    target_x, target_y = self.board.EnemyHead_Pos
                    self.target_player = 2
                else:  # 攻击方是玩家2，攻击玩家1的头像
                    target_x, target_y = self.board.PlayerHead_Pos
                    self.target_player = 1

                # 计算方向
                dx = target_x - piece["x"]
                dy = target_y - piece["y"] + 40
                distance = math.sqrt(dx * dx + dy * dy)

                # 如果距离大于0，计算方向向量
                if distance > 0:
                    dir_x = dx / distance**2
                    dir_y = dy / distance**2
                else:
                    dir_x, dir_y = 0, 0

                acceleration = 800 + (i * 400)
                piece["ax"] = dir_x * acceleration
                piece["ay"] = dir_y * acceleration

                # 更新速度和位置
                piece["vx"] *= 0.9
                piece["vy"] *= 0.9
                piece["vx"] += piece["ax"]
                piece["vy"] += piece["ay"]
                piece["x"] += piece["vx"]
                piece["y"] += piece["vy"]

                # 检查是否碰撞到对方头像
                if distance < 80:
                    self._handle_head_attack(piece)

    def _select_next_collision_pair(self):
        """选择下一对要碰撞的棋子"""
        # 过滤出活跃的棋子
        active_attacking = [p for p in self.attacking_pieces if p["alive"]]
        active_defending = [p for p in self.defending_pieces if p["alive"]]

        # 检查是否还有可碰撞的棋子
        if not active_attacking or not active_defending:
            return False

        # 找到最远的一对棋子
        min_distance = float("inf")
        selected_pair = None

        for piece1 in active_attacking:
            for piece2 in active_defending:
                # 检查这对棋子是否已经碰撞过
                pair_id = tuple(sorted([id(piece1), id(piece2)]))
                if pair_id in self.collided_pairs:
                    continue

                # 计算距离
                dx = piece2["x"] - piece1["x"]
                dy = piece2["y"] - piece1["y"]
                distance = math.sqrt(dx * dx + dy * dy)

                # 更新最远的一对
                if distance < min_distance:
                    min_distance = distance
                    selected_pair = (piece1, piece2)

        # 如果找到了合适的配对
        if selected_pair is not None:
            piece1, piece2 = selected_pair
            pair_id = tuple(sorted([id(piece1), id(piece2)]))
            self.collided_pairs.add(pair_id)
            self.current_collision_pair = selected_pair
            return True

        # 没有找到合适的配对
        return False

    def _handle_collision(self, piece1, piece2):
        """处理棋子之间的碰撞"""
        # 计算碰撞中心位置
        center_x = (piece1["x"] + piece2["x"]) / 2
        center_y = (piece1["y"] + piece2["y"]) / 2

        # 添加碰撞动画
        self.collision_animations.append(
            {
                "x": center_x,
                "y": center_y,
                "radius": 0,
                "alpha": 255,
                "max_radius": 60,
                "duration": 200,
                "elapsed": 0,
            }
        )

        # 如果一个有魔法植物而另一个没有，生成新棋子
        if piece1["has_plant"] != piece2["has_plant"]:
            # 创建新棋子，位置在两个棋子之间
            new_x = (piece1["x"] + piece2["x"]) / 2
            new_y = (piece1["y"] + piece2["y"]) / 2

            # 新棋子的玩家属性由攻击方决定
            new_player = piece1["player"] if piece1["has_plant"] else piece2["player"]

            # 给新棋子一个随机初速度
            angle = random.random() * 2 * math.pi
            speed = 0
            new_vx = math.cos(angle) * speed
            new_vy = math.sin(angle) * speed

            # 创建新棋子
            new_piece = {
                "x": new_x,
                "y": new_y,
                "vx": new_vx,
                "vy": new_vy,
                "ax": 0,
                "ay": 0,
                "player": new_player,
                "has_plant": False,
                "alive": True,
                "original_row": -1,  # 标记为碰撞生成的棋子
                "original_col": -1,
            }

            print(new_piece)

            # 根据玩家添加到相应的数组
            if new_player == self.attacking_player:
                self.attacking_pieces.append(new_piece)
            else:
                self.defending_pieces.append(new_piece)

        # 移除立即将棋子标记为非活跃状态的代码
        # 让棋子继续参与后续的碰撞
        piece1["alive"] = False
        piece2["alive"] = False

    def _prepare_attacks(self):
        """准备对头像的攻击"""
        # 这里可以添加一些准备逻辑
        pass

    def _handle_head_attack(self, piece):
        """处理对头像的攻击"""
        # 标记棋子为非活跃状态
        piece["alive"] = False

        damage = 1 + (1 if piece["has_plant"] else 0)

        # 更新目标玩家的HP
        if hasattr(self.board, "game"):
            if self.target_player == 1:
                # 攻击玩家1，减少玩家1的HP
                if hasattr(self.board.game, "hp1"):
                    self.board.game.hp1 = self.board.game.hp1 - damage
                # 触发受伤动画
                self.board.trigger_hurt_animation(1)
            else:
                # 攻击玩家2，减少玩家2的HP
                if hasattr(self.board.game, "hp2"):
                    self.board.game.hp2 = self.board.game.hp2 - damage
                # 触发受伤动画
                self.board.trigger_hurt_animation(2)

    def draw(self, screen):
        """绘制战斗动画"""
        if not self.active:
            return

        # 绘制碰撞动画（在棋子后面）
        for anim in self.collision_animations:
            # 创建半透明表面
            surf = pygame.Surface(
                (anim["max_radius"] * 2, anim["max_radius"] * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                surf,
                (255, 255, 255, anim["alpha"]),
                (anim["max_radius"], anim["max_radius"]),
                int(anim["radius"]),
            )
            screen.blit(
                surf,
                (
                    int(anim["x"] - anim["max_radius"]),
                    int(anim["y"] - anim["max_radius"]),
                ),
            )

        # 绘制所有活跃的棋子
        for pieces_list in [self.attacking_pieces, self.defending_pieces]:
            for piece in pieces_list:
                if not piece["alive"]:
                    continue

                # 选择合适的棋子图像
                if piece["player"] == 1:
                    if piece["has_plant"]:
                        image = black_Chess_Plant_Image
                    else:
                        image = black_Chess_Image
                else:
                    if piece["has_plant"]:
                        image = white_Chess_Plant_Image
                    else:
                        image = white_Chess_Image

                # 绘制棋子
                pos_x = int(piece["x"] - image.get_width() // 2)
                pos_y = int(piece["y"] - image.get_height() // 2)
                screen.blit(image, (pos_x, pos_y))

    def _update_collision_animations(self, delta_time):
        """更新碰撞动画"""
        for anim in self.collision_animations[:]:
            anim["elapsed"] += delta_time
            progress = anim["elapsed"] / anim["duration"]
            if progress >= 1:
                self.collision_animations.remove(anim)
            else:
                anim["radius"] = progress * anim["max_radius"]
                anim["alpha"] = int(255 * (1 - progress))
