import modules.tools as tools
import modules.UI as ui

if __name__ == "__main__":
    path: str = tools.get_path()  # 工坊路径
    """
    INFO存储所有壁纸信息，格式如下
    {文件夹 :{title: 标题,
            type: 类型
            preview_img: 预览图片
            wpf_path: 壁纸文件路径}}
    """
    info: dict[str, dict[str, str]] = tools.get_info(path)
    ui.MainWindow(info)
