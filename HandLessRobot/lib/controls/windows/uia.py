#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Windows平台的控制模块(UIA模式)
@module uia
@file uia.py
"""

import os
import sys
import re
import copy
import json
import datetime
import psutil
from subprocess import Popen
import win32.lib.win32con as win32con
import uiautomation as auto
import win32.win32gui as win32gui
import win32.win32api as win32api
from HiveNetLib.base_tools.file_tool import FileTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir)))
import HandLessRobot.lib.controls.windows_control as base_control


__MOUDLE__ = 'windows_uia'  # 模块名
__DESCRIPT__ = u'Windows平台的控制模块(UIA模式)'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.04.15'  # 发布日期


class Screen(base_control.Screen):
    pass


class Mouse(base_control.Mouse):
    pass


class Keyboard(base_control.Keyboard):
    pass


class Clipboard(base_control.Clipboard):
    pass


class Window(base_control.Window):
    """
    windows平台的窗口处理模块
    """

    #############################
    # 应用操作
    #############################
    @classmethod
    def start_application(cls, run_para: str, **kwargs) -> int:
        """
        启动应用程序

        @param {str} run_para - 启动参数，例如'c:/path/to/your/application -a -n -y --arguments'
        @param {kwargs} - 扩展参数, 支持的扩展参数参考subprocess.Popen

        @returns {ApplicationSpec} - 返回应用程序对象
        """
        kwargs['run_para'] = run_para
        _app = ApplicationSpec(**kwargs)
        return _app

    @classmethod
    def get_application(cls, **kwargs):
        """
        获取特定的应用程序

        @param {kwargs} - 具体实现类的扩展参数
            muti_search {bool} - 是否返回所有匹配结果，默认为False，仅返回第一个结果
            process {int} - 进程id
            handle {int} - 窗口handle
            name {str} - 程序名
            bin_path {str} - 程序的启动路径, 例如"d:/xx.exe"
            work_path {str} - 程序工作目录
            cmdline_para {str} - 命令行参数（判断是否有传入的命令行参数）
            parent_pid {int} - 父进程id
            children_num {int} - 子进程数量等于
            children_num_less - 子进程数量小于
            children_num_more - 子进程数量大于


        @returns {ApplicationSpec|list} - 返回应用程序对象，如果muti_search为True则返回匹配到的应用数组
        """
        if 'muti_search' not in kwargs.keys():
            kwargs['muti_search'] = False

        _app_list = []
        if 'process' in kwargs.keys():
            _app_list.append(ApplicationSpec(process=kwargs['process']))
        elif 'handle' in kwargs.keys():
            _app_list.append(ApplicationSpec(
                process=WindowControlSpec(handle=kwargs['handle']).process_id))
        else:
            # 通过遍历方式获取进程
            _pids = psutil.pids()
            for _pid in _pids:
                _process = ApplicationSpec(process=_pid)
                try:
                    if 'name' in kwargs.keys():
                        if kwargs['name'] != _process.name:
                            continue

                    if 'bin_path' in kwargs.keys():
                        if kwargs['bin_path'] != _process.bin_path:
                            continue

                    if 'work_path' in kwargs.keys():
                        if kwargs['work_path'] != _process.work_path:
                            continue

                    if 'cmdline_para' in kwargs.keys():
                        if kwargs['cmdline_para'] not in _process.cmdline:
                            continue

                    if 'parent_pid' in kwargs.keys():
                        if kwargs['parent_pid'] != _process.parent_pid:
                            continue

                    if 'children_num' in kwargs.keys():
                        if kwargs['children_num'] != len(_process.childrens):
                            continue

                    if 'children_num_less' in kwargs.keys():
                        if kwargs['children_num_less'] <= len(_process.childrens):
                            continue

                    if 'children_num_more' in kwargs.keys():
                        if kwargs['children_num_more'] >= len(_process.childrens):
                            continue
                except:
                    # 有可能出现权限问题，如果有直接返回不匹配
                    continue

                _app_list.append(_process)
                if not kwargs['muti_search']:
                    # 非多个匹配模式
                    return _process

        # 返回查找到的结果
        if kwargs['muti_search']:
            return _app_list
        else:
            if len(_app_list) > 0:
                return _app_list[0]
            else:
                return None

    @classmethod
    def get_application_pid(cls, app) -> int:
        """
        获取应用的进程id

        @param {ApplicationSpec} app - 获取到的应用对象

        @returns {int} - 应用对应的进程id
        """
        return app.process_id

    @classmethod
    def kill_application(cls, app, soft=True):
        """
        关闭应用程序

        @param {object} app - 要关闭的应用
        @param {bool} soft=True - 是否通过发送关闭信息的方式结束应用，如果为False代表直接杀进程
        """
        return app.kill(soft=soft)

    @classmethod
    def is_application_running(cls, app) -> bool:
        """
        检查应用（进程）是否还在运行

        @param {ApplicationSpec} app - 要判断的应用
        """
        return app.is_running

    @classmethod
    def application_active_window(cls, app):
        """
        获取应用的当前激活窗口

        @param {Application} app - 应用对象

        @returns {WindowSpecification} - 获取到的激活窗口
        """
        _win = cls.find_window(
            muti_search=False,
            process=app.process_id,
            top_level_only=False,
            depth=1
        )
        return _win

    #############################
    # 窗口操作
    #############################
    @classmethod
    def find_window(cls, **kwargs):
        """
        查找指定的窗口

        @param {kwargs} - 具体实现类的扩展参数
            muti_search {bool} - 是否返回所有匹配结果，默认为False，仅返回第一个结果
            handle {int} - 窗口句柄, 如果指定该参数则直接获取该句柄的窗口, 不处理其他参数
            top_level_only {bool} - 仅限顶级元素(默认值=False), 如果指定该参数则仅使用class_name、name检索顶层窗口, 不处理其他参数
            class_name {str} - 窗口的类名(可通过spy++获取到)
            name {str} - 窗口标题
            depth {int} - 最大搜索深度（搜索层级，默认值0xFFFFFFFF）
            class_name_re {str} - 类与此正则表达式匹配的元素
            name_re {str} - 文本与此正则表达式匹配的元素
            parent {int} - 父窗口对象(句柄或WindowControlSpec对象)
            process {int} - 窗口所在的应用进程对象(进程ID)
            visible_only {bool} - 仅可见元素 (默认值=False)
            enabled_only {bool} - 仅启用元素 (默认值=False)
            active_only {bool} - 仅限活动元素（默认= False）
            automation_id {str} - 对象的AutomationId
            control_type {int|auto.ControlType} - 对象的ControlType

        @returns {WindowControlSpec|list} - 返回窗口对象，如果muti_search为True则返回匹配到的窗口数组
        """
        # 默认参数处理
        _kwargs = {
            'muti_search': False,
            'class_name': None,
            'name': None,
            'depth': 0xFFFFFFFF,
            'top_level_only': False,
            'visible_only': False,
            'enabled_only': False,
            'active_only': False,
        }
        _kwargs.update(kwargs)

        # 直接给了窗口句柄，忽略其他条件
        if 'handle' in _kwargs.keys():
            if _kwargs['muti_search']:
                return [WindowControlSpec(handle=kwargs['handle']), ]
            else:
                return WindowControlSpec(handle=kwargs['handle'])

        _windows = []  # 存储返回的对象

        # 只查找顶级元素
        if _kwargs['top_level_only']:
            _root = auto.GetRootControl()  # 桌面对象，所有一级窗口的父对象
            for _control in _root.GetChildren():
                _win_obj = WindowControlSpec(win_object=_control)
                if cls._is_window_match(_win_obj, _kwargs):
                    _windows.append(_win_obj)
                    if not _kwargs['muti_search']:
                        # 非返回所有对象模式，匹配到一个就要返回
                        break
        else:
            # 遍历方式查找
            _parent_control = None
            if 'parent' in _kwargs.keys():
                if type(_kwargs['parent']) == int:
                    _parent_control = auto.ControlFromHandle(_kwargs['parent'])
                else:
                    _parent_control = _kwargs['parent']._win_object
            else:
                # 没有传入，从桌面对象查起
                _parent_control = auto.GetRootControl()

            # 遍历控件树查找对象
            for _control, _depth in auto.WalkControl(_parent_control, includeTop=False, maxDepth=_kwargs['depth']):
                _win_obj = WindowControlSpec(win_object=_control)
                if cls._is_window_match(_win_obj, _kwargs):
                    # 匹配上对象
                    _windows.append(_win_obj)
                    if not _kwargs['muti_search']:
                        # 非返回所有对象模式，匹配到一个就要返回
                        break

        # 返回结果
        if _kwargs['muti_search']:
            return _windows
        else:
            if len(_windows) > 0:
                return _windows[0]
            else:
                # 找不到窗口抛出异常
                raise base_control.WindowException('Window not Found')

    @classmethod
    def find_window_ex(cls, steps: list, parent=None, **kwargs):
        """
        扩展的窗口查询函数

        @param {list} steps - 查找的步骤，格式如下:
            [
                # step 1
                {
                    'by_step': True,  # 是否逐步往下查找，Fasle代表搜索同级控件的所有子对象
                    'pos': 0, # 取查找结果的第几个(0开始)
                    'options': {  # 窗口匹配条件，支持的参数参考find_window
                        ...
                    }
                },
                # step 2
                ...
            ]
            注：支持默认值的情况，比如：
                [None, None, ...] - 代表前两个搜索只获取子节点的第1个
                [{'options': {}}, ] - 代表第1个查询获取查询结果的第1个
                [{'pos': 1}, ] - 代表第1个查询获取全部子节点的第2个
        @param {int|WindowControlSpec} parent=None - 开始查找的窗口对象(句柄或WindowControlSpec对象)
            注：如果不传代表使用桌面根窗口开始查
        """
        # 处理开始查找的节点
        _parent = parent
        if _parent is None:
            _parent = auto.GetRootControl()
        elif type(_parent) == int:
            _parent = WindowControlSpec(handle=parent)

        # 从开始节点往下找
        _win_obj: auto.Control = _parent._win_object
        _has_find_first = False  # 标识是否已经查找到过一次
        for _step in steps:
            if _step is None:
                # 只获取第一个子节点
                _win_obj = _win_obj.GetFirstChildControl()
                _has_find_first = True
            else:
                if 'by_step' in _step.keys() and not _step['by_step']:
                    # 搜索所有子对象
                    _options = copy.deepcopy(_step['options'])
                    _options['parent'] = WindowControlSpec(win_object=_win_obj)
                    _options['muti_search'] = True
                    _childrens = []
                    for _win_spec in cls.find_window(**_options):
                        _childrens.append(_win_spec.automation_control)
                else:
                    # 搜索下一级
                    _childrens = _win_obj.GetChildren()
                    if 'options' in _step.keys():
                        # 需要按条件判断
                        _temp_list = []
                        for _children in _childrens:
                            _win_spec = WindowControlSpec(win_object=_children)
                            if cls._is_window_match(_win_spec, _step['options']):
                                # 匹配上对象，添加到临时队列中
                                _temp_list.append(_children)

                        # 更新回_childrens中
                        _childrens = _temp_list

                # 看找第几个
                if 'pos' in _step.keys():
                    try:
                        _win_obj = _childrens[_step['pos']]
                    except:
                        print('find_window_ex error: {0}'.format(_step))
                        raise
                else:
                    _win_obj = _childrens[0]

                # 没有抛出异常代表找到了一次
                _has_find_first = True

        # 全部处理完成
        if not _has_find_first:
            # 找不到窗口抛出异常
            raise base_control.WindowException('Window not Found')

        # 返回窗口对象
        return WindowControlSpec(win_object=_win_obj)

    @classmethod
    def get_active_window(cls):
        """
        获取当前激活窗口

        @returns {WindowControlSpec} - 返回窗口对象
        """
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            # 没有找到窗口
            raise base_control.WindowException('Window not Found')
        else:
            return WindowControlSpec(handle=hwnd)

    @classmethod
    def print_window_info(cls, win, depth=0xFFFFFFFF, pre_fix_str='', screen_shot_save_path=None,
                          show_all_name: bool = True, property_list=None, print_to_file=None,
                          set_foreground=True, to_json_str=False):
        """
        打印指定窗口信息(含子控件)

        @param {WindowControlSpec} win - 要打印信息的窗口对象
        @param {int} depth=0xFFFFFFFF - 最大搜索深度（搜索层级，默认值0xFFFFFFFF）
        @param {str} pre_fix_str='' - 打印信息前的缩进字符串
        @param {str} screen_shot_save_path=None - 截图保存路径, 非None时代表进行截图
        @param {bool} show_all_name=True - 是否显示全部Name的内容，如果为否则只显示前30个字符
        @param {list} property_list=None - 指定要打印的属性名列表，如果不传代表全部都打印
        @param {str} print_to_file=None - 指定要打印到的文件，如果不传代表打印到屏幕
        @param {bool} set_foreground=True - 是否要将窗口设置在前台展示（部分控件信息不在前台无法获取到）
        @param {bool} to_json_str=False - 是否要整体打印为json格式字符串

        """
        # 处理文件写入
        _file = None
        if print_to_file is not None:
            _path, _file_name = os.path.split(os.path.realpath(print_to_file))
            # 创建路径
            FileTool.create_dir(_path, exist_ok=True)
            # 文件名是否正确
            if _file_name == '':
                _file_name = 'print_window_info.txt'
            # 创建并打开文件
            _file = open(
                os.path.join(_path, _file_name), 'w', encoding='utf-8'
            )

        try:
            # 先打印当前窗口信息
            _seq_num = 0  # 打印顺序号
            win: WindowControlSpec
            _before_win = None
            if set_foreground or screen_shot_save_path is not None:
                _before_win = cls.get_active_window()  # 保存原来在最前面的窗口
                win.set_foreground()

            _print_obj = cls.get_window_print_str(
                win, depth=0, show_all_name=show_all_name, property_list=property_list,
                to_json_str=to_json_str
            )

            _json_obj = dict()
            _parent_depth_index = dict()

            if to_json_str:
                _print_obj['children'] = dict()
                _json_obj[id(win)] = _print_obj
                _parent_depth_index[0] = _print_obj
            else:
                if _file is None:
                    print('%smemory_id: 0-0-%d    %s' % (pre_fix_str, id(win), _print_obj))
                else:
                    _file.write('%smemory_id: 0-0-%d    %s\r\n' %
                                (pre_fix_str, id(win), _print_obj))

            if screen_shot_save_path is not None:
                # 进行控件的屏幕截图
                l, t, r, b = win.win_rect
                try:
                    Screen.screenshot(
                        image_save_file=os.path.join(screen_shot_save_path, '0-0-%s.jpg' % id(win)),
                        region=(l, t, r - l, b - t)
                    )
                except:
                    if _file is None:
                        print('save_screen_shot_err: %s' % str(win.win_rect))
                    else:
                        _file.write('save_screen_shot_err: %s\r\n' % str(win.win_rect))

            if depth > 0:
                for _control, _depth in auto.WalkControl(win.automation_control, includeTop=False, maxDepth=depth):
                    _seq_num += 1
                    _win_ctl = WindowControlSpec(win_object=_control)
                    _print_obj = cls.get_window_print_str(
                        _win_ctl, depth=_depth,
                        show_all_name=show_all_name, property_list=property_list,
                        to_json_str=to_json_str
                    )

                    if to_json_str:
                        _print_obj['children'] = dict()
                        _parent_depth_index[_depth - 1]['children'][id(_win_ctl)] = _print_obj
                        _parent_depth_index[_depth] = _print_obj
                    else:
                        if _file is None:
                            print('%smemory_id: %d-%d-%d    %s' % (
                                ' ' * _depth * 4,
                                _seq_num,
                                _depth,
                                id(_win_ctl),
                                _print_obj
                            ))
                        else:
                            _file.write('%smemory_id: %d-%d-%d    %s\r\n' % (
                                ' ' * _depth * 4,
                                _seq_num,
                                _depth,
                                id(_win_ctl),
                                _print_obj
                            ))

                    if screen_shot_save_path is not None:
                        # 进行控件的屏幕截图
                        l, t, r, b = _win_ctl.win_rect
                        try:
                            Screen.screenshot(
                                image_save_file=os.path.join(
                                    screen_shot_save_path, '%s-%d-%d.jpg' % (_seq_num, _depth, id(_win_ctl))),
                                region=(l, t, r - l, b - t)
                            )
                        except:
                            if _file is None:
                                print('save_screen_shot_err: %s' % str(_win_ctl.win_rect))
                            else:
                                _file.write('save_screen_shot_err: %s\r\n' % str(_win_ctl.win_rect))

            # 如果是json格式，打印
            if to_json_str:
                if _file is None:
                    print(_json_obj)
                else:
                    _file.write(json.dumps(_json_obj, ensure_ascii=False, indent=4))

        finally:
            # 出现异常要关闭文件
            if _file is not None:
                _file.close()

            if _before_win is not None:
                _before_win.set_foreground()

    @classmethod
    def get_window_print_str(cls, window_ctl, depth: int = 0, show_all_name: bool = True,
                             property_list=None, to_json_str=False):
        """
        获取窗口对象的打印字符串

        @param {WindowControlSpec} window_ctl - 要打印的窗口控件
        @param {int} depth=0 - 当前层级
        @param {bool} show_all_name=True - 是否显示全部Name的内容，如果为否则只显示前30个字符
        @param {list} property_list=None - 指定要打印的属性名列表，如果不传代表全部都打印
        @param {bool} to_json_str=False - 是否要整体打印为json格式字符串

        @returns {str|dict} - 打印字符，如果to_json_str为True时返回该对象的字典
        """
        def getKeyName(theDict, theValue):
            for key in theDict:
                if theValue == theDict[key]:
                    return key

        def getLenStr(deal_str, is_show_all):
            if is_show_all:
                return deal_str
            else:
                return '%s%s' % (deal_str[0: 30], '...')

        def addPrintStr(str_list, show_name, show_value):
            if property_list is None or show_name in property_list:
                str_list[show_name] = '{0}'.format(show_value)

        _control: auto.Control = window_ctl.automation_control

        _str_list = dict()
        addPrintStr(_str_list, 'ControlType', _control.ControlTypeName)
        addPrintStr(_str_list, 'ClassName', _control.ClassName)
        addPrintStr(_str_list, 'AutomationId', _control.AutomationId)
        addPrintStr(_str_list, 'Rect', _control.BoundingRectangle)
        addPrintStr(_str_list, 'Name', getLenStr(_control.Name, show_all_name))
        addPrintStr(_str_list, 'Handle', '0x{0:X}({0})'.format(_control.NativeWindowHandle))
        addPrintStr(_str_list, 'Depth', depth)

        _supportedPatterns = list(
            filter(lambda t: t[0], (
                (_control.GetPattern(id_), name)
                for id_, name in auto.PatternIdNames.items())
            )
        )
        _patterns_names = []
        for pt, name in _supportedPatterns:
            _patterns_names.append(name)
            if isinstance(pt, auto.ValuePattern):
                addPrintStr(_str_list, 'ValuePattern.Value', getLenStr(pt.Value, show_all_name))
            elif isinstance(pt, auto.RangeValuePattern):
                addPrintStr(_str_list, 'RangeValuePattern.Value', pt.Value)
            elif isinstance(pt, auto.TogglePattern):
                addPrintStr(
                    _str_list, 'TogglePattern.ToggleState',
                    'ToggleState.' + getKeyName(auto.ToggleState.__dict__, pt.ToggleState)
                )
            elif isinstance(pt, auto.SelectionItemPattern):
                addPrintStr(_str_list, 'SelectionItemPattern.IsSelected', pt.IsSelected)
            elif isinstance(pt, auto.ExpandCollapsePattern):
                addPrintStr(
                    _str_list, 'ExpandCollapsePattern.ExpandCollapseState',
                    'ExpandCollapseState.' + getKeyName(auto.ExpandCollapseState.__dict__,
                                                        pt.ExpandCollapseState)
                )
            elif isinstance(pt, auto.ScrollPattern):
                addPrintStr(_str_list, 'ScrollPattern.HorizontalScrollPercent',
                            pt.HorizontalScrollPercent)
                addPrintStr(_str_list, 'ScrollPattern.VerticalScrollPercent',
                            pt.VerticalScrollPercent)
            elif isinstance(pt, auto.GridPattern):
                addPrintStr(_str_list, 'GridPattern.RowCount', pt.RowCount)
                addPrintStr(_str_list, 'GridPattern.ColumnCount', pt.ColumnCount)
            elif isinstance(pt, auto.GridItemPattern):
                addPrintStr(_str_list, 'GridItemPattern.Row', pt.Row)
                addPrintStr(_str_list, 'GridItemPattern.Column', pt.Column)
            elif isinstance(pt, auto.TextPattern):
                # addPrintStr(_str_list, 'TextPattern.Text', pt.DocumentRange.GetText(30))
                pass
        addPrintStr(_str_list, 'SupportedPattern', ','.join(_patterns_names))

        if to_json_str:
            return _str_list
        else:
            _to_list = [_x + ': ' + '{0}'.format(_str_list[_x]) for _x in _str_list.keys()]
            return '    '.join(_to_list)

    #############################
    # 内部函数
    #############################
    @classmethod
    def _get_run_kwargs(cls, base_dict: dict, para_list: list) -> dict:
        """
        获取只有指定参数的运行字典

        @param {dict} base_dict - 基础参数字典(具备所有值)
        @param {list} para_list - 指定的参数清单

        @returns {dict} - 返回对应的运行字典
        """
        _run_kwargs = {}
        for _para in para_list:
            if _para in base_dict.keys():
                _run_kwargs[_para] = base_dict[_para]

        return _run_kwargs

    @classmethod
    def _get_run_kwargs_without_keys(cls, base_dict: dict, para_list: list) -> dict:
        """
        获取不含指定参数的运行字典

        @param {dict} base_dict - 基础参数字典(具备所有值)
        @param {list} para_list - 需要排除的参数清单

        @returns {dict} - 返回对应的运行字典
        """
        _run_kwargs = copy.deepcopy(base_dict)
        for _para in para_list:
            if _para in _run_kwargs.keys():
                _run_kwargs.pop(_para)

        return _run_kwargs

    @classmethod
    def _is_window_match(cls, window_ctl, search_para: dict) -> bool:
        """
        检查窗口是否与查询参数匹配

        @param {WindowControlSpec} window_ctl - 要检查的窗口
        @param {dict} search_para - 查询参数字典

        @returns {bool} - 返回匹配结果
        """
        window_ctl: WindowControlSpec

        _is_match = True
        for _para in search_para.keys():
            # 逐项匹配
            if _para == 'class_name' and search_para[_para] is not None:
                if window_ctl.class_name != search_para[_para]:
                    _is_match = False
                    break
            elif _para == 'class_name_re':
                if re.match(search_para[_para], window_ctl.class_name) is None:
                    _is_match = False
                    break
            elif _para == 'name' and search_para[_para] is not None:
                if window_ctl.name != search_para[_para]:
                    _is_match = False
                    break
            elif _para == 'name_re':
                if re.match(search_para[_para], window_ctl.name) is None:
                    _is_match = False
                    break
            elif _para == 'process':
                if window_ctl.process_id != search_para[_para]:
                    _is_match = False
                    break
            elif _para == 'visible_only' and search_para[_para]:
                if not window_ctl.is_visible:
                    _is_match = False
                    break
            elif _para == 'enabled_only' and search_para[_para]:
                if not window_ctl.is_enabled:
                    _is_match = False
                    break
            elif _para == 'active_only' and search_para[_para]:
                if not window_ctl.is_active:
                    _is_match = False
                    break
            elif _para == 'automation_id':
                if window_ctl.automation_id != search_para[_para]:
                    _is_match = False
                    break
            elif _para == 'control_type':
                if window_ctl.control_type != search_para[_para]:
                    _is_match = False
                    break

        # 返回匹配结果
        return _is_match


class ApplicationSpec(object):
    """
    应用控件规格对象
    (定义应用的属性和操作)
    """

    #############################
    # 构造函数
    #############################
    def __init__(self, **kwargs):
        """
        构造函数

        @param {kwargs} - 扩展参数
            process {int} - 进程id, 对于已启动的应用传入该参数
            run_para {str} - 启动参数，通过本实例启动进程，例如'c:/path/to/your/application -a -n -y --arguments'
            其他扩展参数参考subprocess.Popen
        """
        if 'process' in kwargs.keys():
            self.process = kwargs['process']
        elif 'run_para' in kwargs.keys():
            _run_para = kwargs['run_para']
            kwargs.pop('run_para')
            _process = Popen(_run_para, **kwargs)
            self.process = _process.pid
        else:
            # 参数不正确
            raise AttributeError('At least one parameter passed in')

        self.process_info = psutil.Process(pid=self.process)

    #############################
    # 属性
    #############################
    @property
    def process_id(self) -> int:
        """
        获取进程号(PID)
        @property {int}
        """
        return self.process

    @property
    def is_running(self) -> bool:
        """
        获取是否运行状态
        @property {bool}
        """
        return (self.process_info.status() == 'running')

    @property
    def name(self) -> str:
        """
        获取进程名(程序文件名)
        @property {str}
        """
        return self.process_info.name()

    @property
    def bin_path(self) -> str:
        """
        进程对应程序路径(完整路径)
        @property {str}
        """
        return self.process_info.exe()

    @property
    def work_path(self) -> str:
        """
        进程工作目录
        @property {str}
        """
        return self.process_info.cwd()

    @property
    def create_time(self):
        """
        进程启动时间
        @property {datetime}
        """
        return datetime.datetime.fromtimestamp(self.process_info.create_time())

    @property
    def parent_pid(self) -> int:
        """
        获取父进程pid(如果找不到返回0)
        @property {int}
        """
        _pid = self.process_info.ppid()
        try:
            # 尝试获取进程信息，判断进程是否存在
            psutil.Process(_pid)
        except:
            _pid = 0
        return _pid

    @property
    def childrens(self) -> list:
        _pid_list = []
        _process_list = self.process_info.children()
        for _process in _process_list:
            _pid_list.append(_process.pid)
        return _pid_list

    @property
    def cmdline(self) -> list:
        """
        获取启动命令的命令行
        (数组包括启动命令、启动参数)
        @property {list}
        """
        return self.process_info.cmdline()

    @property
    def username(self) -> str:
        """
        获取启动命令的用户
        @property {str}
        """
        return self.process_info.username()

    #############################
    # 方法
    #############################
    def kill(self, soft=True):
        """
        关闭进程

        @param {bool} soft=True - False代表强制关闭
        """
        os.popen('taskkill.exe /pid %s /T%s' % (str(self.process), ('' if soft else ' /F')))


class WindowControlSpec(base_control.WindowControlSpec):
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

        @param {kwargs} - 扩展参数
            handle {int} - 按窗口句柄生成对象
            win_object {uiautomation.Control} - 直接传入控件对象
        """
        if 'win_object' in kwargs.keys():
            self._win_object: auto.Control = kwargs['win_object']
        elif 'handle' in kwargs.keys():
            self._win_object: auto.Control = auto.ControlFromHandle(kwargs['handle'])
        else:
            raise AttributeError('At least one parameter passed in')

    #############################
    # UIAutomation 独有的属性
    #############################
    @property
    def automation_control(self) -> auto.Control:
        """
        获取uiautomation控件对象
        @property {uiautomation.Control}
        """
        return self._win_object

    @property
    def automation_id(self) -> str:
        """
        获取对象的AutomationId
        @property {str}
        """
        return self._win_object.AutomationId

    @property
    def control_type(self) -> int:
        """
        获取对象的ControlType
        @property {int|auto.ControlType}
        """
        return self._win_object.ControlType

    @property
    def control_type_name(self) -> str:
        """
        获取对象的ControlTypeName
        @property {str}
        """
        return auto.ControlTypeNames[self._win_object.ControlType]

    @property
    def supported_pattern_ids(self) -> list:
        """
        获取对象支持的PatternId(uiautomation.PatternId)的清单
        注：可通过self.GetPattern(PatternId)获取对应的Pattern实例对象

        @property {list}
        """
        _supported_list = []
        for _pattern_id in auto.PatternIdNames.keys():
            if self._win_object.GetPattern(_pattern_id) is not None:
                _supported_list.append(_pattern_id)

        return _supported_list

    @property
    def supported_pattern_names(self) -> list:
        """
        获取对象支持的PatternName的清单

        @property {list}
        """
        _supported_ids = self.supported_pattern_ids
        _supported_names = []
        for _id in _supported_ids:
            _supported_names.append(auto.PatternIdNames[_id])

        return _supported_names

    #############################
    # 属性
    #############################
    @property
    def handle(self) -> int:
        """
        窗口句柄
        @property {int}
        """
        return self._win_object.NativeWindowHandle

    @property
    def class_name(self) -> str:
        """
        窗口类名
        @property {str}
        """
        return self._win_object.ClassName

    @property
    def name(self) -> str:
        """
        窗口标题
        @property {str}
        """
        return self._win_object.Name

    @property
    def process_id(self) -> int:
        """
        窗口所在进程id
        @property {int}
        """
        return self._win_object.ProcessId

    @property
    def thread_id(self) -> int:
        """
        窗口所在线程id
        @property {int}
        """
        raise NotImplementedError('not support property')

    @property
    def is_active(self) -> bool:
        """
        是否激活状态
        @property {bool}
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            return (self.handle == win32gui.GetForegroundWindow())
        else:
            return (self._win_object.GetTopLevelControl().NativeWindowHandle == win32gui.GetForegroundWindow())

    @property
    def is_visible(self) -> bool:
        """
        窗口是否可见
        @property {bool}
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            return (win32gui.IsWindowVisible(self.handle) != 0)
        else:
            _handle = self._win_object.GetTopLevelControl().NativeWindowHandle
            return (win32gui.IsWindowVisible(_handle) != 0)

    @property
    def is_enabled(self) -> bool:
        """
        窗口是否启用
        @property {bool}
        """
        return self._win_object.IsEnabled

    @property
    def is_minimized(self) -> bool:
        """
        窗口是否最小化(图标化)
        @property {bool}
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            return self._win_object.IsMinimize()
        else:
            return self._win_object.GetTopLevelControl().IsMinimize()

    @property
    def is_maximized(self) -> bool:
        """
        窗口是否最大化
        @property {bool}
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            return self._win_object.IsMaximize()
        else:
            return self._win_object.GetTopLevelControl().IsMaximize()

    @property
    def parent(self):
        """
        获取父窗口对象
        (如果没有父窗口返回None)
        @property {WindowControlSpec}
        """
        _parent = self._win_object.GetParentControl()
        if _parent is None:
            return None
        else:
            return WindowControlSpec(win_object=_parent)

    @property
    def win_rect(self) -> tuple:
        """
        获取窗口的区域(left, top, right, bottom)
        @property {tuple}
        """
        _rect = self._win_object.BoundingRectangle
        return (_rect.left, _rect.top, _rect.right, _rect.bottom)

    @property
    def v_scroll_viewsize(self) -> float:
        """
        获取垂直滚动条的显示区域百分占比
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        _scroll_pattern: auto.ScrollPattern = self._win_object.GetPattern(
            auto.PatternId.ScrollPattern)
        if _scroll_pattern is None:
            # 不可拖动
            return 100.0
        else:
            return _scroll_pattern.VerticalViewSize

    @property
    def v_scroll_pos(self) -> float:
        """
        获取垂直滚动条的当前位置
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        _scroll_pattern: auto.ScrollPattern = self._win_object.GetPattern(
            auto.PatternId.ScrollPattern)
        if _scroll_pattern is None:
            # 不可拖动
            return 100.0
        else:
            return _scroll_pattern.VerticalScrollPercent

    @property
    def h_scroll_viewsize(self) -> float:
        """
        获取水平滚动条的显示区域百分占比
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        _scroll_pattern: auto.ScrollPattern = self._win_object.GetPattern(
            auto.PatternId.ScrollPattern)
        if _scroll_pattern is None:
            # 不可拖动
            return 100.0
        else:
            return _scroll_pattern.HorizontalViewSize

    @property
    def h_scroll_pos(self) -> float:
        """
        获取水平滚动条的当前位置
        注：[0.0, 100.0] 区间内的值

        @property {float}
        """
        _scroll_pattern: auto.ScrollPattern = self._win_object.GetPattern(
            auto.PatternId.ScrollPattern)
        if _scroll_pattern is None:
            # 不可拖动
            return 100.0
        else:
            return _scroll_pattern.HorizontalScrollPercent

    #############################
    # 窗口遍历
    #############################
    def get_childrens(self) -> list:
        """
        获取当前窗口的子对象

        @returns {list} - 返回子窗口对象清单
        """
        _childrens = []
        for _child in self._win_object.GetChildren():
            _childrens.append(
                WindowControlSpec(win_object=_child)
            )

        return _childrens

    def get_next_sibling(self):
        """
        获取当前窗口的下一同级窗口

        @returns {WindowControlSpec} - 下一同级窗口对象，如果找不到返回None
        """
        _next = self._win_object.GetNextSiblingControl()
        if _next is None:
            return None
        else:
            return WindowControlSpec(win_object=_next)

    def get_previous_sibling(self):
        """
        获取当前窗口的上一同级窗口

        @returns {WindowControlSpec} - 上一同级窗口对象，如果找不到返回None
        """
        _prev = self._win_object.GetPreviousSiblingControl()
        if _prev is None:
            return None
        else:
            return WindowControlSpec(win_object=_prev)

    #############################
    # 窗口操作 - 状态
    #############################

    def set_foreground(self):
        """
        将窗口放在前台并激活
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            self._win_object.SetActive()
        else:
            # 取到主窗口激活
            self._win_object.GetTopLevelControl().SetActive()

    def bring_to_top(self):
        """
        将窗口设置到z-index的顶部
        如果窗口为顶层窗口，则该窗口被激活；如果窗口为子窗口，则相应的顶级父窗口被激活
        """
        return auto.BringWindowToTop(self.handle)

    def close_window(self) -> None:
        """
        关闭窗口
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            result = win32gui.PostMessage(self.handle, win32con.WM_CLOSE, 0, 0)
            if result == 0:
                self._raise_last_error()

        else:
            raise NotImplementedError('not support function')

    def set_focus(self):
        """
        将窗口设置焦点
        """
        return self._win_object.SetFocus()

    #############################
    # 窗口操作 - 位置和外观
    #############################
    def set_name(self, name: str):
        """
        设置窗口标题文字

        @param {str} name - 要设置的窗口标题文字
        """
        self._win_object.SetWindowText(name)

    def maximize(self):
        """
        最大化窗口
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            # self._win_object:auto.TopLevel
            self._win_object.Maximize()
        else:
            raise NotImplementedError('not support function')

    def minimize(self):
        """
        最小化窗口
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            self._win_object.Minimize()
        else:
            raise NotImplementedError('not support function')

    def restore(self):
        """
        还原窗口
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            self._win_object.Restore()
        else:
            raise NotImplementedError('not support function')

    def hide(self):
        """
        隐藏窗口
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            self._win_object.Hide()
        else:
            raise NotImplementedError('not support function')

    def show(self):
        """
        显示窗口
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            self._win_object.Show()
        else:
            raise NotImplementedError('not support function')

    def center(self):
        """
        窗口居中显示
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            self._win_object.MoveToCenter()
        else:
            raise NotImplementedError('not support function')

    def move(self, x=None, y=None, width=None, height=None):
        """
        移动窗口

        @param {int} x=None - x位置, None代表保持当前位置
        @param {int} y=None - y位置, None代表保持当前位置
        @param {int} width=None - 窗口宽度, None代表保持当前宽度
        @param {int} height=None - 窗口高度, None代表保持当前高度
        """
        if self._win_object.ControlType in [auto.ControlType.WindowControl, auto.ControlType.PaneControl]:
            l, t, r, b = self.win_rect
            _w = r - l
            _h = b - t
            auto.MoveWindow(
                self.handle,
                l if x is None else x, t if y is None else y,
                _w if width is None else width,
                _h if height is None else height,
                1
            )
        else:
            raise NotImplementedError('not support function')

    #############################
    # 窗口操作 - 滚动条
    #############################
    def v_scroll_to(self, pos: float):
        """
        滚动垂直滚动条到指定位置

        @param {float} pos - 要滚动到的位置百分比，[0.0, 100.0]之间
        """
        _scroll_pattern: auto.ScrollPattern = self._win_object.GetPattern(
            auto.PatternId.ScrollPattern)
        if _scroll_pattern is None or not _scroll_pattern.VerticallyScrollable:
            # 不可拖动
            return

        # 滚动
        _scroll_pattern.SetScrollPercent(
            -1, pos
        )

    def v_scroll_to_head(self):
        """
        滚动垂直滚动条到开头
        """
        return self.v_scroll_to(0.0)

    def v_scroll_to_end(self):
        """
        滚动垂直滚动条到最后
        """
        return self.v_scroll_to(100.0)

    def h_scroll_to(self, pos: float):
        """
        滚动水平滚动条到指定位置

        @param {float} pos - 要滚动到的位置百分比，[0.0, 100.0]之间
        """
        _scroll_pattern: auto.ScrollPattern = self._win_object.GetPattern(
            auto.PatternId.ScrollPattern)
        if _scroll_pattern is None or not _scroll_pattern.VerticallyScrollable:
            # 不可拖动
            return

        # 滚动
        _scroll_pattern.SetScrollPercent(
            pos, -1
        )

    def h_scroll_to_head(self):
        """
        滚动垂直滚动条到开头
        """
        return self.h_scroll_to(0.0)

    def h_scroll_to_end(self):
        """
        滚动垂直滚动条到最后
        """
        return self.h_scroll_to(100.0)

    #############################
    # 窗口操作 - 菜单
    #############################

    #############################
    # 窗口操作 - 控件处理
    #############################

    #############################
    # 内部函数
    #############################
    def _raise_last_error(self):
        """
        抛出最后一次失败的异常信息
        """
        _err_code = win32api.GetLastError()
        raise base_control.WindowException(
            'Error code from Windows: %s - %s' %
            (_err_code, win32api.FormatMessageW(_err_code))
        )


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    # win = auto.WindowControl(searchDepth=1, Name='钉钉')
    # win = WindowControlSpec(win_object=auto.GetRootControl())
    win = WindowControlSpec(handle=66808)
    # print(win.automation_control)
    Window.print_window_info(win, print_to_file='d:/print.json', to_json_str=True)
