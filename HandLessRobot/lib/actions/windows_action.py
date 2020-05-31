#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Windows平台的动作模块
@module common_action
@file common_action.py
"""

import os
import sys
from HiveNetLib.base_tools.run_tool import RunTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.actions.base_action import BaseAction
import HandLessRobot.lib.controls.windows.uia as winuia


__MOUDLE__ = 'windows_action'  # 模块名
__DESCRIPT__ = u'Windows平台的动作模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.05.22'  # 发布日期


# 一些公共的全局变量
WINDOWS_FUN_ROUTER = {
    # 对应用的操作
    'APPLICATION_START': winuia.Window.start_application,
    'GET_APPLICATION': winuia.Window.get_application,
    'APPLICATION_KILL': winuia.Window.kill_application,
    'IS_APPLICATION_RUNNING': winuia.Window.is_application_running,
}

WINDOWS_ATTR_ROUTER = {
    # 实例对象属性
    'WINDOW_ATTR_HANDLE': ['handle', winuia.WindowControlSpec.handle],
    'WINDOW_ATTR_CLASS_NAME': ['class_name', winuia.WindowControlSpec.class_name],
    'WINDOW_ATTR_NAME': ['name', winuia.WindowControlSpec.name],
    'WINDOW_ATTR_PROCESS_ID': ['process_id', winuia.WindowControlSpec.process_id],
    'WINDOW_ATTR_THREAD_ID': ['thread_id', winuia.WindowControlSpec.thread_id],
    'WINDOW_ATTR_IS_ACTIVE': ['is_active', winuia.WindowControlSpec.is_active],
    'WINDOW_ATTR_IS_VISIBLE': ['is_visible', winuia.WindowControlSpec.is_visible],
    'WINDOW_ATTR_IS_ENABLED': ['is_enabled', winuia.WindowControlSpec.is_enabled],
    'WINDOW_ATTR_IS_MINIMIZED': ['is_minimized', winuia.WindowControlSpec.is_minimized],
    'WINDOW_ATTR_IS_MAXIMIZED': ['is_maximized', winuia.WindowControlSpec.is_maximized],
    'WINDOW_ATTR_PARENT': ['parent', winuia.WindowControlSpec.parent],
    'WINDOW_ATTR_WIN_RECT': ['win_rect', winuia.WindowControlSpec.win_rect],
    'WINDOW_ATTR_V_SCROLL_RANGE': ['v_scroll_range', winuia.WindowControlSpec.v_scroll_range],
    'WINDOW_ATTR_V_SCROLL_POS': ['v_scroll_pos', winuia.WindowControlSpec.v_scroll_pos],
    'WINDOW_ATTR_H_SCROLL_RANGE': ['h_scroll_range', winuia.WindowControlSpec.h_scroll_range],
    'WINDOW_ATTR_H_SCROLL_POS': ['h_scroll_pos', winuia.WindowControlSpec.h_scroll_pos],

    # 实例对象函数
    'WINDOW_GET_CHILDRENS': ['get_childrens', winuia.WindowControlSpec.get_childrens],
    'WINDOW_SET_FOREGROUND': ['set_foreground', winuia.WindowControlSpec.set_foreground],
    'WINDOW_BRING_TO_TOP': ['bring_to_top', winuia.WindowControlSpec.bring_to_top],
    'WINDOW_CLOSE': ['close_window', winuia.WindowControlSpec.close_window],
    'WINDOW_SET_FOCUS': ['set_focus', winuia.WindowControlSpec.set_focus],
    'WINDOW_SET_NAME': ['set_name', winuia.WindowControlSpec.set_name],
    'WINDOW_MAXIMIZE': ['maximize', winuia.WindowControlSpec.maximize],
    'WINDOW_MINIMIZE': ['minimize', winuia.WindowControlSpec.minimize],
    'WINDOW_RESTORE': ['restore', winuia.WindowControlSpec.restore],
    'WINDOW_HIDE': ['hide', winuia.WindowControlSpec.hide],
    'WINDOW_SHOW': ['show', winuia.WindowControlSpec.show],
    'WINDOW_CENTER': ['center', winuia.WindowControlSpec.center],
    'WINDOW_MOVE': ['move', winuia.WindowControlSpec.move],
    'WINDOW_V_SCROLL_TO': ['v_scroll_to', winuia.WindowControlSpec.v_scroll_to],
    'WINDOW_V_SCROLL_TO_HEAD': ['v_scroll_to_head', winuia.WindowControlSpec.v_scroll_to_head],
    'WINDOW_V_SCROLL_TO_END': ['v_scroll_to_end', winuia.WindowControlSpec.v_scroll_to_end],
    'WINDOW_H_SCROLL_TO': ['h_scroll_to', winuia.WindowControlSpec.h_scroll_to],
    'WINDOW_H_SCROLL_TO_HEAD': ['h_scroll_to_head', winuia.WindowControlSpec.h_scroll_to_head],
    'WINDOW_H_SCROLL_TO_END': ['h_scroll_to_end', winuia.WindowControlSpec.h_scroll_to_end],
}


WINDOWS_UIA_FUN_ROUTER = {
    # 应用处理
    'APPLICATION_ACTIVE_WINDOW': winuia.Window.application_active_window,

    # 窗口处理
    'GET_ACTIVE_WINDOW': winuia.Window.get_active_window,
    'FIND_WINDOW': winuia.Window.find_window,
    'FIND_WINDOW_EX': winuia.Window.find_window_ex,
}


class WindowsAction(BaseAction):
    """
    Windows平台的动作模块
    """
    @classmethod
    def support_action_types(cls) -> list:
        """
        返回支持的动作类别列表(主要基于列表区分不同平台及技术兼容的动作)

        @returns {list} - 支持的动作类别列表，例如：
            ['*'] - 代表支持所有分类
            ['win32', 'winuia'] - 代表支持win32和winuia两种分类使用
        """
        return ['winuia']

    @classmethod
    def support_platform(cls) -> dict:
        """
        返回支持的平台字典
        (用于自动生成路由表，默认支持全平台全版本，如需要指定需修改该函数返回值)

        @returns {dict} - 支持的平台字典，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        """
        return {'Windows': None}

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
        return WINDOWS_FUN_ROUTER

    #############################
    # 窗口实例对象的通用方法调用
    #############################
    @classmethod
    def get_common_attr_dict(cls):
        """
        获取实例对象内部方法及属性映射字典
        (如果需要实现映射，请继承并修改该函数的返回值)

        @returns {dict} - 返回实例对象内部方法及属性映射字典
            key - 动作名(action_name), 必须为大写
            value - [属性或函数名(字符串), 属性或函数对象]
        """
        return WINDOWS_ATTR_ROUTER


class WindowsUiaAction(BaseAction):
    """
    UIA类型的Windows平台动作模块
    """
    @classmethod
    def support_action_types(cls) -> list:
        """
        返回支持的动作类别列表(主要基于列表区分不同平台及技术兼容的动作)

        @returns {list} - 支持的动作类别列表，例如：
            ['*'] - 代表支持所有分类
            ['win32', 'winuia'] - 代表支持win32和winuia两种分类使用
        """
        return ['winuia']

    @classmethod
    def support_platform(cls) -> dict:
        """
        返回支持的平台字典
        (用于自动生成路由表，默认支持全平台全版本，如需要指定需修改该函数返回值)

        @returns {dict} - 支持的平台字典，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        """
        return {'Windows': None}

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
        return WINDOWS_UIA_FUN_ROUTER


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    a = WindowsAction.get_action_router()
    print(1)
