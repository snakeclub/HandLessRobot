# HandLessRobot
A framework using machine instead of manual operation



## 动作（action）插件开发

### 插件开发步骤

机器人的运作可以视为是执行一个个具体动作（action）组成，可以通过开发动作插件来扩展机器人支持的动作清单，开发一个机器人插件可以通过以下几个简单步骤完成：

1. 创建一个 python 代码文件，例如 simple_action.py ，一个代码文件可以放多个动作插件类，当然从管理角度看也可以一个代码文件放一个插件类

2. 创建一个继承于 HandLessRobot.lib.actions.base_action.BaseAction 的插件类

3. 实现 support_action_types 函数，返回插件提供的动作（action）可支持的动作类型列表，['*'] 代表可支持所有动作类型，['win32', 'winuia'] 代表仅支持 win32 和 winuia 两种动作分类

   **注：动作分类通过字符串区分，由插件自行定义**

4. 实现 support_platform 函数，返回插件支持的操作系统平台和版本清单字典，例如 {'Windows': None} 代表支持Windows全版本，{'Windows': ('7', '10', 'nt')} 代表支持Windows特定版本；如果插件支持全平台全版本，则无需实现该函数

   **注：操作系统和版本标识可以通过 HandLessRobot.robot.RunEnvironment.get_platform() 获取**

5. 在类下面编写你自己的动作函数（@classmethod 修饰），注意前两个入数必须为 “robot_info: dict, action_name: str”，中间可以增加所需的参数，最后必须使用 “**kwargs” 参数兼容函数调用模式；函数可以有返回值，也可以没有返回值

   **注：函数注释必须严格采用 SnakerPy 的注释规范，具体见 [hivenet_python_coding_standards_v1.0.0.md](https://github.com/snakeclub/HiveNetLib/blob/master/docs/source/standards/hivenet_python_coding_standards_v1.0.0.md) , 可以在 Github 上获取该注释规范的 vscode 插件：[autoDocstring](https://github.com/snakeclub/autoDocstring) **

以下是 simple_action.py 的简单示例：

```
from HandLessRobot.lib.actions.base_action import BaseAction

class SimpleAction(BaseAction):
    """
    动作插件示例
    """
    @classmethod
    def support_action_types(cls) -> list:
        """
        返回支持的动作类别列表(主要基于列表区分不同平台及技术兼容的动作)

        @returns {list} - 支持的动作类别列表，例如：
            ['*'] - 代表支持所有分类
            ['win32', 'winuia'] - 代表支持win32和winuia两种分类使用
        """
        return ['*']
      
    @classmethod
    def time_wait(cls, robot_info: dict, action_name: str, interval: float, is_random: bool = False, **kwargs):
        """
        等待指定的时间

        @param {dict} robot_info - 通用参数，调用时默认传入的机器人信息
        @param {str} action_name - 通用参数，调用时默认传入的动作名
        @param {float} interval - 要等待的时间
        @param {bool} is_random=False - 是否等待随机时间，如果True则等待(0, interval)之间的随机时间
        """
        _time = interval
        if is_random:
            _time = random.random(0, interval)

        time.sleep(_time)
```

**注：自动生成的动作路由是不会将内部函数添加进去的，也就是不会处理 "_" 开头的函数。** 



### 将普通类函数及属性映射为插件动作

得益于 BaseAction 通用的 get_action_router 函数，可以直接将现成的普通类函数及属性直接映射为插件动作，无需一个个写动作函数进行调用：

**1、静态函数映射方式**

重载实现插件类的 get_common_fun_dict 函数，函数返回值为静态函数映射字典，字典的 key 填写大写形式的动作名（action_name）， value 为 要执行的函数对象，例如：

```
@classmethod
def get_common_fun_dict(cls):
    """
    获取静态函数通用映射字典
    (如果需要实现映射，请继承并修改该函数的返回值)

    @returns {dict} - 返回静态函数通用映射字典
        key - 动作名(action_name), 必须为大写
        value - 动作对应的执行函数对象
    """
    return {
    	'APPLICATION_START': winuia.Window.start_application,
    	'GET_APPLICATION': winuia.Window.get_application
    }
```

**2、实例化对象的函数和属性映射方式**

遇到有些类对象需要实例化（初始化）后才能执行成员函数或访问属性值的情况，也可以进行映射，需要重载插件类的 get_common_attr_dict 函数，函数返回值为实例化对象函数及属性的映射字典，字典的 key 填写大写形式的动作名（action_name）， value 为 [属性或函数名(字符串), 属性或函数对象] 数组，例如：

```
@classmethod
def get_common_attr_dict(cls):
    """
    获取实例对象内部方法及属性映射字典
    (如果需要实现映射，请继承并修改该函数的返回值)

    @returns {dict} - 返回实例对象内部方法及属性映射字典
        key - 动作名(action_name), 必须为大写
        value - [属性或函数名(字符串), 属性或函数对象]
    """
    return {
    	# 实例对象属性
        'WINDOW_ATTR_HANDLE': ['handle', winuia.WindowControlSpec.handle],
        'WINDOW_ATTR_CLASS_NAME': ['class_name', winuia.WindowControlSpec.class_name],
        # 实例对象函数
        'WINDOW_HIDE': ['hide', winuia.WindowControlSpec.hide],
    	'WINDOW_SHOW': ['show', winuia.WindowControlSpec.show]
    }
```

**注：这种映射方式同样要求映射的函数严格采用 SnakerPy 的注释规范，否则路由的提示信息会不准确。**



### 自定义路由字典

如果不想通过代码自动生成动作路由字典（例如想自行控制路由输出的相关提示信息），也可以通过重载实现 get_action_router 函数，自行产生动作路由字典。

路由字典需要按以下格式定义：

```
{
    'Action_Name': {
        'fun': fun_object,
        'platform': {'system': (ver1, ver2, ...)},
        'instance_class': '',
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
```

字段说明如下：

- fun - 需要调用的函数对象
- platform - 可支持的操作系统平台字典，包括操作系统类型和版本信息
- instance_class - 如果为静态函数，为 '' , 如果为实例化对象的函数和属性，则为对象的类名
- name - 动作展示名
- param - 调用函数的入参描述，为参数数组，每个参数包括参数名、数据类型、默认值、参数说明
- returns - 返回值，为一个数组，包括返回数据类型、返回值说明

