


#%% ---- Chapter III-1 ----
import os
from modules.truss import roof_bracing
from modules.expxlsx import expxlsx
# Directory where hangar.py lives
baseDir = os.path.dirname(__file__)
# Excel folder is inside this directory
excelDir = os.path.join(baseDir, "excel")
beamT = os.path.join(excelDir, "tableaudesprofiles.xlsx")
chI = os.path.join(excelDir, "chapterI.xlsx")
hangarf = os.path.join(excelDir, "hangar.xlsx")
chII_1 = os.path.join(excelDir, "chapterII-1.xlsx")
T1, T2, Trafter, Tcolumn, Tdiagonal, T6, T7, T8, T9, T10, T11, T12, T13,FV1,FV2=\
roof_bracing(hangarf, beamT, chI, chII_1)
# If you want to export:
#Tables = [T1, T2, Trafter, Tcolumn, Tdiagonal, T6, T7, T8, T9, T10, T11, T12, T13]
#sheetNames = ["T1","T2","Ttrafter","Tcolumn","Tdiagonal","T6","T7","T8","T9","T10","T11","T12","T13"]
#expxlsx(Tables, os.path.join(excelDir,"chapterIII-1.xlsx"), sheetNames)
#%% ---- Chapter III-2 ----
import os
from modules.truss import wall_bracing
from modules.expxlsx import expxlsx
# Directory where hangar.py lives
baseDir = os.path.dirname(__file__)
# Excel folder is inside this directory
excelDir = os.path.join(baseDir, "excel")
beamT = os.path.join(excelDir, "tableaudesprofiles.xlsx")
chIII_1 = os.path.join(excelDir, "chapterIII-1.xlsx")
hangarf = os.path.join(excelDir, "hangar.xlsx")
T1, T2, TEave_purlin, Tdiagonal, T3, T4, T5 = wall_bracing(beamT, chIII_1, hangarf)
#Tables = [T1, T2, TEave_purlin, Tdiagonal, T3, T4, T5]
#sheetNames = ["T1", "T2", "TEave_purlin", "Tdiagonal", "T3", "T4", "T5"]
#expxlsx(Tables, os.path.join(excelDir, "chapterIII-2.xlsx"), sheetNames)


# %% chapter IV frame 
import pandas as pd
import numpy as np
from modules.frame import frame 
from modules.expxlsx import expxlsx
# Directory where hangar.py lives
baseDir = os.path.dirname(__file__)
# Excel folder is inside this directory
excelDir = os.path.join(baseDir, "excel")
hangarf = os.path.join(excelDir, "hangar.xlsx")
chI = os.path.join(excelDir, "chapterI.xlsx")
chII_1 = os.path.join(excelDir, "chapterII-1.xlsx")
chII_2 = os.path.join(excelDir, "chapterII-2.xlsx")
chIII_1 = os.path.join(excelDir, "chapterIII-1.xlsx")
chIII_2 = os.path.join(excelDir, "chapterIII-2.xlsx")
E=210e6 #Kpa
#frame(hangarf,chI,chII_1,chIII_1,chIII_2,chII_2):
(Tdistributed_loadG,Tnodal_loadG,T_axial_forces,T_shear_forces,
T_bending_moments,T_displacements_reactions)=frame(hangarf,chI,chII_1,chIII_1,chIII_2,chII_2)
Tables = [Tdistributed_loadG,Tnodal_loadG,T_axial_forces,T_shear_forces,T_bending_moments,T_displacements_reactions]
sheetNames = ["Tdistributed_loadG","Tnodal_loadG","T_axial_forces","T_shear_forces","T_bending_moments","T_displacements_reactions"]
expxlsx(Tables, os.path.join(excelDir, "chapterIV-1-beta.xlsx"), sheetNames)
#%%
import pandas as pd
import numpy as np
import os
from modules.FEM import plot_frame,FEM2D_frame
from modules.expxlsx import expxlsx
nodes=[[0,0],[0,7],[9,9],[18,7],[18,0]]
elements=[[0,1],[1,2],[2,3],[3,4]]
constraints = [0,1,2,  4*3, 4*3+1, 4*3+2]   # all DOFs at node 0 and node 4 are fixed on the gound
#frame properties 
A_rafter = 84.5*10e-4
I_rafter = 23130*10e-8
A_column = 131.4*10e-4
I_column = 19270*10e-8
E=210e6
elem_props = [
# element 0: left column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'w':0},  #KN/m
#element 1: left rafter
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'w':195},  #KN/m
#element 2: right rafter
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'w':195},  #KN/m
#element 3: right column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'w':0},  #KN/m
]
#loads
loads = [[4,-1387.1],[10,-1387.1]] 
#plot_frame(nodes, elements, elem_props, loads, constraints, scale_load):
plot_frame(nodes, elements, elem_props, loads ,constraints, load_scale=0.01)
u, R, N, V, M = FEM2D_frame(
nodes, elements, elem_props, loads, constraints, default_E=210e6)
with open("gable_roof_frame_positive2.txt", "w") as f:
    f.write("=== DISPLACEMENTS (u) ===\n")
    f.write(str(u))
    f.write("\n\n=== REACTIONS (R) ===\n")
    f.write(str(R))
    f.write("\n\n=== AXIAL FORCES (N) ===\n")
    f.write(str(N))
    f.write("\n\n=== SHEAR FORCES (V) ===\n")
    f.write(str(V))
    f.write("\n\n=== MOMENTS (M) ===\n")
    f.write(str(M))
