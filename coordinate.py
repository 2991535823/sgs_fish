
class GameCoordinate:
    def __init__(self,window_rect,bias_y):
        self.bias_y=bias_y
        self.window_rect=(window_rect[0],window_rect[1],window_rect[2],window_rect[3]-self.bias_y)
    def cal_pose(self,rel_x,rel_y):
        abs_x = self.window_rect[0] + self.window_rect[2] * rel_x
        abs_y = self.window_rect[1] + self.window_rect[3] * rel_y+self.bias_y
        return round(abs_x), round(abs_y)
    def cal_ref_pose(self,rel_x,rel_y):
        abs_x = self.window_rect[2] * rel_x
        abs_y = self.window_rect[3] * rel_y+self.bias_y
        return round(abs_x), round(abs_y)