# 文档2: main.py
import sys
from ReadyQue import ReadyQue
from Process import Process
from CPU_Core import CPU_Core
from ProcessGenerator import ProcessGenerator
from new_window_ui import MainWindow,FunctionSelector

if __name__ == '__main__':

    #在此处创建FunctionSelector
    selector = FunctionSelector()
    FunctionKey = selector.get_selection()
    
    # 如果用户直接关闭了算法选择窗口，则退出程序
    if FunctionKey  is None:
        print("用户取消了选择，程序退出")
        sys.exit(0)

    print(f"最终选择的算法: {FunctionKey}")

    #使用FunctionKEy
    rq1 = ReadyQue(algo=FunctionKey, priority=0, time_clip=2)  # 最高优先级，最短时间片
    rq2 = ReadyQue(algo=FunctionKey, priority=1, time_clip=4)  # 中等优先级，中等时间片
    rq3 = ReadyQue(algo=FunctionKey, priority=2, time_clip=8)  # 最低优先级，最长时间片
    rq4 = ReadyQue(algo=FunctionKey, priority=3, time_clip=16)
    rq5 = ReadyQue(algo=FunctionKey, priority=4, time_clip=32)

    rq_list = [rq1, rq2, rq3, rq4, rq5]

    cpu_core = CPU_Core(rq_list)
    process_generator = ProcessGenerator(rq_list)

    # 界面显示设置
    ls1 = [
        ['Queue 1 (Prio:0, Time:2)', []],
        ['Queue 2 (Prio:1, Time:4)', []],
        ['Queue 3 (Prio:2, Time:8)', []],
        ['Queue 4 (Prio:3, Time:16)', []],
        ['Queue 5 (Prio:4, Time:32)', []]
    ]
    ls2 = [
        ['Waiting Queue', []],
        ['CPU', []]
    ]

    #将FunctionKey传给MainWindow
    app = MainWindow(ls1=ls1, ls2=ls2, cpu_core=cpu_core, process_generator=process_generator, rq_list=rq_list, function_key=FunctionKey)
    app.mainloop()
