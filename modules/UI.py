"""有关UI的类"""

from tkinter import Button, Tk, Scrollbar, Canvas
from PIL import ImageTk
# from modules.wpe import DetailWindow


class ImageButton(Button):
    """图片按钮类，继承自Button类"""

    def __init__(self, img: ImageTk.PhotoImage, info: dict[str, str], path: str, output_path: str):
        """
        Args:
            img: tk格式预览图的内存地址
            info: 该壁纸的信息
            path: 壁纸所在路径
            output_path: 输出路径
        """
        self.path = path
        self.info = info
        self.output_path = output_path
        super().__init__(image=img, command=self.command)

    def command(self) -> None:
        """
        创建详细信息窗口
        """
        DetailWindow(path=self.path, info=self.info, output_path=self.output_path)


class ButtonCanvas(Canvas):
    """图片按钮所在的父容器, 继承自Canvas类"""

    def __init__(self, size: tuple[int, int], master: Tk, scrollbar: Scrollbar):
        """
        Args:
            size: 画布的大小(x, y)
            master: 父容器
            scrollbar: 滑动条
        """
        self.x = size[0]
        self.y = size[1]
        self.master = master
        self.scrollbar = scrollbar
        super().__init__(
            master=self.master,
            width=self.x,
            height=self.y,
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set,
            yscrollincrement=10,
            scrollregion=(0, 0, self.x, self.y),
        )
        self.bind_mousewheel()
        self.focus_set()
        self.pack(fill="both", expand=True)

    def bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        # Windows/Linux的滚轮事件
        self.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """处理垂直滚动"""
        if event.num == 5 or event.delta == -120:  # 向下滚动
            self.yview_scroll(7, "units")
        elif event.num == 4 or event.delta == 120:  # 向上滚动
            self.yview_scroll(-7, "units")

    def update_scrollregion(self):
        """更新滚动区域，当内容变化时调用"""
        self.configure(scrollregion=self.bbox("all"))