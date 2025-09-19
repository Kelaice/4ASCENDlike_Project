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

Button_f = pygame.font.Font('resource\\ProggyTinySZ-4.ttf', 100)
PVP_font = Button_f.render("P V P", True, (50, 50, 50))
PVE_font = Button_f.render("P V E", True, (50, 50, 50))
Teach_font = Button_f.render("Learn", True, (50, 50, 50))

PVP_font_Rect = PVP_font.get_rect()
PVE_font_Rect = PVE_font.get_rect()
Teach_font_Rect = Teach_font.get_rect()

PVP_font_Rect.center = (640, 215)
PVE_font_Rect.center = (640, 365)
Teach_font_Rect.center = (640, 510)


class MenuAnimationController:

    def __init__(self):
        self.reset()

    def reset(self):
        self.frame = 0
        self.total_frames = 30  # 增加帧数使动画更流畅
        self.is_finished = False

    def update(self):
        if not self.is_finished:
            self.frame += 1
            if self.frame >= self.total_frames:
                self.is_finished = True
        return self.is_finished

    def draw(self, screen, background_image):
        if self.is_finished:
            return True

        screen.fill(0xffffff)
        screen.blit(background_image, (0, 0))

        # 使用更平滑的插值函数
        progress = self.frame / self.total_frames
        # 使用缓出函数使动画更自然
        eased_progress = 1 - (1 - progress)**3

        # 计算动画参数
        start_y = 600
        end_y = 0
        start_height = 120
        end_height = 720

        current_y = int(start_y + (end_y - start_y) * eased_progress)
        current_height = int(start_height +
                             (end_height - start_height) * eased_progress)

        # 确保不超出图像边界
        if current_y < 0:
            current_height += current_y
            current_y = 0
        if current_height > 720:
            current_height = 720

        if current_height > 0:
            temp = Menu_Animation_Image.subsurface(0, current_y, 1280,
                                                   current_height)
            screen.blit(temp, (0, 0))

        pygame.display.flip()
        return False


# 全局动画控制器
menu_animation = MenuAnimationController()


def MenuAnimation(screen, background_image):
    return menu_animation.draw(screen, background_image)


class MenuButtonController:

    def __init__(self):
        self.hovered_button = None
        self.button_rects = {
            'pvp': pygame.Rect(505, 150, 270, 114),
            'pve': pygame.Rect(505, 300, 270, 114),
            'learn': pygame.Rect(505, 450, 270, 114)
        }
        self.button_scale = {'pvp': 1.0, 'pve': 1.0, 'learn': 1.0}
        self.target_scale = {'pvp': 1.0, 'pve': 1.0, 'learn': 1.0}

    def update_hover(self, mouse_pos):
        self.hovered_button = None
        for button_name, rect in self.button_rects.items():
            if rect.collidepoint(mouse_pos):
                self.hovered_button = button_name
                self.target_scale[button_name] = 1.05  # 轻微放大
            else:
                self.target_scale[button_name] = 1.0

    def update_animations(self):
        # 平滑缩放动画
        for button_name in self.button_scale:
            current = self.button_scale[button_name]
            target = self.target_scale[button_name]
            # 使用线性插值实现平滑过渡
            self.button_scale[button_name] = current + (target - current) * 0.2

    def draw_button_with_scale(self, screen, image, base_pos, button_name):
        scale = self.button_scale[button_name]
        if scale != 1.0:
            # 缩放图像
            original_size = image.get_size()
            new_size = (int(original_size[0] * scale),
                        int(original_size[1] * scale))
            scaled_image = pygame.transform.scale(image, new_size)

            # 计算居中位置
            offset_x = (new_size[0] - original_size[0]) // 2
            offset_y = (new_size[1] - original_size[1]) // 2
            new_pos = (base_pos[0] - offset_x, base_pos[1] - offset_y)

            screen.blit(scaled_image, new_pos)
        else:
            screen.blit(image, base_pos)

    def check_click(self, mouse_pos):
        for button_name, rect in self.button_rects.items():
            if rect.collidepoint(mouse_pos):
                return button_name
        return None


# 全局按钮控制器
button_controller = MenuButtonController()


def drawMenuPage(screen, background_image):
    screen.fill(0xffffff)
    screen.blit(background_image, (0, 0))
    screen.blit(Menu_border_image, (0, 0))

    # 更新按钮动画
    button_controller.update_animations()

    # 绘制按钮（根据悬停状态选择图像）
    if button_controller.hovered_button == 'pvp':
        button_controller.draw_button_with_scale(screen, Menu_Button_PVP_Image,
                                                 (505, 150), 'pvp')
    else:
        button_controller.draw_button_with_scale(screen,
                                                 Menu_Button_Blue_image,
                                                 (505, 150), 'pvp')

    if button_controller.hovered_button == 'pve':
        button_controller.draw_button_with_scale(screen, Menu_Button_PVE_Image,
                                                 (505, 300), 'pve')
    else:
        button_controller.draw_button_with_scale(screen, Menu_Button_Red_image,
                                                 (505, 300), 'pve')

    if button_controller.hovered_button == 'learn':
        button_controller.draw_button_with_scale(screen,
                                                 Menu_Button_Learn_Image,
                                                 (505, 450), 'learn')
    else:
        button_controller.draw_button_with_scale(screen,
                                                 Menu_Button_Gray_image,
                                                 (505, 450), 'learn')

    # 绘制文字
    screen.blit(PVP_font, PVP_font_Rect)
    screen.blit(PVE_font, PVE_font_Rect)
    screen.blit(Teach_font, Teach_font_Rect)


def mouseJudge(screen, mouse_pos):
    """更新鼠标悬停状态"""
    button_controller.update_hover(mouse_pos)


def gameJudge(mouse_pos):
    """处理按钮点击"""
    clicked_button = button_controller.check_click(mouse_pos)
    if clicked_button == 'pvp':
        return 2
    elif clicked_button == 'pve':
        return 3  # 应该返回PVE状态
    elif clicked_button == 'learn':
        return 4  # 应该返回Learn状态
    else:
        return 1  # 保持在菜单状态
