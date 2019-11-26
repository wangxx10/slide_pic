#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
这是一个简单的用pygame 书写的图片华容道小游戏
滑动图片来复原位置

"""
import pygame
import os
from config import *
from pygame.compat import geterror
from datetime import datetime
import random
from pygame.locals import *
import copy
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")


def load_background(nn):
    """加载背景"""
    bb = pygame.image.load(os.path.join(data_dir, nn))
    back_rect = bb.get_rect()
    screen = pygame.display.set_mode((back_rect.right, back_rect.bottom))
    bb = bb.convert()
    return screen, bb, back_rect


def get_rect(count):
    """获取方块"""
    rect_l = []
    x_len = bk_rect.width / count
    y_len = bk_rect.height / count
    for i in range(count ** 2):
        j = int(i / count)  # 第j行
        k = i % count       # 第k列
        my = pygame.rect.Rect(x_len * k, y_len * j, x_len, y_len)
        rect_l.append(my)
        # sc.blit(bk, my, my)
    return rect_l


def draw_pic(shadow):
    """画图"""
    for index, my in enumerate(rect_old):
        if index != shadow:
            sc.blit(bk, my, rect_all[index])


def draw_separate_line(count, color1):
    """划分割线"""
    x_len = bk_rect.width / count
    y_len = bk_rect.height / count
    for i in range(count):
        pygame.draw.line(sc, color1, (i*x_len, 0), (i*x_len, bk_rect.height), 4)
        pygame.draw.line(sc, color1, (0, i*y_len), (bk_rect.width, i*y_len), 4)


def exchange_rect(in1, in2):
    """交换方块"""
    i1 = rect_all.index(in1)
    i2 = rect_all.index(in2)
    rect_all[i1], rect_all[i2] = rect_all[i2], rect_all[i1]
    return rect_all


def get_rect_now():
    """获取当前方块"""
    pos = pygame.mouse.get_pos()
    res = None
    for index, rect in enumerate(rect_old):
        if rect.collidepoint(pos[0], pos[1]):
            res = index
    return res


def check_same():
    """一致检查"""
    for index, rect in enumerate(rect_all):
        if rect_old[index].center != rect.center:
            return False
    return True


def check_adjacent(in1):
    """临近检查"""
    leng = abs(in1 - mark)
    rect_tmp = rect_old[in1].inflate(2, 2)
    if rect_tmp.colliderect(rect_old[mark]):
        if leng == 1 or leng == separate:
            return True
    return False


# 这个模式可以对角线互换，容易一点
def check_adjacent_simple(in1):
    """临近检查"""
    # leng = abs(in1 - mark)
    rect_tmp = rect_old[in1].inflate(2, 2)
    if rect_tmp.colliderect(rect_old[mark]):
        # if leng == 1 or leng == separate:
        return True
    return False


def print_success(ss, color1):
    """结果打印"""
    if pygame.font:
        size = int(bk.get_width()/10)
        font = pygame.font.SysFont(None, size)
        ms = u'''
congratulations !!
restore successfully
:) use:%dmin%dsec
        ''' % ss
        for index, line in enumerate(ms.split('\n')[1:]):
            text = font.render(line, 1, color1)
            textpos = text.get_rect(centerx=bk.get_width() / 2,
                                    centery=bk.get_height() / 2 + index * size * 3/4)
            sc.blit(text, textpos)


def get_run_time(tt):
    """计算事件长"""
    now = datetime.now()
    during = now - tt
    ss = during.seconds
    mm = int(ss / 60)
    s1 = ss % 60
    return mm, s1


def random_rect():
    """确保每个图片的右下角方格不显示"""
    tmp = rect_all[:-1]
    random.shuffle(tmp)
    tmp.append(rect_all[-1])
    return tmp


def load_sound(nn):
    class NoneSound:
        def __init__(self):
            pass

        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, nn)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound


def main(pic_name, f_s):
    # 全局变量
    global separate, sc, bk, bk_rect, rect_all, rect_old, mark, msi

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    pygame.init()
    # pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    sc, bk, bk_rect = load_background(pic_name)
    clock = pygame.time.Clock()
    rect_all = get_rect(separate)
    rect_old = copy.deepcopy(rect_all)
    if f_s:
        so = load_sound('sou.wav')
    else:
        so = None
    background = pygame.Surface(sc.get_size())
    background = background.convert()
    mark = len(rect_old) - 1

    rect_all = random_rect()
    while check_same():
        rect_all = random_rect()

    done = False
    end_game = False

    now = datetime.now()
    while not done:
        clock.tick(100)
        for event in pygame.event.get():  # 事件
            if event.type == pygame.QUIT:  # 关闭按钮
                done = True
            elif event.type == MOUSEBUTTONDOWN:
                index_now = get_rect_now()
                if not end_game:
                    if not diagonal:
                        adj = check_adjacent(index_now)
                    else:
                        adj = check_adjacent_simple(index_now)

                    if adj:
                        if so:
                            so.play()
                        rect_all = exchange_rect(rect_all[mark], rect_all[index_now])
                        mark = index_now

        background.fill(white)
        sc.blit(background, (0, 0))
        draw_pic(mark)
        draw_separate_line(separate, line_color)

        if check_same() and not end_game:
            msi = get_run_time(now)
            end_game = True
        if end_game:
            print_success(msi, word_color)
        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    separate = 3           # 分割n次，n至少是2 能分成 n**n 个
    name = 'squirrel.jpg'  # data 目录下面用来玩的图片
    diagonal = True        # 可以对角线互换,容易些
    f_sound = True         # 打开/关闭声音
    word_color = HotPink1  # 提示语言的颜色
    line_color = white     # 线条颜色
    main(name, f_sound)
