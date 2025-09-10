import pygame


class TitleAnimationController:

    def __init__(self):
        self.reset()

    def reset(self):
        self.frame = 0
        self.total_frames = 180
        self.is_finished = False
        self.skip_animation = False

    def update(self):
        if self.skip_animation:
            self.is_finished = True
            return True

        self.frame += 1

        if not self.is_finished and self.frame >= self.total_frames:
            self.is_finished = True
        return self.is_finished

    def skip(self):
        """跳过动画"""
        self.skip_animation = True
        self.is_finished = True

    def draw(self, screen, titleBackground_image):
        # 计算动画进度
        if self.skip_animation or self.is_finished:
            progress = 1.0
        else:
            progress = self.frame / self.total_frames

        eased_progress = 1 - (1 - progress)**2

        screen.fill((0, 0, 0))  # 黑色背景

        background_alpha = int(255 * eased_progress)

        temp_bg = titleBackground_image.copy()
        temp_bg.set_alpha(background_alpha)
        screen.blit(temp_bg, (0, 0))

        # 绘制提示文字
        hint_font = pygame.font.Font('resource\\pixelfont.ttf', 40)
        hint_text = hint_font.render("Press any key or click to continue",
                                     True, (0, 0, 0))
        hint_rect = hint_text.get_rect()
        hint_rect.center = (640, 600)

        import math
        blink_speed = 1
        blink_factor = (math.sin(self.frame * blink_speed * math.pi / 30) +
                        1) / 2

        # 提示文字透明度（结合淡入效果和闪烁效果）
        base_alpha = 255 * eased_progress
        blink_alpha = int(base_alpha *
                          (0.3 + 0.7 * blink_factor))  # 在30%-100%之间闪烁
        hint_text.set_alpha(blink_alpha)
        screen.blit(hint_text, hint_rect)

        pygame.display.flip()
        return self.is_finished


# 全局标题动画控制器
title_animation = TitleAnimationController()


def drawWelcome(screen, titleBackground_image, events):
    """
    新的标题页面绘制函数
    返回: True 如果应该继续显示标题页面, False 如果应该切换到菜单
    """
    # 检查输入事件
    for event in events:
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if not title_animation.is_finished:
                title_animation.skip()
            else:
                return False  # 切换到菜单

    # 更新和绘制动画
    animation_finished = title_animation.update()
    title_animation.draw(screen, titleBackground_image)

    # 如果动画完成，继续等待用户输入
    return True
