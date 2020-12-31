#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
import unittest
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from HandLessRobot.robot import Robot, RunEnvironment
from HandLessRobot.lib.actions import common_action, windows_action


def setUpModule():
    # 预装载全局的动作类
    # RunEnvironment.init(init_modules=[common_action, windows_action])
    pass


def tearDownModule():
    print("test module end >>>>>>>>>>>>>>")


class Test(unittest.TestCase):
    # 每个用例的开始和结束执行
    def setUp(self):
        # 初始化机器人
        self.robot = Robot(
            'test_robot', init_modules=[common_action, windows_action],
        )

        # 预定义参数
        _config_main = {
            "predef_name": "dingtalk_main",
            "steps": [
                {
                    "step_id": "get_win",
                    "cmd": "run",
                    "action_name": "FIND_WINDOW",
                    "call_para_kwargs": "{'top_level_only': True, 'class_name': 'StandardFrame_DingTalk', 'title': '钉钉'}",
                    "save_to_var": "dingtalk_win",
                    "remark": "查找钉钉窗口"
                },
                {
                    "step_id": "",
                    "cmd": "if",
                    "action_name": "WINDOW_ATTR_HANDLE",
                    "instance_obj": "{$var=dingtalk_win$}",
                    "condition": "type({$local=run_action$}) != int",
                    "remark": "if 判断是否可获取到句柄属性"
                },
                {
                    "step_id": "",
                    "cmd": "end",
                    "remark": "跳转到结束"
                },
                {
                    "step_id": "",
                    "cmd": "endif",
                    "remark": "endif 判断是否可获取到句柄属性"
                },
                {
                    "action_name": "WINDOW_SET_FOREGROUND",
                    "instance_obj": "{$var=dingtalk_win$}",
                    "remark": "设置窗口到最前端"
                },
                {
                    "step_id": "",
                    "cmd": "predef",
                    "predef_name": "dingtalk_move",
                    "remark": "执行预定义操作，设置正常窗口并移动"
                }
            ]
        }

        _config_move = {
            "predef_name": "dingtalk_move",
            "steps": [
                {
                    "step_id": "",
                    "cmd": "predef",
                    "predef_name": "dingtalk_restore",
                    "remark": "恢复窗口未正常模式"
                },
                {
                    "action_name": "WINDOW_MOVE",
                    "instance_obj": "{$var=dingtalk_win$}",
                    "call_para_args": "[0, 0]",
                    "remark": "移动窗口到0, 0"
                },
                {
                    "action_name": "WINDOW_CENTER",
                    "instance_obj": "{$var=dingtalk_win$}",
                    "remark": "设置窗口为正中央"
                }
            ]
        }

        _config_restore = {
            "predef_name": "dingtalk_restore",
            "steps": [
                {
                    "step_id": "",
                    "cmd": "if",
                    "action_name": "WINDOW_ATTR_IS_MAXIMIZED",
                    "instance_obj": "{$var=dingtalk_win$}",
                    "condition": "{$local=run_action$}",
                    "remark": "if 判断窗口是否最大化"
                },
                {
                    "action_name": "WINDOW_RESTORE",
                    "instance_obj": "{$var=dingtalk_win$}",
                    "remark": "恢复窗口为正常模式"
                },
                {
                    "step_id": "",
                    "cmd": "endif",
                    "remark": "endif 判断窗口是否最大化"
                }
            ]
        }

        # 装载预定义参数
        for _config in (_config_main, _config_move, _config_restore):
            self.robot.load_predef_by_config(_config)

    def tearDown(self):
        # 删除机器人
        del self.robot

    def test_action(self):
        print("处理钉钉窗口 - 运行机器人")

        _status = ''
        _predef_name = 'dingtalk_main'
        _step = 0
        while _status not in ('S', 'E'):
            if _status == '':
                _run_id, _status, _output = self.robot.run_predef(
                    _predef_name, is_step_by_step=True)
            else:
                _run_id, _status, _output = self.robot.resume_predef(_predef_name, _run_id)

            # 打印执行信息
            _step += 1
            _status_msg = self.robot.last_status_msg(_predef_name, _run_id)
            for _msg in _status_msg:
                _step_para = self.robot.get_step_para(_msg[0], _run_id, _msg[1])
                print(
                    'run step[%d]: cmd[%s] %s status[%s] msg[%s]' % (
                        _step, _step_para.get('cmd', 'run'),
                        _step_para.get('remark', ''),
                        _msg[2], _msg[3]
                    )
                )

        self.assertTrue(_status == 'S', 'run status error [%s]!' % _status)


if __name__ == '__main__':
    unittest.main()
