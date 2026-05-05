import numpy as np
from modules.FEM import generate_elements2,plot_structure,prepare_fem_inputs,FEM2D_frame
import matplotlib.pyplot as plt
import pandas as pd
from modules.io import exptxt
x = np.array([0, 3.9, 7.75, 12.25, 18.8, 23.2])
z = np.array([0, 4.08, 7.14, 10.2, 13.26])
# Cartesian product
nodes = np.array([[xi, zj] for zj in z for xi in x])

A_beam = 0.3 * 0.5
I_beam = (0.3 * 0.5**3) / 12

A_col = 0.4 * 0.4
I_col = (0.4 * 0.4**3) / 12

E = 30e9  # Pa

elements = generate_elements2(x, z, A_beam, I_beam, A_col, I_col, E, q_beam=10)

show_node_ids = True

elem_conn, elem_props = prepare_fem_inputs(elements)

nodal_loads = []
constraints = []
nx = len(x)
for i in range(nx):
    node = i  # first row (z=0)
    constraints.extend([3*node, 3*node+1, 3*node+2])
title = "structure"
folder = "tall building"
filename = "elevation_view_XZ.png"
plot_structure(nodes,elements,constraints,show_node_ids,title,folder,filename)
u, reactions, N, V, M = FEM2D_frame(
    nodes,
    elem_conn,
    elem_props,
    nodal_loads,
    constraints
)
T_internal=pd.DataFrame({"N":N.reshape(-1),"V":V.reshape(-1),"M":M.reshape(-1),})
T_reactions=pd.DataFrame({"reactions":reactions.reshape(-1)})
T_u=pd.DataFrame({"displacements":u.reshape(-1)})
Tables = [T_internal,T_reactions,T_u]
Names = ["internal","reactions","displacaments"]
exptxt(Tables, Names, "tall building/FEM_frame.txt", 12)
                         
