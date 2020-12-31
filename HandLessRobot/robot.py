#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
机器人模块
@module robot
@file robot.py
"""
import os
import sys
import uuid
import platform
import inspect
import json
import copy
from HiveNetLib.simple_log import Logger
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.base_tools.import_tool import ImportTool
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.pipeline import Pipeline
from HiveNetLib.pipeline_router import GoToNode
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from HandLessRobot.lib.actions.base_action import BaseAction
from HandLessRobot.lib.pipeline_plugin import RobotActionRun, RobotActionControl, RobotPredefRun


__MOUDLE__ = 'process'  # 模块名
__DESCRIPT__ = u'主框架进程处理模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.04.15'  # 发布日期


class RunEnvironment(object):
    """
    机器人运行环境设置框架

    全局变量定义：
    ACTION_ROUTERS - 用于找到不同动作类别的实际动作函数
        {
            '*': {
                    'Action_Name': {
                        'fun': fun_object,
                        'platform': {'system': (ver1, ver2, ...)},
                        'instance_class': '',
                        'is_control': False,
                        'name': '动作名',
                        'desc': '动作描述',
                        'param': [
                            ['para_name', 'data_type', 'default_value', 'desc'],
                            ...
                        ],
                        'returns': ['data_type', 'desc']
                    },
                    ...
            },
            'action_type_1': {
                ...
            },
            'action_type_2': {
                ...
            },
            ...
        }
        说明如下：
        (1)'*', 'action_type_1', 'action_type_2'代表动作类别，通过类的support_action_types函数可以得到该动作类
            可支持的类别清单;
        (2)动作类别下面的动作路由配置可通过类的get_action_router函数获取, 具体字段说明如下：
            Action_Name - 动作名(大小写不敏感)，导入时将统一转换为大写，在机器人动作中根据逻辑中的动作名获取动作对应的执行函数
                fun - 动作执行函数对象，该函数必须严格定义为fun(robot_info: dict, arg, ..., key=xx, ..., **kwargs)
                    其中robot_info和kwargs两个参数为必须的参数，arg和key=xx的参数根据实际需要定义即可
                    robot_info实际上会直接传入下一节说明的全局变量ROBOT_INFOS中对应机器人的信息，即ROBOT_INFOS[robot_id]
                platform - 支持的操作系统信息, 可以支持多个
                    key {str} - 支持的平台名称(例如Windows、Linux), 可通过'platform.system()'获取, '*'代表全平台支持,
                    value {tuple} - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
                instance_class - 如果为静态函数，为 '' , 如果为实例化对象的函数和属性，则为对象的类名
                is_control - 如果是控制动作，为True, 否则为False
                name - 动作中文名
                desc - 动作详细说明
                param - 帮助信息，用于在帮助中展示该函数的入参说明，其中default_value是默认值，如果无默认值该项应为None
                returns - 帮助信息，用于在帮助中展示该函数的返回值说明
        (3)执行一个Action_Name会优先匹配'*'，然后再根据机器人执行时的当前动作类别action_type从对应的路由表查找。

    RESERVED_CONTROL_ACTION_NAME - 预留用于控制的动作名字典
        {
            '*': [Action_Name, Action_Name, ...],
            'robot_id': [Action_Name, Action_Name, ...],
            ...
        }


    ROBOT_SELF_ROUTERS - 每个机器人实例自有的路由，每个机器人id后面的结构跟ACTION_ROUTERS一致
        {
            robot_id: {
                ...
            },
            ...
        }

    ROBOT_INFOS - 用于临时记录每个机器人执行的临时信息
        {
            robot_id: {
                'robot': robot_instance,
                'id': robot_id,
                'use_action_types': ['action_type', ...],
                'predef_pipeline': {
                    'predef_name': Pipeline,
                    ...
                },
                'predef_config': {
                    'predef_name': {},
                    ...
                },
                'run_pipeline': {
                    run_id: Pipeline,
                    ...
                },
                'run_config': {
                    run_id: {},
                    ...
                },
                'vars': {
                    '*':{
                        'var_name': var_value,
                        'var_name': var_value,
                        ...
                    },
                    'run_id_x': {...}
                }
            },
            ...
        }
        说明如下：
        robot_id - 是机器人执行开始时生成的唯一ID，标识工作机器人;
        action_type - 登记当前动作类别action_type
        use_action_types - 登记机器人允许使用的动作类别，同时也会按这个顺序进行查找('*'可以不列进去，总是第一个查找)
        predef_pipeline - 预定义模块管道对象
        predef_config - 预定义模块的配置信息
        run_pipeline - 直接执行的管道对象
        run_config - 直接执行的配置信息
        vars - 登记机器人执行过程中的临时变量，其中 '*' 放置全局变量，也可以放置只在某一个run_id下才能使用的变量

    """

    #############################
    # 公共函数
    #############################
    @classmethod
    def get_platform(cls):
        """
        获取平台信息

        @returns {str, str} - 返回当前操作系统名称和版本号
        """
        return platform.system(), platform.release()

    @classmethod
    def check_platform_matched(cls, platform_setting: dict, ignore_version: bool = False,
                               system=None, release=None) -> bool:
        """
        检查当前操作系统是否与配置匹配

        @param {dict} platform_setting - 配置字典
            key {str} - 支持的平台名称(例如Windows、Linux), 可通过'platform.system()'获取, '*'代表全平台支持,
            value {tuple} - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        @param {bool} ignore_version=False - 是否忽略版本检查
        @param {str} system=None - 支持外部传入系统类型（针对移动端应用测试需要在PC执行脚本的情况）
        @param {str} release=None - 当传入system时使用

        @returns {bool} - 返回匹配结果
        """
        if '*' in platform_setting.keys():
            # 全版本支持, 无需再检查
            return True

        if system is None:
            _system, _release = cls.get_platform()  # 获取执行平台信息
        else:
            _system = system
            _release = release

        if _system not in platform_setting.keys():
            # 没有找到操作系统
            return False

        if platform_setting[_system] is not None:
            # 有限定版本
            if not ignore_version and platform_setting[_system] is not None:
                if _release is not None and _release not in platform_setting[_system]:
                    return False

        # 检查通过
        return True

    @classmethod
    def check_inited(cls):
        """
        检查机器人运行环境是否已加载

        @returns {bool} - 是否已加载
        """
        _ACTION_ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        if _ACTION_ROUTERS is None:
            return False
        else:
            return True

    @classmethod
    def init(cls, init_modules: list = None, init_class: list = None, init_action_path: str = None,
             robot_id: str = None, **kwargs):
        """
        初始化机器人运行环境，装载公共动作配置信息

        @param {list} init_modules=None - 要初始化的插件模块清单
        @param {list} init_class=None - 要初始化的插件类清单
        @param {str} init_action_path=None - 要加载的动作模块路径
        @param {str} robot_id=None - 机器人id，如果有传值代表导入对应机器人实例自有路由中
        """
        # 初始化全局变量
        _ACTION_ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        if _ACTION_ROUTERS is None:
            _ACTION_ROUTERS = {'*': {}}
            RunTool.set_global_var('ACTION_ROUTERS', _ACTION_ROUTERS)

        _RESERVED_CONTROL_ACTION_NAME = RunTool.get_global_var('RESERVED_CONTROL_ACTION_NAME')
        if _RESERVED_CONTROL_ACTION_NAME is None:
            _RESERVED_CONTROL_ACTION_NAME = {
                '*': list()
            }
            RunTool.set_global_var(
                'RESERVED_CONTROL_ACTION_NAME', _RESERVED_CONTROL_ACTION_NAME
            )

        _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
        if _ROBOT_SELF_ROUTERS is None:
            _ROBOT_SELF_ROUTERS = dict()
            RunTool.set_global_var('ROBOT_SELF_ROUTERS', _ROBOT_SELF_ROUTERS)

        _ROBOT_INFOS = RunTool.get_global_var('ROBOT_INFOS')
        if _ROBOT_INFOS is None:
            _ROBOT_INFOS = dict()
            RunTool.set_global_var('ROBOT_INFOS', _ROBOT_INFOS)

        # 加载公共动作模块
        if init_modules is not None:
            for _moudle in init_modules:
                cls._add_action_router_by_module(_moudle, robot_id=None)

        # 加载公共插件类
        if init_class is not None:
            for _class in init_class:
                cls._add_action_router_by_class(_class, robot_id=None)

        # 加载公共插件文件
        if init_action_path is not None:
            for _file in init_action_path:
                cls.load_action_module_by_dir(init_action_path, robot_id=None)

        # 加载管道公共插件
        for _class_obj in [GoToNode, RobotActionRun, RobotActionControl, RobotPredefRun]:
            _plugin_type = 'processer'
            _name_fun = getattr(_class_obj, 'processer_name', None)
            if _name_fun is None:
                _name_fun = getattr(_class_obj, 'router_name', None)
                _plugin_type = 'router'

            if Pipeline.get_plugin(
                _plugin_type, _name_fun()
            ) is None:
                Pipeline.add_plugin(_class_obj)

    @classmethod
    def load_action_module(cls, module_file: str, robot_id: str = None):
        """
        加载动作模块文件

        @param {str} module_file - 要加载的动作模块文件
        @param {str} robot_id=None - 机器人id，如果有传值代表导入对应机器人实例自有路由中
        """
        # 检查环境是否已加载
        cls._check_inited_raise()
        _path, _file = os.path.split(os.path.realpath(module_file))

        # 加载文件
        _module = ImportTool.import_module(_file[0: -3], extend_path=_path, is_force=False)

        # 导入路由信息
        cls._add_action_router_by_module(_module, robot_id=robot_id)

    @classmethod
    def load_action_module_by_dir(cls, module_path: str, robot_id: str = None):
        """
        加载指定目录的动作模块文件

        @param {str} module_path - 要加载的动作模块文件目录
        @param {str} robot_id=None - 机器人id，如果有传值代表导入对应机器人实例自有路由中
        """
        # 检查环境是否已加载
        cls._check_inited_raise()

        # 遍历文件执行加载
        _file_list = FileTool.get_filelist(
            path=module_path, regex_str=r'.*\.py$', is_fullname=False
        )
        for _file in _file_list:
            if _file == '__init__.py':
                continue

            # 逐笔进行加载处理
            cls.load_action_module(os.path.join(module_path, _file), robot_id=robot_id)

    @classmethod
    def get_match_action(cls, action_name: str, robot_id: str = None, use_action_types: list = None,
                         ignore_version: bool = False, system=None, release=None, **kwargs):
        """
        从路由表获取适用的动作配置

        @param {str} action_name - 动作名(不区分大小写)
        @param {str} robot_id=None - 机器人id，如果有传值代表优先从对应机器人实例自有路由中查找
        @param {list} use_action_types=None - 允许使用的动作类别清单顺序
        @param {bool} ignore_version=False - 是否忽略版本检查
        @param {str} system=None - 支持外部传入系统类型（针对移动端应用测试需要在PC执行脚本的情况）
        @param {str} release=None - 当传入system时使用

        @returns {dict} - 返回找到的动作配置字典

        @throws {ModuleNotFoundError} - 找不到抛出异常
        """
        _ACTION_ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        _action_name = action_name.upper()
        _action_dict = None

        # 优先从机器人自有路由中查找
        if robot_id is not None:
            _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
            if robot_id in _ROBOT_SELF_ROUTERS.keys():
                _ROUTERS = _ROBOT_SELF_ROUTERS[robot_id]
                for _action_type in _ROUTERS.keys():
                    if _action_name in _ACTION_ROUTERS[_action_type].keys():
                        if cls.check_platform_matched(
                            _ROUTERS[_action_type][_action_name]['platform'],
                            ignore_version=ignore_version,
                            system=system, release=release
                        ):
                            # 名称及操作系统都支持，已找到函数
                            _action_dict = _ROUTERS[_action_type][_action_name]
                            break

        if _action_dict is not None:
            return _action_dict

        # 继续从全局路由中查找
        # 保证 '*' 是第一位
        _use_action_types = ['*']
        if use_action_types is None:
            _use_action_types.extend(list(_ACTION_ROUTERS.keys()))
        else:
            _use_action_types.extend(use_action_types)

        for _action_type in _use_action_types:
            if _action_name in _ACTION_ROUTERS[_action_type].keys():
                if cls.check_platform_matched(
                    _ACTION_ROUTERS[_action_type][_action_name]['platform'],
                    ignore_version=ignore_version,
                    system=system, release=release
                ):
                    # 名称及操作系统都支持，已找到函数
                    _action_dict = _ACTION_ROUTERS[_action_type][_action_name]
                    break

        if _action_dict is None:
            # 没有找到函数，抛出异常
            raise ModuleNotFoundError(
                'Action name [{0}] not found in action_router!'.format(action_name))
        else:
            return _action_dict

    #############################
    # 私有函数
    #############################
    @classmethod
    def _add_action_router_by_module(cls, module_object, robot_id: str = None):
        """
        通过模块对象导入动作类型路由

        @param {object} module_object - 动作模块对象
        @param {str} robot_id=None - 机器人id，如果有传值代表导入对应机器人实例自有路由中
        """
        _clsmembers = inspect.getmembers(module_object, inspect.isclass)
        for (_class_name, _class) in _clsmembers:
            if not hasattr(_class, 'support_action_types') or _class == BaseAction:
                # 通过support_action_types来判断是否动作类
                continue

            # 按类执行导入处理
            cls._add_action_router_by_class(_class, robot_id=robot_id)

    @classmethod
    def _add_action_router_by_class(cls, class_object, robot_id: str = None):
        """
        通过类导入动作类型路由

        @param {object} class_object - 要导入的类对象
        @param {str} robot_id=None - 机器人id，如果有传值代表导入对应机器人实例自有路由中
        """
        _ROUTERS = None
        _RESERVED_CONTROL_ACTION_NAME = RunTool.get_global_var('RESERVED_CONTROL_ACTION_NAME')
        _CONTROL_LIST = None
        if robot_id is None:
            # 公共动作配置
            _ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
            _CONTROL_LIST = _RESERVED_CONTROL_ACTION_NAME['*']
        else:
            # 机器人私有动作配置
            _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
            if robot_id not in _ROBOT_SELF_ROUTERS.keys():
                _ROBOT_SELF_ROUTERS[robot_id] = {'*': dict()}
            _ROUTERS = _ROBOT_SELF_ROUTERS[robot_id]

            # 私有动作关键字
            if robot_id not in _RESERVED_CONTROL_ACTION_NAME.keys():
                _RESERVED_CONTROL_ACTION_NAME[robot_id] = list()
            _CONTROL_LIST = _RESERVED_CONTROL_ACTION_NAME[robot_id]

        _class_router = class_object.get_action_router()
        _support_types = class_object.support_action_types()

        for _action_name in _class_router.keys():
            # 逐个动作导入处理
            _upper_name = _action_name.upper()
            for _type in _support_types:
                if _type not in _ROUTERS.keys():
                    # 添加新的类型
                    _ROUTERS[_type] = dict()

                # 在指定类型下添加路由
                _ROUTERS[_type][_upper_name] = _class_router[_action_name]

                # 判断是否要加到控制预留关键字
                if _class_router[_action_name].get('is_control', False):
                    _CONTROL_LIST.append(_upper_name)

    @classmethod
    def _check_inited_raise(cls):
        """
        检查环境是否已加载，如果未加载抛出异常
        """
        if not cls.check_inited():
            raise RuntimeError('Robot run environment not initialized!')


class Robot(object):
    """
    机器人主控模块
    """
    #############################
    # 静态工具函数
    #############################
    @classmethod
    def json_to_pipeline_config(cls, config: dict) -> dict:
        """
        JSON格式的步骤配置转换为管道执行配置字典

        @param {dict} config - 机器人执行步骤JSON配置字典

        @returns {dict} - 转换后的pipeline执行配置字典
        """
        _pipeline_config = dict()

        # 获取step数组并遍历处理
        _steps = config['steps']

        _pipe_id = 1  # pipeline的顺序号
        _stack = list()  # if/loop块处理的堆栈

        for _i in range(len(_steps)):
            _step = _steps[_i]
            _cmd = _step.get('cmd', 'run').lower()
            _node_id = str(_pipe_id)

            # 复制配置字典
            _config: dict = copy.deepcopy(_step)
            _config.pop('step_id', None)
            _config.pop('cmd', None)
            _config.pop('exception_to', None)

            if _cmd == 'run':
                # 运行当前节点动作
                _pipeline_config[_node_id] = {
                    'name': _step.get('step_id', ''),
                    'processor': 'RobotActionRun',
                    'context': {
                        'action_config': _config
                    }
                }
            elif _cmd == 'predef':
                _pipeline_config[_node_id] = {
                    'name': _step.get('step_id', ''),
                    'processor': 'RobotPredefRun',
                    'is_sub_pipeline': True,
                    'sub_pipeline_para': {
                        'predef_name': _config['predef_name']
                    }
                }
            else:
                # 控制动作
                _config['control_name'] = _cmd
                _pipeline_config[_node_id] = {
                    'name': _step.get('step_id', ''),
                    'processor': 'RobotActionControl',
                    'context': {
                        'control_config': _config
                    }
                }

                # 支持跳转的动作，增加跳转路由器
                if _cmd in ('if', 'else', 'goto', 'end', 'loop', 'endloop', 'break', 'continue', 'prompt'):
                    _pipeline_config[_node_id]['router'] = 'GoToNode'
                    if _cmd == 'prompt':
                        # 需特殊指定 GoToNode 的参数
                        _pipeline_config[_node_id]['router_para'] = {
                            'default_to_next': True
                        }

                if _cmd in ('if', 'loop'):
                    # 将开始位置放入堆栈
                    _stack.append([_node_id, _cmd])
                elif _cmd == 'else':
                    # else情况，让if标签的配置知道当前节点位置
                    _last_index = len(_stack) - 1
                    if _stack[_last_index][1] != 'if':
                        raise RuntimeError('cmd else must in if block!')
                    _pipeline_config[_stack[_last_index][0]
                                     ]['context']['control_config']['else_node_id'] = _node_id
                elif _cmd == 'endif':
                    # endif情况，让if标签的配置知道当前节点位置
                    _last_cmd = _stack.pop(len(_stack) - 1)
                    if _last_cmd[1] != 'if':
                        raise RuntimeError('cmd endif must in if block!')
                    _pipeline_config[_last_cmd[0]
                                     ]['context']['control_config']['end_node_id'] = _node_id
                    # 如果有else标签，需要让else标签知道结束位置
                    _else_node_id = _pipeline_config[_last_cmd[0]
                                                     ]['context']['control_config'].get('else_node_id', None)
                    if _else_node_id is not None:
                        _pipeline_config[_else_node_id]['context']['control_config']['end_node_id'] = _node_id
                elif _cmd in ('break', 'continue'):
                    # 循环内部控制，需要为自己的配置知道循环开始位置
                    _last_index = len(_stack) - 1
                    if _stack[_last_index][1] != 'loop':
                        raise RuntimeError('cmd %s must in loop block!' % _cmd)
                    _pipeline_config[_node_id]['context']['control_config']['loop_node_id'] = _stack[_last_index][0]
                elif _cmd == 'endloop':
                    # endloop情况，让loop标签的配置知道当前节点位置
                    _last_cmd = _stack.pop(len(_stack) - 1)
                    if _last_cmd[1] != 'loop':
                        raise RuntimeError('cmd endloop must in loop block!')
                    _pipeline_config[_node_id]['context']['control_config']['loop_node_id'] = _last_cmd[0]
                    _pipeline_config[_last_cmd[0]
                                     ]['context']['control_config']['end_node_id'] = _node_id

            # 异常跳转
            if _step.get('exception_to', '') != '':
                _pipeline_config[_node_id]['exception_router'] = 'GoToNode'
                _pipeline_config[_node_id]['exception_router_para'] = {
                    'goto_node_name': _step['exception_to']
                }

            # 管道节点id加1
            _pipe_id += 1

        # 检查块嵌套是否配置错误
        if len(_stack) > 0:
            raise RuntimeError('config error: if/loop block with not end node!')

        # 增加标准的结束节点
        _pipeline_config[str(_pipe_id)] = {
            'name': '{$END_NODE$}',
            'processor': 'RobotActionControl',
            'context': {
                'control_config': {
                    'control_name': 'null'
                }
            }
        }

        return _pipeline_config

    #############################
    # 工具函数
    #############################
    def load_predef_by_config(self, config: dict):
        """
        通过配置字典装载预定义模块

        @param {dict} config - 配置字典
            @param {dict} config - 机器人执行步骤JSON配置字典
            {
                "predef_name": "预定义模板名",
                "steps": [
                    {
                        "step_id": "步骤标识名，可不设置，主要用于步骤之间的跳转",
                        "cmd": "执行命令，如不传则默认为'run'",
                        "action_name": "要执行的动作名",
                        "instance_obj": "要执行动作所在的实例对象变量获取标签，可不设置",
                        "call_para_args": "[value1, value2, ...]",  # 执行按位置传入的参数数组json字符串，可以用变量获取标签替代, 可不设置
                        "call_para_kwargs": "{'key1': value1, 'key2': value2, ...}", # 执行按key-value传入的参数字典json字符串，可以用变量获取标签替代, 可不设置
                        "save_to_var": "要保存到变量的变量名，可不设置",
                        "save_run_id": "与save_to_var配套使用，保存到的变量使用范围，不传默认为当前的run_id，可以传*指定使用全局，或传入指定run_id执行特定运行间变量",
                        "exception_to": "当出现异常时跳转到的step_id，如果不设置出现异常报错后，则停留在报错的步骤",
                        "goto_step_id": "要跳转到的步骤标识名",
                        "condition": "判断条件的python表达式，支持变量获取标签替代",
                        "predef_name": "要执行的预定义模板名",
                        "prompt_router": "{'cmd': 'step_id', 'cmd': 'step_id', ...}",  # prompt参数，命令对应的路由字典
                        "prompt_para": "{'over_time': 0, 'over_time_step_id': None, 'sleep_time': 500}", # prompt参数
                        "remark": "备注信息"
                    },
                    ...
                ]
            }
            注：
            1、cmd支持的传入类型及参数要求
                run - 仅运行动作，执行完成后按顺序执行下一步
                    可用参数：action_name/instance_obj/call_para_args/call_para_kwargs/save_to_var/save_run_id/exception_to
                null - 不做任何处理
                end - 直接结束机器人执行
                goto - 跳转到指定的 step_id 所在步骤
                    可用参数：goto_step_id
                if - 对动作执行结果进行判断
                    可用参数：condition/action_name/instance_obj/call_para_args/call_para_kwargs/save_to_var/save_run_id
                    注：如果条件中需要使用送入的动作执行结果，使用 {$local=run_action$} 替代
                        例如: '{$var=var_name$} > 0 and {$local=run_action$} in ['abc', 'bcd']'
                else - if条件判断False时执行的节点
                endif - if条件判断结尾节点，不做任何处理
                loop - 循环处理
                    可用参数：condition/action_name/instance_obj/call_para_args/call_para_kwargs/save_to_var/save_run_id
                break - 循环结束
                continue - 马上下一次循环
                endloop - 结束循环位置
                predef - 执行预定义模板
                    可用参数：predef_name
                prompt - 提示获取输入，根据输入跳转到对应步骤
                    可用参数：prompt_router/prompt_para/action_name/instance_obj/call_para_args/call_para_kwargs/save_to_var/save_run_id
                    注：prompt命令的 action_name 应指定的是通知输入命令提示的动作，比如打开提示窗口

            2、变量获取标签
                '{$fixed=last$}' - 获取上一步动作执行的结果
                '{$fixed=run_id$}' - 获取当前执行id
                '{$fixed=now$}' - 获取当前时间
                '{$var=var_name$}' 或 {$var=var_name,run_id$} - 获取执行过程保存的变量
                '{$local=var_name$}' - 获取执行过程中可以访问到的变量

        """
        # 生成管道对象
        _pipeline_config = self.json_to_pipeline_config(config)
        _pipeline = Pipeline(
            config['predef_name'], _pipeline_config,
            running_notify_fun=None if self.running_notify_fun is None else self._running_notify_fun,
            end_running_notify_fun=None if self.end_running_notify_fun is None else self._end_running_notify_fun,
            logger=self.logger
        )

        # 装载到机器人
        self.robot_info['predef_pipeline'][config['predef_name']] = _pipeline
        self.robot_info['predef_config'][config['predef_name']] = copy.deepcopy(config)

    def load_predef_by_file(self, file: str, encoding: str = 'utf-8'):
        """
        通过文件装载预定义模板

        @param {str} file - 要装载的文件名
        @param {str} encoding='utf-8' - 文件编码
        """
        _ext = FileTool.get_file_ext(file).lower()
        if _ext == 'json':
            with open(file, 'r', encoding=encoding) as _fp:
                _json = _fp.read()

            _config = json.loads(_json)
        else:
            raise AttributeError('Not support file type [%s]!' % _ext)

        # 装载到机器人
        self.load_predef_by_config(_config)

    def load_predef_by_path(self, path: str, encoding: str = 'utf-8'):
        """
        通过文件路径装载预定义模板

        @param {str} path - 要装载模板的路径

        @param {str} encoding='utf-8' - 文件编码
        """
        _file_list = FileTool.get_filelist(path, is_fullname=True)
        for _file in _file_list:
            self.load_predef_by_file(_file, encoding=encoding)

    def get_config(self, predef_name: str, run_id: str) -> dict:
        """
        获取指定机器人执行配置

        @param {str} predef_name - 预定义模块名，如果是使用run执行的，可以传''
        @param {str} run_id - 执行id，优先用这个获取run执行的配置, 如果要获取预定义模块，可以传None

        @returns {dict} - 执行配置
        """
        _config = None
        # 优先使用run_id获取
        if run_id is not None:
            _config = self.robot_info['run_config'].get(run_id, None)

        if _config is None:
            _config = self.robot_info['predef_config'][predef_name]

        return _config

    def get_step_para(self, predef_name: str, run_id: str, node_id: int) -> dict:
        """
        获取执行步骤对应的参数字典

        @param {str} predef_name - 预定义模块名，如果是使用run执行的，可以传''
        @param {str} run_id - 执行id，优先用这个获取run执行的配置, 如果要获取预定义模块，可以传None
        @param {int} node_id - 节点顺序号，从1开始

        returns {dict} - 执行配置信息
        """
        _config = self.get_config(predef_name, run_id)
        _step_count = len(_config['steps'])

        _para = dict()
        if node_id <= _step_count:
            _para = _config['steps'][node_id - 1]
        elif node_id == _step_count + 1:
            # 是最后一个结算点，固定返回
            _para = {
                "step_id": "{$END_NODE$}",
                "cmd": "null",
                "remark": "End Node"
            }

        return _para

    def current_step_sub(self, predef_name: str, run_id: str):
        """
        获取当前执行节点顺序id（延伸至子管道）

        @param {str} predef_name - 预定义模块名，如果是使用run执行的，可以传''
        @param {str} run_id - 执行id，优先用这个获取run执行的配置

        @returns {str, int} - 当前节点信息 predef_name, node_id
        """
        _pipeline: Pipeline = None
        # 优先使用run_id获取
        _pipeline = self.robot_info['run_pipeline'].get(run_id, None)

        if _pipeline is None:
            _pipeline = self.robot_info['predef_pipeline'][predef_name]

        _predef_name = _pipeline.name
        _node_id = _pipeline.current_node_id(run_id=run_id)
        while _pipeline.pipeline[_node_id].get('is_sub_pipeline', False):
            # 是子管道，获取子管道信息
            _pipeline = _pipeline.running_sub_pipeline.get(run_id, None)
            if _pipeline is None:
                # 没有获取到
                break

            _predef_name = _pipeline.name
            _node_id = _pipeline.current_node_id(run_id=run_id)

        # 返回结果
        return _predef_name, int(_node_id)

    def current_step(self, predef_name: str, run_id: str):
        """
        获取当前执行节点顺序id（只获取当前运行管道）

        @param {str} predef_name - 预定义模块名，如果是使用run执行的，可以传''
        @param {str} run_id - 执行id，优先用这个获取run执行的配置

        @returns {str, int} - 当前节点信息 predef_name, node_id
        """
        _pipeline: Pipeline = None
        # 优先使用run_id获取
        _pipeline = self.robot_info['run_pipeline'].get(run_id, None)

        if _pipeline is None:
            _pipeline = self.robot_info['predef_pipeline'][predef_name]

        _predef_name = _pipeline.name
        _node_id = _pipeline.current_node_id(run_id=run_id)

        return _predef_name, int(_node_id)

    def current_status(self, predef_name: str, run_id: str) -> str:
        """
        获取当前节点运行状态

        @param {str} predef_name - 预定义模块名，如果是使用run执行的，可以传''
        @param {str} run_id - 执行id，优先用这个获取run执行的配置

        @returns {str} - 运行状态
        """
        _pipeline: Pipeline = None
        # 优先使用run_id获取
        _pipeline = self.robot_info['run_pipeline'].get(run_id, None)

        if _pipeline is None:
            _pipeline = self.robot_info['predef_pipeline'][predef_name]

        return _pipeline.current_node_status(run_id=run_id)

    def current_status_msg(self, predef_name: str, run_id: str) -> str:
        """
        获取当前节点运行状态说明

        @param {str} predef_name - 预定义模块名，如果是使用run执行的，可以传''
        @param {str} run_id - 执行id，优先用这个获取run执行的配置

        @returns {str} - 状态说明
        """
        _pipeline: Pipeline = None
        # 优先使用run_id获取
        _pipeline = self.robot_info['run_pipeline'].get(run_id, None)

        if _pipeline is None:
            _pipeline = self.robot_info['predef_pipeline'][predef_name]

        return _pipeline.current_node_status_msg(run_id=run_id)

    def last_status_msg(self, predef_name: str, run_id: str) -> list:
        """
        获取上一步执行的状态和处理结果清单

        @param {str} predef_name - 预定义模块名，如果是使用run执行的，可以传''
        @param {str} run_id - 执行id，优先用这个获取run执行的配置

        @returns {list} - [(predef_name, node_id, status, status_msg),]
        """
        _list = list()
        _pipeline: Pipeline = None
        # 优先使用run_id获取
        _pipeline = self.robot_info['run_pipeline'].get(run_id, None)

        if _pipeline is None:
            _pipeline = self.robot_info['predef_pipeline'][predef_name]

        _trace_list = _pipeline.trace_list(run_id=run_id)
        _predef_name = _pipeline.name
        while len(_trace_list) > 0:
            _last_node = _trace_list[len(_trace_list) - 1]
            if not _last_node['is_sub_pipeline'] or _last_node['status'] in ('S', 'E'):
                # 没有执行子管道或为终态的情况，把自己加入状态中
                _list.insert(0, (
                    _predef_name, int(_last_node['node_id']),
                    _last_node['status'], _last_node['status_msg']
                ))

            if _last_node['is_sub_pipeline']:
                # 有子管道的情况
                _predef_name = _last_node['sub_name']
                _trace_list = _last_node['sub_trace_list']
            else:
                # 退出循环
                break

        # 返回结果
        return _list

    #############################
    # 构造函数
    #############################

    def __init__(self, robot_id: str = None, use_action_types=None, ignore_version=False, init_modules: list = None,
                 init_class: list = None, init_action_path: str = None,
                 running_notify_fun=None, end_running_notify_fun=None,
                 system=None, release=None,
                 logger: Logger = None, **kwargs):
        """
        构造函数（创建一个机器人）
        注：初始化机器人前可以先通过 RunEnvironment.init 装载公用的动作插件

        @param {str} robot_id=None - 机器人id，如果不送则自动生成id
        @param {list} use_action_types=None - 允许使用的动作类型列表及查找顺序，None代表全部动作类型均支持，使用默认顺序
        @param {bool} ignore_version=False - 是否忽略执行函数查找的操作系统版本检查
        @param {list} init_modules=None - 要初始化的插件模块清单
        @param {list} init_class=None - 要初始化的插件类清单
        @param {str} init_action_path=None - 要加载的动作模块路径
        @param {function} running_notify_fun=None = 节点运行通知函数，格式如下：
            fun(robot, run_id, predef_name, node_id, step_id)
                robot {Robot} - 机器人实例对象
                run_id {str} - 运行id
                predef_name {str} - 预定义模块名
                node_id {int} - 在配置中的步骤顺序(从1开始)
                step_id {str} - 步骤标识名
        @param {function} end_running_notify_fun=None = 节点运行完成通知函数，格式如下：
            fun(robot, run_id, predef_name, node_id, step_id, status, status_msg)
                robot {Robot} - 机器人实例对象
                run_id {str} - 运行id
                predef_name {str} - 预定义模块名
                node_id {int} - 在配置中的步骤顺序(从1开始)
                step_id {str} - 步骤标识名
                status {str} 执行状态，'S' - 成功，'E' - 出现异常
                status_msg {str} 状态描述，当异常时送入异常信息
        @param {str} system=None - 支持外部传入系统类型（针对移动端应用测试需要在PC执行脚本的情况）
        @param {str} release=None - 当传入system时使用
        @param {Logger} logger=None - 日志对象
        """
        self.robot_id = robot_id
        if robot_id is None:
            self.robot_id = str(uuid.uuid1())

        # 执行初始化，导入机器人自有路由
        RunEnvironment.init(
            init_modules=init_modules, init_class=init_class, init_action_path=init_action_path,
            robot_id=self.robot_id
        )

        # 内部变量初始化
        if system is None:
            self.system, self.release = RunEnvironment.get_platform()  # 平台信息
        else:
            self.system = system
            self.release = release

        self._ACTION_ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        self._ROBOT_INFOS = RunTool.get_global_var('ROBOT_INFOS')

        # 找到的函数缓存，提升效率, key为action_name, value为最后一次找到的动作配置字典
        self._action_cache = dict()
        self.ignore_version = ignore_version

        # 通知函数
        self.running_notify_fun = running_notify_fun
        self.end_running_notify_fun = end_running_notify_fun

        # 日志对象
        self.logger = logger

        # 机器人信息
        self.robot_info = {
            'robot': self,
            'id': self.robot_id,
            'use_action_types': use_action_types,
            'predef_pipeline': dict(),
            'predef_config': dict(),
            'run_pipeline': dict(),
            'run_config': dict(),
            'vars': {
                '*': {},  # 全局运行变量
            }
        }

        # 加入全局变量
        self._ROBOT_INFOS[self.robot_id] = self.robot_info

    #############################
    # 析构函数
    #############################
    def __del__(self):
        """
        析构函数，删除对象时处理全局变量的删除
        """
        _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
        _ROBOT_SELF_ROUTERS.pop(self.robot_id, None)

        _ROBOT_INFOS = RunTool.get_global_var('ROBOT_INFOS')
        _ROBOT_INFOS.pop(self.robot_id, None)

    #############################
    # 公共函数 - 动作处理
    #############################
    def call_action(self, action_name: str, instance_obj: object = None, run_id: str = None, call_para_args: list = None,
                    call_para_kwargs: dict = None, save_to_var: str = None, save_run_id: str = '*', **kwargs):
        """
        调用动作

        @param {str} action_name - 动作名(不区分大小写)
        @param {object} instance_obj=None - 对于实例化对象，传入要执行的实例化对象
        @param {str} run_id=None - 运行id
        @param {list} call_para_args=None - 对于要传入固定位置参数的情况，传入固定参数值列表，格式为：
            [arg1, arg2, arg3, ...]
            注：如果需要设置函数值，请在该参数的第一个送入要设置的值
        @param {dict} call_para_kwargs=None - 对于要传入key-value形式的值，传入字典，格式为:
                {'key1' : value1, 'key2':value2, ...}
        @param {str} save_to_var - 执行结果保存到指定变量中, None代表直接函数中返回
        @param {str} save_run_id='*' - 指定运行id（通过运行id可以区分存储变量的使用范围），如果不传默认使用全局运行id '*'

        @returns {object} - 返回执行结果
        """
        # 获取函数
        _action_dict = None
        _action_name = action_name.upper()
        if _action_name in self._action_cache.keys():
            _action_dict = self._action_cache[_action_name]
        else:
            _action_dict = RunEnvironment.get_match_action(
                _action_name, robot_id=self.robot_id,
                use_action_types=self.robot_info['use_action_types'],
                ignore_version=self.ignore_version,
                system=self.system, release=self.release
            )
            # 存入缓存
            self._action_cache[_action_name] = _action_dict

        # 调用函数
        _fun = _action_dict['fun']
        _result = None
        if call_para_args is None and call_para_kwargs is None:
            if instance_obj is not None and _action_dict['instance_class'] != '':
                _result = _fun(self.robot_info, _action_name, run_id, instance_obj)
            else:
                _result = _fun(self.robot_info, _action_name, run_id)
        else:
            # 准备传入参数
            _call_para = [
                [] if call_para_args is None else call_para_args,
                {} if call_para_kwargs is None else call_para_kwargs
            ]
            if instance_obj is not None and _action_dict['instance_class'] != '':
                _result = _fun(
                    self.robot_info, _action_name, run_id, instance_obj,
                    *_call_para[0], **_call_para[1]
                )
            else:
                _result = _fun(self.robot_info, _action_name, run_id,
                               *_call_para[0], **_call_para[1])

        # 保存或返回
        if save_to_var is not None:
            if save_run_id not in self.robot_info['vars'].keys():
                self.robot_info['vars'][save_run_id] = dict()

            self.robot_info['vars'][save_run_id][save_to_var] = _result

        return _result

    #############################
    # 公共函数 - 脚本处理
    #############################
    def run_predef(self, predef_name: str, run_id: str = None, context: dict = None, is_step_by_step: bool = False):
        """
        运行预定义模块

        @param {str} predef_name - 预定义模块名
        @param {str} run_id=None - 运行id
        @param {dict} context=None - 嵌套执行时传入上一个步骤的context
        @param {bool} is_step_by_step=Fasle - 是否逐步执行模式

        @returns {str, str, object} - 返回 run_id, status, output
        """
        _pipeline: Pipeline = self.robot_info['predef_pipeline'].get(predef_name, None)
        if _pipeline is None:
            raise RuntimeError('Predef name not exists [%s]!' % predef_name)

        _run_id = run_id if run_id is not None else str(uuid.uuid1())
        _input_data = {
            'robot': self,
            'last_result': None
        }
        _context = context if context is not None else {}

        # 执行管道
        return _pipeline.start(
            input_data=_input_data, context=_context, run_id=_run_id, is_step_by_step=is_step_by_step
        )

    def pause_predef(self, predef_name: str, run_id: str):
        """
        暂停执行预定义模块

        @param {str} predef_name - 预定义模块名
        @param {str} run_id - 运行id
        """
        _pipeline: Pipeline = self.robot_info['predef_pipeline'].get(predef_name, None)
        if _pipeline is None:
            raise RuntimeError('Predef name not exists [%s]!' % predef_name)

        _pipeline.pause(run_id=run_id)

    def resume_predef(self, predef_name: str, run_id: str, run_to_end: bool = False):
        """
        恢复预定义模块执行

        @param {str} predef_name - 预定义模块名
        @param {str} run_id - 运行id
        @param {bool} run_to_end=False - 当设置了step_by_step模式时，可以通过该参数指定执行到结尾

        @returns {str, str, object} - 同步情况返回 run_id, status, output，异步情况返回的status为R
        """
        _pipeline: Pipeline = self.robot_info['predef_pipeline'].get(predef_name, None)
        if _pipeline is None:
            raise RuntimeError('Predef name not exists [%s]!' % predef_name)

        # 恢复管道执行
        return _pipeline.resume(run_id=run_id, run_to_end=run_to_end)

    def run(self, config: dict, run_id: str = None, input_data: object = None, context: dict = None):
        """
        按步骤配置运行机器人
        （一次性执行，不支持重跑，推荐使用run_predef）

        @param {dict} config - 机器人执行步骤JSON配置字典
        @param {str} run_id=None - 运行id, 嵌套执行时传入上一个步骤的run_id
        @param {object} input_data=None - 嵌套执行时传入上一个步骤的output
        @param {dict} context=None - 嵌套执行时传入上一个步骤的context

        @returns {str, str, object} - 返回 run_id, status, output
        """
        # 准备运行参数
        _run_id = run_id if run_id is not None else str(uuid.uuid1())
        _input_data = input_data
        if _input_data is None:
            _input_data = {
                'robot': self,
                'last_result': None
            }
        _context = context if context is not None else {}

        # 生成管道对象
        _pipeline_config = self.json_to_pipeline_config(config)
        _pipeline = Pipeline(
            config['predef_name'], _pipeline_config,
            running_notify_fun=None if self.running_notify_fun is None else self._running_notify_fun,
            end_running_notify_fun=None if self.end_running_notify_fun is None else self._end_running_notify_fun,
            logger=self.logger
        )

        # 添加执行临时信息
        self.robot_info['run_pipeline'][_run_id] = _pipeline
        self.robot_info['run_config'][_run_id] = copy.deepcopy(config)

        try:
            return _pipeline.start(
                input_data=_input_data, context=_context, run_id=_run_id
            )
        finally:
            # 移除执行临时信息
            self.robot_info['run_pipeline'].pop(_run_id, None)
            self.robot_info['run_config'].pop(_run_id, None)

    #############################
    # 私有函数
    #############################
    def _running_notify_fun(self, name: str, run_id: str, node_id: str, node_name: str, pipeline: Pipeline):
        """
        节点执行开始的管道通知函数，将管道执行信息转换为机器人执行步骤的执行信息

        @param name {str} - 管道名称
        @param run_id {str} - 运行id
        @param node_id {str} - 运行节点id
        @param node_name {str} - 运行节点配置名
        @param pipeline {Pipeline} - 管道对象
        """
        if callable(self.running_notify_fun):
            # robot, run_id, predef_name, node_id, step_id
            self.running_notify_fun(
                self, run_id, name, int(node_id), node_name
            )

    def _end_running_notify_fun(self, name: str, run_id: str, node_id: str, node_name: str,
                                status: str, status_msg: str, pipeline: Pipeline):
        """
        节点执行结束的管道通知函数，将管道执行信息转换为机器人执行步骤的执行信息

        @param name {str} - 管道名称
        @param run_id {str} - 运行id
        @param node_id {str} - 运行节点id
        @param node_name {str} - 运行节点配置名
        @param {str} status - 执行状态，'S' - 成功，'E' - 出现异常
        @param {str} status_msg - 状态描述，当异常时送入异常信息
        @param pipeline {Pipeline} - 管道对象
        """
        if callable(self.end_running_notify_fun):
            # fun(robot, run_id, predef_name, node_id, step_id, status, status_msg)
            self.end_running_notify_fun(
                self, run_id, name, int(node_id), node_name, status, status_msg
            )


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    _json_config = {
        "predef_name": "预定义模板名",
        "steps": [
            {
                "step_id": "",
                "cmd": "run",
                "action_name": "a1",
                "instance_obj": "",
                "exception_to": "",
                "goto_step_id": "",
                "condition": "",
            },
            {
                "step_id": "",
                "cmd": "if",
                "action_name": "a2",
                "condition": "{$local=run_action$} > 0",
            },
            {
                "step_id": "",
                "cmd": "run",
                "action_name": "a3",
            },
            {
                "step_id": "",
                "cmd": "run",
                "action_name": "a4",
            },
            {
                "step_id": "",
                "cmd": "else",
            },
            {
                "step_id": "",
                "cmd": "run",
                "action_name": "a5",
            },
            {
                "step_id": "",
                "cmd": "run",
                "action_name": "a6",
            },
            {
                "step_id": "",
                "cmd": "loop",
                "action_name": "a7",
                "condition": "{$local=run_action$} > 0",
            },
            {
                "step_id": "",
                "cmd": "run",
                "action_name": "a8",
            },
            {
                "step_id": "",
                "cmd": "continue",
            },
            {
                "step_id": "",
                "cmd": "break",
            },
            {
                "step_id": "",
                "cmd": "endloop",
            },
            {
                "step_id": "",
                "cmd": "run",
                "action_name": "a9",
            },
            {
                "step_id": "",
                "cmd": "endif",
            },
            {
                "step_id": "",
                "cmd": "null",
            },
        ]
    }

    _pipeline_config = Robot.json_to_pipeline_config(_json_config)
    _str = json.dumps(_pipeline_config, ensure_ascii=False, indent=4)

    print(_str)
