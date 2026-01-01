import cmd
import time

class 交互(cmd.Cmd):
    def __init__(self, ):
        super().__init__()
        self.prompt = '> '

    def default(self, 行):
        开始 = time.time()
        数 = 0
        try:
          数 = int(行)
        except:
          回应 = f"{行} 不是数，请再试"
        回应 = f"得{数}"
        耗时 = (time.time() - 开始)*1000
        print(f"{回应} 耗时：{耗时}毫秒")


交互().cmdloop()