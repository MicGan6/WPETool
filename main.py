import modules.tools as tools
import modules.UI as ui
import modules.wpe as wpe

if __name__ == "__main__":
    tools.pre_check()  # 检测环境
    config = tools.read_config()  # 读取config
    wpe.WPEApplication(
        width=config["UI"]["width"],
        height=config["UI"]["height"],
        line_sum=config["UI"]["line_sum"],
        workshop_path=config["Regular"]["workshop_path"]
    )
