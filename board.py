import pygame

Boardsize = 9

XtoXstart = 220
YtoXstart = 150
XtoYstart = 180
YtoYstart = 180

Rowlenth = 440
Collenth = 420
Distance = 45
Line_color = 0x838383

CheckRidus = 10
PieceRidus = 15
All_Piece = []
Piece_Color = 0

LeftUP_Point = (461,211)
RightDown_Point = (821,571)

PlayerHead_Pos = (150,70)
EnemyHead_Pos = (1100,70)

def drawUI(screen):
    drawState(screen)
    drawBoard(screen)

def drawBoard(screen):
    origin = pygame.Vector2(screen.get_width()/2,screen.get_height()/2)
    xfirstLine_start = origin-pygame.Vector2(XtoXstart,YtoXstart)#横向绘制起点
    yfirstLine_start = origin-pygame.Vector2(XtoYstart,YtoYstart)#纵向绘制起点
    xlineLenth = pygame.Vector2(Rowlenth,0)
    ylineLenth = pygame.Vector2(0,Collenth)
    
    for i in range(Boardsize):#横向棋盘线
        cur_start = xfirstLine_start+pygame.Vector2(0,Distance*i)
        pygame.draw.line(screen,Line_color,cur_start,cur_start+xlineLenth,4)
    for i in range(Boardsize):#纵向棋盘线
        cur_start = yfirstLine_start+pygame.Vector2(Distance*i,0)
        pygame.draw.line(screen,Line_color,cur_start,cur_start+ylineLenth,4)

def drawState(screen):
    player_image = pygame.image.load("resource\\player.png")
    enemy_image = pygame.image.load("resource\\enemy.png")
    screen.blit(player_image,PlayerHead_Pos)
    screen.blit(enemy_image,EnemyHead_Pos)

def findPos():
    mousePos = pygame.mouse.get_pos()

    for i in range(LeftUP_Point[0],RightDown_Point[0]+5,Distance):
        for j in range(LeftUP_Point[1],RightDown_Point[1]+5,Distance):
            L = i-CheckRidus
            R = i+CheckRidus
            U = j+CheckRidus
            D = j-CheckRidus
            if(mousePos[0]>L and mousePos[0]<R and mousePos[1]>D and mousePos[1]<U):
                return pygame.Vector2(i,j)
    return pygame.Vector2(0,0)

def checkMouse(screen):
    piecePos = findPos()
    if piecePos[0]!=0:
        pygame.draw.rect(screen,0x838383,[piecePos[0]-CheckRidus,piecePos[1]-CheckRidus,
                                          CheckRidus*2,CheckRidus*2],1,1)
        return True
    return False

def checkPiece(p:pygame.Vector2):
    for i in All_Piece:
        if(i[0][0]==p[0] and i[0][1]==p[1]):
            return False
    return True

lock = 0
def setPiece(turn):
    global Piece_Color
    global lock
    
    pressed = pygame.mouse.get_pressed()
    piecePos = findPos()

    if turn and not lock:
        if pressed[0]:
            if Piece_Color==0:
                All_Piece.append([[piecePos[0],piecePos[1]],"black"])
            else:
                All_Piece.append([[piecePos[0],piecePos[1]],0xdbdbd9])
            Piece_Color = (Piece_Color+1)%2
    lock = pressed[0]

def drawPiece(screen):
    for i in All_Piece:
        pygame.draw.circle(screen,i[1],i[0],PieceRidus)