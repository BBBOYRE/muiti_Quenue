from Process import Process
import random
import heapq
from typing import Optional
from typing import Union
from typing import List
from typing import Tuple

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


class _PCB:
    ...


class _PCBHeap:
    ...


class ReadyQue:
    # 构建一个就绪队列需要: 算法, 队列优先级, 时间片长度
    def __init__(self, algo: str, priority: int, time_clip: int):      
        if algo != 'SJF' and algo != 'FIFO' and algo != 'HRRN':
            raise TypeError(f'{algo} is not a supported algorithm(FIFO, SJF, HRRN)')

        self._algorithm = algo
        self._que_priority = priority
        self._time_clip = time_clip

        self._pcb_heap = _PCBHeap()
        self._que_tot_time = 0

    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return len(self._pcb_heap) == 0

    # 将进程转换为pcb, 实际上是根据_algorithm变量打包一个优先级,相当于在原先的进程数据中添加一个优先级标识
    def _process2pcb(self, process: Process) -> _PCB:
        # 优先级越小, 越靠前, 这样heap时候就统一用小根堆了
        def get_priority(p: Process) -> float:
            if self._algorithm == 'FIFO':
                # 越早到达越优先
                return p._time_in_quenue
            elif self._algorithm == 'SJF':
                # 剩余时间越少越优先
                return p.time_get_rest()
            elif self._algorithm == 'HRRN':
                # 对于HRRN，优先级是动态的，在pop()中计算。
                # 在这里分配一个默认优先级。
                return 0
            
        return _PCB(process=process, priority=get_priority(process))

    # 向就绪队列中加入一个新的进程
    def offer(self, process: Process):

        from CPU_Core import CPU_core_clock #导入CPU时钟

        process.set_time_in_quenue(CPU_core_clock)

        pcb = self._process2pcb(process)
        self._pcb_heap.push(pcb)
        self._que_tot_time += process.time_get_rest()

    # 根据算法, 在队列中选择一个进程, 如果队列是空的, 返回一个闲逛进程的单例
    # 返回的是[进程, 计划时间]
    def pop(self) -> Union[Process, int]:
        from CPU_Core import CPU_core_clock # 必须在这里导入以获取当前时间

        if self.is_empty():
            return Process(name='HANGING', arrive_time=CPU_core_clock, tot_time=1, que_id=0), 1

        if self._algorithm == 'HRRN':
            # 对于HRRN，每次选择前都必须动态重新计算优先级，
            # 因为等待时间在不断变化。
            for pcb in self._pcb_heap._heap:
                p = pcb.process
                
                # 正确计算等待时间：在系统中的时间 - 已运行时间
                waiting_time = (CPU_core_clock - p.time_get_arrive()) - p.time_get_run()
                # 等待时间不能为负。
                if waiting_time < 0:
                    waiting_time = 0
                
                # 使用总服务时间计算响应比，这是HRRN的标准做法。
                service_time = p.time_get_total()

                # 响应比 = (等待时间 + 服务时间) / 服务时间
                if service_time > 0:
                    response_ratio = (waiting_time + service_time) / service_time
                    print(f"{pcb.process.get_name()}:{response_ratio}\n")
                else:
                    # 如果服务时间为0，则分配最高优先级以将其清除。
                    response_ratio = float('inf')

                # 更新PCB的优先级。我们使用负数，因为它是一个最小堆，
                # 而我们想要最高的响应比。
                pcb.priority = -response_ratio
            
            # 使用新计算的优先级重建堆属性。
            self._pcb_heap.reheapify()

        # 现在，弹出优先级最高的进程（即最小堆中最小的项）。
        top = self._pcb_heap.pop()
        
        if not top:
            return Process(name='HANGING', arrive_time=CPU_core_clock, tot_time=1, que_id=0), 1
            
        self._que_tot_time -= top.process.time_get_rest()
        assert self._que_tot_time >= 0
        return top.process, min(self._time_clip, top.process.time_get_rest())


    def get_que_tot_time(self) -> int:
        return self._que_tot_time

    def get_que_priority(self) -> int:
        return self._que_priority
    
    def maintain(self, curr_clk: int) -> None:
        #
        ...
    
    # 队列内的所有PCB返回为一个列表, 每个元素是List[str, int, int], 分别是进程名, 到达时间, 剩余时间
    def get_que_list(self) -> List[Tuple[str, int, int]]:
        res = []
        for pcb in self._pcb_heap._heap:
            p:Process = pcb.process
            temp = [p.get_name(), p.time_get_arrive(), p.time_get_rest()]
            res.append(temp)
        return res

# 就绪队列里实际上是PCB,只有两个内容, 进程和优先级
# 就绪队列会对PCB的优先级建堆
class _PCB:
    def __init__(self, process: Process, priority: float):
        self.process = process
        self.priority = priority

    # 自定义比较函数lt == less than, 重载 <
    def __lt__(self, other):
        return self.priority < other.priority


# 一个只能接受PCB类型的小根堆
class _PCBHeap:
    def __init__(self):
        self._heap = []

    def push(self, pcb: _PCB) -> None:
        if not isinstance(pcb, _PCB):
            raise TypeError("Only PCB objects can be added to this heap")
        heapq.heappush(self._heap, pcb)

    def pop(self) -> Optional[_PCB]:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def peek(self) -> Optional[_PCB]:
        if not self._heap:
            return None
        return self._heap[0]

    def reheapify(self) -> None:
        """以线性时间将列表重新组织成一个堆。"""
        heapq.heapify(self._heap)

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)
