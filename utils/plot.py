import matplotlib.pyplot as plt
import numpy as np

# Data from the table, with the error values
categories = ['Physical', 'Visual', 'Semantic', 'Correction', 'OOD', 'Multimodal', 'Long-Horizon1', 'Long-Horizon2']
tasks = ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5', 'Task 6', 'Task 7', 'Task 8']

DP = [6, 39, 7, 0, 0, 0, 53.5, 39]
DP_error = [2.14, 3.55, 2.83, 0, 0, 0, 2.07, 3.55]

OpenVLA = [13, 7.5, 0, 0, 4, 9.5, 3.5, 7.5]
OpenVLA_error = [1.85, 3.34, 0, 0, 0, 2.07, 1.85, 3.34]

Octo = [85, 0, 79, 0, 0, 32, 1.85, 7.5]
Octo_error = [4.14, 0, 4.14, 0, 0, 5.55, 4.24, 3.34]

RDT = [100, 74, 76, 0, 7, 32.5, 69.5, 74]
RDT_error = [0, 7.71, 3.02, 0, 5.55, 5.81, 4.24, 7.71]

HiBerNAC = [100, 70, 76.5, 8, 25.5, 48, 76.5, 76]
HiBerNAC_error = [0, 3.02, 1.41, 2.14, 2.98, 1.81, 1.41, 3.02]

# Bar width
barWidth = 0.15

# Set position of bar on X axis
r1 = np.arange(len(tasks))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
r4 = [x + barWidth for x in r3]
r5 = [x + barWidth for x in r4]

# Create figure and plot bars with error bars
plt.figure(figsize=(12, 6))
plt.bar(r1, DP, color='b', width=barWidth, edgecolor='grey', label='DP-VLA', yerr=DP_error, capsize=5)
plt.bar(r2, OpenVLA, color='g', width=barWidth, edgecolor='grey', label='OpenVLA', yerr=OpenVLA_error, capsize=5)
plt.bar(r3, Octo, color='c', width=barWidth, edgecolor='grey', label='Octo', yerr=Octo_error, capsize=5)
plt.bar(r4, RDT, color='y', width=barWidth, edgecolor='grey', label='RDT', yerr=RDT_error, capsize=5)
plt.bar(r5, HiBerNAC, color='r', width=barWidth, edgecolor='black', label='HiBerNAC (Ours)', yerr=HiBerNAC_error, linewidth=2, capsize=5, hatch='//')

# Add labels and title
plt.xlabel('Task Categories', fontweight='bold', fontsize=15)
plt.ylabel('Performance', fontweight='bold', fontsize=15)
plt.xticks([r + barWidth*2 for r in range(len(categories))], categories)
# plt.title('Evaluation of Framework Performances with Standard Deviation')

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
