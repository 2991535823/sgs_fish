import os
import sys
import threading
from copy import deepcopy

import cv2
import numpy as np

from coordinate import GameCoordinate
from monitor import ScreenCapturer
from pidclick import PIDClickController

def get_path(file):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    path = str(os.path.join(bundle_dir, file))
    return  path
def cv_imread(file_path):
    #解决中文路径
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    return cv_img

def phash(image, hash_size=32, dct_size=8):
    # 转换为灰度图并调整尺寸
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hash_size, hash_size), interpolation=cv2.INTER_LINEAR)

    # 2. 转换为浮点并计算DCT
    dct_input = resized.astype(np.float32) / 255.0
    dct_result = cv2.dct(dct_input)

    # 3. 保留低频区域（左上角dct_size x dct_size）
    low_freq = dct_result[:dct_size, :dct_size]

    # 4. 计算哈希值（排除直流分量）
    median = np.median(low_freq[1:, 1:])
    hash_binary = (low_freq > median).flatten().astype(int).tolist()

    return hash_binary


def similar(hash1, hash2):
    if len(hash1) != len(hash2):
        raise ValueError("哈希值长度不一致")

    distance = sum(b1 != b2 for b1, b2 in zip(hash1, hash2))
    similarity = 1 - distance / len(hash1)

    return distance, similarity


class MatchBTN:
    def __init__(self, region,settings):
        self.up = cv2.cvtColor(cv_imread(get_path('u.png')), cv2.COLOR_BGR2GRAY)
        self.down = cv2.cvtColor(cv_imread(get_path('d.png')), cv2.COLOR_BGR2GRAY)
        self.left = cv2.cvtColor(cv_imread(get_path('l.png')), cv2.COLOR_BGR2GRAY)
        self.right = cv2.cvtColor(cv_imread(get_path('r.png')), cv2.COLOR_BGR2GRAY)
        self.feng = cv2.cvtColor(cv_imread(get_path('feng.png')), cv2.COLOR_BGR2GRAY)
        self.huo = cv2.cvtColor(cv_imread(get_path('huo.png')), cv2.COLOR_BGR2GRAY)
        self.lei = cv2.cvtColor(cv_imread(get_path('lei.png')), cv2.COLOR_BGR2GRAY)
        self.dian = cv2.cvtColor(cv_imread(get_path('dian.png')), cv2.COLOR_BGR2GRAY)
        self.btn_dict = {'up': self.up, 'down': self.down, 'left': self.left, 'right': self.right,
                         'feng': self.feng, 'huo': self.huo, 'lei': self.lei, 'dian': self.dian}
        self.conf = settings['detect_conf']
        self.kbtn_size = (round(region[2] / 20), round(region[2] / 20))
        # print('斩杀按钮大小',self.kbtn_size)
        self.resize(self.kbtn_size)

    def crop(self,image, center, width, height):
        x, y = center
        half_w = int(width // 2)
        half_h = int(height // 2)
        x1 = max(0, int(x) - half_w)
        y1 = max(0, int(y) - half_h)
        x2 = min(image.shape[1], x + half_w)
        y2 = min(image.shape[0], y + half_h)
        cropped = image[y1:y2, x1:x2]
        return cropped
    def match(self, image):
        keys=[]
        return keys

    def resize(self, size):
        for key, img in self.btn_dict.items():
            self.btn_dict[key] = cv2.resize(img, size, interpolation=cv2.INTER_LINEAR)


class GameInfo(threading.Thread):
    def __init__(self, region,settings):
        threading.Thread.__init__(self)
        self.process = 0.0
        self.cy_process = 0.0
        self.conf = 0.85
        self.kill_conf=0.65
        self.bias_y = settings['title_height']
        self.is_baigan = False
        if settings['window_title']== '三国杀':
            self.cap_region = (region[0] + 7, region[1], region[2] - 14, region[3] - 7)
        else:
            self.cap_region = region
        self.gc = GameCoordinate(region, self.bias_y)
        self.region = region
        self.fish_size = (round(region[2] / 20), round(region[2] / 20))
        self.kill_size = (round(region[2] / 20), round(region[2] / 20))
        self.baigan_size = (round(region[2] / 10), round((region[3] - 30) / 15))

        self.block_size = round(0.04944 * self.region[2])
        self.kill_match = MatchBTN(region,settings)
        self.capture = ScreenCapturer(self.cap_region, target_fps=settings['cap_fps'])
        self.PID_Click = PIDClickController(settings['progress_tracking'], (settings['kp'], settings['ki'], settings['kd']), (0.001, 0.1))
        self.click_delay = 0
        self._running = True
        self.daemon = True
        self._start_fish = False
        self.finish = cv2.resize(cv_imread(get_path('finish.png')), self.fish_size,
                                 interpolation=cv2.INTER_LINEAR)
        self.baigan = cv2.resize(cv2.cvtColor(cv_imread(get_path('baigan.png')), cv2.COLOR_BGR2GRAY), self.baigan_size,
                                 interpolation=cv2.INTER_LINEAR)
        self.up = cv2.resize(cv_imread(get_path('u.png')), self.kill_size, interpolation=cv2.INTER_LINEAR)
        self.bg_bright = np.mean(
            cv2.cvtColor(cv2.resize(cv_imread(get_path('baigan.png')), self.baigan_size, interpolation=cv2.INTER_LINEAR),
                         cv2.COLOR_BGR2HSV)[:, :, 2])
        self._start_kill = False
        self._kill_res = []
        self.bagan_check = True
        self.baigan_cood = ()
        self.lock = threading.Lock()
        self.sets=settings
    def run(self):
        count=0
        while True:
            if self._running:
                count+=1
                image = self.capture.get_frame()
                self.process = self.get_process(image)

                self.click_delay = self.PID_Click.update(self.process)
                with self.lock:
                    self._start_kill = self.detect_kill(image)
                with self.lock:
                    self._start_fish = self.detect_finish(image)
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                if self.bagan_check:
                    res = self.check_exist(gray_image, self.baigan, 0.8)
                    if res[0]:
                        self.bagan_check = False
                        self.baigan_cood = (int(res[1]), int(res[2])), (
                        int(res[1] + self.baigan_size[0]), int(res[2] + self.baigan_size[1]))
                        print('摆杆点', self.baigan_cood)
                        x=round(int(res[1] + self.baigan_size[0]//2)/self.region[2],4)
                        y=round(int(res[2] + self.baigan_size[1]//2)/self.region[3],4)
                        self.sets['baigan_p']=(x,y)
                self.cy_process = self.detect_ciyu(image)
                # print(f'钓鱼进度{self.process},爆发进度:{self.cy_process}')
                if not self.bagan_check and count%5==0 :
                    self.is_baigan = self.detect_baigan(image)
                    self._start_fish = self._start_fish or self.is_baigan

                if self.start_kill:
                    with self.lock:
                        self._kill_res = self.match_kill(gray_image)
                if count>60:
                    count=0
                if self.sets['debug']:
                    cv2.rectangle(image,self.gc.cal_ref_pose(*self.sets['process_tl']),self.gc.cal_ref_pose(*self.sets['process_br']),(0,0,255))
                    cv2.rectangle(image,self.gc.cal_ref_pose(*self.sets['cy_tl']),self.gc.cal_ref_pose(*self.sets['cy_br']),(0,0,255))
                    cv2.putText(image,f'{round(self.process,2)}',self.gc.cal_ref_pose(*self.sets['process_tl']),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255))
                    cv2.putText(image,f'{round(self.cy_process,2)}',self.gc.cal_ref_pose(*self.sets['cy_tl']),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255))
                    cv2.imshow('debug',image)
                    cv2.waitKey(1)
            else:
                pass

    @property
    def kill_res(self):
        with self.lock:
            return self._kill_res
    @property
    def start_fish(self):
        with self.lock:
            return self._start_fish
    @property
    def start_kill(self):
        with self.lock:
            return self._start_kill

    def check_exist(self, image, ck_img, t):
        ret = cv2.matchTemplate(image, ck_img, cv2.TM_CCOEFF_NORMED)
        res = np.where(ret > t)
        if len(res[0]) > 0:
            return True, res[1][0], res[0][0]
        else:
            return False, 0, 0

    def find_region(self, image):
        pass

    def get_process(self, image):
        tl = self.gc.cal_ref_pose(*self.sets['process_tl'])
        br = self.gc.cal_ref_pose(*self.sets['process_br'])
        process_image = image[tl[1]:br[1], tl[0]:br[0]]

        gray_image = cv2.cvtColor(process_image, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_image, 160, 255, cv2.THRESH_BINARY)
        h, w = binary_img.shape
        process = binary_img[round(h / 2), 0:w]
        process_value=sum(p > 0 for p in process) / process.size
        return process_value

    def detect_baigan(self, image):
        tl = self.baigan_cood[0]
        br = self.baigan_cood[1]
        process_image = image[tl[1]:br[1], tl[0]:br[0]]
        gary_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        res = self.check_exist(gary_image, self.baigan, 0.8)
        if res[0]:
            hsv_image = cv2.cvtColor(process_image, cv2.COLOR_BGR2HSV)
            avg_bright = np.mean(hsv_image[:, :, 2])
            if abs(self.bg_bright - avg_bright) < 10:
                return True
            else:
                return False
        else:
            return False

    def detect_ciyu(self, image):
        tl = self.gc.cal_ref_pose(*self.sets['cy_tl'])
        br = self.gc.cal_ref_pose(*self.sets['cy_br'])
        process_image = deepcopy(image[tl[1]:br[1], tl[0]:br[0]])
        gray_image = cv2.cvtColor(process_image, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_image, 160, 255, cv2.THRESH_BINARY)
        h, w = binary_img.shape
        process = binary_img[round(h / 2), 0:w]
        process_value = sum(p > 0 for p in process) / process.size
        return process_value

    def detect_finish(self, image):
        # image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        return self.check_exist(image, self.finish, 0.75)[0]

    def detect_kill(self, image):
        res = self.check_exist(image, self.up, 0.75)
        return res[0]

    def match_kill(self, image):
        import time
        tl = self.gc.cal_ref_pose(*self.sets['kill_tl'])
        br = self.gc.cal_ref_pose(*self.sets['kill_br'])
        process_image = deepcopy(image[tl[1]:br[1], tl[0]:br[0]])
        _, bin_image = cv2.threshold(process_image, 100, 255, cv2.THRESH_BINARY)
        results = self.kill_match.match(process_image)
        return results

    def stop_cap(self):
        self._running = False

    def start_cap(self):
        self._running = True

    def down_conf(self):
        self.kill_conf = self.kill_match.conf
        if self.kill_conf >= 0.5:
            self.kill_match.conf = self.kill_conf - 0.02
        else:
            self.kill_match.conf = 0.8
