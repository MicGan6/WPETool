"""
Main Process
"""

from tkinter import Toplevel, Tk, Label, Scrollbar, X, Y, LEFT, RIGHT, VERTICAL, Button, messagebox
from PIL import Image, ImageTk
import modules.tools as tools
from threading import Thread
from loguru import logger
import modules.UI as UI
import time


class DetailWindow(Toplevel):
    """壁纸详细信息窗口"""

    def __init__(self, path:str, info: dict[str, str]):
        """
        :param path: 壁纸所在文件夹
        :param info:该壁纸的详细信息
        """
        super().__init__()
        self.path = path
        UI.Center(self, 500, 400)  # 居中 500 * 400 窗口
        self.preview_img = info["preview_img"]  # 预览图片内存地址
        self.title: str = info["title"]  # 壁纸标题
        self.type: str = info["type"]  # 壁纸类型
        self.wpf_path: str = info.get("wpf_path", None)
        self.img_label: Label  # 预览图的标签
        self.title_label: Label
        self.type_label: Label
        self.extract_button: Button
        self.create_label()

    def create_label(self) -> None:
        """
        创建图片和标题
        """
        logger.info(f'所选壁纸信息{self.path}')
        self.img_label = Label(master=self, image=self.preview_img)
        self.img_label.pack()
        self.title_lavel = Label(master=self, text=self.title)
        self.title_lavel.place(y=200)
        self.type_label = Label(master=self, text=f"类型: {self.type}")
        self.type_label.place(y=230)
        self.extract_button = Button(master=self, text="导出", command=self.extract)
        self.extract_button.place(y=250)

    def extract(self):
        if self.wpf_path != None:
            if self.type == "scene" :
                tools.extract_pkg(self.wpf_path, self.title)
            elif self.type == "video":
                tools.extract_mp4(self.wpf_path, self.title)
        else:
            messagebox.showwarning('警告', '未找到该壁纸本体文件，无法导出')



class WPEApplication(Tk):
    """主进程"""

    def __init__(self):
        super().__init__()  # 调用tkinter.TK的构造函数
        self.info: dict[str, dict[str, str]]
        # 计算Button坐标时要用到的变量
        self.x: int  # 横坐标
        self.y: int  # 纵坐标
        self.line: int = 0  # Button在第几行
        self.button_canvas: UI.ButtonCanvas  # 按钮的父容器
        self.scrollbar: Scrollbar  # 滑动条
        self.loading_label: Label  # 加载中文字
        UI.Center(self, 970, 700, -50)  # 居中 970 * 700 向上偏移 50 窗口
        self.title("Wallpaper Engine: 壁纸引擎 第三方工具")
        self.resizable(False, False)
        self.loading_ui()
        # self.after(10, self.setup)
        thr = Thread(target=self.setup)
        thr.start()
        # self.setup()
        self.mainloop()  # 启动！（保持主进程循环）

    def loading_ui(self):
        self.loading_label = Label(self, text="加载中...", font=("Microsoft YaHei", 20))
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.update()
        self.loading_label.update()

    def setup(self):
        """
        实现异步初始化
        """
        """
        INFO存储所有壁纸信息，格式如下
        {文件夹 :{title: 标题,
                type: 类型
                preview_img: 预览图片
                wpf_path: 壁纸文件路径}}
        """
        self.path: str = tools.get_path()
        self.info: dict[str, dict[str, str]] = tools.get_info(self.path)
        # logger.info(f"tools info: {self.info}")
        time.sleep(5)
        self.after(1, self.loading_label.destroy)
        self.after(100, self.setup_ui)

    def setup_ui(self):
        self.create_canvas()  # 创建ButtonCanvas
        self.scrollbar.configure(command=self.button_canvas.yview)
        self.deal_image()  # 处理图片
        self.create_button()  # 创建按钮

    def deal_image(self) -> None:
        """
        处理预览图片
        """
        for key, value in self.info.items():
            self.info[key]["preview_img"] = self._deal_image(value["preview_img"])

    def create_button(self) -> None:
        """
        创建Button
        """

        """
        此处修改info，格式如下
        {文件夹 :{title: 标题,
                type: 类型
                preview_img: 预览图片(tk格式)
                wpf_path: 壁纸文件路径
                button: 按钮组件所在内存地址}}
        """
        flag: int = 1  # 第几个壁纸
        max_x = 0  # 记录最大x坐标（用于更新scrollregion）
        max_y = 0  # 记录最大y坐标
        for key, value in self.info.items():
            self.calc_xy(flag=flag)
            # logger.info(f"flag:{flag}, x: {self.x}, y: {self.y}")
            # 创建按钮（不在这里放置）
            btn = UI.ImageButton(img=value["preview_img"], path = key, info=value)
            # 用Canvas的create_window将按钮嵌入Canvas，坐标为(self.x, self.y)
            self.button_canvas.create_window(
                self.x, self.y, window=btn, anchor="nw"  # anchor="nw"表示左上角对齐
            )
            self.info[key]["button"] = btn  # 存储按钮引用
            # 更新最大x和y（按钮大小100x100，所以最大坐标需加100）
            current_max_x = self.x + 100
            current_max_y = self.y + 100
            if current_max_x > max_x:
                max_x = current_max_x
            if current_max_y > max_y:
                max_y = current_max_y
            flag += 1

        # 所有按钮创建后，更新Canvas的scrollregion为包含所有按钮的区域
        self.button_canvas.configure(scrollregion=(0, 0, max_x, max_y))

    def _deal_image(self, img: str) -> ImageTk.PhotoImage:
        """
        处理预览图片(辅助方法)
        :param img: 预览图片路径
        :return: tk格式的预览图地址
        """
        # logger.info(f"识别图片地址：{img}")
        image = Image.open(img)
        image = ImageTk.PhotoImage(
            image.resize((100, 100))
        )  # 将图片类型适应tkinter并设置大小
        return image

    def calc_xy(self, flag: int) -> None:
        """
        计算按钮横纵坐标
        :param flag: 第几个壁纸
        """
        if flag == 1:
            self.x, self.y, self.line = 0, 0, 0
        else:
            if flag // 9 <= self.line or flag % 9 == 0:
                self.x += 100
            elif flag // 9 > self.line:
                self.x = 0
                self.y += 100
                self.line = flag // 9

    def create_canvas(self):
        """创建Canvas和Scrollbar"""
        self.scrollbar = Scrollbar(master=self, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        flag = len(self.info.keys())
        # 得到最后一个按钮的位置
        x: int = 9 * 100
        y: int = (flag // 9) * 100
        logger.info(f"Canvas大小: {x,y}")
        self.button_canvas = UI.ButtonCanvas(
            size=(x, y), master=self, scrollbar=self.scrollbar
        )
        self.scrollbar.configure(command=self.button_canvas.yview)
