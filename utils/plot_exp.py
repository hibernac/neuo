import matplotlib.pyplot as plt
import numpy as np

# 模型名称顺序
models = ["DP-VLA", "OpenVLA", "Octo", "RDT", "HiBerNAC"]

# 各任务类别对应的平均分
data = {
    "physical": [5.8, 13, 84.8, 100, 100],
    "visual": [39, 6.5, 0, 74.5, 70],
    "semantic": [7, 0, 79, 76, 76.5],
    "correction": [0, 0, 0, 1, 7.5],
    "OOD": [0, 4, 0, 7, 25.5],
    "multimodal": [0, 9.5, 0, 32, 48.5],
    "long-horizon1": [53.5, 2.5, 0, 69.5, 76.5],
    "long-horizon2": [38.5, 7.5, 0, 74, 75],
}
# 模型颜色
task_colors = {
    "DP-VLA": "#1f77b4",
    "OpenVLA": "#ff7f0e",
    "Octo": "#2ca02c",
    "HiBerNAC": "#d62728",
    "OOD": "#9467bd",
    "RDT": "#8c564b",
}
# 设置柱状图的宽度
bar_width = 0.15
# 设置柱状图的间距
bar_spacing = 0.2
# 设置柱状图的起始位置
bar_positions = np.arange(len(models)) * (bar_width + bar_spacing)

# 依次绘制每个任务类别的柱状图
for task, values in data.items():
    plt.figure(figsize=(5, 4))
    # 计算每个任务类别的柱状图位置
    task_bar_positions = bar_positions + (list(data.keys()).index(task) * (bar_width + bar_spacing))
    # bar的颜色为模型颜色
    color = [task_colors[model] for model in models]
    model = task_colors.keys()
    # 绘制柱状图
    bars = plt.bar(task_bar_positions, values, width=bar_width, color=color, edgecolor='black', label=models)
    for i, model in enumerate(models):
        if model == "HiBerNAC":
            bars[i].set_hatch('//')
    
    plt.title(f"Average Performance on {task.capitalize()} Task")
    plt.ylabel("Average success rate (%)")
    plt.xlabel("Models")
    plt.xticks(task_bar_positions, models)
    # use 模型名称 as legend
    plt.legend(title="Models", loc="upper left")
    plt.ylim(0, 110)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 在柱子顶部标注具体数值
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 1, f"{height:.1f}",
                 ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()
    # 保存图像
    plt.savefig(f"{task}_performance.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{task}_performance.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(f"{task}_performance.eps", dpi=300, bbox_inches='tight')
    plt.savefig(f"{task}_performance.svg", dpi=300, bbox_inches='tight')
    plt.close()
# 这段代码将为每个任务类别生成一个柱状图，并在柱子顶部标注具体的平均分数。
# 你可以根据需要调整图像的大小、标题和其他样式参数。
