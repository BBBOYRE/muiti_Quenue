# 修改后的文档1: CPU_Core.py
from ReadyQue import ReadyQue
from Process import Process
from typing import Any
from typing import List
from typing import Union
import random
from prettytable import PrettyTable
from shuffle_utils import infinite_shuffled_reproducible
# CPU时钟，当开始模拟那一刻开始计时
CPU_core_clock = 0
CPU_busy_time = 0  # CPU繁忙时间

class CPU_Core:
    def __init__(self, que_list: List[ReadyQue]) -> None:
        if not que_list:
            raise ValueError(f'Waiting queue list cannot be empty!')
        self.jam_waiting_list = True  # 控制是否阻塞等待队列的处理          该属性其实已经被删除，只是进行保留
        self.io_allow = True  # 控制是否允许IO中断              将随机中断修改为控制io中断后的关键字
        self._que_list = que_list  # 存储所有就绪队列的列表
        self._process_on_core: Process = None  # 当前在CPU上执行的程序，初始值为None
        self._scheduled_time = 0  # 当前进程计划再跑多长时间
        self._open_4interrupt = True  # 初始情况可以中断,控制是否允许中断
        self.user_require_interrupt = False  # 用户请求中断的标志
        # 等待队列只能存放一个被打断的进程
        self._waiting_process = None  # 修改为单个进程而不是队列             等待队列中只允许有一个进程，因此设计成了单个
        self.completed_processes = []  # 用于存储已完成的进程           当进程dead后，将会进入该数组
        self.io_interrupts = []  # 存储IO中断信息
        self.io_completion_times = {}  # 存储IO完成时间             若有当前CPU_Core io_completion_times, 则说明有IO complete
         # 新增的统计指标
        self.total_waiting_time = 0  # 总等待时间
        self.total_turnaround_time = 0  # 总周转时间
        self.total_service_time = 0  # 总服务时间
        self.total_weighted_turnaround_time = 0  # 总带权周转时间
        self.cpu_total_time = 0  # CPU总运行时间        iocreator = infinite_shuffled_reproducible(0, 1, 0.01, seed=42)
        self._io_creator = iocreator
        iotimegen = infinite_shuffled_reproducible(3, 8, 1, seed=99)
        self._io_time_gen = iotimegen
    # if que 有问题
    #在 run_for_1clk中被调用
    def _get_next_process(self) -> Union[Process, int]:
        for que in self._que_list:                   #从 ReadyQue 中 pop a process, when ReadyQue is empty, it will pop a hanging process
            temp, t = que.pop()
            if temp.get_name() != 'HANGING':
                return temp, t
        return self._que_list[0].pop()

    def _has_higher_priority_process(self, current_que_id):
        """检查是否有比当前队列优先级更高的队列中有进程"""
        for i in range(0, current_que_id):
            if not self._que_list[i].is_empty():
                return True
        return False



    def run_for_1clk(self) -> None:
        global CPU_core_clock
        global CPU_busy_time
        
        # 先记录当前是否有用户进程在运行（用于统计繁忙时间）
        has_user_process_before = (self._process_on_core and 
                                self._process_on_core.get_name() != 'HANGING' and 
                                "Interrupt" not in self._process_on_core.get_name())
        
        # 时钟递增
        CPU_core_clock += 1
        self.cpu_total_time += 1
        
        # 检查IO完成事件
        self._check_io_completion()

        # 维护所有队列
        for que in self._que_list:
            que.maintain(CPU_core_clock)

        if self._scheduled_time <= 0:
            # 如果当前安排的时间耗尽
            if self._process_on_core and "Interrupt" in self._process_on_core.get_name():
                # 如果做完的任务是中断, 唤醒, 开中断
                if not self.jam_waiting_list:
                    self._awake_waiting_list()
                self._open_4interrupt = True
                
            # 如果做完了, 扔掉, 记录, 否则进等待队列
            if self._process_on_core:
                if self._process_on_core.time_get_rest() <= 0:
                    self._throw_away()
                elif self._process_on_core.get_name() != 'HANGING':
                    # 进程未完成，降级到下一优先级队列
                    self._demote_process(self._process_on_core)
                self._process_on_core = None

        if not self.jam_waiting_list:
            self._awake_waiting_list()

        interrupt, scheduled_time = self._interrupt_happen()
        if interrupt is not None and self._open_4interrupt:
            # 如果来了新中断, 且开中断, 就安排新中断
            self._scheduled_time = scheduled_time
            if self._process_on_core and self._process_on_core.get_name() != 'HANGING':
                if self._waiting_process is None:
                    self._waiting_process = self._process_on_core
                    self._open_4interrupt = False
            self._process_on_core = interrupt

        # 检查是否有更高优先级的进程需要抢占
        if (self._process_on_core and
                self._process_on_core.get_name() != 'HANGING' and
                "Interrupt" not in self._process_on_core.get_name()):
            current_que_id = self._process_on_core.get_que_id()
            if current_que_id > 0 and self._has_higher_priority_process(current_que_id):
                self._que_list[current_que_id].offer(self._process_on_core)
                self._process_on_core = None
                self._scheduled_time = 0

        if not self._process_on_core:
            # 如果还没事做, 就问反馈队列要一个
            self._process_on_core, self._scheduled_time = self._get_next_process()

        # 关键修改：在运行进程之前统计繁忙时间
        # 判断当前是否有用户进程要运行（非空闲、非中断）
        has_user_process_now = (self._process_on_core and 
                            self._process_on_core.get_name() != 'HANGING' and 
                            "Interrupt" not in self._process_on_core.get_name())
        
        # 如果有用户进程运行，增加繁忙时间
        if has_user_process_now:
            CPU_busy_time += 1

        # 跑一个时钟
        self._scheduled_time -= 1
        if self._process_on_core:
            self._process_on_core.run_for_1clock()
            # 检查运行后进程是否完成
            if self._process_on_core.time_get_rest() <= 0:
                self._throw_away()
                self._scheduled_time = 0

        # 随机生成IO请求
        self._generate_io_events()

        self._brief()

    # 打印当前时钟的进程信息
    def _brief(self):
        global CPU_core_clock
        process_name = self._process_on_core.get_name() if self._process_on_core else "None"
        print(f'clock {CPU_core_clock}: {process_name}, ', end='')
        print(f'scheduled_time={self._scheduled_time}')

        # 唤醒等待队列的进程

    def _awake_waiting_list(self):
        if self._waiting_process is not None:
            process = self._waiting_process
            original_que_id = process.get_que_id()
            if original_que_id < len(self._que_list):
                self._que_list[original_que_id].offer(process)

            self._waiting_process = None
            self._open_4interrupt = True

        # 修改 _throw_away 方法，只将用户进程计入已完成进程
    def _throw_away(self):
        if self._process_on_core:
            process = self._process_on_core
            
            # 检查是否为用户进程（非中断、非闲逛进程）
            is_user_process = (process.get_name() != 'HANGING' and 
                            "Interrupt" not in process.get_name())
            
            if is_user_process:
                # 计算进程的各项时间指标
                turnaround_time = CPU_core_clock - process.time_get_arrive()  # 周转时间
                waiting_time = turnaround_time - process.time_get_total()  # 等待时间
                service_time = process.time_get_total()  # 服务时间
                weighted_turnaround_time = turnaround_time / service_time  # 带权周转时间
                
                # 累加到总统计中
                self.total_waiting_time += waiting_time
                self.total_turnaround_time += turnaround_time
                self.total_weighted_turnaround_time += weighted_turnaround_time
                
                self.completed_processes.append({
                    'pid': process.get_pid(),
                    'name': process.get_name(),
                    'arrive_time': process.time_get_arrive(),
                    'tot_time': service_time,
                    'run_time': process.time_get_run(),
                    'que_id': process.get_que_id(),
                    'turnaround_time': turnaround_time,
                    'waiting_time': waiting_time,
                    'weighted_turnaround_time': weighted_turnaround_time
                })
        
        self._process_on_core = None

        # 返回None, None 或者[Process, int]

    def _interrupt_happen(self):
        global CPU_core_clock
        if self.user_require_interrupt:
            self.user_require_interrupt = False
            t = random.randint(4, 6)
            return Process(name="USER Interrupt", arrive_time=CPU_core_clock, tot_time=t, que_id=0), t
        # 删除随机中断生成
        return None, None

    def get_now_onboard(self):
        res = []
        if self._process_on_core:
            temp = [self._process_on_core.get_name(), self._process_on_core.time_get_arrive(),
                    self._process_on_core.time_get_rest()]
            res.append(temp)
        return res

    def get_waiting_list(self):
        # 返回等待进程的列表表示
        res = []
        if self._waiting_process is not None:
            temp = [self._waiting_process.get_name(), self._waiting_process.time_get_arrive(),
                    self._waiting_process.time_get_rest()]
            res.append(temp)
        return res

    def get_cpu_clock(self) -> int:
        global CPU_core_clock
        return CPU_core_clock

    def generate_and_save_table(self, filename):
        table = PrettyTable()
        table.field_names = ["PID", "Name", "Arrive Time", "Total Time", "Run Time", "Queue ID"]

        for process in self.completed_processes:
            table.add_row([
                process['pid'],
                process['name'],
                process['arrive_time'],
                process['tot_time'],
                process['run_time'],
                process['que_id']
            ])

        with open(filename, 'w') as f:
            f.write(str(table))

    def _demote_process(self, process):
        """将进程降级到下一优先级队列，如果已经在最低优先级，则重新放回最高优先级"""

        from CPU_Core import CPU_core_clock  #导入CPU时钟，用于更新进程进入队列的时间




        current_que_id = process.get_que_id()
        if current_que_id == len(self._que_list) - 1:
            # 如果在最低优先级队列，则重新放回最高优先级队列
            next_que_id = 0
        else:
            next_que_id = current_que_id + 1
        
        process.set_time_in_quenue(CPU_core_clock)
        process._que_id = next_que_id
        self._que_list[next_que_id].offer(process)

    def _generate_io_events(self):
        """随机生成IO请求和完成事件"""
        global CPU_core_clock

        # 检查是否允许IO中断
        if not self.io_allow:
            return

        # 随机生成IO请求（当前运行进程有10%概率发起IO请求）
        if (self._process_on_core and
                self._process_on_core.get_name() != 'HANGING' and
                "Interrupt" not in self._process_on_core.get_name() and
                next(self._io_creator) < 0.10):

            # 检查等待队列是否已满（只能有一个进程）
            if self._waiting_process is not None:
                print("Waiting queue is full, cannot add IO request")
                return

            io_time = next(self._io_time_gen)
            self.io_interrupts.append({
                'process': self._process_on_core,
                'start_time': CPU_core_clock,
                'duration': io_time
            })
            self.io_completion_times[CPU_core_clock + io_time] = self._process_on_core

            print(
                f"Process {self._process_on_core.get_name()} requests IO, will complete at {CPU_core_clock + io_time - 1}")

            # 将当前进程放入等待队列（只能有一个进程）
            self._waiting_process = self._process_on_core
            self._process_on_core = None
            self._scheduled_time = 0
            # 等待队列满时禁止中断
            self._open_4interrupt = False

        # 检查IO完成事件
        self._check_io_completion()

    def _check_io_completion(self):
        """检查并处理IO完成事件"""
        global CPU_core_clock

        # 检查是否有IO完成
        if CPU_core_clock in self.io_completion_times:
            process = self.io_completion_times[CPU_core_clock]
            print(f"IO completed for process {process.get_name()}")

            process.set_time_in_quenue(CPU_core_clock)

            # 将进程放回原来的队列
            original_que_id = process.get_que_id()
            if original_que_id < len(self._que_list):
                self._que_list[original_que_id].offer(process)
            # 添加了如下一段代码，解决等待队列未更新问题
            # 如果完成的进程是等待队列中的进程，则清除等待队列
            if self._waiting_process == process:
                self._waiting_process = None
                # 等待队列空时允许中断
                self._open_4interrupt = True

            # 移除已完成的IO事件
            del self.io_completion_times[CPU_core_clock]

                # 添加获取新指标的方法
    def get_performance_metrics(self):
        """获取性能指标"""
        completed_count = len(self.completed_processes)
        
        if completed_count > 0:
            avg_waiting_time = self.total_waiting_time / completed_count
            avg_turnaround_time = self.total_turnaround_time / completed_count
            avg_weighted_turnaround_time = self.total_weighted_turnaround_time / completed_count
        else:
            avg_waiting_time = avg_turnaround_time = avg_weighted_turnaround_time = 0
        
        # 使用全局的CPU_busy_time而不是实例变量
        global CPU_busy_time
        cpu_utilization = (CPU_busy_time / self.cpu_total_time * 100) if self.cpu_total_time > 0 else 0
        
        return {
            'avg_waiting_time': avg_waiting_time,
            'avg_turnaround_time': avg_turnaround_time,
            'avg_weighted_turnaround_time': avg_weighted_turnaround_time,
            'cpu_utilization': cpu_utilization,
            'cpu_total_time': self.cpu_total_time,
            'total_service_time': CPU_busy_time,  # 使用全局CPU_busy_time
            'completed_count': completed_count
        }
    
        # 在CPU_Core类中添加以下方法
    def save_system_info_to_file(self):
        """将当前系统信息保存到文件"""
        filename = "System_information.txt"
        try:
            metrics = self.get_performance_metrics()
            completed = metrics['completed_count']
            total = completed + sum(len(q.get_que_list()) for q in self._que_list)
            
            with open(filename, 'a', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write(f"系统信息快照 (时钟周期: {CPU_core_clock})\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("性能指标:\n")
                f.write("-" * 30 + "\n")
                f.write(f"已完成进程数: {completed}\n")
                f.write(f"总进程数: {total}\n")
                f.write(f"平均周转时间: {metrics['avg_turnaround_time']:.2f}\n")
                f.write(f"平均等待时间: {metrics['avg_waiting_time']:.2f}\n")
                f.write(f"平均带权周转时间: {metrics['avg_weighted_turnaround_time']:.2f}\n")
                f.write(f"CPU利用率: {metrics['cpu_utilization']:.2f}%\n")
                f.write(f"CPU总运行时间: {metrics['cpu_total_time']}\n")
                f.write(f"总服务时间: {metrics['total_service_time']}\n\n")
                
                f.write("就绪队列状态:\n")
                f.write("-" * 30 + "\n")
                for i, que in enumerate(self._que_list):
                    que_list = que.get_que_list()
                    f.write(f"队列 {i+1}: {len(que_list)} 个进程\n")
                    for j, process in enumerate(que_list):
                        f.write(f"  进程 {j+1}: {process[0]} (到达: {process[1]}, 剩余: {process[2]})\n")
                    f.write("\n")
                
                f.write("当前运行进程:\n")
                f.write("-" * 30 + "\n")
                if self._process_on_core:
                    f.write(f"进程名: {self._process_on_core.get_name()}\n")
                    f.write(f"到达时间: {self._process_on_core.time_get_arrive()}\n")
                    f.write(f"剩余时间: {self._process_on_core.time_get_rest()}\n")
                    f.write(f"队列ID: {self._process_on_core.get_que_id()}\n")
                else:
                    f.write("无进程运行\n")
                f.write("\n")
                
                f.write("等待队列:\n")
                f.write("-" * 30 + "\n")
                if self._waiting_process:
                    f.write(f"进程名: {self._waiting_process.get_name()}\n")
                    f.write(f"到达时间: {self._waiting_process.time_get_arrive()}\n")
                    f.write(f"剩余时间: {self._waiting_process.time_get_rest()}\n")
                    f.write(f"队列ID: {self._waiting_process.get_que_id()}\n")
                else:
                    f.write("等待队列为空\n")
                f.write("\n")
                
                f.write("IO事件:\n")
                f.write("-" * 30 + "\n")
                if self.io_completion_times:
                    for comp_time, process in self.io_completion_times.items():
                        f.write(f"{process.get_name()}: 将在时钟 {comp_time} 完成IO\n")
                else:
                    f.write("无IO事件\n")
                f.write("\n")
                
                f.write("已完成进程列表:\n")
                f.write("-" * 30 + "\n")
                if self.completed_processes:
                    for i, proc in enumerate(self.completed_processes):
                        f.write(f"{i+1}. {proc['name']} (PID: {proc['pid']})\n")
                        f.write(f"   到达时间: {proc['arrive_time']}, 总时间: {proc['tot_time']}\n")
                        f.write(f"   周转时间: {proc['turnaround_time']}, 等待时间: {proc['waiting_time']}\n")
                        f.write(f"   带权周转时间: {proc['weighted_turnaround_time']:.2f}\n")
                else:
                    f.write("暂无已完成进程\n")
            
            print(f"系统信息已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"保存系统信息失败: {e}")
            return None
