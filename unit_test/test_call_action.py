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
    RunEnvironment.init(init_modules=[common_action, windows_action])


def tearDownModule():
    print("test module end >>>>>>>>>>>>>>")


class Test(unittest.TestCase):
    # 每个用例的开始和结束执行
    def setUp(self):
        # 初始化机器人
        self.robot = Robot('test_robot')

    def tearDown(self):
        # 删除机器人
        del self.robot

    def test_action(self):
        print("处理钉钉窗口")
        _top_win_find_para = {
            'top_level_only': True,
            'class_name': 'StandardFrame_DingTalk',
            'title': '钉钉'
        }
        # 查找钉钉窗口
        _top_win = self.robot.call_action(
            'FIND_WINDOW', call_para_kwargs=_top_win_find_para
        )
        # 获取句柄属性
        _handle = self.robot.call_action(
            'WINDOW_ATTR_HANDLE', instance_obj=_top_win
        )
        self.assertTrue(
            type(_handle) == int, '获取钉钉窗口失败'
        )
        # 设置到最前端
        self.robot.call_action(
            'WINDOW_SET_FOREGROUND', instance_obj=_top_win
        )
        # 设置为正常窗口模式
        _is_maximize = self.robot.call_action(
            'WINDOW_ATTR_IS_MAXIMIZED', instance_obj=_top_win
        )
        if _is_maximize:
            self.robot.call_action(
                'WINDOW_RESTORE', instance_obj=_top_win
            )
        # 移动窗口
        self.robot.call_action(
            'WINDOW_MOVE', instance_obj=_top_win, call_para_args=[0, 0]
        )
        # 设置中间显示
        self.robot.call_action(
            'WINDOW_CENTER', instance_obj=_top_win
        )


if __name__ == '__main__':
    unittest.main()
