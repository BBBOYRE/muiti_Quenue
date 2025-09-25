# 文档6: ReadyQue.py
from Process import Process
import random
import heapq
from typing import Optional
from typing import Union
from typing import List
from typing import Tuple
from collections import deque
"""
- 就绪队列ReadyQue类:
- 构造需要算法('FIFO', 'SJF', 'HRRN'), 队列优先级(用于区分多级反馈队列), 队列时间片长度, 举例构造:
- ready_que = ReadyQue(algo='SJF', priority=2, time_clip=5), 约定优先级越小越优先
- 下划线开头的变量/方法都是私有的

- 对外暴露的接口有这些:
- offer(self, process: Process), 给当前队列加入一个进程
- pop(self) -> [Process, int], 当前队列根据算法弹出一个进程, 并返回计划时间片, 计划时间片是队列时间片和进程剩余时间的最小值
- get_que_tot_time(self) -> int, 返回队列中所有进程的剩余时间

- ReadyQue类里面没有que_id, 这个在主函数做比较好
- main里随意实例化几个que都可以, 然后主函数做个字典之类的, 来决定每个队列的id
"""



class ReadyQue:
    # 构建一个就绪队列需要: 算法, 队列优先级, 时间片长度
    def __init__(self, algo: str, priority: int, time_clip: int):
        if algo != 'FIFO':
            raise TypeError(f'{algo} is not a supported algorithm(only FIFO is supported)')

        self._algorithm = algo
        self._que_priority = priority
        self._time_clip = time_clip

        # 使用deque作为FIFO队列
        self._process_queue = deque()
        self._que_tot_time = 0

    # 向就绪队列中加入一个新的进程
    def offer(self, process: Process):
        self._process_queue.append(process)
        self._que_tot_time += process.time_get_rest()

    # 根据FIFO算法, 在队列中选择一个进程, 如果队列是空的, 返回一个闲逛进程的单例
    # 返回的是[进程, 计划时间]
    def pop(self) -> Union[Process, int]:
        if not self._process_queue:
            from CPU_Core import CPU_core_clock
            return Process(name='HANGING', arrive_time=CPU_core_clock, tot_time=1, que_id=0), 1

        process = self._process_queue.popleft()
        self._que_tot_time -= process.time_get_rest()
        assert self._que_tot_time >= 0
        return process, min(self._time_clip, process.time_get_rest())

    def get_que_tot_time(self) -> int:
        return self._que_tot_time

    def get_que_priority(self) -> int:
        return self._que_priority

    def maintain(self, curr_clk: int) -> None:
        # 更新队列中所有进程的等待时间
        # 对于多级反馈队列，这里可以实现老化策略
        pass

    # 队列内的所有PCB返回为一个列表, 每个元素是List[str, int, int], 分别是进程名, 到达时间, 剩余时间
    def get_que_list(self) -> List[Tuple[str, int, int]]:
        res = []
        for process in self._process_queue:
            temp = [process.get_name(), process.time_get_arrive(), process.time_get_rest()]
            res.append(temp)
        return res

    def is_empty(self):
        return len(self._process_queue) == 0


