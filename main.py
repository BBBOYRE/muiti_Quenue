# 文档2: main.py
from ReadyQue import ReadyQue
from Process import Process
from CPU_Core import CPU_Core
from ProcessGenerator import ProcessGenerator
#修改处*******************************************
from new_window_ui import MainWindow

if __name__ == '__main__':
    # 创建至少3个就绪队列，优先级从高到低，时间片递增
    rq1 = ReadyQue(algo='FIFO', priority=0, time_clip=2)  # 最高优先级，最短时间片
    rq2 = ReadyQue(algo='FIFO', priority=1, time_clip=4)  # 中等优先级，中等时间片
    rq3 = ReadyQue(algo='FIFO', priority=2, time_clip=8)  # 最低优先级，最长时间片

    # 可以添加更多队列
    rq4 = ReadyQue(algo='FIFO', priority=3, time_clip=16)
    rq5 = ReadyQue(algo='FIFO', priority=4, time_clip=32)

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

    app = MainWindow(ls1=ls1, ls2=ls2, cpu_core=cpu_core, process_generator=process_generator, rq_list=rq_list)
    app.mainloop()
