# %%
import numpy as np
import pandas as pd
import os
from modules.FEM import plot_truss,FEM2D
from modules.expxlsx import expxlsx
#truss X bracing roof
#nodes, elements = create_X_horizontal_truss(4, 4.5, 4)
#nodes=[[0,0],[4.5,0],[9,0],[13.5,0],[18,0],[0,4],[4.5,4],[9,4],[13.5,4],[18,4]]
#elements=[[0,5],[1,6],[2,7],[3,8],[4,9], #purlins
#          [0,1],[1,2],[2,3],[3,4],[5,6],[6,7],[7,8],[8,9],#rafter
#          [0,6],[5,1],[1,7],[6,2],[2,8],[7,3],[3,9],[8,4],#diagonals  
#       ]                                   
#truss A wall bracing 
nodes=[[0,0],[0,7],[2,7],[4,7],[4,0]]
elements=[[1,2],[2,3],[0,1],[4,3],[0,2],[2,4]]
#Loads for each truss case
#loads = np.array([[1,1282.6], [3,2815.6], [5,3066.1], [7,2815.6], [9,1282.6]]) 
#loads = np.array([[1,-1157.03876], [3,-2200.230815], [5,-2246.597696], [7,-2087.170172], [9,-721.0281682]]) 
loads1=[[0,3334.130615],[2,8965.394952]]
loads2=[[0,-3334.130615],[2,-7786.433877]]
constraints = np.array([0, 1, 8, 9])
plot_truss(nodes, elements, loads1, constraints,load_scale=10e-5)
plot_truss(nodes, elements, loads2, constraints,load_scale=10e-5)
E=210e6
# Areas *1e-4 convert cm2 to m2
A_h = 21.236 * 1e-4   # horizontal eave purlin 
A_v = 131.364 * 1e-4    # vertical column
A_d = 12.267  * 1e-4   # diagonal 
u1, reactions1, axial_forces1, elem_types=\
FEM2D(A_h, A_v, A_d, nodes, elements, loads1, constraints, E=210e6)
u2, reactions2, axial_forces2, _ =\
FEM2D(A_h, A_v, A_d, nodes, elements, loads2, constraints, E=210e6)
# Directory where hangar.py lives
baseDir = os.path.dirname(__file__)
# Excel folder is inside this directory
excelDir = os.path.join(baseDir, "excel")
Tables = [pd.DataFrame(u1),pd.DataFrame(reactions1),pd.DataFrame(axial_forces1),pd.DataFrame(elem_types),
pd.DataFrame(u2),pd.DataFrame(reactions2),pd.DataFrame(axial_forces2)]
sheetNames = ["u1","reactions1","axial_forces1","elem_types","u2","reactions2","axial_forces2"]
expxlsx(Tables, os.path.join(excelDir, "roofbracing.xlsx"), sheetNames)
