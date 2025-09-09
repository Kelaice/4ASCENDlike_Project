#负责棋盘显示
import pygame

white_Chess_Image = pygame.image.load("resource\\white_Chess.png")
black_Chess_Image = pygame.image.load("resource\\black_Chess.png")
white_Chess_Plant_Image = pygame.image.load("resource\\white_Chess_Plant.png")
black_Chess_Plant_Image = pygame.image.load("resource\\black_Chess_Plant.png")


class Board:
    def __init__(self):
        self.Boardsize = 9
        self.Board_x_move = 20
        self.Board_y_move = 10

        self.XtoXstart = 220 +self.Board_x_move
        self.YtoXstart = 150 +self.Board_y_move
        self.XtoYstart = 180 +self.Board_x_move
        self.YtoYstart = 180 +self.Board_y_move

        self.Rowlenth = 490
        self.Collenth = 470
        self.Distance = 50
        self.Line_color = 0x838383

        self.CheckRidus = 10
        self.PieceRidus = 15
        self.All_Piece = []
        self.Piece_Color = 0

        self.Magic_plants = []
        self.Magic_plant_Color = 0xFFECA1

        self.LeftUP_Point = (461 -self.Board_x_move, 210 -self.Board_y_move)
        self.RightDown_Point = (871 -self.Board_x_move, 621 -self.Board_y_move)

        self.PlayerHead_Pos = (150,70)
        self.EnemyHead_Pos = (1100,70)

        self.Lock = 0

    def drawUI(self, screen, hp1=6, hp2=6, initial_hp1=6, initial_hp2=6):
        '''绘制棋盘及玩家状态'''
        self.drawState(screen, hp1, hp2, initial_hp1, initial_hp2)
        self.drawBoard(screen)

    def drawBoard(self,screen):
        #绘制棋盘
        origin = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)
        xfirstLine_start = origin-pygame.Vector2(self.XtoXstart,self.YtoXstart)#横向绘制起点
        yfirstLine_start = origin-pygame.Vector2(self.XtoYstart,self.YtoYstart)#纵向绘制起点
        xlineLenth = pygame.Vector2(self.Rowlenth,0)
        ylineLenth = pygame.Vector2(0,self.Collenth)

        for i in range(self.Boardsize):#横向棋盘线
            cur_start = xfirstLine_start+pygame.Vector2(0,self.Distance*i)
            pygame.draw.line(screen,self.Line_color,cur_start,cur_start+xlineLenth,4)
        for i in range(self.Boardsize):#纵向棋盘线
            cur_start = yfirstLine_start+pygame.Vector2(self.Distance*i,0)
            pygame.draw.line(screen,self.Line_color,cur_start,cur_start+ylineLenth,4)

    def drawState(self,screen,hp1=6,hp2=6,initial_hp1=6,initial_hp2=6):
        # 玩家头像
        player_image = pygame.image.load("resource\\player.png")
        enemy_image = pygame.image.load("resource\\enemy.png")
        screen.blit(player_image,self.PlayerHead_Pos)
        screen.blit(enemy_image,self.EnemyHead_Pos)
        # 玩家1血量条（头像下方）
        bar_width = 100
        bar_height = 20
        avatar_size = 50
        player1_x, player1_y = self.PlayerHead_Pos
        bar_y = player1_y + avatar_size + 10
        bg_rect = pygame.Rect(player1_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (192,192,192), bg_rect)
        pygame.draw.rect(screen, (0,0,0), bg_rect, 2)
        if hp1 > 0:
            fill_width = int((hp1 / initial_hp1) * bar_width)
            fill_rect = pygame.Rect(player1_x, bar_y, fill_width, bar_height)
            color = (0,255,0) if hp1 > 2 else (255,0,0)
            pygame.draw.rect(screen, color, fill_rect)
        for i in range(1, initial_hp1):
            grid_x = player1_x + int((i / initial_hp1) * bar_width)
            pygame.draw.line(screen, (0,0,0), (grid_x, bar_y), (grid_x, bar_y + bar_height), 1)
        f = pygame.font.Font(None, 18)
        hp_text = f.render(f"{hp1}/{initial_hp1}", True, (0,0,0))
        text_rect = hp_text.get_rect(center=(player1_x + bar_width // 2, bar_y + bar_height + 15))
        screen.blit(hp_text, text_rect)
        # 玩家2血量条（头像下方）
        player2_x, player2_y = self.EnemyHead_Pos
        bar_y2 = player2_y + avatar_size + 10
        bg_rect2 = pygame.Rect(player2_x, bar_y2, bar_width, bar_height)
        pygame.draw.rect(screen, (192,192,192), bg_rect2)
        pygame.draw.rect(screen, (0,0,0), bg_rect2, 2)
        if hp2 > 0:
            fill_width2 = int((hp2 / initial_hp2) * bar_width)
            fill_rect2 = pygame.Rect(player2_x, bar_y2, fill_width2, bar_height)
            color2 = (0,255,0) if hp2 > 2 else (255,0,0)
            pygame.draw.rect(screen, color2, fill_rect2)
        for i in range(1, initial_hp2):
            grid_x2 = player2_x + int((i / initial_hp2) * bar_width)
            pygame.draw.line(screen, (0,0,0), (grid_x2, bar_y2), (grid_x2, bar_y2 + bar_height), 1)
        hp_text2 = f.render(f"{hp2}/{initial_hp2}", True, (0,0,0))
        text_rect2 = hp_text2.get_rect(center=(player2_x + bar_width // 2, bar_y2 + bar_height + 15))
        screen.blit(hp_text2, text_rect2)
        # 图片资源留空，未来可替换血条为图片

    def findPos(self):
        '''定位到棋盘节点'''
        mousePos = pygame.mouse.get_pos()

        for i in range(self.LeftUP_Point[0],self.RightDown_Point[0]+5,self.Distance):
            for j in range(self.LeftUP_Point[1],self.RightDown_Point[1]+5,self.Distance):
                L = i-self.CheckRidus
                R = i+self.CheckRidus
                U = j+self.CheckRidus
                D = j-self.CheckRidus
                if(mousePos[0]>L and mousePos[0]<R and mousePos[1]>D and mousePos[1]<U):
                    return pygame.Vector2(i,j)
        return pygame.Vector2(0,0)

    def checkMouse(self,screen):
        '''检查鼠标位置是否合法'''
        piecePos = self.findPos()
        if piecePos[0]!=0 and self.checkPiece(piecePos):
            pygame.draw.rect(screen,self.Line_color,[piecePos[0]-self.CheckRidus,piecePos[1]-self.CheckRidus,
                                            self.CheckRidus*2,self.CheckRidus*2],1,1)
            return True
        return False

    def checkPiece(self,p:pygame.Vector2):
        '''检查当前位置是否已经有棋子'''
        for i in self.All_Piece:
            if(i[0][0]==p[0] and i[0][1]==p[1]):
                return False
        return True

    def drawPiece(self,screen):
        '''绘制棋盘上的所有棋子'''
        for i in self.All_Piece:
            screen.blit(i[1],i[0])

    def drawMagicPlants(self,screen):
        '''绘制棋盘上的所有魔法植物'''
        for i in self.Magic_plants:
            pygame.draw.rect(screen, self.Magic_plant_Color ,
                             [i[0]-5, i[1]-5, 5*2, 5*2])

    def pixel_to_board_index(self, pixel_pos):
        """将像素坐标转换为棋盘格坐标(row, col)"""
        x0, y0 = self.LeftUP_Point
        distance = self.Distance
        x, y = int(pixel_pos[0]), int(pixel_pos[1])
        col = round((x - x0) / distance)
        row = round((y - y0) / distance)
        return row, col

    def syncFromPieces(self, pieces, magic_plants):
        '''根据核心数据pieces同步棋盘显示数据All_Piece'''
        self.All_Piece = []
        self.Magic_plants = []

        for row in range(self.Boardsize):
            for col in range(self.Boardsize):
                if pieces[row][col] == 1:
                    if  magic_plants[row][col] == 1:
                        self.All_Piece.append([[self.LeftUP_Point[0] + col * self.Distance - 20,
                                            self.LeftUP_Point[1] + row * self.Distance - 20], black_Chess_Plant_Image])
                    else:
                        self.All_Piece.append([[self.LeftUP_Point[0] + col * self.Distance - 20,
                                            self.LeftUP_Point[1] + row * self.Distance - 20], black_Chess_Image])
                elif pieces[row][col] == -1:
                    if  magic_plants[row][col] == 1:
                        self.All_Piece.append([[self.LeftUP_Point[0] + col * self.Distance - 20,
                                            self.LeftUP_Point[1] + row * self.Distance - 20], white_Chess_Plant_Image])
                    else:
                        self.All_Piece.append([[self.LeftUP_Point[0] + col * self.Distance - 20,
                                            self.LeftUP_Point[1] + row * self.Distance - 20], white_Chess_Image])

                if magic_plants[row][col] == 1 and pieces[row][col] == 0:
                    self.Magic_plants.append([self.LeftUP_Point[0] + col * self.Distance,
                                              self.LeftUP_Point[1] + row * self.Distance])
