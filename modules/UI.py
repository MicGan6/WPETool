"""有关UI的类"""

from tkinter import Button, Tk, Scrollbar, Canvas
from PIL import ImageTk
from modules.wpe import DetailWindow


class ImageButton(Button):
    """图片按钮类，继承自Button类"""

    def __init__(self, img: ImageTk.PhotoImage, info: dict[str, str], path: str):
        """
        :param img: tk格式预览图的内存地址
        :param info: 该壁纸的信息
        """
        self.path = path
        self.info = info
        super().__init__(image=img, command=self.command)

    def command(self) -> None:
        """
        创建详细信息窗口
        :return:
        """
        DetailWindow(path=self.path, info=self.info)


class ButtonCanvas(Canvas):
    """图片按钮所在的父容器, 继承自Canvas类"""

    def __init__(self, size: tuple[int, int], master: Tk, scrollbar: Scrollbar):
        """
        :param size: 画布的大小(x, y)
        :param master: 父容器
        :param scrollbar: 滑动条
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
        self.bind("<mouse_wheel>", self.on_mousewheel)
        self.pack(fill="both", expand=True)
    def on_mousewheel(self, event):
        self.yview_scroll(int(-1 * (event.delta / 120)), "units")


def Center(root: Tk, width: int, height: int, office: int = 0):
    root.geometry(
        f"{width}x{height}+{(root.winfo_screenwidth()-width)//2}+{(root.winfo_screenheight()-height)//2+office}"
    )
