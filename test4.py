import numpy as np
from modules.FEM import generate_elements2,plot_structure,prepare_fem_inputs,FEM2D_frame
import matplotlib.pyplot as plt

x = np.array([0, 5, 10])
z = np.array([0, 4.08, 7.14])
# Cartesian product
nodes = np.array([[xi, zj] for zj in z for xi in x])

A_beam = 0.3 * 0.5
I_beam = (0.3 * 0.5**3) / 12

A_col = 0.4 * 0.4
I_col = (0.4 * 0.4**3) / 12

E = 30e9  # Pa

elements = generate_elements2(x, z, A_beam, I_beam, A_col, I_col, E, q_beam=10)


show_node_ids = True
plot_structure(nodes, elements, show_node_ids, "tall building", "elevation_view_XZ.png")

elem_conn, elem_props = prepare_fem_inputs(elements)
nodal_loads = []
constraints = [0,1,2,3,4,5,6,7,8]   # all DOFs at node 0 and node 4 are fixed on the gound

u, reactions, N, V, M = FEM2D_frame(
    nodes,
    elem_conn,
    elem_props,
    nodal_loads,
    constraints
)

print(N)
print(V)
print(M)
