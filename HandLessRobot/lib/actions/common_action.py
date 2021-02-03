#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
通用动作模块
@module common_action
@file common_action.py
"""

import os
import sys
import time
import random
import datetime
from HiveNetLib.base_tools.run_tool import RunTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.actions.base_action import BaseAction
from HandLessRobot.lib.controls.windows_control import Screen, Mouse, Keyboard, Clipboard


__MOUDLE__ = 'common_action'  # 模块名
__DESCRIPT__ = u'通用动作模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.05.22'  # 发布日期


# 一些公共的全局变量
COMMON_FUN_ROUTER = {
    # 屏幕处理
    'SCREEN_SIZE': Screen.size,
    'IS_ON_SCREEN': Screen.on_screen,
    'GET_RECT_CENTER': Screen.center,
    'SCREEN_PIXEL_COLOR': Screen.pixel_color,
    'SCREENSHOT': Screen.screenshot,
    'IMAGE_LOCATE_ON_SCREEN': Screen.locate_all_on_screen,
    'IMAGE_LOCATE_CENTER_ON_SCREEN': Screen.locate_center_on_screen,
    'IMAGE_LOCATE_ALL_ON_SCREEN': Screen.locate_all_on_screen,

    # 鼠标处理
    'MOUSE_POSITION': Mouse.position,
    'MOUSE_MOVE': Mouse.move,
    'MOUSE_MOVE_TO': Mouse.move_to,
    'MOUSE_DRAG': Mouse.drag,
    'MOUSE_DRAP_TO': Mouse.drap_to,
    'MOUSE_CLICK': Mouse.click,
    'MOUSE_DOUBLE_CLICK': Mouse.double_click,
    'MOUSE_DOWN': Mouse.mouse_down,
    'MOUSE_UP': Mouse.mouse_up,
    'MOUSE_SCROLL': Mouse.scroll,

    # 键盘处理
    'KEYBOARD_WRITE': Keyboard.write,
    'KEYBOARD_PRESS': Keyboard.press,
    'KEYBOARD_KEY_DOWN': Keyboard.key_down,
    'KEYBOARD_KEY_UP': Keyboard.key_up,
    'KEYBOARD_HOTKEY': Keyboard.hotkey,

    # 剪贴版处理
    'CLIPBOARD_WRITE_TEXT': Clipboard.write_text,
    'CLIPBOARD_GET_TEXT': Clipboard.get_text,
}


class CommonAction(BaseAction):
    """
    通用动作模块
    """
    @classmethod
    def support_action_types(cls) -> list:
        """
        返回支持的动作类别列表(主要基于列表区分不同平台及技术兼容的动作)

        @returns {list} - 支持的动作类别列表，例如：
            ['*'] - 代表支持所有分类
            ['win32', 'winuia'] - 代表支持win32和winuia两种分类使用
        """
        return ['*']

    #############################
    # 常用函数通用映射
    #############################
    @classmethod
    def get_common_fun_dict(cls):
        """
        获取常用函数通用映射字典
        (如果需要实现映射，请继承并修改该函数的返回值)

        @returns {dict} - 返回常用函数通用映射字典
            key - 动作名(action_name), 必须为大写
            value - 动作对应的执行函数对象
        """
        return COMMON_FUN_ROUTER

    #############################
    # 运行中临时变量处理
    #############################
    @classmethod
    def get_run_variable(cls, robot_info: dict, action_name: str, run_id: str, var_name: str,
                         default_value=None, get_run_id: str = '*', **kwargs):
        """
        获取运行变量值

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {str} var_name - 变量名
        @param {object} default_value=None - 如果找不到变量的默认值
        @param {str} get_run_id='*' - 机器人运行id

        @returns {object} - 返回的变量值
        """
        if get_run_id in robot_info['vars'].keys():
            return robot_info['vars'][get_run_id].get(var_name, default_value)
        else:
            return default_value

    @classmethod
    def set_run_variable(cls, robot_info: dict, action_name: str, run_id: str, var_name: str, set_value,
                         set_run_id: str = '*', **kwargs):
        """
        设置运行变量值

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {str} var_name - 变量名
        @param {object} set_value - 要设置的变量值
        @param {str} set_run_id='*' - 机器人运行id
        """
        if set_run_id not in robot_info['vars'].keys():
            robot_info['vars'][set_run_id] = dict()

        robot_info['vars'][set_run_id][var_name] = set_value

    @classmethod
    def del_run_variable(cls, robot_info: dict, action_name: str, run_id: str, var_name: str,
                         del_run_id: str = '*', **kwargs):
        """
        删除运行变量值

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {str} var_name - 变量名
        @param {str} del_run_id='*' - 机器人运行id
        """
        if del_run_id in robot_info['vars'].keys():
            robot_info['vars'][del_run_id].pop(var_name)

    @classmethod
    def del_all_run_variable(cls, robot_info: dict, action_name: str, run_id: str, del_run_id: str = None, **kwargs):
        """
        删除所有运行变量

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {str} del_run_id=None - 机器人运行id, None代表清空所有变量
        """
        if del_run_id is None:
            # 清空所有变量
            for _key in robot_info['vars'].keys():
                robot_info['vars'][_key].clear()
        else:
            if del_run_id in robot_info['vars'].keys():
                robot_info['vars'][del_run_id].clear()

    #############################
    # 执行脚本
    #############################
    @classmethod
    def run_script(cls, robot_info: dict, action_name: str, run_id: str, script_str: str, **kwargs):
        """
        运行Python脚本

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {str} script_str - 要运行的python脚本
            注：脚本中可以直接通过robot_info变量访问robot对象
                如果需要返回值，可以在脚本中改变"_return_val"的值进行返回
        """
        _return_val = None
        exec(script_str)
        return _return_val

    #############################
    # 逻辑控制方法
    #############################
    @classmethod
    def time_wait(cls, robot_info: dict, action_name: str, run_id: str, interval: float, is_random: bool = False, **kwargs):
        """
        等待指定的时间

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {float} interval - 要等待的时间
        @param {bool} is_random=False - 是否等待随机时间，如果True则等待(0, interval)之间的随机时间
        """
        _time = interval
        if is_random:
            _time = random.random(0, interval)

        time.sleep(_time)

    @classmethod
    def time_wait_global(cls, robot_info: dict, action_name: str, run_id: str, multiple: float = 1.0, **kwargs):
        """
        等待全局统一设置的时间

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {float} multiple=1 - 等待时间的倍数
        """
        _time = RunTool.get_global_var('COMMON_ACTION_TIME_WAIT')
        if _time is None:
            _time = 0.5  # 默认0.5秒
            RunTool.set_global_var('COMMON_ACTION_TIME_WAIT', 0.5)

        time.sleep(_time * multiple)

    @classmethod
    def set_global_time_wait(cls, robot_info: dict, action_name: str, run_id: str, interval: float, **kwargs):
        """
        设置全局统一等待时长

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {float} interval - 要设置的等待时长
        """
        RunTool.set_global_var('COMMON_ACTION_TIME_WAIT', interval)


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
