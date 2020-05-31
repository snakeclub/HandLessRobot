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
import copy
import uuid
import platform
import inspect
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.base_tools.import_tool import ImportTool
from HiveNetLib.base_tools.file_tool import FileTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import HandLessRobot.lib.actions.common_action as common_action
import HandLessRobot.lib.actions.windows_action as windows_action
from HandLessRobot.lib.actions.base_action import BaseAction


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
                name - 动作中文名
                desc - 动作详细说明
                param - 帮助信息，用于在帮助中展示该函数的入参说明，其中default_value是默认值，如果无默认值该项应为None
                returns - 帮助信息，用于在帮助中展示该函数的返回值说明
        (3)执行一个Action_Name会优先匹配'*'，然后再根据机器人执行时的当前动作类别action_type从对应的路由表查找。

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
                'vars': {
                    'var_name': var_value,
                    'var_name': var_value,
                    ...
                }
            },
            ...
        }
        说明如下：
        robot_id - 是机器人执行开始时生成的唯一ID，标识工作机器人;
        action_type - 登记当前动作类别action_type
        use_action_types - 登记机器人允许使用的动作类别，同时也会按这个顺序进行查找('*'可以不列进去，总是第一个查找)
        vars - 登记机器人执行过程中的临时变量

    IMPORTED_MODULE - 用于记录已经导入的模块清单
        {
            '*': ['moudle_real_path', ...],
            'robot_id': ['moudle_real_path', ...],
            ...
        }

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
    def check_platform_matched(cls, platform_setting: dict, ignore_version: bool = False) -> bool:
        """
        检查当前操作系统是否与配置匹配

        @param {dict} platform_setting - 配置字典
            key {str} - 支持的平台名称(例如Windows、Linux), 可通过'platform.system()'获取, '*'代表全平台支持,
            value {tuple} - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        @param {bool} ignore_version=False - 是否忽略版本检查

        @returns {bool} - 返回匹配结果
        """
        if '*' in platform_setting.keys():
            # 全版本支持, 无需再检查
            return True

        _system, _release = cls.get_platform()  # 平台信息
        if _system not in platform_setting.keys():
            # 没有找到操作系统
            return False

        if platform_setting[_system] is not None:
            # 有限定版本
            if not ignore_version and _release not in platform_setting[_system]:
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
    def init(cls, private_action_path: str = None, **kwargs):
        """
        初始化机器人运行环境

        @param {str} private_action_path=None - 要加载的私有动作模块路径
        """
        # 初始化全局变量
        _ACTION_ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        if _ACTION_ROUTERS is None:
            _ACTION_ROUTERS = {'*': {}}
            RunTool.set_global_var('ACTION_ROUTERS', _ACTION_ROUTERS)

        _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
        if _ROBOT_SELF_ROUTERS is None:
            _ROBOT_SELF_ROUTERS = dict()
            RunTool.set_global_var('ROBOT_SELF_ROUTERS', _ROBOT_SELF_ROUTERS)

        _ROBOT_INFOS = RunTool.get_global_var('ROBOT_INFOS')
        if _ROBOT_INFOS is None:
            _ROBOT_INFOS = dict()
            RunTool.set_global_var('ROBOT_INFOS', _ROBOT_INFOS)

        _IMPORTED_MODULE = RunTool.get_global_var('IMPORTED_MODULE')
        if _IMPORTED_MODULE is None:
            # 已加载的模块清单
            _IMPORTED_MODULE = {'*': []}
            RunTool.set_global_var('IMPORTED_MODULE', _IMPORTED_MODULE)

        # 加载动作模块
        if len(_ACTION_ROUTERS['*']) == 0:
            # 加载默认模块
            cls._add_action_router_by_module(common_action, robot_id=None)
            cls._add_action_router_by_module(windows_action, robot_id=None)

            # 加载私有模块
            if private_action_path is not None:
                cls.load_action_module_by_dir(private_action_path, robot_id=None)

    @classmethod
    def load_action_module(cls, module_file: str, robot_id: str = None):
        """
        加载动作模块文件

        @param {str} module_file - 要加载的动作模块文件
        @param {str} robot_id=None - 机器人id，如果有传值代表导入对应机器人实例自有路由中
        """
        # 检查环境是否已加载
        cls._check_inited_raise()

        _import_id = '*'
        if robot_id is not None:
            _import_id = robot_id

        _IMPORTED_MODULE = RunTool.get_global_var('IMPORTED_MODULE')
        _real_path = os.path.realpath(module_file)
        if _import_id in _IMPORTED_MODULE.keys() and _real_path.upper() in _IMPORTED_MODULE[_import_id]:
            # 已经加载过，无需再处理
            return

        # 加载模块并导入路由信息
        _path, _file = os.path.split(_real_path)
        _module = ImportTool.import_module(_file[0: -3], extend_path=_path, is_force=True)
        cls._add_action_router_by_module(_module, robot_id=robot_id)

        # 将模块加入已加载清单
        if _import_id not in _IMPORTED_MODULE.keys():
            _IMPORTED_MODULE[_import_id] = list()

        _IMPORTED_MODULE[_import_id].append(_real_path.upper())

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
    def get_match_action_fun(cls, action_name: str, robot_id: str = None, use_action_types: list = None,
                             ignore_version: bool = False, **kwargs):
        """
        从路由表获取适用的动作函数对象

        @param {str} action_name - 动作名(不区分大小写)
        @param {str} robot_id=None - 机器人id，如果有传值代表优先从对应机器人实例自有路由中查找
        @param {list} use_action_types=None - 允许使用的动作类别清单顺序
        @param {bool} ignore_version=False - 是否忽略版本检查

        @returns {function} - 返回找到的函数对象

        @throws {ModuleNotFoundError} - 找不到抛出异常
        """
        _ACTION_ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        _action_name = action_name.upper()
        _fun = None

        # 优先从机器人自有路由中查找
        if robot_id is not None:
            _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
            if robot_id in _ROBOT_SELF_ROUTERS.keys():
                _ROUTERS = _ROBOT_SELF_ROUTERS[robot_id]
                for _action_type in _ROUTERS.keys():
                    if _action_name in _ACTION_ROUTERS[_action_type].keys():
                        if cls.check_platform_matched(
                            _ROUTERS[_action_type][_action_name]['platform'],
                            ignore_version=ignore_version
                        ):
                            # 名称及操作系统都支持，已找到函数
                            _fun = _ROUTERS[_action_type][_action_name]['fun']
                            break

        if _fun is not None:
            return _fun

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
                    ignore_version=ignore_version
                ):
                    # 名称及操作系统都支持，已找到函数
                    _fun = _ACTION_ROUTERS[_action_type][_action_name]['fun']
                    break

        if _fun is None:
            # 没有找到函数，抛出异常
            raise ModuleNotFoundError(
                'Action name [{0}] not found in action_router!'.format(action_name))
        else:
            return _fun

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
            cls._add_action_router_by_class(_class)

    @classmethod
    def _add_action_router_by_class(cls, class_object, robot_id: str = None):
        """
        通过类导入动作类型路由

        @param {object} class_object - 要导入的类对象
        @param {str} robot_id=None - 机器人id，如果有传值代表导入对应机器人实例自有路由中
        """
        _ROUTERS = None
        if robot_id is None:
            _ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        else:
            _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
            if robot_id not in _ROBOT_SELF_ROUTERS.keys():
                _ROBOT_SELF_ROUTERS[robot_id] = {'*': dict()}
            _ROUTERS = _ROBOT_SELF_ROUTERS[robot_id]

        _class_router = class_object.get_action_router()
        _support_types = class_object.support_action_types()

        for _action_name in _class_router.keys():
            # 逐个动作处理
            _upper_name = _action_name.upper()
            for _type in _support_types:
                if _type not in _ROUTERS.keys():
                    # 添加新的类型
                    _ROUTERS[_type] = dict()

                # 在指定类型下添加路由
                _ROUTERS[_type][_upper_name] = _class_router[_action_name]

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
    def run_script(cls, script: str):
        """
        运行脚本

        @param {str} script - 要执行的脚本(python)
        """
        pass

    @classmethod
    def run_config(cls, config_file: str):
        """
        执行动作配置

        @param {str} config_file - xml配置形式的执行配置
        """
        pass

    @classmethod
    def run_module(cls, module_name: str, extend_path=None, call_name=None):
        """
        执行模块

        @param {string} module_name - 要导入的模块名
        @param {string} extend_path=None - 对于存放在非python搜索路径（sys.path）外的模块，需要指定扩展搜索路径
        @param {str} call_name=None - 调用名(用于确认调用模块中的哪个类)
        """
        pass

    #############################
    # 构造函数
    #############################
    def __init__(self, use_action_types=None, ignore_version=False, robot_action_path: str = None, **kwargs):
        """
        构造函数（创建一个机器人）

        @param {list} use_action_types=None - 允许使用的动作类型列表及查找顺序，None代表全部动作类型均支持，使用默认顺序
        @param {bool} ignore_version=False - 是否忽略执行函数查找的操作系统版本检查
        @param {str} robot_action_path=None - 要加载的机器人自有动作模块路径

        """
        # 检查是否已经初始化，如果没有则自动执行初始化
        if not RunEnvironment.check_inited():
            RunEnvironment.init()

        # 内部变量初始化
        self.os_system, self.os_release = RunEnvironment.get_platform()  # 平台信息
        self._ACTION_ROUTERS = RunTool.get_global_var('ACTION_ROUTERS')
        self._ROBOT_INFOS = RunTool.get_global_var('ROBOT_INFOS')

        # 找到的函数缓存，提升效率, key为action_name, value为最后一次找到的函数对象
        self._action_cache = dict()
        self.ignore_version = ignore_version

        # 机器人信息
        self.robot_info = {
            'robot': self,
            'id': str(uuid.uuid1()),
            'use_action_types': use_action_types,
            'vars': {}
        }
        # 加入全局变量
        self._ROBOT_INFOS[self.robot_info['id']] = self.robot_info

        # 加载机器人自有动作模块
        if robot_action_path is not None:
            RunEnvironment.load_action_module_by_dir(
                robot_action_path, robot_id=self.robot_info['id'])

    #############################
    # 析构函数
    #############################
    def __del__(self):
        """
        析构函数，删除对象时处理全局变量的删除
        """
        _id = self.robot_info['id']
        _ROBOT_SELF_ROUTERS = RunTool.get_global_var('ROBOT_SELF_ROUTERS')
        if _id in _ROBOT_SELF_ROUTERS.keys():
            _ROBOT_SELF_ROUTERS.pop(_id)

        _ROBOT_INFOS = RunTool.get_global_var('ROBOT_INFOS')
        if _id in _ROBOT_INFOS.keys():
            _ROBOT_INFOS.pop(_id)

        _IMPORTED_MODULE = RunTool.get_global_var('IMPORTED_MODULE')
        if _id in _IMPORTED_MODULE.keys():
            _IMPORTED_MODULE.pop(_id)

    #############################
    # 公共函数 - 动作处理
    #############################
    def call_action(self, action_name: str, call_para: list = None, save_to_var: str = None, **kwargs):
        """
        调用动作

        @param {str} action_name - 动作名(不区分大小写)
        @param {list} call_para=None - 执行参数，格式为:
            [
                [arg1, arg2, arg3, ...],
                {'key1' : value1, 'key2':value2, ...}
            ]
        @param {str} save_to_var - 执行结果保存到指定变量中, None代表直接函数中返回

        @returns {object} - 返回执行结果, 如果存储到变量中则返回None
        """
        # 获取函数
        _fun = None
        _action_name = action_name.upper()
        if _action_name in self._action_cache.keys():
            _fun = self._action_cache[_action_name]
        else:
            _fun = RunEnvironment.get_match_action_fun(
                _action_name, robot_id=self.robot_info['id'],
                use_action_types=self.robot_info['use_action_types'],
                ignore_version=self.ignore_version
            )
            # 存入缓存
            self._action_cache[_action_name] = _fun

        # 调用函数
        _result = None
        if call_para is None:
            _result = _fun(self.robot_info, _action_name)
        else:
            _result = _fun(self.robot_info, _action_name, *call_para[0], **call_para[1])

        # 保存或返回
        if save_to_var is None:
            return _result
        else:
            self.robot_info['vars'][save_to_var] = _result
            return None

    #############################
    # 公共函数 - 预定义处理
    #############################

    def import_run_script(self, call_name: str, script: str, supports={'*': None}):
        """
        装载预定义执行脚本

        @param {str} call_name - 调用名(不可重复)
        @param {str} script - 要执行的脚本(python)
        @param {dict} supports={'*': '*'} - 支持执行的平台清单
            key {str} - 支持的平台名称(例如Windows、Linux), 可通过'platform.system()'获取, '*'代表全平台支持,
            value {tuple} - 支持的版本清单, 例如('7', '10', 'nt') ,None代表全版本支持
        """
        pass

    def import_run_config(self, call_name: str, config_file: str, supports={'*': None}):
        """
        装载预定义执行动作配置

        @param {str} call_name - 调用名(不可重复)
        @param {str} config_file - xml配置形式的执行配置
        @param {dict} supports={'*': None} - 支持执行的平台清单
            key {str} - 支持的平台名称(例如Windows、Linux), 可通过'platform.system()'获取, '*'代表全平台支持,
            value {tuple} - 支持的版本清单, 例如('7', '10', 'nt') ,None代表全版本支持
        """
        pass

    def import_run_module(self, module_name: str, extend_path=None):
        """
        装载预定义执行模块
        (装载模块内继承PreDefinedModuleClass的类实例对象)

        @param {string} module_name - 要导入的模块名
        @param {string} extend_path=None - 对于存放在非python搜索路径（sys.path）外的模块，需要指定扩展搜索路径
        """
        pass

    def unimport_run_predef(self, callname: str):
        """
        取消预定义执行模块的加载

        @param {str} callname - 要卸载的调用名
        """
        pass

    #############################
    # 公共函数 - 执行
    #############################
    def run_predef(self, call_name: str, ignore_supports=False):
        """
        执行预定义对象

        @param {str} call_name - 要访问的预定义调用名
        @param {bool} ignore_supports=False - 是否忽略平台支持检查
        """
        pass


class PreDefinedModuleClass(object):
    """
    预定义模块的框架
    """
    #############################
    # 构造函数
    #############################

    def __init__(self):
        """
        构造函数
        """
        pass

    #############################
    # 公共函数
    #############################
    def get_call_name(self):
        """
        获取调用名

        @retrun {str} - 调用名
        """
        raise NotImplementedError()

    def get_supports(self):
        """
        获取模块的平台支持参数

        @returns {dict} - 支持执行的平台清单
            key {str} - 支持的平台名称(例如Windows、Linux), 可通过'platform.system()'获取, '*'代表全平台支持,
            value {tuple} - 支持的版本清单, 例如('7', '10', 'nt') ,None代表全版本支持
        """
        raise NotImplementedError()

    def run(self):
        """
        执行操作
        """
        raise NotImplementedError()


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    def a(x, y):
        print(x, y)

    b = (1, 2)
    c = {}
    a(*b, **c)
