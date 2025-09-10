import pygame

pygame.init()



Menu_Animation_Image = pygame.image.load('resource\\Menu_Animation_Image.png')
Menu_border_image = pygame.image.load('resource\\Menu_border.png')
Menu_Button_Blue_image = pygame.image.load('resource\\Menu_Button_Blue.png')
Menu_Button_Gray_image = pygame.image.load('resource\\Menu_Button_Gray.png')
Menu_Button_Red_image = pygame.image.load('resource\\Menu_Button_Red.png')
Menu_Button_PVP_Image = pygame.image.load('resource\\Menu_Button_PVP.png')
Menu_Button_PVE_Image = pygame.image.load('resource\\Menu_Button_PVE.png')
Menu_Button_Learn_Image = pygame.image.load('resource\\Menu_Button_Learn.png')


Button_f = pygame.font.Font('resource\\ProggyTinySZ-4.ttf',100)
PVP_font = Button_f.render("P V P",True,(50,50,50))
PVE_font = Button_f.render("P V E",True,(50,50,50))
Teach_font = Button_f.render("Learn",True,(50,50,50))

PVP_font_Rect = PVP_font.get_rect()
PVE_font_Rect = PVE_font.get_rect()
Teach_font_Rect = Teach_font.get_rect()

PVP_font_Rect.center = (640,215)
PVE_font_Rect.center = (640,365)
Teach_font_Rect.center = (640,510)

def MenuAnimation(screen,background_image):
    p=50;a=600;b=120
    for i in range(0,19):
        screen.fill(0xffffff)
        screen.blit(background_image, (0, 0))
        temp=Menu_Animation_Image.subsurface(0,a,1280,b)
        a-=p;b+=p;p-=2
        screen.blit(temp, (0, 0))
        pygame.display.flip()
        pygame.time.wait(16)
    return False


def drawMenuPage(screen,background_image):
    screen.fill(0xffffff)
    screen.blit(background_image, (0, 0))
    screen.blit(Menu_border_image, (0, 0))
    screen.blit(Menu_Button_Blue_image,(505,150))
    screen.blit(Menu_Button_Red_image,(505,300))
    screen.blit(Menu_Button_Gray_image,(505,450))
    screen.blit(PVP_font,PVP_font_Rect)
    screen.blit(PVE_font,PVE_font_Rect)
    screen.blit(Teach_font,Teach_font_Rect)
def mouseJudge(screen,x,y):
    if 505 <= x <= 775 and 150 <= y <= 264:
        screen.blit(Menu_Button_PVP_Image,(505,150))
        pygame.display.update((505,150,250,114))
    elif 505 <= x <= 775 and 300 <= y <= 414:
        screen.blit(Menu_Button_PVE_Image,(505,300))
        pygame.display.update((505,300,250,114))
    elif 505 <= x <= 775 and 450 <= y <= 564:
        screen.blit(Menu_Button_Learn_Image,(505,450))
        pygame.display.update((505,450,250,114))

def gameJudge(x,y):
    if 505 <= x <= 775 and 150 <= y <= 264:
        return 2
    else:
        return 1