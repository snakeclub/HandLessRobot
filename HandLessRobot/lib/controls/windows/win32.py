#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Windows平台的控制模块
注：计划废弃，不再维护
@module windows
@file windows.py
"""

import os
import sys
import copy
import time
import datetime
import ctypes
import re
import psutil
import signal
from subprocess import Popen
import win32.win32gui as win32gui
import win32.win32api as win32api
import win32com
import win32.lib.win32con as win32con
import win32.win32process as win32process
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir)))
import HandLessRobot.lib.controls.base_control as base_control


__MOUDLE__ = 'windows'  # 模块名
__DESCRIPT__ = u'Windows平台的控制模块'  # 模块描述
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
    def start_application(cls, run_para: str, **kwargs):
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
        # TODO({$AUTHOR$}): Todo Descript

        _win = cls.find_window(
            muti_search=False,
            process=app.process_id,
            top_level_only=False,
            active_only=True
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
            top_level_only {bool} - 仅限顶级元素(默认值=True), 如果指定该参数则仅使用class_name、name检索顶层窗口, 不处理其他参数
            class_name {str} - 窗口的类名(可通过spy++获取到)
            name {str} - 窗口标题
            depth {int} - 最大搜索深度（数量，默认值5000）
            class_name_re {str} - 类与此正则表达式匹配的元素
            name_re {str} - 文本与此正则表达式匹配的元素
            parent {int} - 父窗口对象(句柄或WindowControlSpec对象)
            process {int} - 窗口所在的应用进程对象(进程ID)
            visible_only {bool} - 仅可见元素 (默认值=False)
            enabled_only {bool} - 仅启用元素 (默认值=False)
            active_only {bool} - 仅限活动元素（默认= False）

        @returns {WindowControlSpec|list} - 返回窗口对象，如果muti_search为True则返回匹配到的窗口数组
        """
        # 默认参数处理
        _kwargs = {
            'muti_search': False,
            'class_name': None,
            'name': None,
            'depth': 5000,
            'top_level_only': True,
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

        # 只查找顶级元素
        if _kwargs['top_level_only']:
            _hwnd = win32gui.FindWindow(_kwargs['class_name'], _kwargs['name'])
            if _hwnd == 0:
                if _kwargs['muti_search']:
                    return []
                else:
                    # 找不到窗口抛出异常
                    raise base_control.WindowException('Window not Found')

            if _kwargs['muti_search']:
                return [WindowControlSpec(handle=_hwnd), ]
            else:
                return WindowControlSpec(handle=_hwnd)

        # 遍历方式查找
        _enum_para = {
            'search_para': _kwargs,  # 传入的匹配参数
            'current_depth': 0,  # 当前搜索数量
            'windows': []  # 存储返回的对象
        }

        if 'parent' in _kwargs.keys():
            # 有主窗口的情况
            try:
                win32gui.EnumChildWindows(
                    _kwargs['parent'], cls._enum_windows_call_back, _enum_para)
            except:
                # 如果回调函数返回False，将会抛出异常，需要屏蔽处理
                pass
        else:
            # 从主窗口开始遍历查找
            try:
                win32gui.EnumWindows(cls._enum_windows_call_back, _enum_para)
            except:
                # 如果回调函数返回False，将会抛出异常，需要屏蔽处理
                pass

            # 再遍历查找子窗口
            if len(_enum_para['windows']) == 0 or _kwargs['muti_search']:
                _enum_para_child = {
                    'search_para': _kwargs,  # 传入的匹配参数
                    'current_depth': _enum_para['current_depth'],  # 当前搜索数量
                    'windows': []  # 存储返回的对象
                }
                for _win in _enum_para['windows']:
                    try:
                        win32gui.EnumChildWindows(
                            _win.handle, cls._enum_windows_call_back, _enum_para_child
                        )
                        if not _kwargs['muti_search'] and len(_enum_para_child['windows']) > 0:
                            break
                    except:
                        # 如果回调函数返回False，将会抛出异常，需要屏蔽处理
                        pass

                # 合并两个数组
                _enum_para['windows'].extend(_enum_para_child['windows'])

        # 返回结果
        if _kwargs['muti_search']:
            return _enum_para['windows']
        else:
            if len(_enum_para['windows']) > 0:
                return _enum_para['windows'][0]
            else:
                # 找不到窗口抛出异常
                raise base_control.WindowException('Window not Found')

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
    def print_window_info(cls, win, depth=5000, pre_fix_str='', screen_shot_save_path=None):
        """
        打印指定窗口信息(含子控件)

        @param {WindowControlSpec} win - 要打印信息的窗口对象
        @param {int} depth=5000 - 最大窗口搜索深度（数量）
        @param {str} pre_fix_str='' - 打印信息前的缩进字符串
        @param {str} screen_shot_save_path=None - 截图保存路径, 非None时代表进行截图
        """
        # 先打印当前窗口信息
        win: WindowControlSpec
        _parent = win.parent
        if _parent is None:
            _parent_handle = 0
        else:
            _parent_handle = _parent.handle

        print('%s__handle:%s(%#x)  pid:%s(%#x)  name:%s  class_name:%s  parent:%s(%#x)  rect:%s' % (
            pre_fix_str, str(win.handle), win.handle, str(win.process_id), win.process_id,
            win.name, win.class_name,
            str(_parent_handle), _parent_handle, str(win.win_rect)
        ))

        if screen_shot_save_path is not None:
            # 进行控件的屏幕截图，先将窗口设置最前面
            win.set_foreground()
            l, t, r, b = win.win_rect
            try:
                Screen.screenshot(
                    image_save_file=os.path.join(screen_shot_save_path, '%s.jpg' % str(win.handle)),
                    region=(l, t, r - l, b - t)
                )
            except SystemError:
                print('save_screen_shot_err: ', win.win_rect)

        # 判断是否要打印子窗口
        if depth > 1:
            # 处理参数
            _enum_para = {
                'depth': depth,
                'current_depth': 1,
                'screen_shot_save_path': screen_shot_save_path,
                'pre_fix_str': {
                    win.handle: ''
                }
            }
            try:
                # 搜索子窗口对象
                win32gui.EnumChildWindows(
                    win.handle, cls._enum_child_windows_print_call_back, _enum_para
                )
            except:
                pass

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
    def _enum_windows_call_back(cls, hwnd, extra):
        """
        遍历窗口查找适配窗口的call_back函数

        @param {int} hwnd - 遍历的窗口句柄
        @param {dict} extra - 传入的执行参数
            search_para : 匹配参数
            current_depth : 当前层级
            windows : 找到的窗口对象

        @returns {bool} - 是否继续执行，如果返回False代表中断搜索
        """
        _window = WindowControlSpec(handle=hwnd)

        if extra['current_depth'] >= extra['search_para']['depth']:
            # 超过搜索数量
            return False

        extra['current_depth'] += 1

        # 判断当前窗口是否符合标准
        if cls._is_window_match(_window, extra['search_para']):
            # 匹配上
            extra['windows'].append(_window)
            if not extra['search_para']['muti_search']:
                # 非多匹配模式，找到就不再搜索了
                return False

        # 没有搜索到，继续找下一个
        return True

    @classmethod
    def _enum_child_windows_print_call_back(cls, hwnd, extra):
        """
        遍历子窗口执行打印处理

        @param {int} hwnd - 遍历窗口句柄
        @param {dict} extra - 传入的执行参数
            depth {int} : 最大搜索深度(数量)
            current_depth {int} : 当前深度
            pre_fix_str {dict} : 登记每一个handle的对应pre_fix_str
                key : handle
                value : pre_fix_str值

        @returns {bool} - 是否继续执行，如果返回False代表中断搜索
        """
        _enum_para = extra
        _window = WindowControlSpec(handle=hwnd)

        if _enum_para['current_depth'] < _enum_para['depth']:
            # 可以继续搜索
            _enum_para['current_depth'] += 1
            _pre_fix_str = '%s  |' % _enum_para['pre_fix_str'][_window.parent.handle]
            _enum_para['pre_fix_str'][_window.handle] = _pre_fix_str

            # 打印
            cls.print_window_info(
                _window, depth=0, pre_fix_str=_pre_fix_str,
                screen_shot_save_path=_enum_para['screen_shot_save_path']
            )
            return True
        else:
            return False

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
            elif _para == 'parent' and search_para[_para]:
                if window_ctl.parent is None or window_ctl.parent.handle != search_para[_para]:
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

        @param handle {int} - 窗口句柄
        """
        self._handle = kwargs['handle']
        if win32gui.IsWindow(self._handle) == 0:
            raise AttributeError('Is not a valid window handle')

    #############################
    # 属性
    #############################
    @property
    def handle(self) -> int:
        """
        窗口句柄
        @property {int}
        """
        return self._handle

    @property
    def class_name(self) -> str:
        """
        窗口类名
        @property {str}
        """
        return win32gui.GetClassName(self.handle)

    @property
    def name(self) -> str:
        """
        窗口标题
        @property {str}
        """
        return win32gui.GetWindowText(self.handle)

    @property
    def process_id(self) -> int:
        """
        窗口所在进程id
        @property {int}
        """
        _thread_id, _process_id = win32process.GetWindowThreadProcessId(self.handle)
        return _process_id

    @property
    def thread_id(self) -> int:
        """
        窗口所在线程id
        @property {int}
        """
        _thread_id, _process_id = win32process.GetWindowThreadProcessId(self.handle)
        return _thread_id

    @property
    def is_active(self):
        """
        窗口是否激活
        @property {bool}
        """
        return (self.handle == win32gui.GetForegroundWindow())

    @property
    def is_visible(self) -> bool:
        """
        窗口是否可见
        @property {bool}
        """
        return (win32gui.IsWindowVisible(self.handle) != 0)

    @property
    def is_enabled(self) -> bool:
        """
        窗口是否启用
        @property {bool}
        """
        return (win32gui.IsWindowEnabled(self.handle) != 0)

    @property
    def is_minimized(self) -> bool:
        """
        窗口是否最小化(图标化)
        @property {bool}
        """
        return (win32gui.IsIconic(self.handle) != 0)

    @property
    def is_maximized(self) -> bool:
        """
        窗口是否最大化
        @property {bool}
        """
        return ctypes.windll.user32.IsZoomed(self.handle) != 0

    @property
    def parent(self):
        """
        获取父窗口对象
        (如果没有父窗口返回None)
        @property {WindowControlSpec}
        """
        _parent_handle = win32gui.GetParent(self.handle)
        if _parent_handle:
            _parent = WindowControlSpec(handle=_parent_handle)
        else:
            _parent = None
        return _parent

    @property
    def win_rect(self) -> tuple:
        """
        获取窗口的区域(left, top, right, bottom)
        @property {tuple}
        """
        return win32gui.GetWindowRect(self.handle)

    @property
    def v_scroll_range(self) -> tuple:
        """
        获取垂直滚动条的取值范围
        @property {tuple}
        """
        _info = win32gui.GetScrollInfo(self.handle, win32con.SB_VERT, win32con.SIF_RANGE)
        if _info:
            return (_info[1], _info[2])
        else:
            # 没有找到返回(0, 0)
            return (0, 0)

    @property
    def v_scroll_pos(self) -> int:
        """
        获取垂直滚动条的当前位置
        @property {int}
        """
        _info = win32gui.GetScrollInfo(self.handle, win32con.SB_VERT, win32con.SIF_POS)
        if _info:
            return _info[4]
        else:
            # 没有找到返回0
            return 0

    @property
    def h_scroll_range(self) -> tuple:
        """
        获取水平滚动条的取值范围
        @property {tuple}
        """
        _info = win32gui.GetScrollInfo(self.handle, win32con.SB_HORZ, win32con.SIF_RANGE)
        if _info:
            return (_info[1], _info[2])
        else:
            # 没有找到返回(0, 0)
            return (0, 0)

    @property
    def h_scroll_pos(self) -> int:
        """
        获取水平滚动条的当前位置
        @property {int}
        """
        _info = win32gui.GetScrollInfo(self.handle, win32con.SB_HORZ, win32con.SIF_POS)
        if _info:
            return _info[4]
        else:
            # 没有找到返回0
            return 0

    #############################
    # 窗口遍历
    #############################
    def get_childrens(self):
        """
        获取当前窗口的子对象
        """
        raise NotImplementedError()

    #############################
    # 窗口操作 - 状态
    #############################
    def set_foreground(self):
        """
        将窗口放在前台并激活
        """
        # _shell = win32com.client.Dispatch("WScript.Shell")
        # _shell.SendKeys('%')
        win32api.keybd_event(13, 0, 0, 0)
        if self.parent is None:  # 避免非顶级窗口
            result = win32gui.SetForegroundWindow(self.handle)
            if result == 0:
                self._raise_last_error()
                # ?return win32gui.SetActiveWindow(self.handle)

    def bring_to_top(self):
        """
        将窗口设置到z-index的顶部
        如果窗口为顶层窗口，则该窗口被激活；如果窗口为子窗口，则相应的顶级父窗口被激活
        """
        win32gui.BringWindowToTop(self.handle)

    def close_window(self) -> None:
        """
        关闭窗口
        """
        result = win32gui.PostMessage(self.handle, win32con.WM_CLOSE, 0, 0)
        if result == 0:
            self._raise_last_error()

    def set_focus(self):
        """
        将窗口设置焦点
        """
        win32gui.SetFocus(self.handle)

    #############################
    # 窗口操作 - 位置和外观
    #############################
    def set_name(self, name: str):
        """
        设置窗口标题文字

        @param {str} name - 要设置的窗口标题文字
        """
        win32gui.SetWindowText(self.handle, name)

    def maximize(self):
        """
        最大化窗口
        """
        win32gui.ShowWindow(self.handle, win32con.SW_MAXIMIZE)

    def minimize(self):
        """
        最小化窗口
        """
        win32gui.ShowWindow(self.handle, win32con.SW_MINIMIZE)

    def restore(self):
        """
        还原窗口
        """
        win32gui.ShowWindow(self.handle, win32con.SW_RESTORE)

    def hide(self):
        """
        隐藏窗口
        """
        win32gui.ShowWindow(self.handle, win32con.SW_HIDE)

    def show(self):
        """
        显示窗口
        """
        win32gui.ShowWindow(self.handle, win32con.SW_SHOW)

    def center(self):
        """
        窗口居中显示
        """
        _sw, _sh = Screen.size()  # 屏幕大小
        _x, _y, _r, _b = self.win_rect  # 窗口大小
        _w = _r - _x
        _h = _b - _y
        self.move(
            x=((_sw - _w) // 2),
            y=((_sh - _h) // 2),
        )

    def move(self, x=None, y=None, width=None, height=None):
        """
        移动窗口

        @param {int} x=None - x位置, None代表保持当前位置
        @param {int} y=None - y位置, None代表保持当前位置
        @param {int} width=None - 窗口宽度, None代表保持当前宽度
        @param {int} height=None - 窗口高度, None代表保持当前高度
        """
        l, t, r, b = self.win_rect
        _w = r - l
        _h = b - t
        win32gui.MoveWindow(
            self.handle,
            l if x is None else x, t if y is None else y,
            _w if width is None else width,
            _h if height is None else height,
            1
        )

    #############################
    # 窗口操作 - 滚动条
    #############################
    def v_scroll_to(self, pos: int) -> int:
        """
        滚动垂直滚动条到指定位置

        @param {int} pos - 要滚动到的位置

        @returns {int} - 设置后的当前位置
        """
        return win32gui.SetScrollInfo(
            self.handle,
            (win32con.SB_VERT, 0, 0, 0, pos, 0)
        )

    def v_scroll_to_head(self) -> int:
        """
        滚动垂直滚动条到开头

        @returns {int} - 设置后的当前位置
        """
        return self.v_scroll_to(0)

    def v_scroll_to_end(self) -> int:
        """
        滚动垂直滚动条到最后

        @returns {int} - 设置后的当前位置
        """
        return self.v_scroll_to(self.v_scroll_range()[1])

    def h_scroll_to(self, pos: int) -> int:
        """
        滚动水平滚动条到指定位置

        @param {int} pos - 要滚动到的位置

        @returns {int} - 设置后的当前位置
        """
        return win32gui.SetScrollInfo(
            self.handle,
            (win32con.SB_HORZ, 0, 0, 0, pos, 0)
        )

    def h_scroll_to_head(self) -> int:
        """
        滚动垂直滚动条到开头

        @returns {int} - 设置后的当前位置
        """
        return self.h_scroll_to(0)

    def h_scroll_to_end(self) -> int:
        """
        滚动垂直滚动条到最后

        @returns {int} - 设置后的当前位置
        """
        return self.h_scroll_to(self.h_scroll_range()[1])

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

    # _top_win_find_para = {
    #     'top_level_only': True,
    #     'class_name': 'StandardFrame_DingTalk',
    #     'name': '钉钉'
    # }
    # _top_win = Window.find_window(**_top_win_find_para)
    # # _top_win.move(x=0, y=0)
    # Window.print_window_info(_top_win, screen_shot_save_path='d:/test_win/')

    # Window.print_window_info(
    #     WindowControlSpec(handle=1445208), screen_shot_save_path='d:/test_win/'
    # )

    _app_list = Window.get_application(
        muti_search=True, name='DingTalk.exe'
    )
    for _app in _app_list:
        try:
            print(_app.process_id)
            _win = Window.application_active_window(_app)
        except:
            print('not win found', _app.process_id)
            import traceback
            print(traceback.format_exc())
            continue

    #     Window.print_window_info(_win, screen_shot_save_path='d:/test_win/')
