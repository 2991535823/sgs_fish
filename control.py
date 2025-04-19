from os import times_result
import pyautogui
import random
import time
import math
from enum import Enum

class Direction(Enum):
    """简化后的方向枚举"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class TouchController:
    def __init__(self, 
                 default_offset=1,
                 drag_duration=(0.5, 1.0),
                 click_delay=(0.1, 0.2)):
        self.default_offset = default_offset
        self.drag_duration = drag_duration
        self.click_delay = click_delay
        
        # 初始化安全参数
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.001

    def _get_real_pos(self, pos):
        """添加随机偏移的实际操作位置"""
        return (
            pos[0] + random.randint(-self.default_offset, self.default_offset),
            pos[1] + random.randint(-self.default_offset, self.default_offset)
        )
        

    def drag(self, start_pos, direction, distance,drag_duration=None):
        if not isinstance(direction, Direction):
            raise ValueError("必须使用Direction枚举指定方向")
        # 计算带随机角度的方向向量
        base_x, base_y = direction.value
        angle = math.radians(random.uniform(-3, 3))  # 小范围随机角度
        
        dx = distance * (base_x * math.cos(angle) - base_y * math.sin(angle))
        dy = distance * (base_x * math.sin(angle) + base_y * math.cos(angle))

        # 拟真参数计算
        if drag_duration:
            duration = random.uniform(*drag_duration)
        else:
            duration = random.uniform(*self.drag_duration)
        start_pos = self._get_real_pos(start_pos)

        try:
            # 带加速度曲线的拖拽
            pyautogui.moveTo(start_pos, duration=0.0)
            pyautogui.dragRel(
                dx, dy,
                duration=duration,
                tween=pyautogui.easeInOutQuad,
                button='left'
            )
            return (round(dx), round(dy))
        except pyautogui.FailSafeException:
            self._handle_failsafe()
            return None

    def click(self, target_pos,delay):
        pyautogui.click(*target_pos,duration=delay)
        return None
    def mouse_click(self,target_pos):
        actual_pos = self._get_real_pos(target_pos)
        pyautogui.mouseDown(*actual_pos)
        time.sleep(random.uniform(*self.click_delay))
        pyautogui.mouseUp(*actual_pos)

    def _random_approach(self, target_pos):
        """随机路径接近目标位置"""
        waypoints = [
            (target_pos + random.randint(-20, 20),
             target_pos + random.randint(-20, 20))
            for _ in range(random.randint(1, 3))
        ]
        
        for pos in waypoints:
            pyautogui.moveTo(
                pos,
                duration=random.uniform(0.05, 0.2),
                tween=pyautogui.easeOutQuad
            )

    def _handle_failsafe(self):
        """安全机制触发处理"""
        pyautogui.alert("操作已中断！")
        pyautogui.moveTo(50, 50)

# 使用示例
if __name__ == "__main__":
    controller = TouchController(
        default_offset=3,
        drag_duration=(0.4, 0.8),
        click_delay=(0.08, 0.12)
    )
    
    # 从(300,500)向右滑动200像素
    # controller.drag((300, 500), Direction.RIGHT, 200)
    
    # 点击(150, 600)位置
    controller.click((300, 600))