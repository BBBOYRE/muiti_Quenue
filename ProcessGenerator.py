# 文档5: ProcessGenerator.py
from Process import Process
from ReadyQue import ReadyQue
import random
from shuffle_utils import infinite_shuffled_reproducible
process_cnt = 0
"""
ProcessGenerator.run_for_1clk()
ProcessGenerator类中的核心方法，负责在每个时钟周期随机生成新进程并将其添加到合适的就绪队列中
"""


class ProcessGenerator:
    def __init__(self, ls: list[ReadyQue]) -> None:
        self._rq_list = ls
        self._process_generator = infinite_shuffled_reproducible(0, 1, 0.01, 42)
        self._process_time_generator = infinite_shuffled_reproducible(2, 10, 1, 99)
    def run_for_1clk(self) -> None:
        global process_cnt
        from CPU_Core import CPU_core_clock

        # 随机生成新进程（10%概率）
        if next(self._process_generator) < 0.10:
            process_cnt += 1
            t = next(self._process_time_generator)  # 随机生成进程的总运行时间
            # 新进程总是进入最高优先级队列（队列0）
            self._rq_list[0].offer(Process(name=f'P{process_cnt}', arrive_time=CPU_core_clock, tot_time=t, que_id=0))
            print(f"Generated new process: P{process_cnt}, Total Time = {t}")