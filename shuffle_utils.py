import random

def infinite_shuffled_reproducible(firstnum, secondnum, step, seed):
    # 创建一个独立的随机数生成器，避免影响全局 random 状态
    rng = random.Random(seed)
    # 确保参数是数值类型，并转换为适当的类型
    if isinstance(step, float) and step < 1:
        # 如果步长是小于1的浮点数，生成0到1之间的浮点数序列
        items = [i/100 for i in range(int(firstnum*100), int(secondnum*100), int(step*100))]
    else:
        # 确保参数是整数类型
        firstnum = int(firstnum)
        secondnum = int(secondnum)
        step = int(step)
        items = list(range(firstnum, secondnum, step))
    
    while True:
        shuffled = items[:]
        rng.shuffle(shuffled)   # 使用独立 RNG 打乱
        yield from shuffled
