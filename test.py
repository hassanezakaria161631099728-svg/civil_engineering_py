import numpy as np
import os
x = np.array([0, 3.9, 7.75, 12.25, 18.8, 23.2])
y = np.array([0, 3.7, 7.4, 13.8, 18.6])

# Cartesian product
nodes = np.array([[xi, yj] for yj in y for xi in x])
print(nodes)
import matplotlib.pyplot as plt

size = 0.3  # column size

fig, ax = plt.subplots()

for xi, yj in nodes:
    square = plt.Rectangle((xi - size/2, yj - size/2),
                           size, size,
                           edgecolor='black',
                           facecolor='black')
    ax.add_patch(square)

# Horizontal segments
for yj in y:
    for i in range(len(x) - 1):
        ax.plot([x[i], x[i+1]], [yj, yj], linestyle='--', linewidth=1)

# Vertical segments
for xi in x:
    for j in range(len(y) - 1):
        ax.plot([xi, xi], [y[j], y[j+1]], linestyle='--', linewidth=1)
ax.set_aspect('equal')
ax.set_xlim(min(x)-1, max(x)+1)
ax.set_ylim(min(y)-1, max(y)+1)
#ax.grid(True)
# Full path
filepath = os.path.join("tall building", "ground_level_XY2.png")
# Save figure
plt.savefig(filepath, dpi=300, bbox_inches='tight')
plt.show()


