"""
switch picture partitions to restore the picture
author wangxx10
date 2020/12/17
"""
import pygame
import os,random
from config import *
from datetime import datetime
from pygame.locals import *

# 文件放在 data 目录下面
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")


class MyGroup(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)


class MySprite(pygame.sprite.Sprite):
    def __init__(self, parent_surface,sprite_rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = parent_surface.subsurface(sprite_rect)
        # self.image.fill(color)

        self.rect = sprite_rect
        self.primary_rect = sprite_rect
        # self.rect = self.image.get_rect()  # 不更新rect
        # print(self.rect.center,'bbb')
        self.adjacent_group = MyGroup()

    def add_adjacent_sp_to_group(self):
        self.adjacent_group.empty()
        if hard_level == 1:   # 对角线就算临近
            rect_tmp = self.rect.inflate(2, 2)
            for sprite in all_group.sprites():
                if rect_tmp.colliderect(sprite.rect):
                    self.adjacent_group.add(sprite)
        elif hard_level == 2:  # 平移才算临近
            list_move = [(0,2),(0,-2),(2,0),(-2,0),]
            for move in list_move:
                rect_tmp = self.rect.move(move)
                for sprite in all_group.sprites():
                    if rect_tmp.colliderect(sprite.rect):
                        self.adjacent_group.add(sprite)


def load_background(image_name):
    """
    :param image_name:
    """
    image_surface = pygame.image.load(os.path.join(data_dir, image_name))
    back_rect = image_surface.get_rect()
    screen_surface = pygame.display.set_mode((back_rect.right, back_rect.bottom))
    image_surface = image_surface.convert()   # 转换在定义屏幕之后

    return screen_surface, image_surface, back_rect


def get_rect_list(count):
    """
    输入要分隔的列数，返回一个矩形列表
    :param count:
    :return:
    """
    rect_l = []
    x_len = bk_rect.width / count
    y_len = bk_rect.height / count
    for i in range(count ** 2):
        j = int(i / count)  # 第j行
        k = i % count       # 第k列
        my = pygame.rect.Rect(int(x_len * k), int(y_len * j), int(x_len), int(y_len))
        rect_l.append(my)
        # screen.blit(bk, my, my)
    return rect_l


def draw_separate_line(count, color):
    """划分割线"""
    x_len = bk_rect.width / count
    y_len = bk_rect.height / count
    for i in range(count):
        pygame.draw.line(screen, color, (int(i*x_len), 0), (int(i*x_len), bk_rect.height), 4)
        pygame.draw.line(screen, color, (0, int(i*y_len)), (bk_rect.width, int(i*y_len)), 4)


def get_sprite_now():
    """获取当前方块"""
    pos = pygame.mouse.get_pos()
    res = None
    for i_sprite in all_group.sprites():
        i_rect = i_sprite.rect
        if i_rect.collidepoint(pos[0], pos[1]):
            res = i_sprite
    return res


def do_switch(blank_sprite):
    global click_count
    if blank_sprite:
        current_sprite = get_sprite_now()
        current_sprite.rect,blank_sprite.rect = blank_sprite.rect,current_sprite.rect
        click_count += 1


def shuffle_sprite(rectangle_list):
    random.shuffle(rectangle_list)
    for index,sp in enumerate(all_group.sprites()):
        sp.rect = rectangle_list[index]


def check_adjacent(blank_sprite):
    blank_sprite.add_adjacent_sp_to_group()
    current_sprite = get_sprite_now()
    if blank_one.adjacent_group.has(current_sprite):
        return True
    return False


def check_same():
    for sp in all_group.sprites():
        if sp.rect.center != sp.primary_rect.center:
            return False
    return True


def get_run_time(tt):
    """计算事件长"""
    now = datetime.now()
    during = now - tt
    ss = during.seconds
    return int(ss / 60), ss % 60


def echo_success(ss, color1):
    """结果打印"""
    if pygame.font:
        size = int(bk.get_width()/10)
        font = pygame.font.SysFont(None, size)
        ms = f'''
congratulations!
restore successfully
:) you used:{ss[0]}min{ss[1]}sec
click:{click_count} times
        '''
        for index, line in enumerate(ms.split('\n')[1:]):
            text = font.render(line, 1, color1)
            text_pos = text.get_rect(centerx=int(bk.get_width() / 2 + index),
                                     centery=int(int(bk.get_height() / 2) + index * size * 3/4))
            screen.blit(text, text_pos)


def main():
    global screen, bk, bk_rect, all_group, blank_one, click_count
    pygame.init()
    pygame.display.set_caption("click & switch")
    screen, bk, bk_rect = load_background(pic_name)
    # screen.blit(bk, (0, 0))

    all_group = MyGroup()
    rect_list = get_rect_list(split_count)
    blank_one = None
    for index,rect in enumerate(rect_list):      # 初始化全部的分区
        my_sprite = MySprite(bk,rect)
        if index == len(rect_list) - 1:          # 最后一个为白板
            my_sprite.image.fill(white)
            blank_one = my_sprite
        # print(rect.center,'aaa')
        all_group.add(my_sprite)

    while 1:
        if check_same():
            shuffle_sprite(rect_list)  # 洗牌
        else:
            break

    done = False                                 # 进程结束
    end_game = False                             # 游戏结束
    minute_of_use = 0                            # 游戏耗时初始 0
    click_count = 0                              # 点击次数
    clock = pygame.time.Clock()
    now = datetime.now()
    while not done:
        for event in pygame.event.get():           # 事件
            if event.type == pygame.QUIT:          # 关闭按钮
                done = True
            elif event.type == MOUSEBUTTONDOWN:    # 任意键按下
                if hard_level != 0:                # 最低难度不校验临近与否
                    if check_adjacent(blank_one) and not end_game:
                        do_switch(blank_one)           # 交换
                elif not end_game:
                    do_switch(blank_one)
        if check_same() and not end_game:
            minute_of_use = get_run_time(now)
            end_game = True

        all_group.draw(screen)
        all_group.update()
        draw_separate_line(split_count,line_color)
        if end_game:
            echo_success(minute_of_use, word_color)

        pygame.display.update()
        clock.tick(100)
    pygame.quit()


if __name__ == '__main__':
    main()

