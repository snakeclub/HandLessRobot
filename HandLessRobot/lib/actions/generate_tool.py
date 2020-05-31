#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
action代码生成工具
@module generate_tool
@file generate_tool.py
"""

import os
import sys
import re
import json
import inspect
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))


__MOUDLE__ = 'generate_tool'  # 模块名
__DESCRIPT__ = u'action代码生成工具'  # 模块描述
__VERSION__ = '{$VERSION$}'  # 版本
__AUTHOR__ = u'{$AUTHOR$}'  # 作者
__PUBLISH__ = '2020.05.25'  # 发布日期


class ActionCodeTool(object):
    """
    动作代码生成工具
    """

    @classmethod
    def get_action_router_by_function(cls, fun_obj, call_fun_obj=None,
                                      action_name: str = None, fun_pre_fix: str = None,
                                      platform: dict = {'*': None},
                                      standards: str = 'SnakerPy', to_json: bool = False,
                                      para_default_none_to_str: str = None,
                                      is_common_attr_call=False):
        """
        根据指定函数返回对应的动作路由(Action Router)字典

        @param {function} fun_obj - 调用函数
        @param {function} call_fun_obj=None - 路由表中执行的函数对象，如果不为None则传入该对象进路由字典(适配common_fun的使用)
        @param {str} action_name=None - 动作名, 如果不传代表和函数名相同
        @param {str} fun_pre_fix=None - 函数名前缀, 如果为None时字典里为函数对象(function)；如果需要转换为函数名字符串，可以设置为''
            也可以设置为前置字符串，例如'cls.'，这样将会在函数名字符串前增加前缀
        @param {dict} platform={'*': None} - 支持的平台参数，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        @param {str} standards='SnakerPy' - 注释规范类型
        @param {bool} to_json=False - 是否返回json字符串
        @param {str} para_default_none_to_str=None - 将参数默认值为None的情况转换为指定字符串
        @param {bool} is_common_attr_call=False - 是否通用实例方法及属性调用，如果是则需要在入参中增加配置信息

        @returns {dict} - 返回生成的动作路由(Action Router)字典，如果to_json为True则返回json字符串
        """
        # 解析doc string
        _doc = fun_obj.__doc__
        _doc_dict = cls._analysis_doc_string(_doc, standards=standards)

        # 处理一些参数
        _action_name = action_name
        if _action_name is None:
            _action_name = fun_obj.__name__
        _action_name = _action_name.upper()

        _fun = fun_obj if fun_pre_fix is None else '%s%s' % (fun_pre_fix, fun_obj.__name__)
        if call_fun_obj is not None:
            _fun = call_fun_obj if fun_pre_fix is None else '%s%s' % (
                fun_pre_fix, call_fun_obj.__name__)

        # 通用实例方法及属性的处理
        if is_common_attr_call:
            _doc_dict['param'].insert(1, ['instance_obj', 'object', None, '要执行的实例对象'])

        # 组成字典代码
        _action_router = {
            _action_name: {
                'fun': _fun,
                'platform': platform,
                'name': _doc_dict['title'],
                'desc': _doc_dict['descript'],
                'param': _doc_dict['param'],
                'returns': None if len(_doc_dict['returns']) == 0 else _doc_dict['returns']
            },
        }

        # 处理param中的默认值
        if to_json or para_default_none_to_str is not None:
            # 平台
            for _key in _action_router[_action_name]['platform'].keys():
                if _action_router[_action_name]['platform'][_key] is None:
                    _action_router[_action_name]['platform'][_key] = '{$=None$}'

            # 参数值
            for _param in _action_router[_action_name]['param']:
                if _param[2] is None:
                    if para_default_none_to_str is not None:
                        _param[2] = para_default_none_to_str
                    else:
                        _param[2] = '{$=None$}'

            # 返回值
            if _action_router[_action_name]['returns'] is None:
                _action_router[_action_name]['returns'] = '{$=None$}'

        # 返回结果
        if to_json:
            if type(_action_router[_action_name]['fun']) == str:
                # 转换后要将函数名替换为没有引号的模式
                _action_router[_action_name]['fun'] = '{$fun=%s$}' % _action_router[_action_name]['fun']

            _json = json.dumps(_action_router, ensure_ascii=False, indent=4)

            if para_default_none_to_str is None:
                _json = _json.replace('"{$=None$}"', 'None')

            if type(_action_router[_action_name]['fun']) == str:
                _json = re.sub(r'\"\{\$fun\=.*?\$\}\"', lambda m: m.group(0)[7: -3], _json)

            return _json
        else:
            return _action_router

    @classmethod
    def get_action_router_by_class(cls, class_obj, fun_pre_fix: str = None,
                                   platform: dict = {'*': None},
                                   standards: str = 'SnakerPy', to_json: bool = False,
                                   para_default_none_to_str: str = None,
                                   igonre_base_action_fun=True):
        """
        根据指定类返回对应的动作路由(Action Router)字典

        @param {object} class_obj - 类对象
        @param {function} fun_obj - 调用函数
        @param {str} fun_pre_fix=None - 函数名前缀, 如果为None时字典里为函数对象(function)；如果需要转换为函数名字符串，可以设置为''
            也可以设置为前置字符串，例如'cls.'，这样将会在函数名字符串前增加前缀
        @param {str} action_name=None - 动作名, 如果不传代表和函数名相同
        @param {dict} platform={'*': None} - 支持的平台参数，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        @param {str} standards='SnakerPy' - 注释规范类型
        @param {bool} to_json=False - 是否返回json字符串
        @param {str} para_default_none_to_str=None - 将参数默认值为None的情况转换为指定字符串
        @param {bool} igonre_base_action_fun=True - 是否忽略BaseAction的默认函数

        @returns {dict} - 返回生成的动作路由(Action Router)字典，如果to_json为True则返回json字符串
        """
        # 控制生成结果的参数
        _to_json = False
        _para_default_none_to_str = para_default_none_to_str
        if _para_default_none_to_str is None and to_json:
            _para_default_none_to_str = '{$=None$}'

        _fun_pre_fix = fun_pre_fix

        if _fun_pre_fix is None and to_json:
            # 要转换为字符串的情况，认定需要转为类名前缀
            _fun_pre_fix = class_obj.__name__ + '.'

        # 遍历处理生成
        _action_router = {}
        for _name, _value in inspect.getmembers(class_obj):
            if not _name.startswith('_') and callable(_value):
                if igonre_base_action_fun and _name in [
                    'support_action_types', 'get_action_router', 'common_fun',
                    'get_common_fun_dict', 'support_platform',
                    'get_common_attr_dict', 'common_attr_call'
                ]:
                    # 默认函数不处理
                    continue

                _temp_router = cls.get_action_router_by_function(
                    _value, fun_pre_fix=_fun_pre_fix,
                    platform=platform,
                    standards=standards, to_json=_to_json,
                    para_default_none_to_str=_para_default_none_to_str
                )

                # 合并
                _action_router.update(_temp_router)

        # 处理返回结果
        if to_json:
            if _fun_pre_fix is not None:
                for _temp_name in _action_router.keys():
                    _action_router[_temp_name]['fun'] = '{$fun=%s$}' % _action_router[_temp_name]['fun']

            _json = json.dumps(_action_router, ensure_ascii=False, indent=4)

            if para_default_none_to_str is None:
                _json = _json.replace('"{$=None$}"', 'None')

            if _fun_pre_fix is not None:
                _json = re.sub(r'\"\{\$fun\=.*?\$\}\"', lambda m: m.group(0)[7: -3], _json)

            return _json
        else:
            return _action_router

    @classmethod
    def get_action_router_by_fun_dict(cls, fun_dict: dict, call_fun_obj=None, fun_pre_fix: str = None,
                                      platform: dict = {'*': None},
                                      standards: str = 'SnakerPy', to_json: bool = False,
                                      para_default_none_to_str: str = None):
        """
        根据指定函数映射字典返回对应的动作路由(Action Router)字典

        @param {dict} fun_dict - 函数映射字典
        @param {function} call_fun_obj=None - 路由表中执行的函数对象，如果不为None则传入该对象进路由字典(适配common_fun的使用)
        @param {str} fun_pre_fix=None - 函数名前缀, 如果为None时字典里为函数对象(function)；如果需要转换为函数名字符串，可以设置为''
            也可以设置为前置字符串，例如'cls.'，这样将会在函数名字符串前增加前缀
        @param {dict} platform={'*': None} - 支持的平台参数，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        @param {str} standards='SnakerPy' - 注释规范类型
        @param {bool} to_json=False - 是否返回json字符串
        @param {str} para_default_none_to_str=None - 将参数默认值为None的情况转换为指定字符串
        """
        # 控制生成结果的参数
        _to_json = False
        _para_default_none_to_str = para_default_none_to_str
        if _para_default_none_to_str is None and to_json:
            _para_default_none_to_str = '{$=None$}'

        # 遍历处理生成
        _action_router = {}
        for _action_name in fun_dict.keys():
            _fun_pre_fix = fun_pre_fix
            if to_json and _fun_pre_fix is None:
                _fun_pre_fix = fun_dict[_action_name].__qualname__[
                    0: -len(fun_dict[_action_name].__name__)]

            _temp_router = cls.get_action_router_by_function(
                fun_dict[_action_name], call_fun_obj=call_fun_obj,
                action_name=_action_name,
                fun_pre_fix=_fun_pre_fix,
                platform=platform,
                standards=standards, to_json=_to_json,
                para_default_none_to_str=_para_default_none_to_str
            )

            # 合并
            _action_router.update(_temp_router)

        # 处理返回结果
        if to_json:
            if _fun_pre_fix is not None:
                for _temp_name in _action_router.keys():
                    _action_router[_temp_name]['fun'] = '{$fun=%s$}' % _action_router[_temp_name]['fun']

            _json = json.dumps(_action_router, ensure_ascii=False, indent=4)

            if para_default_none_to_str is None:
                _json = _json.replace('"{$=None$}"', 'None')

            if _fun_pre_fix is not None:
                _json = re.sub(r'\"\{\$fun\=.*?\$\}\"', lambda m: m.group(0)[7: -3], _json)

            return _json
        else:
            return _action_router

    @classmethod
    def get_action_router_by_attr_dict(cls, attr_dict: dict, call_fun_obj=None,
                                       platform: dict = {'*': None},
                                       standards: str = 'SnakerPy', to_json: bool = False,
                                       para_default_none_to_str: str = None):
        """
        根据指定函数映射字典返回对应的动作路由(Action Router)字典

        @param {dict} attr_dict - 实例对象内部方法及属性映射字典
        @param {function} call_fun_obj=None - 路由表中执行的函数对象，如果不为None则传入该对象进路由字典(适配common_fun的使用)
        @param {dict} platform={'*': None} - 支持的平台参数，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        @param {str} standards='SnakerPy' - 注释规范类型
        @param {bool} to_json=False - 是否返回json字符串
        @param {str} para_default_none_to_str=None - 将参数默认值为None的情况转换为指定字符串
        """
        # 控制生成结果的参数
        _to_json = False
        _para_default_none_to_str = para_default_none_to_str
        if _para_default_none_to_str is None and to_json:
            _para_default_none_to_str = '{$=None$}'

        _fun_pre_fix = None
        if to_json:
            _fun_pre_fix = 'cls.'

        # 遍历处理生成
        _action_router = {}
        for _action_name in attr_dict.keys():
            _temp_router = cls.get_action_router_by_function(
                attr_dict[_action_name][1], call_fun_obj=call_fun_obj,
                action_name=_action_name,
                fun_pre_fix=_fun_pre_fix,
                platform=platform,
                standards=standards, to_json=_to_json,
                para_default_none_to_str=_para_default_none_to_str,
                is_common_attr_call=True
            )

            # 合并
            _action_router.update(_temp_router)

        # 处理返回结果
        if to_json:
            if _fun_pre_fix is not None:
                for _temp_name in _action_router.keys():
                    _action_router[_temp_name]['fun'] = '{$fun=%s$}' % _action_router[_temp_name]['fun']

            _json = json.dumps(_action_router, ensure_ascii=False, indent=4)

            if para_default_none_to_str is None:
                _json = _json.replace('"{$=None$}"', 'None')

            if _fun_pre_fix is not None:
                _json = re.sub(r'\"\{\$fun\=.*?\$\}\"', lambda m: m.group(0)[7: -3], _json)

            return _json
        else:
            return _action_router

    #############################
    # 内部函数
    #############################
    @classmethod
    def _analysis_doc_string(cls, doc_string: str, standards: str = 'SnakerPy'):
        """
        按规范解析DocString

        @param {str} doc_string - 要解析的doc_string
        @param {str} standards='SnakerPy' - 注释规范类型，可按需要自行改造增加自定义类型

        @returns {dict} - 解析后的DocString字典，格式为：
            title {str} - 第1行描述
            descript {str} - 第2行开始的详细描述
            param {list} - 入参清单，格式为
                [
                    ['para_name', 'data_type', 'default_value', 'desc'],
                    ...
                ]
            returns {list} - 返回值，格式为['data_type', 'desc']
        """
        _dict = {
            'title': '',
            'descript': '',
            'param': [],
            'returns': []
        }

        _step = 'title'
        _lines = doc_string.splitlines()

        for _line in _lines:
            try:
                _line = _line.strip(' ')
                if _line == '':
                    # 空行都跳过
                    continue

                # 寻找title的值
                if _step == 'title':
                    _dict[_step] = _line
                    _step = 'descript'
                    continue

                # 寻找详细描述的值
                if _step == 'descript':
                    if _line.startswith('@'):
                        # 遇到@开头，结束详细描述的获取
                        _step = ''
                    else:
                        _dict[_step] = '%s%s\n' % (_dict[_step], _line)
                        continue

                # 判断是否要退出循环, 已经到returns阶段，但又遇到@开头的情况
                if _step == 'returns' and _line.startswith('@'):
                    break

                # 变换位置
                if _line.startswith('@param'):
                    if _step == '' or _step == 'title' or _step == 'descript':
                        _step = 'param'
                elif _line.startswith('@returns') or _line.startswith('@property'):
                    _step = 'returns'

                # 参数的处理
                if _step == 'param':
                    if _line.startswith('@param'):
                        # 新的参数
                        _index1 = _line.find('-')
                        _temparray = _line[0: _index1].strip(' ').split(' ')
                        _name = ''
                        if len(_temparray) > 2:
                            _name = _temparray[2]
                        _default = None
                        _index2 = _name.find('=')
                        if _index2 > 0:
                            _default = _name[_index2 + 1:]
                            _name = _name[0:_index2]
                        _dict['param'].append([
                            _name, _temparray[1].strip(
                                '{}'), _default, _line[_index1 + 1:].strip(' ')
                        ])
                        continue
                    elif not _line.startswith('@'):
                        # 老参数的描述内容
                        _dict['param'][len(_dict['param']) - 1][3] += '\n%s' % _line
                        continue

                # 返回值的处理
                if _step == 'returns':
                    if _line.startswith('@returns'):
                        _index1 = _line.find('-')
                        _temparray = _line[0: _index1].strip(' ').split(' ')
                        _dict['returns'] = [
                            _temparray[1].strip('{}'),
                            _line[_index1 + 1:].strip(' ')
                        ]
                    elif _line.startswith('@property'):
                        _dict['returns'] = [
                            _line.strip(' ').split(' ')[1].strip('{}'),
                            ''
                        ]
                    elif not _line.startswith('@'):
                        _dict['returns'][1] += '\n%s' % _line
                        continue
            except:
                print('Exception On: %s' % _line)

        # 返回结果
        _dict['descript'] = _dict['descript'].strip('\n')
        return _dict


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))

    # a = ActionCodeTool.get_action_router_by_function(
    #     ActionCodeTool._analysis_doc_string, to_json=True, fun_pre_fix='cls.'
    # )
    # print(a)

    # from HandLessRobot.lib.controls.windows.uia import WindowControlSpec
    # a = ActionCodeTool.get_action_router_by_class(WindowControlSpec, to_json=True)
    # print(a)
