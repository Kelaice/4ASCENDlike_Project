import numpy as np
import random


# 4ASCEND核心游戏逻辑类
class FourAscendGame:
    def __init__(self, board_size: int = 9, hp1: int = 6, hp2: int = 6):
        """
        初始化游戏参数
        board_size: 棋盘大小
        hp1, hp2: 双方初始血量
        """
        self.board_size = board_size
        self.max_hp1 = hp1
        self.max_hp2 = hp2
        self.hp1 = hp1
        self.hp2 = hp2
        self.plant_timer = 0
        self.grid_count = board_size * board_size

        self.DP1 = 0
        self.connect1 = False
        self.DP2 = 0
        self.connect2 = False

    def getInitBoard(self):
        """
        获取初始棋盘状态
        返回: (棋子矩阵, 魔法植物矩阵, 升华状态矩阵, 玩家1血量, 玩家2血量, 植物计时器)
        """
        pieces = np.zeros((self.board_size, self.board_size), dtype=np.int8)
        magic_plants = np.zeros((self.board_size, self.board_size), dtype=np.int8)
        ascend_state = np.zeros((self.board_size, self.board_size), dtype=np.bool_)
        return (
            pieces,
            magic_plants,
            ascend_state,
            self.hp1,
            self.hp2,
            self.plant_timer,
        )

    def getCanonicalForm(self, board, player):
        """
        返回标准化棋盘状态（用于AI训练）
        player=1时返回原始棋盘，player=-1时交换双方信息
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        if player == 1:
            return board
        else:
            return (-pieces, magic_plants, ascend_state, hp2, hp1, plant_timer)

    def getValidMoves(self, board, player):
        """
        获取当前玩家所有合法落子位置
        返回: 一维数组，1表示可落子，0表示不可落子
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        if (player == 1 and hp1 <= 0) or (player == -1 and hp2 <= 0):
            return np.zeros(self.grid_count, dtype=np.int8)
        return (pieces == 0).flatten().astype(np.int8)

    def getNextState(self, board, player, action):
        """
        根据玩家行动，返回下一步棋盘状态和下一个玩家
        action: 落子编号（0~80）
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        pieces = pieces.copy()
        magic_plants = magic_plants.copy()
        ascend_state = ascend_state.copy()

        row, col = action // self.board_size, action % self.board_size
        pieces[row][col] = player

        is_defense_turn = np.any(ascend_state == 1)

        if is_defense_turn:
            # 防御阶段
            defense_power, defense_connected = self.ascend(
                pieces,
                magic_plants,
                ascend_state,
                row,
                col,
                player,
                set_ascend_value=False,
            )
            ascend_state[row][col] = False
            attack_power = np.sum(ascend_state) + np.sum(magic_plants[ascend_state])
            damage = abs(attack_power - defense_power)

            # 结算血量
            if attack_power > defense_power:
                if player == 1:
                    hp1 -= damage
                else:
                    hp2 -= damage
            elif attack_power < defense_power:
                if player == 1:
                    hp2 -= damage
                else:
                    hp1 -= damage

            hp1 = max(0, hp1)
            hp2 = max(0, hp2)
            magic_plants[ascend_state == 1] = 0
            ascend_state.fill(0)
        else:
            # 攻击阶段
            self.ascend(
                pieces,
                magic_plants,
                ascend_state,
                row,
                col,
                player,
                set_ascend_value=True,
            )

        self.plant_timer += 1
        if self.plant_timer > 6:
            self.spawn_magic_plants(pieces, magic_plants, 2)
            self.plant_timer = 0

        # 返回最新棋盘状态和血量
        return (pieces, magic_plants, ascend_state, hp1, hp2, plant_timer), -player

    def getDefenseAnimationData(self, board, player, action):
        """
        获取防御阶段动画所需的数据，不修改游戏状态
        返回: (攻击威力, 防御威力, 攻击方玩家)
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        pieces_copy = pieces.copy()
        magic_plants_copy = magic_plants.copy()
        ascend_state_copy = ascend_state.copy()

        row, col = action // self.board_size, action % self.board_size
        pieces_copy[row][col] = player

        # 计算攻击威力（当前ascend状态，但排除被防御方覆盖的位置）
        attacking_player = -player  # 攻击方是另一个玩家

        # 如果防御方落子位置有ascend棋子，需要排除它
        adjusted_ascend_state = ascend_state.copy()
        adjusted_magic_plants = magic_plants.copy()

        if ascend_state[row][col]:
            # 防御方覆盖了攻击方的ascend棋子，这个棋子不参与攻击威力计算
            adjusted_ascend_state[row][col] = False
            # 相应的魔法植物加成也不算

        attack_power = np.sum(adjusted_ascend_state) + np.sum(
            adjusted_magic_plants[adjusted_ascend_state]
        )

        # 计算防御威力
        defense_power, defense_connected = self.ascend(
            pieces_copy,
            magic_plants_copy,
            ascend_state_copy,
            row,
            col,
            player,
            set_ascend_value=False,
        )

        return attack_power, defense_power, attacking_player

    def getGameEnded(self, board, player):
        """
        判断游戏是否结束，返回胜负结果
        None - 未结束
        1    - 玩家1胜
        -1   - 玩家2胜
        0    - 平局
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        if hp1 <= 0 and hp2 <= 0:
            return 0  # 平局
        elif hp1 <= 0:
            return -1  # 玩家2胜
        elif hp2 <= 0:
            return 1  # 玩家1胜
        if not np.any(pieces == 0):
            # 棋盘无空位，按血量判胜负
            if hp1 > hp2:
                return 1
            elif hp2 > hp1:
                return -1
            else:
                return 0
        return None

    def spawn_magic_plants(self, pieces, magic_plants, count):
        """
        在棋盘上随机生成魔法植物
        count: 生成数量
        """
        empty_indices = np.where((pieces == 0) & (magic_plants < 2))
        if len(empty_indices[0]) >= count:
            selected_idx = np.random.choice(len(empty_indices[0]), count, replace=False)
            for idx in selected_idx:
                i, j = empty_indices[0][idx], empty_indices[1][idx]
                magic_plants[i, j] += 1

    def ascend(
        self,
        pieces,
        magic_plants,
        ascend_state,
        row,
        col,
        player,
        set_ascend_value,
    ):
        total_power = 0
        successful_connection = False
        directions = np.array([(0, 1), (1, 0), (1, 1), (1, -1)], dtype=np.int8)

        for dx, dy in directions:
            connected_pos = []
            r, c = row + dx, col + dy
            while (
                0 <= r < self.board_size
                and 0 <= c < self.board_size
                and pieces[r, c] == player
            ):
                connected_pos.append((r, c))
                r, c = r + dx, c + dy

            r, c = row - dx, col - dy
            while (
                0 <= r < self.board_size
                and 0 <= c < self.board_size
                and pieces[r, c] == player
            ):
                connected_pos.append((r, c))
                r, c = r - dx, c - dy

            power = len(connected_pos)
            if power >= 3:
                successful_connection = True
                magic_bonus = sum(magic_plants[r, c] for r, c in connected_pos)
                total_power += power + magic_bonus

                for r, c in connected_pos:
                    if r != row or c != col:
                        pieces[r, c] = 0
                        ascend_state[r, c] = set_ascend_value
                        if not set_ascend_value:
                            magic_plants[r, c] = 0

        if successful_connection:
            total_power += 1 + magic_plants[row, col]
            pieces[row, col] = 0
            ascend_state[row, col] = set_ascend_value
            if not set_ascend_value:
                magic_plants[row, col] = 0

        return total_power, successful_connection


# 傻子AI玩家（带简单策略）
class StupidFourAscendPlayer:
    def __init__(self, game):
        """初始化傻子AI玩家"""
        self.game = game
        self.directions = np.array([(0, 1), (1, 0), (1, 1), (1, -1)], dtype=np.int8)

    def play(self, board):
        """
        根据局势选择落子位置
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        valid = self.game.getValidMoves(board, -1)
        valid_actions = [i for i in range(len(valid)) if valid[i]]
        if not valid_actions:
            return 0
        is_defense_turn = np.any(ascend_state == 1)
        if is_defense_turn:
            return self._choose_defense_move(board, valid_actions)
        else:
            return self._choose_attack_move(board, valid_actions)

    def _choose_defense_move(self, board, valid_actions, player=-1):
        """
        防御阶段：选择使自己伤害最小化、对方伤害最大化的位置
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        opponent_player = -player
        original_opponent_power = np.sum(ascend_state) + np.sum(
            magic_plants[ascend_state]
        )
        candidates = []
        for action in valid_actions:
            row, col = action // self.game.board_size, action % self.game.board_size
            test_pieces = pieces.copy()
            test_magic_plants = magic_plants.copy()
            test_ascend_state = ascend_state.copy()
            can_remove_opponent_piece = ascend_state[row, col] == opponent_player
            if can_remove_opponent_piece:
                test_ascend_state[row, col] = False
                reduced_opponent_power = np.sum(test_ascend_state) + np.sum(
                    magic_plants[test_ascend_state]
                )
            else:
                reduced_opponent_power = original_opponent_power
            test_pieces[row][col] = player
            defense_power, defense_connected = self.game.ascend(
                test_pieces,
                test_magic_plants,
                test_ascend_state,
                row,
                col,
                player,
                set_ascend_value=False,
            )
            final_opponent_power = reduced_opponent_power
            damage = abs(final_opponent_power - defense_power)
            if final_opponent_power > defense_power:
                my_damage = damage
                opponent_damage = 0
            elif final_opponent_power < defense_power:
                my_damage = 0
                opponent_damage = damage
            else:
                my_damage = 0
                opponent_damage = 0
            candidates.append((action, my_damage, opponent_damage))
        if not candidates:
            return valid_actions[0]
        # 找到最小 my_damage
        min_my_damage = min(c[1] for c in candidates)
        # 在最小 my_damage 中，选最大 opponent_damage
        best_candidates = [c for c in candidates if c[1] == min_my_damage]
        best_action = max(best_candidates, key=lambda c: c[2])[0]
        return best_action

    def _choose_attack_move(self, board, valid_actions):
        """
        攻击阶段：优先阻止对方高伤害位置，但检查安全；否则延长自己连线
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        # 尝试阻止高伤害位置
        max_damage = 0
        best_action = None
        for action in valid_actions:
            damage = self._calculate_potential_damage(board, action, 1)
            if damage > max_damage:
                max_damage = damage
                best_action = action
        if best_action is not None and max_damage > 0:
            if self._is_safe_to_attack(board, best_action):
                return best_action
        # 尝试连3
        three_move = self._find_three_connection_move(
            pieces, magic_plants, -1, valid_actions
        )
        if three_move is not None:
            return three_move
        # 尝试赢
        win_move = self._find_winning_move(pieces, magic_plants, -1, valid_actions)
        if win_move is not None:
            return win_move
        # 最佳位置
        return self._choose_best_position(pieces, magic_plants, -1, valid_actions)

    def _find_blocking_move(self, pieces, magic_plants, opponent_player, valid_actions):
        """
        寻找阻止对方连成4子的位置
        """
        for action in valid_actions:
            row, col = action // self.game.board_size, action % self.game.board_size
            if self._can_form_four(pieces, magic_plants, row, col, opponent_player):
                return action
        return None

    def _find_winning_move(self, pieces, magic_plants, player, valid_actions):
        """
        寻找能连成4子的位置
        """
        for action in valid_actions:
            row, col = action // self.game.board_size, action % self.game.board_size
            if self._can_form_four(pieces, magic_plants, row, col, player):
                return action
        return None

    def _find_three_connection_move(self, pieces, magic_plants, player, valid_actions):
        """
        寻找能连成3子的位置
        """
        best_action = None
        best_power = 0
        for action in valid_actions:
            row, col = action // self.game.board_size, action % self.game.board_size
            test_pieces = pieces.copy()
            test_magic_plants = magic_plants.copy()
            test_ascend_state = np.zeros_like(pieces, dtype=np.bool_)
            test_pieces[row][col] = player
            power, connected = self.game.ascend(
                test_pieces,
                test_magic_plants,
                test_ascend_state,
                row,
                col,
                player,
                set_ascend_value=True,
            )
            if connected and power > best_power:
                best_power = power
                best_action = action
        return best_action

    def _can_form_four(self, pieces, magic_plants, row, col, player):
        """
        检查在指定位置下棋是否能连成4子
        """
        test_pieces = pieces.copy()
        test_pieces[row][col] = player
        for dx, dy in self.directions:
            count = 1
            r, c = row + dx, col + dy
            while (
                0 <= r < self.game.board_size
                and 0 <= c < self.game.board_size
                and test_pieces[r, c] == player
            ):
                count += 1
                r, c = r + dx, c + dy
            r, c = row - dx, col - dy
            while (
                0 <= r < self.game.board_size
                and 0 <= c < self.game.board_size
                and test_pieces[r, c] == player
            ):
                count += 1
                r, c = r - dx, c - dy
            if count >= 4:
                return True
        return False

    def _choose_best_position(self, pieces, magic_plants, player, valid_actions):
        """
        选择最佳位置（启发式评估）
        """
        best_action = valid_actions[0]
        best_score = float("-inf")
        for action in valid_actions:
            row, col = action // self.game.board_size, action % self.game.board_size
            score = self._evaluate_position(pieces, magic_plants, row, col, player)
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

    def _evaluate_position(self, pieces, magic_plants, row, col, player):
        """
        评估位置价值
        """
        score = 0
        score += magic_plants[row][col] * 2
        center = self.game.board_size // 2
        distance_to_center = abs(row - center) + abs(col - center)
        score += max(0, center - distance_to_center)
        for dx, dy in self.directions:
            line_score = self._evaluate_line(pieces, row, col, dx, dy, player)
            score += line_score
        return score

    def _evaluate_line(self, pieces, row, col, dx, dy, player):
        """
        评估某个方向的连接潜力
        """
        score = 0
        my_pieces = 0
        empty_spaces = 0
        opponent_pieces = 0
        for direction in [1, -1]:
            r, c = row + direction * dx, col + direction * dy
            for _ in range(3):
                if 0 <= r < self.game.board_size and 0 <= c < self.game.board_size:
                    if pieces[r][c] == player:
                        my_pieces += 1
                    elif pieces[r][c] == 0:
                        empty_spaces += 1
                    else:
                        opponent_pieces += 1
                        break
                    r, c = r + direction * dx, c + direction * dy
                else:
                    break
        if opponent_pieces == 0:
            if my_pieces >= 2:
                score += 10 * my_pieces
            elif my_pieces == 1:
                score += 3
            score += empty_spaces
        return score

    def _calculate_potential_damage(self, board, action, opponent_player):
        """
        计算对方下子后的潜在攻击威力
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        row, col = action // self.game.board_size, action % self.game.board_size
        test_pieces = pieces.copy()
        test_magic_plants = magic_plants.copy()
        test_ascend_state = ascend_state.copy()
        test_pieces[row][col] = opponent_player
        attack_power, _ = self.game.ascend(
            test_pieces,
            test_magic_plants,
            test_ascend_state,
            row,
            col,
            opponent_player,
            set_ascend_value=True,
        )
        return attack_power

    def _is_safe_to_attack(self, board, action):
        """
        检查下子后是否会导致自己受到伤害
        """
        pieces, magic_plants, ascend_state, hp1, hp2, plant_timer = board
        row, col = action // self.game.board_size, action % self.game.board_size
        test_pieces = pieces.copy()
        test_magic_plants = magic_plants.copy()
        test_ascend_state = ascend_state.copy()
        test_pieces[row][col] = -1  # 自己是 -1
        attack_power, _ = self.game.ascend(
            test_pieces,
            test_magic_plants,
            test_ascend_state,
            row,
            col,
            -1,
            set_ascend_value=True,
        )
        if attack_power == 0:
            return True  # 没有触发，不会有伤害
        # 触发了，模拟对手防御
        opponent_ai = StupidFourAscendPlayer(self.game)
        valid = self.game.getValidMoves((test_pieces, test_magic_plants, test_ascend_state, hp1, hp2, plant_timer), 1)
        valid_actions = [i for i in range(len(valid)) if valid[i]]
        if not valid_actions:
            return True
        defense_action = opponent_ai._choose_defense_move((test_pieces, test_magic_plants, test_ascend_state, hp1, hp2, plant_timer), valid_actions, 1)
        # 模拟对手下子
        d_row, d_col = defense_action // self.game.board_size, defense_action % self.game.board_size
        test_pieces2 = test_pieces.copy()
        test_magic_plants2 = magic_plants.copy()
        test_ascend_state2 = test_ascend_state.copy()
        test_pieces2[d_row][d_col] = 1
        defense_power, _ = self.game.ascend(
            test_pieces2,
            test_magic_plants2,
            test_ascend_state2,
            d_row,
            d_col,
            1,
            set_ascend_value=False,
        )
        # 计算伤害
        if attack_power > defense_power:
            return False  # 自己受到伤害
        else:
            return True
