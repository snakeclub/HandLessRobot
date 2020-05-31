#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
动作模块基础框架
@module base_action
@file base_action.py
"""

import os
import sys
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.actions.generate_tool import ActionCodeTool


__MOUDLE__ = 'base_action'  # 模块名
__DESCRIPT__ = u'动作模块基础框架'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.05.21'  # 发布日期


class BaseAction(object):
    """
    动作模块基础框架类

    动作模块的应用机制如下：
        1、机器人控制台启动时加载所有动作模块（包含系统默认模块及私有模块）；
        2、查找每个动作模块内部继BaseAction的动作类，将其信息导入全局变量ACTION_ROUTERS中
        3、机器人执行开始时会设置一个全局变量ROBOT_INFOS，登记机器人执行过程中的信息
    """
    @classmethod
    def support_action_types(cls) -> list:
        """
        返回支持的动作类别列表(主要基于列表区分不同平台及技术兼容的动作)
        (需继承并实现该函数)

        @returns {list} - 支持的动作类别列表，例如：
            ['*'] - 代表支持所有分类
            ['win32', 'winuia'] - 代表支持win32和winuia两种分类使用
        """
        raise NotImplementedError()

    @classmethod
    def support_platform(cls) -> dict:
        """
        返回支持的平台字典
        (用于自动生成路由表，默认支持全平台全版本，如需要指定需修改该函数返回值)

        @returns {dict} - 支持的平台字典，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        """
        return {'*': None}

    @classmethod
    def get_action_router(cls) -> dict:
        """
        获取动作函数路由表
        (如果需要自定义路由表的生成逻辑，请继承并修改该函数)

        @returns {dict} - 返回定义该类中的动作路由表，路由表定义如下：
            {
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
            }
        """
        # 类自身函数
        _action_router = ActionCodeTool.get_action_router_by_class(
            cls, platform=cls.support_platform()
        )

        # 函数映射字典
        _temp_router = ActionCodeTool.get_action_router_by_fun_dict(
            cls.get_common_fun_dict(), call_fun_obj=cls.common_fun,
            platform=cls.support_platform()
        )
        _action_router.update(_temp_router)

        # 实例对象属性及函数映射字典
        _temp_router = ActionCodeTool.get_action_router_by_attr_dict(
            cls.get_common_attr_dict(), call_fun_obj=cls.common_attr_call,
            platform=cls.support_platform()
        )
        _action_router.update(_temp_router)

        return _action_router

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

    @classmethod
    def common_fun(cls, robot_info: dict, action_name: str, *args, **kwargs):
        """
        通用调用函数

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        """
        _action_name = action_name.upper()
        _fun_dict = cls.get_common_fun_dict()
        if _action_name not in _fun_dict.keys():
            raise NotImplementedError('Action name [%s] not found' % action_name)

        return _fun_dict[_action_name](*args, **kwargs)

    #############################
    # 实例对象属性及方法的通用映射
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
        return {}

    @classmethod
    def common_attr_call(cls, robot_info: dict, action_name: str, instance_obj: object, *args, **kwargs):
        """
        通用实例对象内部方法及属性执行函数
        注：不支持通过该方法设置属性值

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {object} instance_obj - 要执行的实例对象
        """
        _action_name = action_name.upper()
        _attr_dict = cls.get_common_attr_dict()
        if _action_name not in _attr_dict.keys():
            raise NotImplementedError('Attr name [%s] not found' % action_name)

        _attr = getattr(instance_obj, _attr_dict[_action_name][0])
        if _attr is None:
            raise AttributeError('Instance has not attribute [%s]' % _attr_dict[_action_name][0])

        if callable(_attr):
            # 执行函数
            return _attr(*args, **kwargs)
        else:
            # 直接返回属性值
            return _attr


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
