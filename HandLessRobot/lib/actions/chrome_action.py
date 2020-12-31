#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Chrome浏览器的动作模块
@module common_action
@file common_action.py
"""

import os
import sys
import time
import datetime
from bs4 import BeautifulSoup, PageElement
from uiautomation import ControlType, Keys, Control
from HiveNetLib.base_tools.run_tool import RunTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.actions.base_action import BaseAction
from HandLessRobot.lib.actions.common_action import CommonAction
from HandLessRobot.lib.controls.windows_control import WindowException
import HandLessRobot.lib.controls.windows.uia as winuia


__MOUDLE__ = 'chrome_action'  # 模块名
__DESCRIPT__ = u'Chrome浏览器的动作模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.05.22'  # 发布日期


# 已经验证的控件查找配置
DEFAULT_FIND_STEPS = {
    'win7+64+chrome83': {
        'GET_TABS': [
            {'options': {'name': 'Google Chrome'}},
            {'pos': 1, 'options': {}},
            {'pos': 0},
            {'pos': 0, 'options': {'control_type': ControlType.PaneControl}},
            {'pos': 0, 'options': {'control_type': ControlType.TabControl}},
        ],
        'GET_URL_EDITER': [
            {'by_step': False, 'options': {'name': '地址和搜索栏',
                                           'control_type': ControlType.EditControl, 'depth': 6}},
        ],
        'GET_EXTENSION': [
            {'by_step': False, 'options': {'control_type': ControlType.CustomControl, 'name': '扩展程序', 'depth': 5}},
        ],
    },
    'win10+64+chrome83': {
        'GET_TABS': [
            {'options': {'name': 'Google Chrome'}},
            {'pos': 1, 'options': {'control_type': ControlType.PaneControl}},
            {'pos': 0},
            {'pos': 0, 'options': {'control_type': ControlType.PaneControl}},
            {'pos': 0, 'options': {'control_type': ControlType.TabControl}},
        ],
        'GET_URL_EDITER': [
            {'options': {'name': 'Google Chrome'}},
            {'pos': 1, 'options': {'control_type': ControlType.PaneControl}},
            {'pos': 0},
            {'pos': 1, 'options': {'control_type': ControlType.PaneControl}},
            {'pos': 0, 'options': {'control_type': ControlType.GroupControl}},
            {'pos': 0, 'options': {'name': '地址和搜索栏', 'control_type': ControlType.EditControl}}
        ],
        'GET_EXTENSION': [
            {'options': {'name': 'Google Chrome'}},
            {'pos': 1, 'options': {'control_type': ControlType.PaneControl}},
            {'pos': 0},
            {'pos': 1, 'options': {'control_type': ControlType.PaneControl}},
            {'pos': 0, 'options': {'control_type': ControlType.GroupControl, 'name': '扩展程序'}},
        ],
    }
}


class WindowsChromeAction(BaseAction):
    """
    Chrome浏览器的动作模块(Windows平台)
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
        return {}

    #############################
    # 自定义的动作函数
    #############################

    #############################
    # 公共参数管理
    #############################
    @classmethod
    def chrome_para_get_wait_less_timeout(cls, robot_info: dict, action_name: str, run_id: str,
                                          **kwargs) -> float:
        """
        获取参数值 - 最小等待超时时间
        注：该参数定义了获取Windows对象失败后重做的超时时间

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id

        @returns {float} - 超时时间，默认为10秒
        """
        return cls._get_global_var_default('CHROME_ACTION_PARA_WAIT_LESS_TIMEOUT', 10.0)

    @classmethod
    def chrome_para_set_wait_less_timeout(cls, robot_info: dict, action_name: str, run_id: str, value: float,
                                          **kwargs) -> float:
        """
        获取参数值 - 最小等待超时时间

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {float} value - 要设置的参数，单位秒2秒
        """
        RunTool.set_global_var('CHROME_ACTION_PARA_WAIT_LESS_TIMEOUT', value)

    @classmethod
    def chrome_para_get_find_step_tag(cls, robot_info: dict, action_name: str, run_id: str,
                                      **kwargs) -> str:
        """
        获取参数值 - 控件查找类型标志
        注：该参数定义了不同操作系统查找chrome控件的配置

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id

        @returns {str} - 控件查找类型标志
        """
        return cls._get_global_var_default('CHROME_ACTION_PARA_FIND_STEPS_TAG', 'win10+64+chrome83')

    @classmethod
    def chrome_para_set_find_step_tag(cls, robot_info: dict, action_name: str, run_id: str, value: float,
                                      **kwargs) -> float:
        """
        获取参数值 - 控件查找类型标志

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {float} value - 要设置的参数
        """
        RunTool.set_global_var('CHROME_ACTION_PARA_FIND_STEPS_TAG', value)

    #############################
    # 应用启动关闭
    #############################
    @classmethod
    def get_chrome_app(cls, robot_info: dict, action_name: str, run_id: str,
                       bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                       name='chrome.exe',
                       **kwargs) -> winuia.ApplicationSpec:
        """
        获取已启动的Chrome应用对象

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {string} bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe' - 启动程序路径
        @param {string} name='chrome.exe' - 进程名

        @returns {ApplicationSpec} - 找到的应用对象，如果找不到返回None
        """
        return winuia.Window.get_application(
            name=name,
            bin_path=bin_path,
            children_num_more=0
        )

    @classmethod
    def chrome_start(cls, robot_info: dict, action_name: str, run_id: str,
                     bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                     name='chrome.exe', run_paras=['--force-renderer-accessibility'],
                     **kwargs) -> winuia.ApplicationSpec:
        """
        启动Chrome浏览器

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {string} bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe' - 启动程序路径
        @param {string} name='chrome.exe' - 进程名
        @param {list} run_paras=['--force-renderer-accessibility'] - 启动参数列表

        @returns {ApplicationSpec} - 返回启动的应用对象
        """
        # 查找是不是已打开浏览器
        _app = winuia.Window.get_application(
            name=name,
            bin_path=bin_path,
            children_num_more=0
        )
        if _app is None:
            _app = winuia.Window.start_application(
                '"%s"%s%s' % (
                    bin_path, '' if len(run_paras) == 0 else ' ',
                    ' '.join(run_paras)
                )
            )

        return _app

    @classmethod
    def get_chrome_window(cls, robot_info: dict, action_name: str, run_id: str,
                          app: winuia.ApplicationSpec = None,
                          bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                          name='chrome.exe', run_paras=['--force-renderer-accessibility'],
                          **kwargs) -> winuia.WindowControlSpec:
        """
        获取Chrome窗口对象

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {winuia.ApplicationSpec} app=None - 已获取到的chorme进程对象，如果为None则根据启动参数自动启动
        @param {string} bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe' - 启动程序路径
        @param {string} name='chrome.exe' - 进程名
        @param {list} run_paras=['--force-renderer-accessibility'] - 启动参数列表

        @returns {WindowControlSpec} - 获取到的窗口对象
        """
        # 启动应用
        _app = app
        if _app is None:
            _app = cls.chrome_start(
                robot_info, 'chorme_start', bin_path=bin_path,
                name=name, run_paras=run_paras
            )

        # 获取窗口
        return cls._wait_less_run_fun(
            winuia.Window.application_active_window, {}, _app
        )

    @classmethod
    def chrome_close(cls, robot_info: dict, action_name: str, run_id: str,
                     chrome_win: winuia.WindowControlSpec = None,
                     chrome_app: winuia.ApplicationSpec = None,
                     **kwargs):
        """
        关闭Chrome浏览器

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win=None - 通过指定Chrome浏览器窗口关闭
        @param {ApplicationSpec} chrome_app=None - 通过指定Chrome浏览器应用关闭
        """
        _app = chrome_app
        if _app is None:
            _app = winuia.ApplicationSpec(process=chrome_win.process_id)
        winuia.Window.kill_application(_app, soft=False)

    #############################
    # 地址跳转
    #############################
    @classmethod
    def chrome_get_url_editer(cls, robot_info: dict, action_name: str, run_id: str,
                              chrome_win: winuia.WindowControlSpec,
                              name: str = '地址和搜索栏',
                              **kwargs):
        """
        获取Chrome地址栏编辑框

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {winuia.WindowControlSpec} chrome_win - Chrome浏览器窗口
        @param {str} name='地址和搜索栏' - 地址栏名称，注意如果多国语言为非中文需要传入正确的值

        @returns {winuia.WindowControlSpec} - 地址栏编辑框对象
        """
        FIND_STEPS_TAG = cls._get_global_var_default(
            'CHROME_ACTION_PARA_FIND_STEPS_TAG', 'win10+64+chrome83'
        )
        _find_steps = DEFAULT_FIND_STEPS[FIND_STEPS_TAG]['GET_URL_EDITER']

        # 获取地址栏编辑框
        return cls._wait_less_run_fun(
            winuia.Window.find_window_ex, {}, _find_steps, parent=chrome_win
        )

    @classmethod
    def chrome_goto_url(cls, robot_info: dict, action_name: str, run_id: str, url: str,
                        chrome_win: winuia.WindowControlSpec = None,
                        url_editer: winuia.WindowControlSpec = None,
                        name: str = '地址和搜索栏',
                        **kwargs):
        """
        跳转到指定url页面

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {str} url - 要跳转到的地址
        @param {winuia.WindowControlSpec} chrome_win=None - 浏览器主窗口，如果url_editer为None则必送
        @param {winuia.WindowControlSpec} url_editer=None - 地址栏编辑对象，如果chrome_win为None则必送
        @param {str} name='地址和搜索栏' - 地址栏名称，注意如果多国语言为非中文需要传入正确的值
        """
        # 获取地址栏
        _url_editer = url_editer
        if url_editer is None:
            _url_editer = cls.chrome_get_url_editer(
                robot_info, 'chrome_get_url_editer', chrome_win, name=name
            )

        # 修改地址栏地址并跳转
        _value_pattern = _url_editer.automation_control.GetValuePattern()
        _value_pattern.SetValue(url)
        _url_editer.automation_control.SendKey(Keys.VK_ENTER)

    #############################
    # 标签页操作
    #############################
    @classmethod
    def chrome_get_tabs(cls, robot_info: dict, action_name: str, run_id: str,
                        chrome_win: winuia.WindowControlSpec,
                        **kwargs) -> list:
        """
        获取Chrome浏览器的页签清单

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口

        @returns {list} - 页签对象清单
            注：最后一个页签对象是新建页签按钮，使用时需注意

        """
        FIND_STEPS_TAG = cls._get_global_var_default(
            'CHROME_ACTION_PARA_FIND_STEPS_TAG', 'win10+64+chrome83'
        )
        _find_steps = DEFAULT_FIND_STEPS[FIND_STEPS_TAG]['GET_TABS']

        # 获取页签对象
        _tabs = cls._wait_less_run_fun(
            winuia.Window.find_window_ex, {}, _find_steps, parent=chrome_win
        )

        return _tabs.get_childrens()

    @classmethod
    def chrome_get_selected_tab(cls, robot_info: dict, action_name: str, run_id: str,
                                chrome_win: winuia.WindowControlSpec,
                                **kwargs) -> winuia.WindowControlSpec:
        """
        获取当前选择的页面标签对象

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口

        @returns {WindowControlSpec} - 当前选择的页面标签对象
        """
        _tabs = cls.chrome_get_tabs(
            robot_info, 'chrome_get_tabs', chrome_win
        )
        for _tab in _tabs:
            if _tab.control_type != ControlType.TabItemControl:
                continue

            _selection_pattern = _tab.automation_control.GetSelectionItemPattern()
            if _selection_pattern.IsSelected:
                return _tab

        return None

    @classmethod
    def chrome_select_tab(cls, robot_info: dict, action_name: str, run_id: str,
                          chrome_win: winuia.WindowControlSpec,
                          index: int = 0, name: str = None, name_with: str = None,
                          **kwargs) -> winuia.WindowControlSpec:
        """
        选中Chrome中指定tab页签

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {winuia.WindowControlSpec} chrome_win - Chrome浏览器窗口
        @param {int} index=0 - 按位置选择，当不传其他选择方式时才使用
        @param {str} name=None - 按名字完全匹配选择
        @param {str} name_with=None - 名字中包含文字则选择

        @returns {WindowControlSpec} - 选中的tab页签，如果没有找到返回None
        """
        _tabs = cls.chrome_get_tabs(
            robot_info, 'chrome_get_tabs', chrome_win
        )

        # 查找tab
        _fit_tab = None
        if name is not None or name_with is not None:
            for _tab in _tabs:
                if _tab.control_type != ControlType.TabItemControl:
                    continue

                if name is not None and _tab.name == name:
                    _fit_tab = _tab
                    break
                elif name_with is not None and _tab.name.find(name_with) != -1:
                    _fit_tab = _tab
                    break
        else:
            if len(_tabs) - 1 > index:
                _fit_tab = _tabs[index]

        # 设置为选中
        if _fit_tab is not None:
            _fit_tab.automation_control.Click()

        return _fit_tab

    @classmethod
    def chrome_close_tab(cls, robot_info: dict, action_name: str, run_id: str,
                         chrome_tab: winuia.WindowControlSpec = None,
                         chrome_win: winuia.WindowControlSpec = None,
                         index: int = 0, name: str = None, name_with: str = None,
                         **kwargs) -> None:
        """
        关闭指定tab页签

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_tab=None - 直接指定要关闭的页签，如果不传可以通过以下条件找到页签再关闭
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口，当需要以下参数进行页签选择时使用
        @param {int} index=0 - 按位置选择，当不传其他选择方式时才使用
        @param {str} name=None - 按名字完全匹配选择
        @param {str} name_with=None - 名字中包含文字则选择
        """
        _fit_tab = chrome_tab
        if _fit_tab is None:
            # 查找合适的页签
            _tabs = cls.chrome_get_tabs(
                robot_info, 'chrome_get_tabs', chrome_win
            )

            # 查找tab
            _fit_tab = None
            if name is not None or name_with is not None:
                for _tab in _tabs:
                    if _tab.control_type != ControlType.TabItemControl:
                        continue

                    if name is not None and _tab.name == name:
                        _fit_tab = _tab
                        break
                    elif name_with is not None and _tab.name.find(name_with) != -1:
                        _fit_tab = _tab
                        break
            else:
                if len(_tabs) - 1 > index:
                    _fit_tab = _tabs[index]

        if _fit_tab is not None:
            # 点击关闭按钮执行关闭
            _close_btn = _fit_tab.get_childrens()
            if len(_close_btn) > 0:
                _close_btn[0].automation_control.Click()

    @classmethod
    def chrome_new_tab(cls, robot_info: dict, action_name: str, run_id: str,
                       chrome_win: winuia.WindowControlSpec,
                       **kwargs) -> winuia.WindowControlSpec:
        """
        新增加Chrome页签

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口

        @returns {WindowControlSpec} - 新增的页签对象
        """
        # 使用最后一个按钮新增
        _tabs = cls.chrome_get_tabs(
            robot_info, 'chrome_get_tabs', chrome_win
        )
        _tabs[len(_tabs) - 1].automation_control.Click()

        # 重新获取一次
        _tabs = cls.chrome_get_tabs(
            robot_info, 'chrome_get_tabs', chrome_win
        )

        return _tabs[len(_tabs) - 2]

    #############################
    # 右键菜单操作
    #############################
    @classmethod
    def chrome_click_pop_menu(cls, robot_info: dict, action_name: str, run_id: str,
                              chrome_win: winuia.WindowControlSpec, menu_names: list,
                              **kwargs):
        """
        点击弹出菜单(右键菜单)

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口
        @param {list} menu_names - 菜单查找名称路径, 从数组的第1开始逐步弹出子菜单
            [
                ['MenuControl_name', 'MenuItemControl_name'],
                ['MenuControl_name', 'MenuItemControl_name'],
            ]
        """
        _menu = None
        for _names in menu_names:
            # 逐行执行菜单的处理
            if _names[0] is None or _names[0] == '':
                # 不放在MenuControl里面，直接获取MenuItemControl
                _menu = cls._wait_less_run_fun(
                    winuia.Window.find_window, {},
                    parent=chrome_win, control_type=ControlType.MenuItemControl, name=_names[1],
                    depth=5
                )
            else:
                # 从MenuControl中获取
                _control = cls._wait_less_run_fun(
                    winuia.Window.find_window, {},
                    parent=chrome_win, control_type=ControlType.MenuControl, name=_names[0],
                    depth=5
                )
                _menu = winuia.Window.find_window(
                    parent=_control, control_type=ControlType.MenuItemControl, name=_names[1],
                    depth=1
                )

            # 把鼠标移上去
            _menu._win_object.MoveCursorToMyCenter()

        # 点击最后一个按钮
        _menu._win_object.Click()

    #############################
    # 网页内容操作
    #############################
    @classmethod
    def chrome_get_page_doc(cls, robot_info: dict, action_name: str, run_id: str,
                            chrome_win: winuia.WindowControlSpec,
                            **kwargs) -> winuia.WindowControlSpec:
        """
        获取Chrome网页文档窗口对象

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口

        @returns {WindowControlSpec} - 网页文档对象
        """
        _find_steps = [
            {'pos': 0, 'options': {
                'control_type': ControlType.DocumentControl,
                'class_name': 'Chrome_RenderWidgetHostHWND'
            }},
        ]

        return cls._wait_less_run_fun(
            winuia.Window.find_window_ex, {}, _find_steps, parent=chrome_win
        )

    #############################
    # DevTool操作
    #############################
    @classmethod
    def chrome_is_devtool_opened(cls, robot_info: dict, action_name: str, run_id: str,
                                 chrome_win: winuia.WindowControlSpec,
                                 **kwargs) -> bool:
        """
        判断Chrome浏览器的DevTool是否打开

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口

        @returns {bool} - 指示DevTool是否打开
        """
        # 通过找第二个DocumentControl来判断是否打开
        _find_steps = [{'pos': 1, 'options': {'control_type': ControlType.DocumentControl}}, ]
        try:
            winuia.Window.find_window_ex(_find_steps, parent=chrome_win)
        except:
            return False

        return True

    @classmethod
    def chrome_open_devtool(cls, robot_info: dict, action_name: str, run_id: str,
                            chrome_win: winuia.WindowControlSpec,
                            **kwargs):
        """
        打开开发调试工具

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口
        """
        if not cls.chrome_is_devtool_opened(
            robot_info, 'chrome_is_devtool_opened', chrome_win
        ):
            # 没有打开的情况，使用快捷键打开
            winuia.Keyboard.hotkey('ctrl', 'shift', 'i')

            # 等待一个标准时间
            CommonAction.time_wait_global(
                robot_info, ''
            )

    @classmethod
    def chrome_close_devtool(cls, robot_info: dict, action_name: str, run_id: str,
                             chrome_win: winuia.WindowControlSpec,
                             **kwargs):
        """
        关闭开发调试工具

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口
        """
        if cls.chrome_is_devtool_opened(
            robot_info, 'chrome_is_devtool_opened', chrome_win
        ):
            # 打开的情况，使用快捷键关闭
            winuia.Keyboard.hotkey('ctrl', 'shift', 'i')

    @classmethod
    def chrome_get_dom_html(cls, robot_info: dict, action_name: str, run_id: str,
                            chrome_win: winuia.WindowControlSpec,
                            check_complete: dict = None, check_overtime: float = 10.0,
                            **kwargs) -> str:
        """
        获取当前网页的dom代码

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口
        @param {dict} check_complete = None - 检查是否已完成的调整，格式如下
            'name' {str} - 标签名，例如div
            'attrs' {dict} - 标签属性匹配值，具体参考BeautifulSoup.find
        @param {float} check_overtime=10.0 - 检查超时时间

        @returns {str} - 返回获取到的dom代码
        """
        # 开启DevTool
        cls.chrome_open_devtool(
            robot_info, 'chrome_open_devtool', chrome_win
        )

        def self_get_html_item():
            # 获取dom窗口对象
            _find_steps = [{'pos': 1, 'options': {'control_type': ControlType.DocumentControl}}, ]
            _doc = winuia.Window.find_window_ex(_find_steps, parent=chrome_win)
            _dom_edit = winuia.Window.find_window(
                parent=_doc, control_type=ControlType.TreeControl, name='Page DOM'
            )
            # 找到html节点
            _find_steps = [{
                'pos': 0, 'options': {
                    'control_type': ControlType.TreeItemControl,
                    'name_re': r'^<html.*'
                }},
            ]
            return winuia.Window.find_window_ex(_find_steps, parent=_dom_edit)

        _dom_html = ''
        _start_time = datetime.datetime.now()
        while True:
            # html节点对象
            _html_item = cls._wait_less_run_fun(
                self_get_html_item, {}
            )

            # 通过菜单复制到剪贴版
            _html_item.automation_control.RightClick()  # 打开右键菜单

            # 执行点击操作
            cls.chrome_click_pop_menu(
                robot_info, 'chrome_click_pop_menu', chrome_win,
                [[None, 'Copy'], ['Copy', 'Copy element']]
            )

            # 从剪贴板获取内容
            _dom_html = winuia.Clipboard.get_text()

            # 检查
            if check_complete is not None:
                _soup = BeautifulSoup(_dom_html, 'html.parser')
                if _soup.find(**check_complete) is None:
                    # 未检查通过
                    if (datetime.datetime.now() - _start_time).total_seconds() < check_overtime:
                        time.sleep(0.01)
                        continue
                    else:
                        raise RuntimeError('Get dom check complete overtime!')

            # 正常执行完成，退出循环
            break

        # 关闭DevTool
        cls.chrome_close_devtool(
            robot_info, 'chrome_close_devtool', chrome_win
        )

        return _dom_html

    #############################
    # 扩展插件操作
    #############################
    @classmethod
    def chrome_get_extension(cls, robot_info: dict, action_name: str, run_id: str,
                             chrome_win: winuia.WindowControlSpec,
                             group_name: str = '扩展程序',
                             index: int = 0, name_with: str = None,
                             **kwargs) -> winuia.WindowControlSpec:
        """
        获取扩展插件对象(地址栏后面的插件图标)

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {str} run_id - 运行id
        @param {WindowControlSpec} chrome_win - Chrome浏览器窗口
        @param {str} group_name='扩展程序' - 获取扩展程序分组的窗口名，如果是其他语言需要修改传入
        @param {int} index=0 - 按位置获取，当name_with为None时使用
        @param {str} name_with=None - 获取name中存在指定字符的插件

        @returns {WindowControlSpec} - 返回插件窗口对象
        """
        FIND_STEPS_TAG = cls._get_global_var_default(
            'CHROME_ACTION_PARA_FIND_STEPS_TAG', 'win10+64+chrome83'
        )
        _find_steps = DEFAULT_FIND_STEPS[FIND_STEPS_TAG]['GET_EXTENSION']

        _ext_group = cls._wait_less_run_fun(
            winuia.Window.find_window_ex, {}, _find_steps, parent=chrome_win
        )

        _exts = _ext_group.get_childrens()

        # 开始获取扩展程序对象
        _find_ext = None
        _current_index = 0
        for _ext in _exts:
            if _ext.control_type != ControlType.ButtonControl:
                # 非按钮类型不处理
                continue

            if name_with is None:
                # 按索引位置获取
                if _current_index == index:
                    _find_ext = _ext
                    break
            else:
                # 按名字匹配
                if _ext.name.find(name_with) != -1:
                    _find_ext = _ext
                    break

            # 继续下一个
            _current_index += 1

        # 返回结果
        if _find_ext is None:
            raise WindowException('Extension not found')
        else:
            return _find_ext

    #############################
    # 内部函数
    #############################
    @classmethod
    def _get_global_var_default(cls, var_name: str, default_value: object = None) -> object:
        """
        获取全局变量值，当获取不到返回默认值

        @param {str} var_name - 变量名
        @param {object} default_value=None - 默认值

        @returns {object} - 返回的全局变量值
        """
        _value = RunTool.get_global_var(var_name)
        if _value is None:
            _value = default_value

        return _value

    @classmethod
    def _wait_less_run_fun(cls, fun, wait_less_para: dict, *args, **kwargs):
        """
        以最小等待循环模式执行指定函数

        @param {function} fun - 要执行的函数对象
        @param {dict} wait_less_para - 循环等待处理模式参数
        @param {list} args - 执行占位参数
        @param {dict} kwargs - 执行的key-value参数
        """
        # 以超时形式处理
        _wait_less_timeout = cls.chrome_para_get_wait_less_timeout(None, '')

        _start_time = datetime.datetime.now()
        _return = None
        while True:
            try:
                # 获取主窗口对象
                _return = fun(*args, **kwargs)

                # 正常完成可以退出
                break
            except:
                if (datetime.datetime.now() - _start_time).total_seconds() < _wait_less_timeout:
                    # 未超时, 尝试重新获取
                    time.sleep(0.01)
                    # print('Wait less redo {0}, {1}, {2}'.format(fun, args, kwargs))
                    continue
                else:
                    # 超时
                    raise

        return _return


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
