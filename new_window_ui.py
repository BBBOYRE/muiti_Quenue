# 修改后的文档3: MainWindow.py - 新UI设计
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import random
import string
from Process import Process
from ReadyQue import ReadyQue


class MainWindow(tk.Tk):
    def __init__(self, ls1, ls2, cpu_core, process_generator, rq_list):
        """
        初始化主窗口
        """
        super().__init__()  # 初始化父类

        self.ls1 = ls1  # 存储各个就绪队列的列表
        self.ls2 = ls2
        self.cpu_core = cpu_core
        self.process_generator = process_generator
        self.rq_list = rq_list
        self.auto_gen = True
        self.user_require_interrupt = False
        self.current_scroll_area = None  # 绑定鼠标滚轮

        # 设置窗口标题和大小
        self.title("操作系统课设 - 多级反馈队列调度模拟")
        self.geometry("1200x800")  # 减小窗口高度
        self.configure(bg="#f8f9fa")  # 设置浅灰色背景

        # 初始化存储区域列表
        self.areas = []

        # 现代配色方案
        self.primary_color = "#4f46e5"  # 主色调
        self.secondary_color = "#6366f1"  # 次要色调
        self.accent_color = "#10b981"  # 强调色
        self.danger_color = "#ef4444"  # 危险/警告色
        self.light_bg = "#f3f4f6"  # 浅背景色
        self.dark_text = "#1f2937"  # 深色文字

        # 创建样式
        self.setup_styles()

        # 创建主容器（带滚动条）
        self._create_main_container()

        # 创建顶部标题
        self.create_header()

        # 创建主体内容区域
        self.create_content_area()

        # 创建底部按钮区域
        self.create_button_area()

        # 初始化内容
        self.refresh_content()

        # 自动刷新标志和任务ID
        self.auto_refresh = False
        self.auto_refresh_task = None

        # 绑定全局鼠标滚轮事件（添加）
        self.bind_all("<MouseWheel>", self.bind_global_mousewheel)

    def setup_styles(self):
        """设置自定义样式"""
        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题作为基础

        # 配置标签样式
        style.configure('Header.TLabel',
                        font=('Arial', 16, 'bold'),  # 减小字体大小
                        foreground=self.primary_color,
                        background=self.light_bg)

        # 配置按钮样式
        style.configure('Primary.TButton',
                        font=('Arial', 9, 'bold'),  # 减小字体大小
                        background=self.primary_color,
                        foreground='white',
                        padding=(8, 4))  # 减小内边距

        style.configure('Secondary.TButton',
                        font=('Arial', 9),
                        background=self.light_bg,
                        foreground=self.dark_text,
                        padding=(8, 4))

        style.configure('Accent.TButton',
                        font=('Arial', 9),
                        background=self.accent_color,
                        foreground='white',
                        padding=(8, 4))

        style.configure('Danger.TButton',
                        font=('Arial', 9),
                        background=self.danger_color,
                        foreground='white',
                        padding=(8, 4))

        # 配置框架样式
        style.configure('Card.TFrame',
                        background='white',
                        relief='raised',
                        borderwidth=1)

        style.configure('Info.TFrame',
                        background=self.light_bg,
                        relief='flat')

    def _create_main_container(self):
        """创建主容器并提供垂直滚动条"""
        self.main_container = ttk.Frame(self, style='Info.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.main_canvas = tk.Canvas(self.main_container, bg=self.light_bg, highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.main_frame = ttk.Frame(self.main_canvas, padding=10)
        self.main_window = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.main_frame.bind("<Configure>", self._on_main_frame_configure)
        self.main_canvas.bind("<Configure>", self._on_main_canvas_configure)

    def create_header(self):
        """创建顶部标题区域"""
        header_frame = ttk.Frame(self.main_frame, style='Info.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))  # 减小垂直间距

        title_label = ttk.Label(header_frame,
                                text="多级反馈队列调度模拟系统",
                                style='Header.TLabel')
        title_label.pack(pady=8)  # 减小垂直间距

        # CPU时钟显示
        clock_frame = ttk.Frame(header_frame, style='Card.TFrame')
        clock_frame.pack(side=tk.LEFT, padx=8, pady=4)  # 减小内边距

        ttk.Label(clock_frame,
                  text="CPU时钟:",
                  font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=4)  # 减小字体大小和内边距

        self.cpu_clock_label = ttk.Label(clock_frame,
                                         text="0",
                                         font=('Arial', 10, 'bold'),  # 减小字体大小
                                         foreground=self.primary_color)
        self.cpu_clock_label.pack(side=tk.LEFT, padx=4)  # 减小内边距

        # 状态指示器
        status_frame = ttk.Frame(header_frame, style='Card.TFrame')
        status_frame.pack(side=tk.RIGHT, padx=8, pady=4)  # 减小内边距

        ttk.Label(status_frame,
                  text="自动生成:",
                  font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=4)  # 减小字体大小和内边距

        self.auto_gen_label = ttk.Label(status_frame,
                                        text="开启",
                                        font=('Arial', 9),  # 减小字体大小
                                        foreground=self.accent_color)
        self.auto_gen_label.pack(side=tk.LEFT, padx=4)  # 减小内边距

    def create_content_area(self):
        """创建主体内容区域"""
        # 创建左右分栏
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧就绪队列区域
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))  # 减小内边距

        # 右侧状态区域
        right_frame = ttk.Frame(content_frame, width=280)  # 减小宽度
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))  # 减小内边距
        right_frame.pack_propagate(False)  # 固定宽度

        # 创建就绪队列区域
        self.create_ready_queues(left_frame)

        # 创建右侧状态区域
        self.create_status_panel(right_frame)

    def create_ready_queues(self, parent):
        """创建就绪队列显示区域"""
        # 队列标题
        queue_header = ttk.Frame(parent, style='Info.TFrame')
        queue_header.pack(fill=tk.X, pady=(0, 8))  # 减小垂直间距

        ttk.Label(queue_header,
                  text="就绪队列",
                  font=('Arial', 12, 'bold'),  # 减小字体大小
                  foreground=self.dark_text).pack(pady=4)  # 减小垂直间距

        # 创建队列框架
        queues_frame = ttk.Frame(parent)
        queues_frame.pack(fill=tk.BOTH, expand=True)

        # 创建5个队列区域
        for i, area_info in enumerate(self.ls1):
            self.create_queue_area(queues_frame, i, area_info[0])

    def create_queue_area(self, parent, index, label):
        """创建单个队列区域"""
        # 队列卡片
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill=tk.BOTH, pady=4)  # 减小垂直间距

        # 队列标题
        header = ttk.Frame(card)
        header.pack(fill=tk.X, padx=8, pady=4)  # 减小内边距

        ttk.Label(header,
                  text=label,
                  font=('Arial', 10, 'bold'),  # 减小字体大小
                  foreground=self.primary_color).pack(side=tk.LEFT)

        # 进程计数
        count_label = ttk.Label(header,
                                text="0 进程",
                                font=('Arial', 9),  # 减小字体大小
                                foreground=self.dark_text)
        count_label.pack(side=tk.RIGHT)

        # 进程内容区域 - 减小高度
        content_frame = ttk.Frame(card)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))  # 减小内边距

        # 使用Canvas和Frame实现可滚动区域
        canvas = tk.Canvas(content_frame, bg='white', highlightthickness=0, height=80)  # 减小高度
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        # 修改为tk.Frame并设置背景色为白色
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # 绑定到画布和框架
        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 存储区域引用
        self.areas.append((scrollable_frame, count_label, canvas))  # 修改这行，添加canvas引用

    def create_status_panel(self, parent):
        """创建右侧状态面板"""
            # 面板标题
        ttk.Label(parent,
                text="系统状态",
                font=('Arial', 12, 'bold'),
                foreground=self.dark_text).pack(pady=(0, 12))

        # CPU状态区域
        cpu_frame = ttk.Frame(parent, style='Card.TFrame')
        cpu_frame.pack(fill=tk.X, pady=4)

        ttk.Label(cpu_frame,
                text="CPU状态",
                font=('Arial', 10, 'bold')).pack(pady=4)

        self.cpu_status_label = ttk.Label(cpu_frame,
                                        text="空闲",
                                        font=('Arial', 9),
                                        foreground=self.accent_color)
        self.cpu_status_label.pack(pady=(0, 8))

        # 等待队列区域
        waitq_frame = ttk.Frame(parent, style='Card.TFrame')
        waitq_frame.pack(fill=tk.X, pady=4)

        ttk.Label(waitq_frame,
                text="等待队列",
                font=('Arial', 10, 'bold')).pack(pady=4)

        # 使用Canvas和Frame实现可滚动区域 - 减小高度
        waitq_canvas = tk.Canvas(waitq_frame, height=80, bg='white', highlightthickness=0)  # 减小高度
        waitq_scrollbar = ttk.Scrollbar(waitq_frame, orient="vertical", command=waitq_canvas.yview)
        # 修改为tk.Frame并设置背景色为白色
        self.waitq_frame = tk.Frame(waitq_canvas, bg='white')

        self.waitq_frame.bind(
            "<Configure>",
            lambda e: waitq_canvas.configure(scrollregion=waitq_canvas.bbox("all"))
        )

        waitq_canvas.create_window((0, 0), window=self.waitq_frame, anchor="nw")
        waitq_canvas.configure(yscrollcommand=waitq_scrollbar.set)

        # 绑定鼠标滚轮事件（添加）
        def on_mousewheel(event):
            waitq_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        waitq_canvas.bind("<MouseWheel>", on_mousewheel)
        self.waitq_frame.bind("<MouseWheel>", on_mousewheel)

        waitq_canvas.pack(side="left", fill="both", expand=True, padx=4, pady=4)  # 减小内边距
        waitq_scrollbar.pack(side="right", fill="y", pady=4)  # 减小内边距

            # IO事件区域
        io_frame = ttk.Frame(parent, style='Card.TFrame')
        io_frame.pack(fill=tk.X, pady=4)

        ttk.Label(io_frame,
                text="IO事件",
                font=('Arial', 10, 'bold')).pack(pady=4)

        self.io_label = ttk.Label(io_frame,
                                text="无事件",
                                font=('Arial', 9),
                                wraplength=230)
        self.io_label.pack(pady=(0, 8), padx=8)

        # 系统信息区域 - 更新标签列表
        info_frame = ttk.Frame(parent, style='Card.TFrame')
        info_frame.pack(fill=tk.X, pady=4)

        ttk.Label(info_frame,
                text="系统信息",
                font=('Arial', 10, 'bold')).pack(pady=4)

        # 更新信息标签，添加新的性能指标
        info_labels = [
            ("已完成进程:", "0"),
            ("总进程数:", "0"),
            ("平均周转时间:", "0"),
            ("平均等待时间:", "0"),  # 新增
            ("平均带权周转时间:", "0"),  # 新增
            ("CPU利用率:", "0%"),  # 新增
            ("CPU总运行时间:", "0"),  # 新增
            ("总服务时间:", "0")  # 新增
        ]

        self.info_vars = {}

        for text, default in info_labels:
            row = ttk.Frame(info_frame)
            row.pack(fill=tk.X, padx=8, pady=2)

            ttk.Label(row, text=text, font=('Arial', 9)).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            ttk.Label(row, textvariable=var, font=('Arial', 9)).pack(side=tk.RIGHT)
            self.info_vars[text] = var

    def create_button_area(self):
        """创建底部按钮区域"""
        button_frame = ttk.Frame(self.main_frame, style='Info.TFrame')
        button_frame.pack(fill=tk.X, pady=(12, 0))  # 减小垂直间距

        # 第一行按钮
        row1 = ttk.Frame(button_frame)
        row1.pack(pady=4)  # 减小垂直间距

        # 添加进程按钮
        ttk.Button(row1,
                   text='添加进程',
                   command=self.add_process_dialog,
                   style='Accent.TButton').pack(side=tk.LEFT, padx=4)  # 减小内边距

        # 下一步按钮
        ttk.Button(row1,
                   text='下一步',
                   command=self.refresh_content,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=4)  # 减小内边距

        # 自动开始按钮
        self.auto_button = ttk.Button(row1,
                                      text='自动开始',
                                      command=self.toggle_auto_refresh,
                                      style='Secondary.TButton')
        self.auto_button.pack(side=tk.LEFT, padx=4)  # 减小内边距

        # 停止生成按钮
        self.gen_button = ttk.Button(row1,
                                     text='停止生成',
                                     command=self.toggle_gen,
                                     style='Secondary.TButton')
        self.gen_button.pack(side=tk.LEFT, padx=4)  # 减小内边距

        # 第二行按钮
        row2 = ttk.Frame(button_frame)
        row2.pack(pady=4)  # 减小垂直间距

        # 保存表格按钮
        ttk.Button(row2,
                   text='保存表格',
                   command=self.save_table,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=4)  # 减小内边距

        # IO中断按钮 - 修改为控制是否允许IO中断
        initial_text = 'IO中断: 允许' if self.cpu_core.io_allow else 'IO中断: 禁止'
        self.random_button = ttk.Button(row2,
                                        text=initial_text,
                                        command=self.toggle_io_allow,
                                        style='Secondary.TButton')
        self.random_button.pack(side=tk.LEFT, padx=4)  # 减小内边距

        # 配置队列按钮
        ttk.Button(row2,
                   text='配置队列',
                   command=self.config_queues,
                   style='Secondary.TButton').pack(side=tk.LEFT, padx=4)  # 减小内边距

    def add_process_dialog(self):
        # 创建一个顶层对话框窗口
        dialog = tk.Toplevel(self)
        dialog.title("添加进程")
        dialog.geometry("300x200")
        dialog.transient(self)  # 设置为主窗口的临时窗口
        dialog.grab_set()  # 模态对话框，阻止主窗口交互

        # 居中显示对话框
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # 创建对话框内容
        ttk.Label(dialog, text="进程名称:").pack(pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="总运行时间:").pack(pady=5)
        time_var = tk.StringVar()
        time_entry = ttk.Entry(dialog, textvariable=time_var)
        time_entry.pack(pady=5)

        ttk.Label(dialog, text="队列编号 (1-5):").pack(pady=5)
        queue_var = tk.StringVar()
        queue_entry = ttk.Entry(dialog, textvariable=queue_var)
        queue_entry.pack(pady=5)

        def on_ok():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("错误", "进程名称不能为空", parent=dialog)
                return

            try:
                total_time = int(time_var.get())
                if total_time <= 1:
                    messagebox.showerror("错误", "总运行时间必须大于1", parent=dialog)
                    return
            except ValueError:
                messagebox.showerror("错误", "总运行时间必须是整数", parent=dialog)
                return

            try:
                queue_number = int(queue_var.get())
                if queue_number not in range(1, 6):
                    messagebox.showerror("错误", "队列编号必须在1到5之间", parent=dialog)
                    return
            except ValueError:
                messagebox.showerror("错误", "队列编号必须是整数", parent=dialog)
                return

            # 获取当前 CPU 时钟时间
            t = self.cpu_core.get_cpu_clock()

            # 创建进程对象，队列ID设为用户选择的队列编号减1
            p = Process(name=name, arrive_time=t, tot_time=total_time, que_id=queue_number - 1)

            # 将进程添加到指定的队列中
            self.rq_list[queue_number - 1].offer(p)

            print(f"添加新进程: 名称 = {name}, 总运行时间 = {total_time}, 队列 = {queue_number}")
            dialog.destroy()
            self.refresh_content()

        def on_cancel():
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="确定", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.LEFT, padx=5)

        # 设置焦点到名称输入框
        name_entry.focus_set()

        # 绑定回车键到确定按钮
        dialog.bind('<Return>', lambda e: on_ok())

        # 等待对话框关闭
        self.wait_window(dialog)

    def refresh_content(self):
        try:
            # 保持原有逻辑不变
            self.cpu_core.run_for_1clk()
            if self.auto_gen:
                self.process_generator.run_for_1clk()

            # 更新队列信息
            for i in range(5):
                self.ls1[i][1] = self.rq_list[i].get_que_list()
            # 更新等待列表
            self.ls2[0][1] = self.cpu_core.get_waiting_list()
            # 更新当前CPU正在处理的进程
            self.ls2[1][1] = self.cpu_core.get_now_onboard()

            # 更新UI显示
            self.update_ui()

            # 更新CPU时钟显示
            self.cpu_clock_label.config(text=f"{self.cpu_core.get_cpu_clock()}")

            # 更新自动生成状态
            status_text = "开启" if self.auto_gen else "关闭"
            status_color = self.accent_color if self.auto_gen else self.danger_color
            self.auto_gen_label.config(text=status_text, foreground=status_color)

            # 强制刷新界面
            self.update_idletasks()
            self.update()

        except Exception as e:
            print(f"Error in refresh_content: {e}")
            import traceback
            traceback.print_exc()

    def update_ui(self):
        """更新UI显示"""
        # 更新就绪队列
        for i, area_info in enumerate(self.areas[:5]):
            # 检查元组长度
            if len(area_info) == 3:
                area, count_label, canvas = area_info
            else:
                area, count_label = area_info

            # 清理现有的内容
            for widget in area.winfo_children():
                widget.destroy()

            content = self.ls1[i][1]

            # 更新进程计数
            count_label.config(text=f"{len(content)} 进程")

            # 添加进程显示 - 确保即使为空也设置背景色
            if content:
                for item in content:
                    self.create_process_card(area, item, self.get_queue_color(i))
            else:
                # 当队列为空时，添加一个占位符标签以确保背景色正确
                placeholder = ttk.Label(area, text="空", font=('Arial', 8), foreground='gray')
                placeholder.pack(pady=10)

        # 更新等待队列
        for widget in self.waitq_frame.winfo_children():
            widget.destroy()

        waitq_content = self.ls2[0][1]
        if waitq_content:
            for item in waitq_content:
                self.create_process_card(self.waitq_frame, item, "#d1d5db")  # 灰色
        else:
            # 当等待队列为空时，添加一个占位符
            placeholder = ttk.Label(self.waitq_frame, text="空", font=('Arial', 8), foreground='gray')
            placeholder.pack(pady=10)

        # 更新CPU状态
        cpu_content = self.ls2[1][1]
        if cpu_content:
            item = cpu_content[0]
            if item[0] == 'HANGING':
                status_text = "挂起"
                status_color = self.accent_color
            elif 'Interrupt' in item[0]:
                status_text = "中断"
                status_color = self.danger_color
            else:
                status_text = f"运行: {item[0]}"
                status_color = self.primary_color
        else:
            status_text = "空闲"
            status_color = self.accent_color

        self.cpu_status_label.config(text=status_text, foreground=status_color)

        # 更新IO事件显示
        io_events = []
        for comp_time, process in self.cpu_core.io_completion_times.items():
            io_events.append(f"{process.get_name()}: {comp_time - 1}")

        io_text = "\n".join(io_events) if io_events else "无事件"
        self.io_label.config(text=io_text)
        # 获取性能指标
        metrics = self.cpu_core.get_performance_metrics()
        # 更新系统信息
        completed = metrics['completed_count']
        total = completed + sum(len(q.get_que_list()) for q in self.rq_list)

        self.info_vars["已完成进程:"].set(str(completed))
        self.info_vars["总进程数:"].set(str(total))
        
        # 更新新的性能指标
        self.info_vars["平均周转时间:"].set(f"{metrics['avg_turnaround_time']:.2f}")
        self.info_vars["平均等待时间:"].set(f"{metrics['avg_waiting_time']:.2f}")
        self.info_vars["平均带权周转时间:"].set(f"{metrics['avg_weighted_turnaround_time']:.2f}")
        self.info_vars["CPU利用率:"].set(f"{metrics['cpu_utilization']:.2f}%")
        self.info_vars["CPU总运行时间:"].set(str(metrics['cpu_total_time']))
        self.info_vars["总服务时间:"].set(str(metrics['total_service_time']))

    def create_process_card(self, parent, item, color):
        """创建进程显示卡片 - 减小尺寸"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill=tk.X, pady=1, padx=1)  # 减小间距

        # 进程名称
        name_label = ttk.Label(card,
                               text=item[0],
                               font=('Arial', 8, 'bold'),  # 减小字体大小
                               foreground='white',
                               background=color)
        name_label.pack(fill=tk.X, padx=3, pady=(3, 0))  # 减小内边距

        # 进程详情
        details_frame = ttk.Frame(card)
        details_frame.pack(fill=tk.X, padx=3, pady=(0, 3))  # 减小内边距

        ttk.Label(details_frame,
                  text=f"到达: {item[1]}",
                  font=('Arial', 7)).pack(side=tk.LEFT)  # 减小字体大小

        ttk.Label(details_frame,
                  text=f"剩余: {item[2]}",
                  font=('Arial', 7)).pack(side=tk.RIGHT)  # 减小字体大小

    def get_queue_color(self, index):
        """获取队列颜色"""
        colors = [
            "#3b82f6",  # 蓝色
            "#6366f1",  # 靛靛蓝色
            "#8b5cf6",  # 紫色
            "#ec4899",  # 粉色
            "#f59e0b",  # 橙色
        ]
        return colors[index % len(colors)]

    def toggle_auto_refresh(self):
        if self.auto_refresh:
            self.auto_refresh = False
            if self.auto_refresh_task:
                self.after_cancel(self.auto_refresh_task)
                self.auto_refresh_task = None
            self.auto_button.config(text="自动开始", style='Secondary.TButton')
        else:
            self.auto_refresh = True
            self.auto_button.config(text="停止自动", style='Danger.TButton')
            self.auto_refresh_content()

    def auto_refresh_content(self):
        if self.auto_refresh:
            self.refresh_content()
            self.auto_refresh_task = self.after(100, self.auto_refresh_content)

    def toggle_gen(self):
        self.auto_gen = not self.auto_gen
        if self.auto_gen:
            self.gen_button.config(text="停止生成", style='Secondary.TButton')
        else:
            self.gen_button.config(text="开始生成", style='Accent.TButton')

    def toggle_io_allow(self):
        """切换是否允许IO中断"""
        self.cpu_core.io_allow = not self.cpu_core.io_allow
        status = "允许" if self.cpu_core.io_allow else "禁止"
        self.random_button.config(text=f"IO中断: {status}")

    def save_table(self):
        filename = "completed_processes.txt"
        self.cpu_core.generate_and_save_table(filename)
        messagebox.showinfo("保存成功", f"表格已保存至 {filename}")

    def config_queues(self):
        """配置就绪队列的个数、优先级和时间片"""
        # 创建配置窗口
        config_window = tk.Toplevel(self)
        config_window.title("配置队列")
        config_window.geometry("400x300")

        # 创建标签和输入框
        ttk.Label(config_window, text="队列数量 (3-5):").grid(row=0, column=0, padx=5, pady=5)
        num_queues_var = tk.StringVar(value=str(len(self.rq_list)))
        num_queues_entry = ttk.Entry(config_window, textvariable=num_queues_var)
        num_queues_entry.grid(row=0, column=1, padx=5, pady=5)

        # 创建队列配置区域
        config_frame = ttk.Frame(config_window)
        config_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        priority_vars = []
        time_clip_vars = []

        for i in range(5):
            ttk.Label(config_frame, text=f"队列 {i + 1} 优先级:").grid(row=i, column=0, padx=5, pady=2)
            priority_var = tk.StringVar(value=str(self.rq_list[i].get_que_priority() if i < len(self.rq_list) else i))
            priority_entry = ttk.Entry(config_frame, textvariable=priority_var, width=5)
            priority_entry.grid(row=i, column=1, padx=5, pady=2)
            priority_vars.append(priority_var)

            ttk.Label(config_frame, text=f"时间片:").grid(row=i, column=2, padx=5, pady=2)
            time_clip_var = tk.StringVar(value=str(self.rq_list[i]._time_clip if i < len(self.rq_list) else 2 ** i))
            time_clip_entry = ttk.Entry(config_frame, textvariable=time_clip_var, width=5)
            time_clip_entry.grid(row=i, column=3, padx=5, pady=2)
            time_clip_vars.append(time_clip_var)

        def apply_config():
            try:
                num_queues = int(num_queues_var.get())
                if num_queues < 3 or num_queues > 5:
                    messagebox.showerror("错误", "队列数量必须在3到5之间")
                    return

                new_rq_list = []
                for i in range(num_queues):
                    priority = int(priority_vars[i].get())
                    time_clip = int(time_clip_vars[i].get())
                    new_rq_list.append(ReadyQue(algo='FIFO', priority=priority, time_clip=time_clip))

                # 更新队列列表
                self.rq_list = new_rq_list
                self.cpu_core._que_list = new_rq_list
                self.process_generator._rq_list = new_rq_list

                # 更新界面显示
                for i in range(5):
                    if i < num_queues:
                        self.ls1[i][
                            0] = f'队列 {i + 1} (优先级:{priority_vars[i].get()}, 时间片:{time_clip_vars[i].get()})'
                    else:
                        self.ls1[i][0] = f'队列 {i + 1} (已禁用)'

                config_window.destroy()
                self.refresh_content()
                messagebox.showinfo("成功", "队列配置已更新")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的整数值")

        ttk.Button(config_window, text="应用", command=apply_config).grid(row=6, column=0, columnspan=2, pady=10)

    def _on_main_frame_configure(self, event):
        """更新主画布的滚动区域"""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _on_main_canvas_configure(self, event):
        """确保主内容区域宽度随窗口调整"""
        self.main_canvas.itemconfigure(self.main_window, width=event.width)

    def bind_global_mousewheel(self, event):
        """全局鼠标滚轮事件处理"""
        # 查找鼠标位置下的画布
        widget = event.widget
        while widget and not isinstance(widget, tk.Canvas):
            widget = widget.master

        if widget and isinstance(widget, tk.Canvas):
            # 滚动该画布
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")