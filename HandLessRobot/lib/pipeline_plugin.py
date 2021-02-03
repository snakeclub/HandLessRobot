#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
机器人执行通用管道处理器
@module pipeline_plugin
@file pipeline_plugin.py
"""

import os
import sys
import time
import datetime
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.formula import FormulaTool, StructFormulaKeywordPara, StructFormula
from HiveNetLib.pipeline import PipelineProcesser, Tools, SubPipeLineProcesser
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))


__MOUDLE__ = 'pipeline_plugin'  # 模块名
__DESCRIPT__ = u'机器人执行通用管道处理器'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.11.06'  # 发布日期


class RobotActionRun(PipelineProcesser):
    """
    机器人动作run命令执行处理器
    """
    @classmethod
    def initialize(cls):
        """
        初始化处理类，仅在装载的时候执行一次初始化动作
        创建公用的公式处理实例
        """
        # 定义字符串公式的公共关键字参数，例如python中的""引起来的认为是字符串
        _string_para = StructFormulaKeywordPara()
        _string_para.is_string = True  # 声明是字符串参数
        _string_para.has_sub_formula = False  # 声明公式中不会有子公式
        # 在查找字符串结束关键字时忽略的转义情况，例如"this is a string ,ignore \" , this is real end"
        _string_para.string_ignore_chars = ['\\"']

        # 定义字符串公式的公共关键字参数，例如python中的''引起来的认为是字符串
        _string_para1 = StructFormulaKeywordPara()
        _string_para1.is_string = True  # 声明是字符串参数
        _string_para1.has_sub_formula = False  # 声明公式中不会有子公式
        # 在查找字符串结束关键字时忽略的转义情况，例如'this is a string ,ignore \' , this is real end'
        _string_para1.string_ignore_chars = ["\\'"]

        # 定义公式解析的关键字参数
        _keywords = {
            # 第一个定义了字符串的公式匹配参数
            'String': [
                ['"', list(), list()],  # 公式开始标签
                ['"', list(), list()],  # 公式结束标签
                _string_para  # 公式检索参数
            ],
            'String1': [
                ["'", list(), list()],  # 公式开始标签
                ["'", list(), list()],  # 公式结束标签
                _string_para1  # 公式检索参数
            ],
            'Fixed': [
                ['{$fixed=', list(), list()],  # 公式开始标签
                ['$}', list(), list()],  # 公式结束标签
                StructFormulaKeywordPara()  # 公式检索参数
            ],
            'Var': [
                ['{$var=', list(), list()],
                ['$}', list(), list()],
                StructFormulaKeywordPara()
            ],
            'Local': [
                ['{$local=', list(), list()],
                ['$}', list(), list()],
                StructFormulaKeywordPara()
            ]
        }

        # 定义公式对象处理函数
        _deal_fun_list = {
            'String': cls._string_formula_deal_fun,  # 保留标签原样值(包括引号)
            'String1': cls._string_formula_deal_fun,  # 保留标签原样值(包括引号)
            'Fixed': cls._fixed_formula_deal_fun,  # 固定替换值
            'Var': cls._var_formula_deal_fun,  # 自定义公式处理函数
            'Local': cls._local_formula_deal_fun,  # 访问本地变量
        }

        # 初始化公式类
        _formula_obj = FormulaTool(
            keywords=_keywords,
            ignore_case=False,
            deal_fun_list=_deal_fun_list,
            default_deal_fun=None
        )

        # 放入全局变量供使用
        RunTool.set_global_var('ROBOT_ACTION_RUN_FORMULA', _formula_obj)

    @classmethod
    def processer_name(cls) -> str:
        """
        处理器名称，唯一标识处理器

        @returns {str} - 当前处理器名称
        """
        return 'RobotActionRun'

    @classmethod
    def execute(cls, input_data, context: dict, pipeline_obj, run_id: str):
        """
        执行处理

        @param {object} input_data - 固定为一个字典，定义如下：
            robot {HandLessRobot.robot.Robot} - 执行管道的机器人实例对象
            last_result {object} - 上一个动作执行的结果

        @param {dict} context - 传递上下文，该字典信息将在整个管道处理过程中一直向下传递，可以在处理器中改变该上下文信息
            要传入的动作执行信息包括（在管道配置中定义）:
                action_config {dict} - 动作执行配置
                    action_name {str} - 动作名(不区分大小写)
                    instance_obj {str} - 要执行动作所在的实例对象变量获取标签
                    call_para_args {str} - 执行按位置传入的参数数组json字符串，可以用变量获取标签替代
                    call_para_kwargs {str} - 执行按key-value传入的参数字典json字符串，可以用变量获取标签替代
                    save_to_var {str} - 要保存到变量的变量名
                    save_run_id {str} - 与save_to_var配套使用，保存到的变量使用范围，不传默认为run_id, 可以用变量获取标签替代
        @param {Pipeline} pipeline_obj - 管道对象，作用如下：
            1、更新执行进度
            2、输出执行日志
            3、异步执行的情况主动通知继续执行管道处理
        @param {str} run_id - 当前管道的运行id

        @returns {object} - 固定为一个字典，定义如下：
            robot {HandLessRobot.robot.Robot} - 执行管道的机器人实例对象
            last_result {object} - 上一个动作执行的结果
        """
        # 处理执行参数
        _formula_obj: FormulaTool = RunTool.get_global_var('ROBOT_ACTION_RUN_FORMULA')
        _formula_kwargs = {
            'robot': "input_data['robot']",
            'fixed_last': "input_data.get('last_result', None)",
            'fixed_run_id': "run_id"
        }

        _action_config = context.pop('action_config')
        _action_name = _action_config['action_name'].upper()

        _instance_obj = _action_config.get('instance_obj', None)
        if type(_instance_obj) == str:
            _instance_obj = eval(
                _formula_obj.run_formula_as_string(_instance_obj, **_formula_kwargs).formula_value
            )

        _call_para_args = _action_config.get('call_para_args', None)
        if type(_call_para_args) == str:
            _call_para_args = eval(
                _formula_obj.run_formula_as_string(_call_para_args, **_formula_kwargs).formula_value
            )

        _call_para_kwargs = _action_config.get('call_para_kwargs', None)
        if type(_call_para_kwargs) == str:
            _call_para_kwargs = eval(
                _formula_obj.run_formula_as_string(
                    _call_para_kwargs, **_formula_kwargs).formula_value
            )

        _save_to_var = _action_config.get('save_to_var', None)
        _save_run_id = _action_config.get('save_run_id', run_id)

        # 执行动作函数
        _result = input_data['robot'].call_action(
            _action_name, instance_obj=_instance_obj, run_id=run_id, call_para_args=_call_para_args,
            call_para_kwargs=_call_para_kwargs, save_to_var=_save_to_var, save_run_id=_save_run_id,
        )

        # 处理输出
        _RESERVED_CONTROL_ACTION_NAME = RunTool.get_global_var('RESERVED_CONTROL_ACTION_NAME')
        if not (_action_name in _RESERVED_CONTROL_ACTION_NAME['*'] or _action_name in _RESERVED_CONTROL_ACTION_NAME.get(
            run_id, list()
        )):
            # 不是控制动作才变更上一执行结果
            input_data['last_result'] = _result

        return input_data

    #############################
    # 内部静态函数 - 公式处理函数
    #############################
    @classmethod
    def _string_formula_deal_fun(cls, formular_obj: StructFormula, **kwargs):
        """
        处理String公式标签

        @param {StructFormula} formular_obj - 要计算的公式
        """
        formular_obj.formula_value = formular_obj.formula_string

    @classmethod
    def _fixed_formula_deal_fun(cls, formular_obj: StructFormula, **kwargs):
        """
        处理Fixed公式标签

        @param {StructFormula} formular_obj - 要计算的公式
        """
        if formular_obj.content_string == 'last':
            # 获取上一输出结果
            formular_obj.formula_value = kwargs['fixed_last']
        elif formular_obj.content_string == 'run_id':
            formular_obj.formula_value = kwargs['fixed_run_id']
        elif formular_obj.content_string == 'now':
            formular_obj.formula_value = "datetime.datetime.now()"
        else:
            raise RuntimeError('Not supported fixed tag [%s]!' % formular_obj.content_string)

    @classmethod
    def _var_formula_deal_fun(cls, formular_obj: StructFormula, **kwargs):
        """
        处理Var公式标签

        @param {StructFormula} formular_obj - 要计算的公式
        """
        _para = formular_obj.content_string.split(',')
        if len(_para) == 1:
            # 只有变量名，默认使用当前run_id
            formular_obj.formula_value = "%s.robot_info['vars'][run_id]['%s']" % (
                kwargs['robot'], _para[0])
        else:
            # 指定了run_id
            formular_obj.formula_value = "%s.robot_info['vars']['%s']['%s']" % (
                kwargs['robot'], _para[1], _para[0]
            )

    @classmethod
    def _local_formula_deal_fun(cls, formular_obj: StructFormula, **kwargs):
        """
        处理Local公式标签

        @param {StructFormula} formular_obj - 要计算的公式
        """
        formular_obj.formula_value = formular_obj.content_string


class RobotActionControl(PipelineProcesser):
    """
    机器人动作控制命令执行处理器
    """
    @classmethod
    def processer_name(cls) -> str:
        """
        处理器名称，唯一标识处理器

        @returns {str} - 当前处理器名称
        """
        return 'RobotActionControl'

    @classmethod
    def execute(cls, input_data, context: dict, pipeline_obj, run_id: str):
        """
        执行处理

        @param {object} input_data - 固定为一个字典，定义如下：
            robot {HandLessRobot.robot.Robot} - 执行管道的机器人实例对象
            last_result {object} - 上一个动作执行的结果

        @param {dict} context - 传递上下文，该字典信息将在整个管道处理过程中一直向下传递，可以在处理器中改变该上下文信息
            要传入的动作执行信息包括（在管道配置中定义）:
                control_config {dict} - 命令执行配置，不同命令配置信息不同
                    control_name {str} - 命令名
                        null - 不做任何处理
                        end - 直接跳转到执行结束
                        goto - 跳转到指定的 step_id 所在步骤
                        break - 循环结束（实际逻辑是增加循环结束标志并跳转到循环开始位置）
                        continue - 马上下一次循环(跳转到循环开始位置)
                        endloop - 结束循环位置
                        else - if条件判断False时执行的节点
                        endif - if条件判断结尾节点，不做任何处理
                        if - 条件判断，如果True执行下一个节点，False执行else块或结束块
                        loop - 循环，如果True继续循环，False跳过循环

                    goto命令所需参数
                        goto_step_id {str} - 要跳转到的步骤标识名

                    break/continue/endloop命令所需参数:
                        loop_node_id {str} - 循环开始节点id

                    if/loop/else命令所需参数:
                        end_node_id {str} - 块结束所在节点

                    if命令所需参数:
                        else_node_id {str} - else坐在节点

                    if/loop命令所需参数:
                        condition {str} - 判断条件的python表达式，支持变量获取标签替代
                            如果条件中需要使用送入的动作执行结果，使用 {$local=run_action$} 替代
                            例如: '{$var=var_name$} > 0 and {$local=run_action$} in ['abc', 'bcd']'
                        action_name {str} - 动作名(不区分大小写)
                        instance_obj {str} - 要执行动作所在的实例对象变量获取标签
                        call_para_args {str} - 执行按位置传入的参数数组json字符串，可以用变量获取标签替代
                        call_para_kwargs {str} - 执行按key-value传入的参数字典json字符串，可以用变量获取标签替代
                        save_to_var {str} - 要保存到变量的变量名
                        save_run_id {str} - 与save_to_var配套使用，保存到的变量使用范围，不传默认为run_id, 可以用变量获取标签替代

                    prompt命令所需参数：
                        prompt_router {str} - 命令对应的路由字典对应的json字符串, key为命令字符串, value为要跳转到的step_id
                        prompt_para {str} - 扩展参数对应的json字符串，格式如："{'over_time': 0.0, 'over_time_step_id': None, 'sleep_time': 500}"
                            over_time {float} - 超时时间，单位为秒，默认为0.0，如果为0代表一直不会超时
                            over_time_step_id {str} - 当执行超时时跳转到的步骤id，如果为None则按照正常节点完成方式执行下一个节点
                            sleep_time {int} - 间隔轮询命令的睡眠时间，单位为毫秒，默认为500
                        以下参数将执行一个动作进行命令输入的通知，也可以不传（不通知）：
                        action_name {str} - 动作名(不区分大小写)
                        instance_obj {str} - 要执行动作所在的实例对象变量获取标签
                        call_para_args {str} - 执行按位置传入的参数数组json字符串，可以用变量获取标签替代
                        call_para_kwargs {str} - 执行按key-value传入的参数字典json字符串，可以用变量获取标签替代
                        save_to_var {str} - 要保存到变量的变量名
                        save_run_id {str} - 与save_to_var配套使用，保存到的变量使用范围，不传默认为run_id, 可以用变量获取标签替代

        @param {Pipeline} pipeline_obj - 管道对象，作用如下：
            1、更新执行进度
            2、输出执行日志
            3、异步执行的情况主动通知继续执行管道处理
        @param {str} run_id - 当前管道的运行id

        @returns {object} - 固定为一个字典，定义如下：
            robot {HandLessRobot.robot.Robot} - 执行管道的机器人实例对象
            last_result {object} - 上一个动作执行的结果
        """
        # 参数
        _control_config: dict = context.pop('control_config')
        _cmd = _control_config['control_name'].lower()

        # 先处理简单命令
        if _cmd in ('null', 'endif'):
            # 不做任何处理
            pass
        elif _cmd == 'goto':
            # 跳转到指定位置
            context['goto_node_name'] = _control_config['goto_step_id']
        elif _cmd == 'end':
            context['goto_node_name'] = '{$END_NODE$}'
        elif _cmd == 'break':
            context['loop_break'] = True
            context['goto_node_id'] = _control_config['loop_node_id']
        elif _cmd == 'continue':
            context['goto_node_id'] = _control_config['loop_node_id']
        elif _cmd == 'endloop':
            context['goto_node_id'] = _control_config['loop_node_id']
        elif _cmd == 'else':
            # 如果会运行到else，代表是从True条件执行下来的，直接跳过块结尾就好
            context['goto_node_id'] = str(int(_control_config['end_node_id']) + 1)
        elif _cmd == 'loop' and context.pop('loop_break', False):
            # 跳出循环
            context['goto_node_id'] = str(int(_control_config['end_node_id']) + 1)
        elif _cmd in ('if', 'loop', 'prompt'):
            # 对于prompt，需要先清理 {$WAIT_COMMAND$} 变量，避免历史数据的干扰
            if _cmd == 'prompt':
                if run_id in input_data['robot'].robot_info['vars'].keys():
                    input_data['robot'].robot_info['vars'][run_id].pop('{$WAIT_COMMAND$}')

            # 公式计算对象
            _formula_obj: FormulaTool = RunTool.get_global_var('ROBOT_ACTION_RUN_FORMULA')
            _formula_kwargs = {
                'robot': "input_data['robot']",
                'fixed_last': "input_data.get('last_result', None)",
                'fixed_run_id': "run_id"
            }

            # 执行处理动作
            run_action = None
            if _control_config.get('action_name', '') != '':
                _instance_obj = _control_config.get('instance_obj', None)
                if type(_instance_obj) == str and _instance_obj != '':
                    _instance_obj = eval(
                        _formula_obj.run_formula_as_string(
                            _instance_obj, **_formula_kwargs).formula_value
                    )
                else:
                    _instance_obj = None

                _call_para_args = _control_config.get('call_para_args', None)
                if type(_call_para_args) == str and _call_para_args != '':
                    _call_para_args = eval(
                        _formula_obj.run_formula_as_string(
                            _call_para_args, **_formula_kwargs).formula_value
                    )
                else:
                    _call_para_args = None

                _call_para_kwargs = _control_config.get('call_para_kwargs', None)
                if type(_call_para_kwargs) == str and _call_para_kwargs != '':
                    _call_para_kwargs = eval(
                        _formula_obj.run_formula_as_string(
                            _call_para_kwargs, **_formula_kwargs).formula_value
                    )
                else:
                    _call_para_kwargs = None

                _save_to_var = _control_config.get('save_to_var', None)
                if _save_to_var == '':
                    _save_to_var = None
                _save_run_id = _control_config.get('save_run_id', run_id)
                if _save_run_id == '':
                    _save_run_id = run_id

                # 执行动作函数
                run_action = input_data['robot'].call_action(
                    _control_config['action_name'], instance_obj=_instance_obj, run_id=run_id, call_para_args=_call_para_args,
                    call_para_kwargs=_call_para_kwargs, save_to_var=_save_to_var, save_run_id=_save_run_id,
                )

            # 对于prompt方式单独执行自有的逻辑，不执行后面的条件判断逻辑
            if _cmd == 'prompt':
                _prompt_router = eval(_control_config.get('prompt_router', '{}'))
                _prompt_para = eval(_control_config.get('prompt_para', '{}'))
                _over_time = _prompt_para.get('over_time', 0.0)
                _over_time_step_id = _prompt_para.get('over_time_step_id', None)
                _sleep_time = _prompt_para.get('sleep_time', 500)
                _start = datetime.datetime.now()
                while True:
                    if run_id in input_data['robot'].robot_info['vars'].keys():
                        _get_cmd = input_data['robot'].robot_info['vars'][run_id].pop(
                            '{$WAIT_COMMAND$}', None)
                        if _get_cmd is not None:
                            # 找到命令
                            if _get_cmd not in _prompt_router.keys():
                                raise KeyError('Not support cmd [%s]!' % _get_cmd)

                            # 设置跳转参数
                            context['goto_node_name'] = _prompt_router[_get_cmd]
                            return input_data

                    # 未获取到命令，检查是否超时
                    if _over_time > 0 and (datetime.datetime.now() - _start).total_seconds() > _over_time:
                        if _over_time_step_id is not None:
                            # 指定跳转到超时指定步骤
                            context['goto_node_name'] = _over_time_step_id

                        # 跳出循环
                        return input_data

                    # 休眠一段时间，继续尝试获取
                    time.sleep(_sleep_time)

            # 处理条件判断
            _condition = eval(
                _formula_obj.run_formula_as_string(
                    _control_config['condition'], **_formula_kwargs).formula_value
            )

            # 加这行是为了变量不被释放
            if run_action:
                pass

            if _condition:
                # 执行当前节点的下一个节点
                context['goto_node_id'] = str(int(pipeline_obj.current_node_id(run_id=run_id)) + 1)
            else:
                # 不满足条件
                if _cmd == 'if' and _control_config.get('else_node_id', None) is not None:
                    # 跳转到else块
                    context['goto_node_id'] = str(int(_control_config['else_node_id']) + 1)
                else:
                    # 跳转到结束节点的下一节点
                    context['goto_node_id'] = str(int(_control_config['end_node_id']) + 1)

        # 控制命令不改变输入输出
        return input_data


class RobotPredefRun(SubPipeLineProcesser):
    """
    机器人预定义模块执行处理器
    """
    @classmethod
    def processer_name(cls) -> str:
        """
        处理器名称，唯一标识处理器

        @returns {str} - 当前处理器名称
        """
        return 'RobotPredefRun'

    @classmethod
    def get_sub_pipeline(cls, input_data, context: dict, pipeline_obj, run_id: str, sub_pipeline_para: dict):
        """
        获取子管道对象的函数

        @param {object} input_data - 固定为一个字典，定义如下：
            robot {HandLessRobot.robot.Robot} - 执行管道的机器人实例对象
            last_result {object} - 上一个动作执行的结果
        @param {dict} context - 传递上下文，该字典信息将在整个管道处理过程中一直向下传递，可以在处理器中改变该上下文信息
        @param {Pipeline} pipeline_obj - 发起的管道对象
        @param {str} run_id - 当前管道的运行id
        @param {dict} sub_pipeline_para - 获取子管道对象的参数字典
            predef_name {str} - 预定义模块的子管道对象

        @returns {Pipeline} - 返回获取到的子管道对象（注意该子管道对象的使用模式必须与is_asyn一致）
        """
        return input_data['robot'].robot_info['predef_pipeline'][sub_pipeline_para['predef_name']]


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
