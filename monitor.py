import time

import pyautogui
import cv2
import numpy as np
import cv2
import numpy as np
import dxcam  # 需要安装：pip install dxcam


class HighPerfFPS:
    def __init__(self, buffer_size=1000):
        self.timestamps = np.zeros(buffer_size, dtype=np.float64)
        self.index = 0

    def update(self):
        """记录时间戳"""
        if self.index < len(self.timestamps):
            self.timestamps[self.index] = time.perf_counter()
            self.index += 1
        else:
            # 环形缓冲区
            self.timestamps[:-1] = self.timestamps[1:]
            self.timestamps[-1] = time.perf_counter()

    def get_stats(self):
        """获取帧率统计信息"""
        if self.index < 2:
            return 0, 0, 0

        valid = self.timestamps[:self.index] if self.index < len(self.timestamps) else self.timestamps
        deltas = np.diff(valid)
        avg = np.mean(deltas)
        min_val = np.min(deltas)
        max_val = np.max(deltas)
        return 1 / avg, 1 / max_val, 1 / min_val  # FPS转换

class ScreenCapturer:
    def __init__(self, region: tuple = None, target_fps: int = 60):
        """
        初始化高性能截图器

        参数：
        - region: (left, top, width, height) 截图区域
        - target_fps: 目标采集帧率
        """
        self.camera = dxcam.create(output_idx=0, output_color="BGR")
        self.region = region
        self.target_fps = target_fps
        self._setup_capture()
        # self.fps=HighPerfFPS()
    def _setup_capture(self):
        """配置采集参数"""
        if self.region:
            left, top, width, height = self.region
            self.camera.start(region=(left, top, left + width, top + height),
                              target_fps=self.target_fps)
        else:
            self.camera.start(target_fps=self.target_fps)

    def get_frame(self) -> np.ndarray:
        """获取最新帧（非阻塞模式）"""
        frame = self.camera.get_latest_frame()
        if frame is None:
            raise RuntimeError("无法获取屏幕帧")
        return frame

    def stop(self):
        """停止采集"""
        self.camera.stop()


# 使用示例
if __name__ == "__main__":
    # 初始化采集器（截取屏幕中心 800x600 区域）
    screen_width, screen_height = 1920, 1080  # 根据实际屏幕设置
    region = (
        (screen_width - 800) // 2,
        (screen_height - 600) // 2,
        800,
        600
    )

    capturer = ScreenCapturer(region=region, target_fps=144)

    try:
        # 实时显示截图（演示用）
        while True:
            frame = capturer.get_frame()
            cv2.imshow("High-Speed Capture", frame)
            if cv2.waitKey(1) == 27:  # ESC退出
                break
    finally:
        capturer.stop()
        cv2.destroyAllWindows()