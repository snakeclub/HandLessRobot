#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
控制操作模块基础框架
@module base_control
@file base_control.py
"""

import os
import sys
import pyautogui
import pyperclip
from PIL import Image
from HiveNetLib.base_tools.file_tool import FileTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))


__MOUDLE__ = 'windows_control'  # 模块名
__DESCRIPT__ = u'电脑控制操作模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.04.15'  # 发布日期


class Screen(object):
    """
    获取屏幕信息
    """
    @classmethod
    def size(cls) -> tuple:
        """
        获取屏幕大小

        @returns {(int, int)} - 返回屏幕的大小(width, height)
        """
        return pyautogui.size()

    @classmethod
    def on_screen(cls, x: int, y: int = None) -> bool:
        """
        检查xy坐标是否在屏幕范围中

        @param {int} x - x坐标
        @param {int} y=None - y坐标

        @returns {bool} - 检查结果
        """
        return pyautogui.onScreen(x, y=y)

    @classmethod
    def center(cls, coords) -> tuple:
        """
        返回指定区域的中心位置

        @param {(int,int,int,int)} coords - 区域坐标(x, y, width, height)

        @returns {(int, int)} - 返回的中心位置(x, y)
        """
        return pyautogui.center(coords=coords)

    @classmethod
    def pixel_color(cls, x=None, y=None) -> tuple:
        """
        获取屏幕指定位置的像素颜色

        @param {int} x=None - 屏幕x坐标, None代表获取鼠标当前坐标
        @param {int} y=None - 屏幕y坐标, None代表获取鼠标当前坐标

        @returns {(int, int, int)} - 返回RGB三色结果
        """
        _x, _y = Mouse.position(x=x, y=y)
        return pyautogui.pixel(_x, _y)

    @classmethod
    def screenshot(cls, image_save_file=None, region=None):
        """
        屏幕截图

        @param {str} image_save_file=None - 截图保存路径和文件名, None代表不保存文件
        @param {tuple} region=None - 指定截图区域 (x, y, witdh, height), None代表全屏
            例如: (0, 0, 300, 200)

        @returns {PIL.Image} - 返回屏幕截图的图片对象
        """
        FileTool.create_dir(os.path.split(image_save_file)[0], exist_ok=True)
        return pyautogui.screenshot(imageFilename=image_save_file, region=region)

    @classmethod
    def locate_on_screen(cls, image, grayscale=False, **kwargs):
        """
        在屏幕中定位指定图片的位置

        @param {str|PIL.Image} image - 要定位的图片文件路径或图片对象
        @param {bool} grayscale=False - 是否转换图片为灰度检索(提升30%速度)
        @param {dict} kwargs - 其他执行参数:
            {int} limit=10000 - 匹配数量限制
            {int} step=1 - 匹配步骤，支持送1或2，如果为2会跳过细节，大约能提升3倍速度，但有可能匹配不上
            {float} confidence=0.999 - 匹配度

        @returns {(int, int, int, int)} - 返回图片的位置(x, y, width, height)
        """
        if type(image) == str:
            _image = Image.open(image)
        else:
            _image = image
        return pyautogui.locateOnScreen(_image, grayscale=grayscale, **kwargs)

    @classmethod
    def locate_center_on_screen(cls, image, grayscale=False):
        """
        在屏幕中定位指定图片的位置，返回中心坐标

        @param {str} image - 要定位的图片文件
        @param {bool} grayscale=False - 是否转换图片为灰度检索(提升30%速度)

        @returns {(int, int)} - 返回图片的中心位置(x, y)
        """
        return pyautogui.locateCenterOnScreen(image, grayscale=grayscale)

    @classmethod
    def locate_all_on_screen(cls, image, grayscale=False):
        """
        在屏幕中定位指定图片的所有位置

        @param {str} image - 要定位的图片文件
        @param {bool} grayscale=False - 是否转换图片为灰度检索(提升30%速度)

        @returns {list} - 返回所找到的所有图片的位置
            [(x, y, width, height), ..]
        """
        return list(pyautogui.locateAllOnScreen(image, grayscale=grayscale))


class Mouse(object):
    """
    鼠标控制模块
    """

    @classmethod
    def position(cls, x=None, y=None):
        """
        获取鼠标位置

        @param {int} x=None - 如果不为空，输出时x覆盖为该数值(不会移动鼠标)
        @param {int} y=None - 如果不为空，输出时y覆盖为该数值(不会移动鼠标)

        @returns {(int, int)} - 返回鼠标在屏幕的位置(x, y)
        """
        return pyautogui.position(x=x, y=y)

    @classmethod
    def move(cls, x_offset=None, y_offset=None, duration=0.0):
        """
        移动鼠标到当前位置的相对位置

        @param {int} x_offset=None - 与当前位置的x坐标相对距离
        @param {int} y_offset=None - 与当前位置的y坐标相对距离
        @param {float} duration=0.0 - 移动鼠标所需时长
        """
        pyautogui.move(xOffset=x_offset, yOffset=y_offset, duration=duration)

    @classmethod
    def move_to(cls, x=None, y=None, duration=0.0):
        """
        移动鼠标到指定位置

        @param {int} x=None - 要移动到的x坐标，None代表当前位置，如果超出屏幕则移动到屏幕边缘
        @param {int} y=None - 要移动到的y坐标，None代表当前位置，如果超出屏幕则移动到屏幕边缘
        @param {float} duration=0.0 - 移动鼠标所需时长
        """
        pyautogui.moveTo(x=x, y=y, duration=duration)

    @classmethod
    def drag(cls, x_offset=None, y_offset=None, duration=0.0, button='primary', mouse_down_up=True):
        """
        按下鼠标并拖动到当前位置的相对位置

        @param {int} x_offset=None - 与当前位置的x坐标相对距离
        @param {int} y_offset=None - 与当前位置的y坐标相对距离
        @param {float} duration=0.0 - 移动鼠标所需时长
        @param {string} button='primary' - 按下的按钮
            primary - 鼠标主按键，默认对应为left，除非系统设置了鼠标为左手模式
            secondary - 鼠标次按键，默认对应为right，除非系统设置了鼠标为左手模式
            left - 鼠标左键
            middle - 鼠标中键
            right - 鼠标右键
        @param {bool} mouse_down_up=True - 如果为True，则不会执行mouseUp/Down动作
            注：可以允许通过多个分解动作执行拖动
        """
        pyautogui.drag(xOffset=x_offset, yOffset=y_offset,
                       duration=duration, button=button, mouseDownUp=mouse_down_up)

    @classmethod
    def drap_to(cls, x=None, y=None, duration=0.0, button='primary', mouse_down_up=True):
        """
        按下鼠标并拖动到指定位置

        @param {int} x=None - 要移动到的x坐标，None代表当前位置，如果超出屏幕则移动到屏幕边缘
        @param {int} y=None - 要移动到的y坐标，None代表当前位置，如果超出屏幕则移动到屏幕边缘
        @param {float} duration=0.0 - 移动鼠标所需时长
        @param {string} button='primary' - 按下的按钮
            primary - 鼠标主按键，默认对应为left，除非系统设置了鼠标为左手模式
            secondary - 鼠标次按键，默认对应为right，除非系统设置了鼠标为左手模式
            left - 鼠标左键
            middle - 鼠标中键
            right - 鼠标右键
        @param {bool} mouse_down_up=True - 如果为True，则不会执行mouseUp/Down动作
            注：可以允许通过多个分解动作执行拖动
        """
        pyautogui.dragTo(x=x, y=y, duration=duration, button=button, mouseDownUp=mouse_down_up)

    @classmethod
    def click(cls, x=None, y=None, clicks=1, interval=0.0, button='primary', duration=0.0):
        """
        点击鼠标

        @param {int} x=None - 要点击鼠标的x坐标，None代表当前位置
        @param {int} y=None - 要点击鼠标的y坐标，None代表当前位置
        @param {int} clicks=1 - 连续点击鼠标次数
        @param {float} interval=0.0 - 连续点击鼠标中间的间隔时长
        @param {str} button='primary' - 鼠标按钮
            primary - 鼠标主按键，默认对应为left，除非系统设置了鼠标为左手模式
            secondary - 鼠标次按键，默认对应为right，除非系统设置了鼠标为左手模式
            left - 鼠标左键
            middle - 鼠标中键
            right - 鼠标右键
        @param {float} duration=0.0 - 移动鼠标所需时长
        """
        pyautogui.click(x=x, y=y, clicks=clicks, interval=interval,
                        button=button, duration=duration)

    @classmethod
    def double_click(cls, x=None, y=None, interval=0.0, button='primary', duration=0.0):
        """
        双击鼠标

        @param {int} x=None - 要点击鼠标的x坐标，None代表当前位置
        @param {int} y=None - 要点击鼠标的y坐标，None代表当前位置
        @param {float} interval=0.0 - 连续点击鼠标中间的间隔时长
        @param {str} button='primary' - 鼠标按钮
            primary - 鼠标主按键，默认对应为left，除非系统设置了鼠标为左手模式
            secondary - 鼠标次按键，默认对应为right，除非系统设置了鼠标为左手模式
            left - 鼠标左键
            middle - 鼠标中键
            right - 鼠标右键
        @param {float} duration=0.0 - 移动鼠标所需时长
        """
        cls.click(x=x, y=y, clicks=2, interval=interval, button=button, duration=duration)

    @classmethod
    def mouse_down(cls, x=None, y=None, button='primary', duration=0.0):
        """
        按下鼠标按键

        @param {int} x=None - 要点击鼠标的x坐标，None代表当前位置
        @param {int} y=None - 要点击鼠标的y坐标，None代表当前位置
        @param {str} button='primary' - 鼠标按钮
            primary - 鼠标主按键，默认对应为left，除非系统设置了鼠标为左手模式
            secondary - 鼠标次按键，默认对应为right，除非系统设置了鼠标为左手模式
            left - 鼠标左键
            middle - 鼠标中键
            right - 鼠标右键
        @param {float} duration=0.0 - 移动鼠标所需时长
        """
        pyautogui.mouseDown(x=x, y=y, button=button, duration=duration)

    @classmethod
    def mouse_up(cls, x=None, y=None, button='primary', duration=0.0):
        """
        释放鼠标按键

        @param {int} x=None - 要点击鼠标的x坐标，None代表当前位置
        @param {int} y=None - 要点击鼠标的y坐标，None代表当前位置
        @param {str} button='primary' - 鼠标按钮
            primary - 鼠标主按键，默认对应为left，除非系统设置了鼠标为左手模式
            secondary - 鼠标次按键，默认对应为right，除非系统设置了鼠标为左手模式
            left - 鼠标左键
            middle - 鼠标中键
            right - 鼠标右键
        @param {float} duration=0.0 - 移动鼠标所需时长
        """
        pyautogui.mouseUp(x=x, y=y, button=button, duration=duration)

    @classmethod
    def scroll(cls, clicks: float):
        """
        鼠标滚动

        @param {float} clicks - 向下滚动的距离，负数为向上滚动
        """
        pyautogui.scroll(clicks)


class Keyboard(object):
    """
    键盘控制模块

    键盘对应表：
    ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'returns', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
    'command', 'option', 'optionleft', 'optionright']
    """
    @classmethod
    def write(cls, message: str, interval=0.0):
        """
        进行可见字符输入(单字符，不支持中文)

        @param {str} message - 要输入的字符信息，见键盘对应表
        @param {float} interval=0.0 - 按下字符按键的间隔时长
        """
        return pyautogui.write(message, interval=interval)

    @classmethod
    def press(cls, keys: str, presses=1, interval=0.0):
        """
        敲指定的按键

        @param {str|list} keys - 要敲的按键，见键盘对应表
            注：如果是list, 则为敲多个字符
        @param {int} presses=1 - 重复敲多少次
        @param {float} interval=0.0 - 按键间隔时间
        """
        return pyautogui.press(keys, presses=presses, interval=interval)

    @classmethod
    def key_down(cls, key: str):
        """
        按下按键不释放

        @param {str} key - 要按下的按键，见键盘对应表
        """
        return pyautogui.keyDown(key)

    @classmethod
    def key_up(cls, key: str):
        """
        释放按下的按键

        @param {str} key - 要释放的按键，见键盘对应表
        """
        return pyautogui.keyUp(key)

    @classmethod
    def hotkey(cls, *args, **kwargs):
        """
        同时敲多个按键

        @param {args} - 需要同时敲的按键清单
            例如: hotkey('ctrl', 'shift', 'esc')
        """
        return pyautogui.hotkey(*args, **kwargs)


class Clipboard(object):
    """
    剪贴板的操作
    """

    @classmethod
    def write_text(cls, text: str):
        """
        向剪贴板写入文本

        @param {str} text - 要写入的文本
        """
        pyperclip.copy(text)

    @classmethod
    def get_text(cls) -> str:
        """
        从剪贴版获取文本

        @returns {str} - 获取到的文本
        """
        return pyperclip.paste()


class Window(object):
    """
    程序窗口操作模块(需实现类具体实现)
    """

    #############################
    # 应用操作
    #############################
    @classmethod
    def start_application(cls, run_para: str, **kwargs):
        """
        启动应用程序

        @param {str} run_para - 启动参数，例如'c:\path\to\your\application -a -n -y --arguments'
        @param {kwargs} - 具体实现类的扩展参数

        @returns {object} - 返回启动后的应用程序对象
        """
        raise NotImplementedError

    @classmethod
    def get_application(cls, **kwargs):
        """
        获取特定的应用程序

        @param {kwargs} - 具体实现类的扩展参数

        @returns {object} - 返回查找到的应用程序对象
        """
        raise NotImplementedError

    @classmethod
    def get_application_pid(cls, app):
        """
        获取应用的进程id

        @param {object} app - 获取到的应用对象

        @returns {int} - 应用对应的进程id
        """
        raise NotImplementedError

    @classmethod
    def kill_application(cls, app, soft=True):
        """
        关闭应用程序

        @param {object} app - 要关闭的应用
        @param {bool} soft=True - 是否通过发送关闭信息的方式结束应用，如果为False代表直接杀进程

        @retrun {bool} - 执行结果
        """
        raise NotImplementedError

    @classmethod
    def is_application_running(cls, app):
        """
        检查应用（进程）是否还在运行

        @param {object} app - 要检查的应用

        @returns {bool} - 是否还在运行
        """
        raise NotImplementedError

    @classmethod
    def application_active_window(cls, app):
        """
        获取应用的当前激活窗口

        @param {object} app - 应用对象

        @returns {object} - 获取到的激活窗口
        """
        raise NotImplementedError

    @classmethod
    def application_top_window(cls, app):
        """
        获取应用当前的最顶层窗口

        @param {object} app - 应用对象

        @returns {object} - 获取到的顶层窗口
        """
        raise NotImplementedError

    #############################
    # 窗口操作
    #############################
    @classmethod
    def get_active_window(cls, **kwargs):
        """
        获取当前激活窗口对象

        @param {kwargs} - 具体实现类的扩展参数

        @returns {object} - 返回当前激活的窗口对象
        """
        raise NotImplementedError

    @classmethod
    def find_window(cls, **kwargs):
        """
        根据指定条件查找窗口对象

        @param {kwargs} - 具体实现类的扩展参数

        @returns {object} - 查找到的窗口对象, 如果找不到返回None
        """
        raise NotImplementedError


class WindowException(Exception):
    """
    自定义的窗口操作异常类
    """
    pass


class WindowControlSpec(object):
    """
    窗体控件规格对象
    (定义窗体控件的属性和操作)
    """

    #############################
    # 构造函数
    #############################
    def __init__(self, **kwargs):
        """
        构造函数
        """
        raise NotImplementedError()

    #############################
    # 属性
    #############################
    @property
    def handle(self) -> int:
        """
        窗口句柄
        @property {int}
        """
        raise NotImplementedError()

    @property
    def class_name(self) -> str:
        """
        窗口类名
        @property {str}
        """
        raise NotImplementedError()

    @property
    def name(self) -> str:
        """
        窗口标题
        @property {str}
        """
        raise NotImplementedError()

    @property
    def process_id(self) -> int:
        """
        窗口所在进程id
        @property {int}
        """
        raise NotImplementedError()

    @property
    def thread_id(self) -> int:
        """
        窗口所在线程id
        @property {int}
        """
        raise NotImplementedError()

    @property
    def is_active(self) -> bool:
        """
        是否激活状态
        @property {bool}
        """
        raise NotImplementedError()

    @property
    def is_visible(self) -> bool:
        """
        窗口是否可见
        @property {bool}
        """
        raise NotImplementedError()

    @property
    def is_enabled(self) -> bool:
        """
        窗口是否启用
        @property {bool}
        """
        raise NotImplementedError()

    @property
    def is_minimized(self) -> bool:
        """
        窗口是否最小化(图标化)
        @property {bool}
        """
        raise NotImplementedError()

    @property
    def is_maximized(self) -> bool:
        """
        窗口是否最大化
        @property {bool}
        """
        raise NotImplementedError()

    @property
    def parent(self):
        """
        获取父窗口对象
        (如果没有父窗口返回None)
        @property {WindowControlSpec}
        """
        raise NotImplementedError()

    @property
    def win_rect(self) -> tuple:
        """
        获取窗口的区域(left, top, right, bottom)
        @property {tuple}
        """
        raise NotImplementedError()

    @property
    def v_scroll_viewsize(self) -> float:
        """
        获取垂直滚动条的显示区域百分占比
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        raise NotImplementedError()

    @property
    def v_scroll_pos(self) -> float:
        """
        获取垂直滚动条的当前位置
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        raise NotImplementedError()

    @property
    def h_scroll_viewsize(self) -> float:
        """
        获取水平滚动条的显示区域百分占比
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        raise NotImplementedError()

    @property
    def h_scroll_pos(self) -> float:
        """
        获取水平滚动条的当前位置
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        raise NotImplementedError()

    #############################
    # 窗口遍历
    #############################
    def get_childrens(self):
        """
        获取当前窗口的子对象

        @returns {list} - 返回子窗口对象清单
        """
        raise NotImplementedError()

    def get_next_sibling(self):
        """
        获取当前窗口的下一同级窗口

        @returns {WindowControlSpec} - 下一同级窗口对象，如果找不到返回None
        """
        raise NotImplementedError()

    def get_previous_sibling(self):
        """
        获取当前窗口的上一同级窗口

        @returns {WindowControlSpec} - 上一同级窗口对象，如果找不到返回None
        """
        raise NotImplementedError()

    #############################
    # 窗口操作 - 状态
    #############################
    def set_foreground(self):
        """
        将窗口放在前台并激活
        """
        raise NotImplementedError()

    def bring_to_top(self):
        """
        将窗口设置到z-index的顶部
        如果窗口为顶层窗口，则该窗口被激活；如果窗口为子窗口，则相应的顶级父窗口被激活
        """
        raise NotImplementedError()

    def close_window(self) -> None:
        """
        关闭窗口
        """
        raise NotImplementedError()

    def set_focus(self):
        """
        将窗口设置焦点
        """
        raise NotImplementedError()

    #############################
    # 窗口操作 - 位置和外观
    #############################
    def set_name(self, name: str):
        """
        设置窗口标题文字

        @param {str} name - 要设置的窗口标题文字
        """
        raise NotImplementedError()

    def maximize(self):
        """
        最大化窗口
        """
        raise NotImplementedError()

    def minimize(self):
        """
        最小化窗口
        """
        raise NotImplementedError()

    def restore(self):
        """
        还原窗口
        """
        raise NotImplementedError()

    def hide(self):
        """
        隐藏窗口
        """
        raise NotImplementedError()

    def show(self):
        """
        显示窗口
        """
        raise NotImplementedError()

    def center(self):
        """
        窗口居中显示
        """
        raise NotImplementedError()

    def move(self, x=None, y=None, width=None, height=None):
        """
        移动窗口

        @param {int} x=None - x位置, None代表保持当前位置
        @param {int} y=None - y位置, None代表保持当前位置
        @param {int} width=None - 窗口宽度, None代表保持当前宽度
        @param {int} height=None - 窗口高度, None代表保持当前高度
        """
        raise NotImplementedError()

    #############################
    # 窗口操作 - 滚动条
    #############################
    def v_scroll_to(self, pos: float):
        """
        滚动垂直滚动条到指定位置

        @param {float} pos - 要滚动到的位置百分比，[0.0, 100.0]之间
        """
        raise NotImplementedError()

    def v_scroll_to_head(self):
        """
        滚动垂直滚动条到开头
        """
        raise NotImplementedError()

    def v_scroll_to_end(self):
        """
        滚动垂直滚动条到最后
        """
        raise NotImplementedError()

    def h_scroll_to(self, pos: float):
        """
        滚动水平滚动条到指定位置

        @param {float} pos - 要滚动到的位置百分比，[0.0, 100.0]之间
        """
        raise NotImplementedError()

    def h_scroll_to_head(self):
        """
        滚动垂直滚动条到开头
        """
        raise NotImplementedError()

    def h_scroll_to_end(self) -> int:
        """
        滚动垂直滚动条到最后
        """
        raise NotImplementedError()

    #############################
    # 窗口操作 - 菜单
    #############################

    #############################
    # 窗口操作 - 控件处理
    #############################


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    # Clipboard.write_text('测试中文')
    s = Clipboard.get_text()
    print('haha')
