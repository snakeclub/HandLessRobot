#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
appium移动操作控制
@module appium_control
@file appium_control.py
"""

import os
import sys
import copy
import math
import time
import subprocess
from enum import Enum
import pyscreeze
from io import BytesIO
from PIL import Image
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from HiveNetLib.base_tools.file_tool import FileTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))


__MOUDLE__ = 'appium_control'  # 模块名
__DESCRIPT__ = u'appium移动操作控制'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.11.17'  # 发布日期


class EnumAndroidKeycode(Enum):
    """
    安卓的按键编码
    可参考的清单：https://elementalx.org/button-mapper/android-key-codes/

    @enum {int}
    """
    #############################
    # 电话键
    #############################
    CALL = 5  # 拨号键
    ENDCALL = 6  # 挂机键
    HOME = 3  # 按键Home
    MENU = 82  # 菜单键
    BACK = 4  # 返回键
    SEARCH = 84  # 搜索键
    CAMERA = 27  # 拍照键
    FOCUS = 80  # 拍照对焦键
    POWER = 26  # 电源键
    NOTIFICATION = 83  # 通知键
    MUTE = 91  # 话筒静音键
    VOLUME_MUTE = 164  # 扬声器静音键
    VOLUME_UP = 24  # 音量增加键
    VOLUME_DOWN = 25  # 音量减小键
    #############################
    # 控制键
    #############################
    ENTER = 66  # 回车键
    ESCAPE = 111  # ESC键
    DPAD_CENTER = 23  # 确定键
    DPAD_UP = 19  # 向上
    DPAD_DOWN = 20  # 向下
    DPAD_LEFT = 21  # 向左
    DPAD_RIGHT = 22  # 向右
    MOVE_HOME = 122  # 光标移动到开始键
    MOVE_END = 123  # 光标移动到末尾键
    PAGE_UP = 92  # 向上翻页键
    PAGE_DOWN = 93  # 向下翻页键
    DEL = 67  # 退格键
    FORWARD_DEL = 112  # 删除键
    INSERT = 124  # 插入键
    TAB = 61  # Tab键
    CAPS_LOCK = 115  # 大写锁定键
    BREAK = 121  # Break/Pause键
    SCROLL_LOCK = 116  # 滚动锁定键
    ZOOM_IN = 168  # 放大键
    ZOOM_OUT = 169  # 缩小键
    #############################
    # 按键
    #############################
    KEY_0 = 7  # 按键'0'
    KEY_1 = 8  # 按键'1'
    KEY_2 = 9  # 按键'2'
    KEY_3 = 10  # 按键'3'
    KEY_4 = 11  # 按键'4'
    KEY_5 = 12  # 按键'5'
    KEY_6 = 13  # 按键'6'
    KEY_7 = 14  # 按键'7'
    KEY_8 = 15  # 按键'8'
    KEY_9 = 16  # 按键'9'
    KEY_A = 29  # 按键'A'
    KEY_B = 30  # 按键'B'
    KEY_C = 31  # 按键'C'
    KEY_D = 32  # 按键'D'
    KEY_E = 33  # 按键'E'
    KEY_F = 34  # 按键'F'
    KEY_G = 35  # 按键'G'
    KEY_H = 36  # 按键'H'
    KEY_I = 37  # 按键'I'
    KEY_J = 38  # 按键'J'
    KEY_K = 39  # 按键'K'
    KEY_L = 40  # 按键'L'
    KEY_M = 41  # 按键'M'
    KEY_N = 42  # 按键'N'
    KEY_O = 43  # 按键'O'
    KEY_P = 44  # 按键'P'
    KEY_Q = 45  # 按键'Q'
    KEY_R = 46  # 按键'R'
    KEY_S = 47  # 按键'S'
    KEY_T = 48  # 按键'T'
    KEY_U = 49  # 按键'U'
    KEY_V = 50  # 按键'V'
    KEY_W = 51  # 按键'W'
    KEY_X = 52  # 按键'X'
    KEY_Y = 53  # 按键'Y'
    KEY_Z = 54  # 按键'Z'
    #############################
    # 符号
    #############################
    PLUS = 81  # 按键'+'
    MINUS = 69  # 按键'-'
    STAR = 17  # 按键'*'
    SLASH = 76  # 按键'/'
    EQUALS = 70  # 按键'='
    AT = 77  # 按键'@'
    POUND = 18  # 按键'#'
    APOSTROPHE = 75  # 按键''' (单引号)
    BACKSLASH = 73  # 按键'\'
    COMMA = 55  # 按键','
    PERIOD = 56  # 按键'.'
    LEFT_BRACKET = 71  # 按键'['
    RIGHT_BRACKET = 72  # 按键']'
    SEMICOLON = 74  # 按键';'
    GRAVE = 68  # 按键'`'
    SPACE = 62  # 空格键
    #############################
    # 小键盘
    #############################
    NUM_LOCK = 143  # 小键盘NUM_LOCK按键
    NUMPAD_0 = 144  # 小键盘按键'0'
    NUMPAD_1 = 145  # 小键盘按键'1'
    NUMPAD_2 = 146  # 小键盘按键'2'
    NUMPAD_3 = 147  # 小键盘按键'3'
    NUMPAD_4 = 148  # 小键盘按键'4'
    NUMPAD_5 = 149  # 小键盘按键'5'
    NUMPAD_6 = 150  # 小键盘按键'6'
    NUMPAD_7 = 151  # 小键盘按键'7'
    NUMPAD_8 = 152  # 小键盘按键'8'
    NUMPAD_9 = 153  # 小键盘按键'9'
    NUMPAD_ADD = 157  # 小键盘按键'+'
    NUMPAD_SUBTRACT = 156  # 小键盘按键'-'
    NUMPAD_MULTIPLY = 155  # 小键盘按键'*'
    NUMPAD_DIVIDE = 154  # 小键盘按键'/'
    NUMPAD_EQUALS = 161  # 小键盘按键'='
    NUMPAD_COMMA = 159  # 小键盘按键','
    NUMPAD_DOT = 158  # 小键盘按键'.'
    NUMPAD_LEFT_PAREN = 162  # 小键盘按键'('
    NUMPAD_RIGHT_PAREN = 163  # 小键盘按键')'
    NUMPAD_ENTER = 160  # 小键盘按键回车
    #############################
    # 功能键
    #############################
    F1 = 131  # 按键F1
    F2 = 132  # 按键F2
    F3 = 133  # 按键F3
    F4 = 134  # 按键F4
    F5 = 135  # 按键F5
    F6 = 136  # 按键F6
    F7 = 137  # 按键F7
    F8 = 138  # 按键F8
    F9 = 139  # 按键F9
    F10 = 140  # 按键F10
    F11 = 141  # 按键F11
    F12 = 142  # 按键F12
    #############################
    # 多媒体控制
    #############################
    MEDIA_PLAY = 126  # 多媒体键 播放
    MEDIA_STOP = 86  # 多媒体键 停止
    MEDIA_PAUSE = 127  # 多媒体键 暂停
    MEDIA_PLAY_PAUSE = 85  # 多媒体键 播放/暂停
    MEDIA_FAST_FORWARD = 90  # 多媒体键 快进
    MEDIA_REWIND = 89  # 多媒体键 快退
    MEDIA_NEXT = 87  # 多媒体键 下一首
    MEDIA_PREVIOUS = 88  # 多媒体键 上一首
    MEDIA_RECORD = 130  # 多媒体键 录音
    #############################
    # 组合键
    #############################
    ALT_LEFT = 57  # Alt+Left
    ALT_RIGHT = 58  # Alt+Right
    CTRL_LEFT = 113  # Control+Left
    CTRL_RIGHT = 114  # Control+Right
    SHIFT_LEFT = 59  # Shift+Left
    SHIFT_RIGHT = 60  # Shift+Right
    #############################
    # META 元素标记
    #############################
    META_ALT_LEFT_ON = 16  # This mask is used to check whether the left ALT meta key is pressed.
    # This mask is a combination of META_ALT_ON, META_ALT_LEFT_ON and META_ALT_RIGHT_ON.
    META_ALT_MASK = 50
    META_ALT_ON = 2  # This mask is used to check whether one of the ALT meta keys is pressed.
    # This mask is used to check whether the right the ALT meta key is pressed.
    META_ALT_RIGHT_ON = 32
    META_CAPS_LOCK_ON = 1048576  # This mask is used to check whether the CAPS LOCK meta key is on.
    # This mask is used to check whether the left CTRL meta key is pressed.
    META_CTRL_LEFT_ON = 8192
    # This mask is a combination of META_CTRL_ON, META_CTRL_LEFT_ON and META_CTRL_RIGHT_ON.
    META_CTRL_MASK = 28672
    META_CTRL_ON = 4096  # This mask is used to check whether one of the CTRL meta keys is pressed.
    # This mask is used to check whether the right CTRL meta key is pressed.
    META_CTRL_RIGHT_ON = 16384
    META_FUNCTION_ON = 8  # This mask is used to check whether the FUNCTION meta key is pressed.
    # This mask is used to check whether the left META meta key is pressed.
    META_META_LEFT_ON = 131072
    # This mask is a combination of META_META_ON, META_META_LEFT_ON and META_META_RIGHT_ON.
    META_META_MASK = 458752
    META_META_ON = 65536  # This mask is used to check whether one of the META meta keys is pressed.
    # This mask is used to check whether the right META meta key is pressed.
    META_META_RIGHT_ON = 262144
    META_NUM_LOCK_ON = 2097152  # This mask is used to check whether the NUM LOCK meta key is on.
    # This mask is used to check whether the SCROLL LOCK meta key is on.
    META_SCROLL_LOCK_ON = 4194304
    # This mask is used to check whether the left SHIFT meta key is pressed.
    META_SHIFT_LEFT_ON = 64
    # This mask is a combination of META_SHIFT_ON, META_SHIFT_LEFT_ON and META_SHIFT_RIGHT_ON.
    META_SHIFT_MASK = 193
    META_SHIFT_ON = 1  # This mask is used to check whether one of the SHIFT meta keys is pressed.
    # This mask is used to check whether the right SHIFT meta key is pressed.
    META_SHIFT_RIGHT_ON = 128
    META_SYM_ON = 4  # This mask is used to check whether the SYM meta key is pressed.


class AppElement(object):
    """
    应用元素类
    """

    #############################
    # 构造函数
    #############################
    def __init__(self, element: webdriver.WebElement, driver: webdriver.webdriver.WebDriver):
        """
        应用元素类

        @param {webdriver.WebElement} element - 初始化元素对象
        @param {webdriver.webdriver.WebDriver} driver - appium WebDriver
        """
        self.element = element
        self.driver = driver

    def __eq__(self, element):
        """
        判断两个元素是否同一个
        """
        return hasattr(element, 'id') and self.id == element.id

    #############################
    # 属性
    #############################
    @property
    def id(self):
        """
        返回元素id

        @property {int}
        """
        return self.element.id

    @property
    def appium_element(self) -> webdriver.WebElement:
        """
        获取WebElement对象

        @property {webdriver.WebElement}
        """
        return self.element

    @property
    def appium_driver(self):
        """
        appium WebDriver

        @property {webdriver.webdriver.WebDriver}
        """
        return self.driver

    @property
    def text(self) -> str:
        """
        获取元素可见文本

        @property {str}
        """
        return self.element.text

    @property
    def tag_name(self) -> str:
        """
        获取元素标签名

        @property {str}
        """
        return self.element.tag_name

    @property
    def is_selected(self) -> bool:
        """
        获取元素是否被选中

        @property {bool}
        """
        return self.element.is_selected

    @property
    def is_enabled(self) -> bool:
        """
        获取元素是否可操作

        @property {bool}
        """
        return self.element.is_enabled

    @property
    def is_displayed(self) -> bool:
        """
        获取元素是否可见

        @property {bool}
        """
        return self.element.is_displayed

    @property
    def location(self) -> tuple:
        """
        获取元素在页面中的位置(左上角)

        @property {tuple[int, int]} - (x, y) 坐标
        """
        _location = self.element.location
        return _location['x'], _location['y']

    @property
    def location_in_view(self) -> tuple:
        """
        获取元素在视图中的位置(左上角)

        @property {tuple[int, int]} - (x, y) 坐标
        """
        _location = self.element.location_in_view
        return _location['x'], _location['y']

    @property
    def size(self) -> tuple:
        """
        获取元素大小

        @property {tuple[int, int]} - (width, height) 大小
        """
        _size = self.element.size
        return _size['width'], _size['height']

    @property
    def rect(self) -> tuple:
        """
        获取元素区域

        @property {tuple[int, int, int, int]} - (x, y, width, height)
        """
        _rect = self.element.rect
        return _rect['x'], _rect['y'], _rect['width'], _rect['height']

    def get_attribute(self, name: str) -> str:
        """
        获取元素指定名称的属性(attribute/property)

        @param {str} name - 属性名

        @returns {str} - 属性取值，如果属性不存在返回空字符串
        """
        return self.element.get_attribute(name)

    def get_css_property(self, property_name: str) -> str:
        """
        获取元素的CSS属性值

        @param {str} property_name - css的属性名，例如 'style' 或 'background-color'

        @returns {str} - 返回属性值
        """
        return self.element.value_of_css_property(property_name)

    #############################
    # 屏幕操作
    #############################
    def screenshot(self, filename: str = None) -> Image:
        """
        保存元素截图

        @param {str} filename=None - 要保存的路径

        @returns {PIL.Image} - 图片对象
        """
        _image = Image.open(BytesIO(self.element.screenshot_as_png))
        if filename is not None:
            _image.save(filename)

        return _image

    #############################
    # 对元素的操作
    #############################
    def set_value(self, value: str):
        """
        设置元素的值

        @param {str} value - 要设置的值
        """
        self.element.set_value(value=value)

    def click(self):
        """
        在元素的中心点进行点击
        """
        self.element.click()

    def clear(self):
        """
        清除元素的值
        """
        self.element.clear()

    def send_keys(self, *value):
        """
        向元素输入一连串的按键值(字符串)

        @param {args:str} - 输入一个或多个字符串
        """
        self.element.send_keys(*value)

    def tap(self, count: int = 1, pre_action: TouchAction = None) -> TouchAction:
        """
        点击元素

        @param {int} count=1 - 连续点击的次数
        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        # 执行操作
        return _action.tap(element=self.element, count=count).perform()

    def long_press(self, duration: int = 1000,
                   pre_action: TouchAction = None) -> TouchAction:
        """
        在元素上长按

        @param {int} duration=1000 - 经历时长，单位为毫秒
        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        # 执行操作
        return _action.long_press(el=self.element, duration=duration).perform()

    def drag_and_drop(self, element=None, x: int = None, y: int = None, duration: int = 0,
                      pre_action: TouchAction = None) -> TouchAction:
        """
        拖动元素到指定位置

        @param {AppElement} element=None - 要拖动到的目标元素
        @param {int} x=None - 要拖动到的位置x
        @param {int} y=None - 要拖动到的位置y
        @param {int} duration=0 - 拖动过程耗时
        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        # 组合动作
        _action.press(el=self.element)
        if element is not None:
            _action.move_to(el=element.element)
        else:
            if x is None or y is None:
                _w, _h = self.size
            if x is None:
                x = math.ceil(_w / 2.0)
            if y is None:
                y = math.ceil(_h / 2.0)

            _action.move_to(x=x, y=y)

        if duration > 0:
            _action.wait(duration)

        # 执行
        return _action.perform()


class AppDevice(object):
    """
    移动设备操作模块
    """
    #############################
    # 静态的连接参数
    #############################
    @classmethod
    def get_app_device(cls, appium_server: str = None, desired_caps: dict = None,
                       driver: webdriver.webdriver.WebDriver = None, **kwargs):
        """
        获取移动应用设备对象

        @param {str} appium_server=None - appium服务器连接
            示例：'http://localhost:4723/wd/hub'
        @param {dict} desired_caps=None - 设备连接参数字典
            参考：http://appium.io/docs/cn/writing-running-appium/caps/
            主要参数如下：
            platformName {str} - 使用的手机操作系统, iOS, Android, 或者 FirefoxOS
            platformVersion {str} - 手机操作系统的版本, 例如 7.1, 4.4
            deviceName {str} - 使用的手机或模拟器类型, 填入 adb devices -l 显示的设备连接名,
                示例: 127.0.0.1:21513
            noReset {bool} - 在当前 session 下不会重置应用的状态, 防止缓存状态丢失。默认值为 False
            appPackage {str} - 安卓独有参数, 连接时运行的 Android 应用的包名, 例如: com.android.browser
            appActivity {str} - 安卓独有参数, 包中所要启动的 Android acticity, 例如: .BrowserActivity
        @param {webdriver.webdriver.WebDriver} driver=None - 如果传入该值，说明直接使用现有的实例对象创建
            注意：如果传入driver，则关闭时不退出driver测试
        @param {kwargs} - 扩展参数，支持的扩展参数包括
            driver_settings {dict} - 设置driver的配置信息，具体定义参考 https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md
                默认设置的参考包括:
                    "waitForIdleTimeout" : 100    # 用于降低空闲等待的超时时间，提高执行速度
            shell_encoding {str} - shell命令的编码方式, 在使用到命令行工具时使用, 默认为 'utf-8'
            adb_name {str} - 安卓专用, adb命令的启动名称, 默认为 'adb'

        @returns {AppDevice} - 返回Appium的设备对象
        """
        return AppDevice(
            appium_server=appium_server, desired_caps=desired_caps,
            driver=driver, **kwargs
        )

    #############################
    # 构造函数及析构函数
    #############################
    def __init__(self, appium_server: str = None, desired_caps: dict = None,
                 driver: webdriver.webdriver.WebDriver = None, **kwargs):
        """
        构造函数

        @param {str} appium_server=None - appium服务器连接
            示例：'http://localhost:4723/wd/hub'
        @param {dict} desired_caps=None - 设备连接参数字典
            参考：http://appium.io/docs/cn/writing-running-appium/caps/
            主要参数如下：
            platformName {str} - 使用的手机操作系统, iOS, Android, 或者 FirefoxOS
            platformVersion {str} - 手机操作系统的版本, 例如 7.1, 4.4
            deviceName {str} - 使用的手机或模拟器类型, 填入 adb devices -l 显示的设备连接名,
                示例: 127.0.0.1:21513
            noReset {bool} - 在当前 session 下不会重置应用的状态, 防止缓存状态丢失。默认值为 False
            appPackage {str} - 安卓独有参数, 连接时运行的 Android 应用的包名, 例如: com.android.browser
            appActivity {str} - 安卓独有参数, 包中所要启动的 Android acticity, 例如: .BrowserActivity
        @param {webdriver.webdriver.WebDriver} driver=None - 如果传入该值，说明直接使用现有的实例对象创建
            注意：如果传入driver，则关闭时不退出driver测试
        @param {kwargs} - 扩展参数，支持的扩展参数包括
            driver_settings {dict} - 设置driver的配置信息，具体定义参考 https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md
                默认设置的参考包括:
                    "waitForIdleTimeout" : 100    # 用于降低空闲等待的超时时间，提高执行速度
            shell_encoding {str} - shell命令的编码方式, 在使用到命令行工具时使用, 默认为 'utf-8'
            adb_name {str} - adb命令的启动名称, 安卓adb版专用, 默认为 'adb'
            tmp_path {str} - 临时目录, 处理adb资源文件, 安卓adb版专用, 默认为当前工作目录
        """
        self._appium_server = ''
        self._desired_caps = {}
        self.driver: webdriver.webdriver.WebDriver = None
        self.is_from_driver = False
        if driver is not None:
            self.driver = driver
            self.is_from_driver = True
        else:
            self._appium_server = appium_server
            self._desired_caps = copy.deepcopy(desired_caps)
            self.driver = webdriver.Remote(self._appium_server, self._desired_caps)

        # 提升参数
        self.driver.update_settings(
            {
                "waitForIdleTimeout": 100
            }.update(kwargs.get('driver_settings', {}))
        )

        # 其他参数
        self.shell_encoding = kwargs.get('shell_encoding', 'utf-8')
        self.adb_name = kwargs.get('adb_name', 'adb')
        self.tmp_path = os.path.abspath(kwargs.get('tmp_path', ''))
        FileTool.create_dir(self.tmp_path, exist_ok=True)

        # 判断命令行
        self.grep_str = 'findstr' if sys.platform == 'win32' else 'grep'

        # 缓存字典
        self.cache = dict()

    def __del__(self):
        """
        析构函数
        """
        if not self.is_from_driver:
            self.driver.quit()

    #############################
    # 实例基础属性
    #############################
    @property
    def appium_driver(self) -> webdriver.webdriver.WebDriver:
        """
        获取连接上的 WebDriver 对象
        @property {webdriver.webdriver.WebDriver}
        """
        return self.driver

    @property
    def size(self) -> tuple:
        """
        获取屏幕大小
        @property {tuple[int, int]}
        """
        _size = self.driver.get_window_size()
        return _size['width'], _size['height']

    @property
    def desired_caps(self) -> dict:
        """
        返回设备连接参数
        @property {dict}
        """
        return self.driver.desired_capabilities

    @property
    def appium_server(self) -> str:
        """
        返回连接的appium server的地址
        @property {str}
        """
        return self._appium_server

    #############################
    # 工具类函数
    #############################
    @classmethod
    def center(cls, coords) -> tuple:
        """
        返回指定区域的中心位置

        @param {(int,int,int,int)} coords - 区域坐标(x, y, width, height)

        @returns {(int, int)} - 返回的中心位置(x, y)
        """
        _x = coords[0] + math.ceil(coords[2] / 2.0)
        _y = coords[1] + math.ceil(coords[3] / 2.0)
        return _x, _y

    #############################
    # 会话相关处理
    #############################
    @property
    def page_source(self) -> str:
        """
        获取当前页面源码

        @property {str}
        """
        return self.driver.page_source

    def update_settings(self, settings: dict):
        """
        更新设置

        @param {dict} settings - 要更新的设置字典, 有用的几个参数：
            IMAGE_MATCH_THRESHOLD {float} - 匹配度，默认0.4，可以设置小一点更容易匹配上
            FIX_IMAGE_FIND_SCREENSHOT_DIMENSIONS {bool} - 该参数可以解决屏幕快照和设备尺寸不匹配的问题, 默认为true, 可以设置为false不进行处理减少CPU消耗
            FIX_IMAGE_TEMPLATE_SIZE {bool} - 解决查找图片大小和屏幕原大小不一致的问题，默认为false，如果希望查找图片大小不受限制，可以设置为true
        """
        self.driver.update_settings(settings)

    def get_clipboard_text(self) -> str:
        """
        获取剪切板文本

        @returns {str} - 获取到的文本，如果没有信息返回空字符串
        """
        return self.driver.get_clipboard_text()

    def set_clipboard_text(self, text: str, label: str = None):
        """
        设置剪贴版文本

        @param {str} text - 要设置的文本
        @param {str} label=None - 仅用于Android的剪贴板数据标签
        """
        self.driver.set_clipboard_text(text, label=label)

    #############################
    # app操作相关
    #############################

    def query_app_state(self, app_id: str) -> int:
        """
        查询应用状态

        @param {str} app_id - iOS bundleID或Android包名

        @returns {int} - 应用状态码
            0 is not installed.
            1 is not running.
            2 is running in background or suspended.
            3 is running in background.
            4 is running in foreground.
        """
        return self.driver.query_app_state(app_id)

    def is_app_installed(self, bundle_id: str) -> bool:
        """
        是否安装了指定的应用程序

        @param {str} bundle_id - iOS bundleID或Android包名

        @returns {bool} - 检查结果
        """
        self.driver.is_app_installed(bundle_id)

    def install_app(self, app_path: str, **options):
        """
        安装应用

        @param {str} app_path - app安装路径
        @param {kwargs} options - 安装参数（安卓专用）:
            replace (bool): [Android only] whether to reinstall/upgrade the package if it is
                already present on the device under test. True by default
            timeout (int): [Android only] how much time to wait for the installation to complete.
                60000ms by default.
            allowTestPackages (bool): [Android only] whether to allow installation of packages marked
                as test in the manifest. False by default
            useSdcard (bool): [Android only] whether to use the SD card to install the app. False by default
            grantPermissions (bool): [Android only] whether to automatically grant application permissions
                on Android 6+ after the installation completes. False by default
        """
        return self.driver.install_app(app_path, **options)

    def remove_app(self, app_id: str, **options):
        """
        删除应用

        @param {str} app_id - iOS appID, bundleID或Android包名
            示例: 'com.example.AppName'
        @param {kwargs} options - 卸载参数（安卓专用）:
            keepData (bool): [Android only] whether to keep application data and caches after it is uninstalled.
                False by default
            timeout (int): [Android only] how much time to wait for the uninstall to complete.
                20000ms by default.
        """
        self.driver.remove_app(app_id, **options)

    def launch_app(self):
        """
        启动被测应用
        注：如果被测应用（AUT）已关闭或在后台运行，它将启动它。如果AUT已打开，它将使其放到后台并重新启动。
        """
        self.driver.launch_app()

    def background_app(self, seconds: int):
        """
        将当前正在运行的应用放置在后台执行

        @param {int} seconds - 执行的时长，单位为秒
        """
        self.driver.background_app(seconds)

    def close_app(self):
        """
        关闭当前正在测试的应用
        """
        self.driver.close_app()

    def reset_app(self):
        """
        重置当前正在运行的应用
        """
        self.driver.reset()

    def activate_app(self, app_id: str):
        """
        激活指定应用

        @param {str} app_id - iOS bundleID或Android包名
            示例：'com.apple.Preferences'
        """
        self.driver.activate_app(app_id)

    def terminate_app(self, app_id: str, **options) -> bool:
        """
        中止应用运行

        @param {str} app_id - iOS bundleID或Android包名
            示例：'com.apple.Preferences'
        @param {kwargs} - options - 中止参数（安卓专用）:
            `timeout` (int): [Android only] how much time to wait for the uninstall to complete.
                500ms by default.

        @returns {bool} - 是否中止成功
        """
        return self.driver.terminate_app(app_id, **options)

    #############################
    # 动作 - 控制
    #############################

    def wait(self, duration: int = 0, pre_action: TouchAction = None) -> TouchAction:
        """
        执行动作之间的主动等待时长

        @param {int} duration=0 - 经历时长，单位为毫秒
        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        return _action.wait(ms=duration).perform()

    def implicitly_wait(self, time_to_wait: float):
        """
        设置在查找元素时driver必须等待的时间量

        @param {float} time_to_wait - 等待超时时间，单位为秒
        """
        self.driver.implicitly_wait(time_to_wait)

    #############################
    # 屏幕操作
    #############################
    @property
    def orientation(self) -> str:
        """
        获取当前显示方式（横屏/竖屏）

        @property {str} - LANDSCAPE - 横向显示，PORTRAIT - 纵向显示
        """
        return self.driver.orientation

    def set_orientation(self, show_type: str):
        """
        设置当前显示方式（横屏/竖屏）

        @param {str} show_type - LANDSCAPE - 横向显示，PORTRAIT - 纵向显示, 不区分大小写
        """
        self.driver.orientation = show_type

    def screenshot(self, filename: str = None) -> Image:
        """
        保存屏幕截图

        @param {str} filename=None - 要保存的路径

        @returns {PIL.Image} - 图片对象
        """
        _image = Image.open(BytesIO(self.driver.get_screenshot_as_png()))
        if filename is not None:
            _image.save(filename)

        return _image

    def locate_on_screen(self, image, minSearchTime: int = 0, **kwargs):
        """
        在屏幕中定位指定图片的位置

        @param {str|PIL.Image} image - 要定位的图片文件路径或图片对象
        @param {int} minSearchTime=0 - 最长搜索时间，单位为毫秒，设置这个值可以在找不到图片的情况下，循环等待屏幕变化重新匹配
        @param {dict} kwargs - 其他执行参数:
            {bool} grayscale=False - 是否转换图片为灰度检索(提升30%速度)
            {int} limit=10000 - 匹配数量限制
            {int} step=1 - 匹配步骤，支持送1或2，如果为2会跳过细节，大约能提升3倍速度，但有可能匹配不上
            {float} confidence=0.999 - 匹配度

        @returns {(int, int, int, int)} - 返回图片的位置(x, y, width, height), 找不到返回None
        """
        if type(image) == str:
            _image = Image.open(image)
        else:
            _image = image

        start = time.time()
        while True:
            try:
                screenshotIm = self.screenshot()
                retVal = pyscreeze.locate(_image, screenshotIm, **kwargs)
                if retVal or time.time() - start > minSearchTime:
                    return retVal
            except pyscreeze.ImageNotFoundException:
                return None

    def locate_all_on_screen(self, image, **kwargs):
        """
        在屏幕中定位指定图片的所有位置

        @param {str|PIL.Image} image - 要定位的图片文件路径或图片对象
        @param {dict} kwargs - 其他执行参数:
            {bool} grayscale=False - 是否转换图片为灰度检索(提升30%速度)
            {int} limit=10000 - 匹配数量限制
            {int} step=1 - 匹配步骤，支持送1或2，如果为2会跳过细节，大约能提升3倍速度，但有可能匹配不上
            {float} confidence=0.999 - 匹配度

        @returns {list} - 返回所找到的所有图片的位置
            [(x, y, width, height), ..]
        """
        if type(image) == str:
            _image = Image.open(image)
        else:
            _image = image

        screenshotIm = self.screenshot()
        retVal = pyscreeze.locateAll(_image, screenshotIm, **kwargs)
        return list(retVal)

    #############################
    # 动作 - 滑动
    #############################

    def swipe(self, start: tuple, end: tuple, duration: int = 0):
        """
        执行两点之间的滑动

        @param {tuple} start - 滑动开始点的 (x, y) 位置
        @param {tuple} end - 滑动结束点的 (x, y) 位置
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        self.driver.swipe(
            start[0], start[1], end[0], end[1], duration=duration
        )

    def swipe_up(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向上滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间下方距离swipe_len一半的位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕高度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_h / 3.0)
        if y is None:
            y = min(math.ceil(_h / 2.0 + swipe_len / 2.0), _h)

        # 执行滑动处理
        self.swipe(
            (x, y), (x, max(y - swipe_len, 0)), duration=duration
        )

    def swipe_down(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向下滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间上方距离swipe_len一半的位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕高度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_h / 3.0)
        if y is None:
            y = max(math.ceil(_h / 2.0 - swipe_len / 2.0), 0)

        # 执行滑动处理
        self.swipe(
            (x, y), (x, min(y + swipe_len, _h)), duration=duration
        )

    def swipe_left(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向左滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间右方距离swipe_len一半的位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_w / 3.0)
        if x is None:
            x = min(math.ceil(_w / 2.0 + swipe_len / 2.0), _w)

        # 执行滑动处理
        self.swipe(
            (x, y), (max(x - swipe_len, 0), y), duration=duration
        )

    def swipe_right(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向左滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间左方距离swipe_len一半的位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_w / 3.0)
        if x is None:
            x = max(math.ceil(_w / 2.0 - swipe_len / 2.0), 0)

        # 执行滑动处理
        self.swipe(
            (x, y), (min(x + swipe_len, _w), y), duration=duration
        )

    def swipe_plus(self, points: list, pre_action: TouchAction = None, is_release: bool = True) -> TouchAction:
        """
        超级滑动处理

        @param {list} points - 要滑动的点配置，每个点为一个 tuple(x, y, duration)
        @param {TouchAction} pre_action=None - 预定义动作实例，如果传入则代表已按下，
            将沿用原来动作痕迹继续处理，无需再执行press动作
        @param {bool} is_release=True - 执行到结尾是否提起手指

        @returns {TouchAction} - 动作实例对象
        """
        if pre_action is None:
            # 新创建动作
            _action = TouchAction(self.driver).press(
                x=points[0][0], y=points[0][1]).wait(points[0][2])
        else:
            # 延续上一动作，先执行第一个点，单独执行是决对路径
            _action = pre_action.move_to(
                x=points[0][0], y=points[0][1]).wait(points[0][2]).perform()

        # 遍历处理
        for _index in range(1, len(points)):
            _point = points[_index]
            _action = _action.move_to(
                x=_point[0] - points[_index - 1][0], y=_point[1] - points[_index - 1][1]
            ).wait(_point[2])

        # 释放按钮
        if is_release:
            _action = _action.release()

        # 执行整个操作
        return _action.perform()

    def swipe_zoom_in(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0,
                      is_horizontal: bool = True):
        """
        手势放大（两个手指从中间向两边画）

        @param {int} x=None - 放大的中心点x位置，如果不传默认为屏幕中间
        @param {int} y=None - 放大的中心点x位置，如果不传默认为屏幕中间
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        @param {bool} is_horizontal=True - 是否沿用水平方向
        """
        # 计算参数
        _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(
                (_w if is_horizontal else _h) / 3.0
            )

        if is_horizontal:
            _start_x_distance = 1
            _start_y_distance = 0
            _end_x_distance = min(swipe_len, _w - x - 1, x - 1)  # 避免超过屏幕
            _end_y_distance = 0
        else:
            _start_x_distance = 0
            _start_y_distance = 1
            _end_x_distance = 0
            _end_y_distance = min(swipe_len, _h - y - 1, y - 1)  # 避免超过屏幕

        # 形成两个手指动作
        _action1 = TouchAction(driver=self.driver).press(
            x=x + _start_x_distance, y=y + _start_y_distance
        ).move_to(
            x=_end_x_distance, y=_end_y_distance
        ).wait(ms=duration).release()

        _action2 = TouchAction(driver=self.driver).press(
            x=x - _start_x_distance, y=y - _start_y_distance
        ).move_to(
            x=0 - _end_x_distance, y=0 - _end_y_distance
        ).wait(ms=duration).release()

        # 多点触控执行
        MultiAction(self.driver).add(_action1, _action2).perform()

    def swipe_zoom_out(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0,
                       is_horizontal: bool = True):
        """
        手势缩小（两个手指从两边向中间画）

        @param {int} x=None - 缩小的中心点x位置，如果不传默认为屏幕中间
        @param {int} y=None - 缩小的中心点y位置，如果不传默认为屏幕中间
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        @param {bool} is_horizontal=True - 是否沿用水平方向
        """
        # 计算参数
        _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(
                (_w if is_horizontal else _h) / 3.0
            )

        if is_horizontal:
            _start_x_distance = 1
            _start_y_distance = 0
            _end_x_distance = min(swipe_len, _w - x - 1, x - 1)  # 避免超过屏幕
            _end_y_distance = 0
        else:
            _start_x_distance = 0
            _start_y_distance = 1
            _end_x_distance = 0
            _end_y_distance = min(swipe_len, _h - y - 1, y - 1)  # 避免超过屏幕

        # 形成两个手指动作
        _action1 = TouchAction(driver=self.driver).press(
            x=x + _start_x_distance + _end_x_distance, y=y + _start_y_distance + _end_y_distance
        ).move_to(
            x=0 - _end_x_distance, y=0 - _end_y_distance
        ).wait(ms=duration).release()

        _action2 = TouchAction(driver=self.driver).press(
            x=x - _start_x_distance - _end_x_distance, y=y - _start_y_distance - _end_y_distance
        ).move_to(
            x=_end_x_distance, y=_end_y_distance
        ).wait(ms=duration).release()

        # 多点触控执行
        MultiAction(self.driver).add(_action1, _action2).perform()

    #############################
    # 动作 - 点击
    #############################
    def tap(self, x: int = None, y: int = None, count: int = 1, pre_action: TouchAction = None) -> TouchAction:
        """
        点击指定位置

        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {int} count=1 - 点击的次数
        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        # 计算点击位置
        if x is None or y is None:
            _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)

        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        # 执行操作
        return _action.tap(x=x, y=y, count=count).perform()

    def press(self, x: int = None, y: int = None, pre_action: TouchAction = None) -> TouchAction:
        """
        在指定位置按下手指

        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        if x is None or y is None:
            _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)

        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        # 执行操作
        return _action.press(x=x, y=y).perform()

    def release(self, pre_action: TouchAction = None) -> TouchAction:
        """
        抬起手指（对应press）

        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        return _action.release().perform()

    def long_press(self, x: int = None, y: int = None, duration: int = 1000,
                   pre_action: TouchAction = None) -> TouchAction:
        """
        在指定位置长按

        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {int} duration=1000 - 经历时长，单位为毫秒
        @param {TouchAction} pre_action=None - 预定义动作实例

        @returns {TouchAction} - 动作实例对象
        """
        if x is None or y is None:
            _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)

        if pre_action is None:
            _action = TouchAction(self.driver)
        else:
            _action = pre_action

        # 执行操作
        return _action.long_press(x=x, y=y, duration=duration).perform()

    #############################
    # 动作 - 按键
    #############################
    def press_keycode(self, key_code, metastate=None, flags=None):
        """
        按下物理按键

        @param {int|str} key_code - 要按下的按键代码，支持传入int、EnumAndroidKeycode和str三种格式
            注：传入的str格式字符串必须与 EnumAndroidKeycode 定义的名称一致
        @param {int|str} metastate=None - 指定组合按键使用状态，可传入EnumAndroidKeycode中 META_ 开头的状态值
        @param {int|str} flags=None - 组合按键代码，可传入 EnumAndroidKeycode 的组合按键码

        @example 如果需要同时按 ctrl + a，可以按以下方式传值：
            press_keycode(
                EnumAndroidKeycode.KEY_A, EnumAndroidKeycode.META_CTRL_ON, EnumAndroidKeycode.CTRL_LEFT
            )
        """
        _key_code = key_code
        if type(key_code) == str:
            # 通过字符串获取key值
            _key_code = eval('EnumAndroidKeycode.%s' % key_code.upper()).value
        elif type(key_code) == EnumAndroidKeycode:
            _key_code = key_code.value

        _metastate = metastate
        if type(metastate) == str:
            # 通过字符串获取key值
            _metastate = eval('EnumAndroidKeycode.%s' % metastate.upper()).value
        elif type(metastate) == EnumAndroidKeycode:
            _metastate = metastate.value

        _flags = flags
        if type(flags) == str:
            # 通过字符串获取key值
            _flags = eval('EnumAndroidKeycode.%s' % flags.upper()).value
        elif type(flags) == EnumAndroidKeycode:
            _flags = flags.value

        self.driver.press_keycode(
            _key_code, metastate=_metastate, flags=_flags
        )

    def long_press_keycode(self, key_code, metastate=None, flags=None):
        """
        长按物理按键

        @param {int|str} key_code - 要按下的按键代码，支持传入int、EnumAndroidKeycode和str三种格式
            注：传入的str格式字符串必须与 EnumAndroidKeycode 定义的名称一致
        @param {int|str} metastate=None - 指定组合按键使用状态，可传入EnumAndroidKeycode中 META_ 开头的状态值
        @param {int|str} flags=None - 组合按键代码，可传入 EnumAndroidKeycode 的组合按键码
        """
        _key_code = key_code
        if type(key_code) == str:
            # 通过字符串获取key值
            _key_code = eval('EnumAndroidKeycode.%s' % key_code.upper()).value
        elif type(key_code) == EnumAndroidKeycode:
            _key_code = key_code.value

        _metastate = metastate
        if type(metastate) == str:
            # 通过字符串获取key值
            _metastate = eval('EnumAndroidKeycode.%s' % metastate.upper())
        elif type(metastate) == EnumAndroidKeycode:
            _metastate = metastate.value

        _flags = flags
        if type(flags) == str:
            # 通过字符串获取key值
            _flags = eval('EnumAndroidKeycode.%s' % flags.upper())
        elif type(flags) == EnumAndroidKeycode:
            _flags = flags.value

        self.driver.long_press_keycode(
            _key_code, metastate=_metastate, flags=_flags
        )

    def is_keyboard_shown(self) -> bool:
        """
        判断软键盘是否有显示

        @returns {bool} - 判断结果
        """
        return self.driver.is_keyboard_shown()

    def hide_keyboard(self, key_name: str = None, key: str = None, strategy: str = None):
        """
        隐藏软键盘
        注：安卓无需使用这些参数

        @param {str} key_name=None - 要按的退出软键盘的keyName，例如"Done"
        @param {str} key=None - 要按的退出键盘的key
        @param {str} strategy=None - 隐藏键盘策略（可选，仅UIAutomation）
            可用策略-'press'，'pressKey'，'swipeDown'，'tapOut'，'tapOutside'，'default'.
        """
        return self.driver.hide_keyboard(
            key_name=key_name, key=key, strategy=strategy
        )

    #############################
    # 元素查找
    #############################

    def get_active_element(self) -> AppElement:
        """
        获取当前焦点元素

        @returns {AppElement} - 获取到的元素对象
        """
        return AppElement(self.driver.switch_to.active_element, self.driver)

    def find_element(self, by: str = MobileBy.ID, value=None) -> AppElement:
        """
        查找元素

        @param {str|MobileBy} by=MobileBy.ID - 查找类型
        @param {str|dict} value=None - 查找类型对应的查找参数，不同类型的定义如下
            MobileBy.ID {str} - 要获取的元素的id属性，例如 'foo_id'
            MobileBy.XPATH {str} - 要获取元素的xpath字符串，例如 '//div/td[1]'
            MobileBy.LINK_TEXT {str} - 要获取元素的连接显示文本，例如 'Sign In'  # 暂不支持
            MobileBy.PARTIAL_LINK_TEXT {str} - 要获取元素的部分连接显示文本，例如 'Sign'  # 暂不支持
            MobileBy.NAME {str} - 要获取元素的name属性，例如 'foo'
            MobileBy.TAG_NAME {str} - 要获取元素的标签名，例如 'h1'
            MobileBy.CLASS_NAME {str} - 要获取元素的CSS类名，例如 'foo'
            MobileBy.CSS_SELECTOR {str} - 要获取元素的CSS选择器文本，例如 'a.nav#home'

        @returns {AppElement} - 查找到的元素对象
        """
        return AppElement(self.driver.find_element(by=by, value=value), self.driver)

    def find_elements(self, by: str = MobileBy.ID, value=None) -> list:
        """
        查找元素

        @param {str|MobileBy} by=By.ID - 查找类型
        @param {str|dict} value=None - 查找类型对应的查找参数，不同类型的定义如下
            MobileBy.ID {str} - 要获取的元素的id属性，例如 'foo_id'
            MobileBy.XPATH {str} - 要获取元素的xpath字符串，例如 '//div/td[1]'
            MobileBy.LINK_TEXT {str} - 要获取元素的连接显示文本，例如 'Sign In'  # 暂不支持
            MobileBy.PARTIAL_LINK_TEXT {str} - 要获取元素的部分连接显示文本，例如 'Sign'  # 暂不支持
            MobileBy.NAME {str} - 要获取元素的name属性，例如 'foo'
            MobileBy.TAG_NAME {str} - 要获取元素的标签名，例如 'h1'
            MobileBy.CLASS_NAME {str} - 要获取元素的CSS类名，例如 'foo'
            MobileBy.CSS_SELECTOR {str} - 要获取元素的CSS选择器文本，例如 'a.nav#home'

        @returns {list[AppElement]} - 查找到的对象
        """
        _list = list()
        for _element in self.driver.find_elements(by=by, value=value):
            _list.append(AppElement(_element, self.driver))

        return _list

    def find_element_by_xpath(self, xpath: str) -> AppElement:
        """
        通过xpath获取一个元素

        @param {str} xpath - 要获取元素的xpath字符串

        @returns {AppElement} - 获取到的元素对象

        @example
            element = driver.find_element_by_xpath('//div/td[1]')
        """
        return AppElement(self.driver.find_element_by_xpath(xpath), self.driver)

    def find_elements_by_xpath(self, xpath: str) -> list:
        """
        通过xpath获取多个元素

        @param {str} xpath - 要获取元素的xpath值

        @returns {list[AppElement]} - 获取到的元素对象

        @example
            elements = driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        _list = list()
        for _elements in self.driver.find_elements_by_xpath(xpath):
            _list.append(AppElement(_elements, self.driver))

        return _list

    def find_element_by_image(self, img_path: str) -> AppElement:
        """
        通过图片查找元素

        @param {str} img_path - 图片地址，注意图片为png格式，最好是在原图大小中截取

        @returns {AppElement} - 获取到的元素对象
        """
        return AppElement(self.driver.find_element_by_image(img_path), self.driver)

    def find_elements_by_image(self, img_path: str) -> list:
        """
        通过图片查找元素

        @param {str} img_path - 图片地址，注意图片为png格式，最好是在原图大小中截取

        @returns {list[AppElement]} - 获取到的元素对象
        """
        _list = list()
        for _elements in self.driver.find_elements_by_image(img_path):
            _list.append(AppElement(_elements, self.driver))

        return _list

    #############################
    # 内部函数
    #############################
    def _exec_sys_cmd(self, cmd: str, shell_encoding: str = None):
        """
        执行系统命令

        @param {str} cmd - 要执行的命令
        @param {str} shell_encoding=None - 传入指定的编码

        @returns {(int, list)} - 返回命令执行结果数组, 第一个为 exit_code, 0代表成功; 第二个为输出信息行数组
        """
        _shell_encoding = self.para['shell_encoding'] if shell_encoding is None else shell_encoding
        _sp = subprocess.Popen(
            cmd, close_fds=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True
        )

        # 循环等待执行完成
        _exit_code = None
        _info_str = ''
        while True:
            # 获取输出信息 .replace('\r', '').replace('\n', '')
            _info_str += _sp.stdout.readline().decode(
                _shell_encoding
            ).replace('\r', '\n').replace('\n\n', '\n')

            _exit_code = _sp.poll()
            if _exit_code is not None:
                # 结束，打印异常日志
                _info_str += _sp.stdout.read().decode(
                    _shell_encoding).replace('\r', '\n').replace('\n\n', '\n')
                if _exit_code != 0:
                    _info_str += _sp.stdout.read().decode(
                        _shell_encoding).replace('\r', '\n').replace('\n\n', '\n')

                break

            # 释放一下CPU
            time.sleep(0.01)

        return (_exit_code, _info_str.split('\n'))


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    # desired_caps = {
    #     'platformName': 'Android',  # 被测手机是安卓
    #     'platformVersion': '7.1',  # 模拟器安卓版本
    #     'deviceName': '127.0.0.1:21513',  # 设备名，安卓手机可以随意填写
    #     'appPackage': 'com.android.browser',  # 启动APP Package名称
    #     'appActivity': '.BrowserActivity',  # 启动Activity名称
    #     # 'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
    #     # 'resetKeyboard': True,  # 执行完程序恢复原来输入法
    #     'noReset': True,       # 不要重置App，防止登录信息丢失
    #     # 'newCommandTimeout': 6000,
    #     # 'automationName': 'UiAutomator2'
    # }
    # driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    # driver.implicitly_wait(5)  # 设置隐式等待的时长（查找元素的时间）
    # action = TouchAction(driver)
    # el_url = driver.find_element_by_id("com.android.browser:id/url")
    # el_url.clear()
    # el_url.click()
    # el_url.send_keys("www.baidu.com")
    # driver.press_keycode(66)  # 回车
    # time.sleep(5)
    # size = driver.get_window_size()
    # x1 = int(size['width'] * 0.5)
    # y1 = int(size['height'] * 0.9)
    # y2 = int(size['height'] * 0.1)
    # driver.swipe(x1, y1, x1, y2, 500)

    # # action.press(x=422, y=642).move_to(x=493, y=261).release().perform()  # 向上滑动
    # time.sleep(5)
    # driver.quit()

    a = [1, 2, 3]
    print(a[-2])
