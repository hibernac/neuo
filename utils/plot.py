import matplotlib.pyplot as plt
import numpy as np

# Data from the table
categories = ['Physical', 'Visual', 'Semantic', 'Correction', 'OOD', 'Multimodal', 'Long-Horizon1', 'Long-Horizon2']
subjects = ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5', 'Task 6', 'Task 7', 'Task 8']
DP = [6, 39, 7, 0, 0, 0, 53.5, 39]
OpenVLA = [13, 7.5, 0, 0, 4, 9.5, 3.5, 7.5]
Octo = [85, 0, 79, 0, 0, 32, 1.85, 7.5]
RDT = [100, 74, 76, 0, 7, 32.5, 69.5, 74]
HiBerNAC = [100, 70, 76.5, 8, 25.5, 48, 76.5, 76]

# Bar width
barWidth = 0.15

# Set position of bar on X axis
r1 = np.arange(len(categories))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
r4 = [x + barWidth for x in r3]
r5 = [x + barWidth for x in r4]

# Create figure and plot bars
plt.figure(figsize=(12, 6))
plt.bar(r1, DP, color='b', width=barWidth, edgecolor='grey', label='DP')
plt.bar(r2, OpenVLA, color='g', width=barWidth, edgecolor='grey', label='OpenVLA')
plt.bar(r3, Octo, color='c', width=barWidth, edgecolor='grey', label='Octo')
plt.bar(r4, RDT, color='y', width=barWidth, edgecolor='grey', label='RDT')
plt.bar(r5, HiBerNAC, color='r', width=barWidth, edgecolor='black', label='HiBerNAC (Ours)', linewidth=2)

# Add labels and title
plt.xlabel('Task Categories', fontweight='bold', fontsize=15)
plt.ylabel('Performance', fontweight='bold', fontsize=15)
plt.xticks([r + barWidth*2 for r in range(len(categories))], categories)
# plt.title('Evaluation of Framework Performances')

# Add legend
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()
# Save the plot
plt.savefig('framework_performance.png', dpi=300, bbox_inches='tight')
plt.savefig('framework_performance.pdf', dpi=300, bbox_inches='tight')
plt.savefig('framework_performance.eps', dpi=300, bbox_inches='tight')
plt.savefig('framework_performance.svg', dpi=300, bbox_inches='tight')