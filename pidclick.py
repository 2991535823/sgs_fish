import time
import numpy as np
import threading

class PIDClickController:
    def __init__(self, target_process=0.8,
                 pid_params=(0.5, 0.1, 0.05),
                 delay_range=(0.1, 2.0)):
        # PID参数
        self.Kp, self.Ki, self.Kd = pid_params
        self.target = target_process
        self.delay_min, self.delay_max = delay_range

        # PID状态变量
        self.last_error = 0
        self.integral = 0
        self.last_time = time.perf_counter()
        self.last_process = 0

        # 低通滤波器参数（用于微分项）
        self.alpha = 0.3  # 滤波系数

        # 安全参数
        self.stability_threshold = 0.02  # 稳定判定阈值
        self.stable_counter = 0

    def update(self, current_process):
        # 计算时间差
        now = time.perf_counter()
        dt = now - self.last_time
        dt=max(dt,1e-9)
        self.last_time = now

        # 计算误差
        error = self.target - current_process

        # 积分项（带抗饱和）
        self.integral += error * dt
        self.integral = np.clip(self.integral, -2.0, 2.0)

        # 微分项（带低通滤波）
        derivative = (error - self.last_error) / dt
        filtered_derivative = self.alpha * derivative + (1 - self.alpha) * self.last_error

        # 计算PID输出
        output = (self.Kp * error +
                  self.Ki * self.integral +
                  self.Kd * filtered_derivative)

        # 保存误差状态
        self.last_error = error
        # 转换输出为延迟时间（反向关系）
        base_delay = np.clip(1/output, 0.001, 0.5)

        # 动态调整范围
        # adjusted_delay = np.clip(base_delay, self.delay_min, self.delay_max)

        # 稳定性检测
        if abs(error) < self.stability_threshold:
            self.stable_counter += 1
            if self.stable_counter > 5:
                # 进入稳定状态后降低积分累积
                self.integral *= 0.9
        else:
            self.stable_counter = 0

        return base_delay # 返回click_delay所需的元组格式


class EnhancedAutoClicker:
    def __init__(self, target_pos, pid_params, refresh_interval=0.5):
        """
        增强型自动点击器

        参数：
        - target_pos: 目标点击位置 (x, y)
        - pid_params: PID控制器参数
        - refresh_interval: 进度刷新间隔（秒）
        """
        self.target_pos = target_pos
        self.pid = PIDClickController(pid_params=pid_params)
        self.refresh_interval = refresh_interval

        # 初始点击延迟
        self.current_delay = (0.5, 0.5)  # (min_delay, max_delay)

        # 控制线程
        self.running = False
        self.control_thread = None

    def _control_loop(self):
        """控制循环线程"""
        while self.running:
            try:
                # 获取当前进度
                current_process = self.get_process()

                # 更新PID控制器
                self.current_delay = self.pid.update(current_process)

                # 记录状态
                print(f"当前进度: {current_process:.2%} | 点击延迟: {self.current_delay[0]:.2f}s")

                time.sleep(self.refresh_interval)
            except Exception as e:
                print(f"控制循环异常: {str(e)}")
                break

    def start(self):
        """启动点击系统"""
        self.running = True
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()

        # 主点击循环
        while self.running:
            self.click(self.target_pos, ck_delay=self.current_delay)
            # 添加安全间隔
            time.sleep(0.05)

    def stop(self):
        """停止点击系统"""
        self.running = False
        if self.control_thread:
            self.control_thread.join(timeout=1)



# 保持您原有的进度获取方法...

# 使用示例
if __name__ == "__main__":
    # 初始化参数
    TARGET_POS = (500, 500)  # 目标点击位置
    PID_PARAMS = (0.6, 0.15, 0.08)  # 需要根据实际响应调节

    clicker = EnhancedAutoClicker(
        target_pos=TARGET_POS,
        pid_params=PID_PARAMS,
        refresh_interval=0.3
    )

    try:
        clicker.start()
        while True:
            time.sleep(1)  # 主线程保持运行
    except KeyboardInterrupt:
        clicker.stop()
        print("系统已安全停止")