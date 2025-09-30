# 文档4: Process.py
"""
进程Process类
类属性：
    进程名
    到达系统的时间
    完成该进程所需要的总时间
    队列ID


"""

"""
- 进程Process类:
- 构造需要进程名, 到达时间, 总时间, 归属队列id, 构造举例:
- process = Process(name='QQ', arrive_time=0, tot_time=5, que_id=1)
- 构造时会检查数据合法性

- 对外暴露的接口有:
- run_for_1clock(self), 进程运行一个时钟, 运行完会自动检查数据合法性
- get_pid, 返回pid
- get_que_id(self) -> int, 返回进程归属que_id
- is_dead(self) -> bool, 返回self._run_time == self._tot_time
- 一大堆time_get函数
- time_get_waiting(self) -> int, 等待时间
- time_get_rest(self) -> int, 距离完成任务剩余的时间
- time_get_arrive(self) -> int, 到达时间
- time_get_total(self) -> int, 总时间
- ime_get_run(self) -> int, 已经跑过的时间
- 这些函数在运行时候, 都会assert检查数据合法性

- 包含一个特殊的进程HANGING, 作为闲逛进程, 已经实例化
-   2024.9.20 现在觉得HANGING不应该是单例了
-   arrive_time, run_time 变来变去的
-   直接现场生成吧还是
"""


class Process:
    # 自动增加的类变量(静态变量), 用以分配pid
    # 每次实例化自动+1
    _next_id = 0

    def __init__(self, name: str, arrive_time: int, tot_time: int, que_id: int):
        self._pid = Process._next_id  # 自动分配pid, 0已经分配给闲逛
        Process._next_id += 1

        # Python的属性定义通过构造函数实现
        self._name = name  # 进程的名称，用于标识和显示，访问方式：通过get_name()公开访问
        self._arrive_time = arrive_time  # 记录进程到达系统的时间（以时钟周期为单位）
        self._tot_time = tot_time  # 进程总共需要运行的时间
        self._que_id = que_id  # 标识进程所属的就绪队列

        #进入最新队列的时间
        self._time_in_quenue = 0 #初始时间为到达系统的时间，后续会在每一次进入新队列时进行更新

        self._run_time = 0  # 最开始已经运行时间是0
        # 修改方式：通过run_for_lclock()方式每次增加1，或通过tiome_set_run()方式直接设置
        self._check_consistency()

    # debug_brief()是Process类中的一个调试方法，用于以易读的格式打印进程的详细信息。这个方法主要用于开发和调试阶段，帮助开发者快速来哦姐进程的当前状态
    def debug_brief(self):
        print(f'Process {self._name}:')
        print(f'pid={self._pid}, que_id={self._que_id}')
        print(
            f'arr_time={self._arrive_time}, tot_time={self._tot_time}, run_time={self._run_time}, rst_time={self.time_get_rest()}')

    # 进程合法性检查
    def _check_consistency(self):
        # 数值非负检查
        assert self._pid >= 0 and self._arrive_time >= 0 and self._tot_time > 0 and self._run_time >= 0
        assert self._que_id >= 0
        # 进程名字符串型检查
        assert isinstance(self._name, str)
        # 剩余时间有效性检查
        assert (self._tot_time - self._run_time >= 0)
    '''
    #原代码
    # 进程运行一个时钟单位
    def run_for_1clock(self):
        # assert self.run_time + add_time <= self.tot_time
        self._run_time += 1
        self._check_consistency()
    '''
    def run_for_1clock(self):
        # 确保运行时间不会超过总时间
        if self._run_time < self._tot_time:
            self._run_time += 1
        self._check_consistency()

    def get_pid(self) -> int:
        return self._pid

    def get_que_id(self) -> int:
        return self._que_id

    def get_name(self) -> str:
        return self._name

    def add_run_time(self):
        self._run_time+=1

    # 是否已经完成
    def is_dead(self) -> bool:
        return self._run_time == self._tot_time

    # 很多关于时间的变量, 这里约定凡是查询时间的, 都用time_get开头的函数
    #def time_get_waiting(self) -> int:
     #   def get_cpu_clock() -> int:
            # import main
            # return main.clock
      #      from CPU_Core import CPU_core_clock  # 使用局部导入来获取CPU内核时间
       #     return CPU_core_clock

        #waiting_time = get_cpu_clock() - self._arrive_time
        #assert waiting_time >= 0
        #return waiting_time
    #*******************************************************************修改的部分
    def time_get_waiting(self) -> int:
        # 避免循环导入，通过参数传递时钟值
        try:
            from CPU_Core import CPU_core_clock
            waiting_time = CPU_core_clock - self._arrive_time
        except ImportError:
            # 如果无法导入，返回一个默认值或抛出更明确的异常
            waiting_time = 0
        assert waiting_time >= 0
        return waiting_time

    def time_get_rest(self) -> int:  # 获取进程还需要运行的时间
        rest_time = self._tot_time - self._run_time
        #assert rest_time >= 0
        # 确保剩余时间不会为负数
        if rest_time < 0:
            rest_time = 0
        return rest_time
    
    def time_get_arrive(self) -> int:
        assert self._arrive_time >= 0
        return self._arrive_time

    def time_get_total(self) -> int:
        assert self._tot_time >= 0
        return self._tot_time
    
    # 修改已经运行的时间
    def time_set_run(self, run_time: int):
        assert run_time > self._run_time
        self._run_time = run_time

    def time_get_run(self) -> int:
        assert self._run_time >= 0
        return self._run_time
    
    #用于先进先服务算法的新增函数
    def time_get_in_quenue(self) -> int:
        assert self._tot_time >=0
        return self._time_in_quenue



    def set_time_in_quenue(self, time: int):
        """设置进程进入队列的时间"""
        self._time_in_quenue = time

    
        

        