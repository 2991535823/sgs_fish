import os
import sys
import threading
import time
from platform import system


class EscMonitor:
    def __init__(self, detection_interval=0.05):
        """
        参数：
        - detection_interval: 检测间隔（秒），默认0.01秒（10ms）
        """
        self.detection_interval = detection_interval
        self._exit_flag = False
        self._thread = None

        # 根据操作系统选择检测方式

        self._check = self._windows_check


    def _windows_check(self):
        """Windows系统专用检测方法"""
        import ctypes
        VK_ESCAPE = 0x1B
        return ctypes.windll.user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000 != 0
    def _monitor(self):
        """后台监控线程"""
        while not self._exit_flag:
            if self._check():
                print('用户退出')
                os._exit(1)
            time.sleep(self.detection_interval)

    def start(self):
        """启动监控"""
        if not self._thread or not self._thread.is_alive():
            self._exit_flag = False
            self._thread = threading.Thread(target=self._monitor, daemon=True)
            self._thread.start()

    def stop(self):
        """停止监控"""
        self._exit_flag = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)


# 使用示例
if __name__ == "__main__":
    monitor = EscMonitor()
    monitor.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("程序终止")
    finally:
        monitor.stop()