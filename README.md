这里是徐占国，增加了新指标，完成了任务3、6，对ui有所修改
1.	新增多种算法进行对比
2.	新增初始UI，可选择算法进行运行
3.	每个算法运行完后会将数据转换为txt文件（尝试将txt文件转为图）
4.	原先黑框调试需要在ui进行展示
5.	CPU_Core将在初始界面选择确定算法后生成，在算法运行完后进行销毁
6.	要生成当前运行的各项指标（要转换到之前的txt文件中，方便后续进行比较）
解决思路：
1.在main生成队列之前，进入FunctionSelector进行算法选择，通过点击FunctionSelector中的按钮来修改位于main中的str FunctionKey，随后将FunctionKey传入Quenue中作为algorithm
    同时FunctionSelector也会将修改ReadyQue中的参数 AlgorithmSelector（等同于main中的FunctionKey避免循环导入）用于进行队列维护选择
2.在mainWindow中添加一个返回按钮，使得程序返回FunctionSelector进行算法选择
3.在ReadyQue中应该返回小根堆模式并恢复PCB块，通过区分self.algorithm来区分如何计算优先级


