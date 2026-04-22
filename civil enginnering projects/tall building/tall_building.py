import sys
import numpy as np
import pandas as pd
from modules.building_elements import (stairs,RC_column,RC_shear_force,shape_geometry_attributes,
sectorial,building_masses,dynamic1,dynamic2)
from modules.FEM import generate_grid,plot_grid
from modules.io import matrix_to_table,export_matrices_txt2,exptxt,read_tables_txt3

def elements():
 print("Running case 1: elements")
 # your code here
 #stairs
 story_height = 3.06 # m
 vertical_step = 18 # cm
 horizontal_step = 25 # cm
 (statement,story_height,stairs_height,vertical_step,n_stairs,
 horizontal_step,stairs_length,slope_angle,slope_angle_deg)=\
 stairs(story_height, vertical_step, horizontal_step)
 T1 = pd.DataFrame({"statement": [statement],"story_height": [story_height],"stairs_height": [stairs_height],
 "vertical_step": [vertical_step],"n_stairs": [n_stairs],"horizontal_step": [horizontal_step],
 "stairs_length": [stairs_length],"slope_angle": [slope_angle],"slope_angle_deg": [slope_angle_deg]})
 #reinforced concrete column
 # number of floors above the base level
 #in general case the base level isn't necessary the ground floor but the last underneath floor
 # the last floor under the surface of soil
 nSF = 9 # number of floors above the soil surface
 nUF = 0 # number of floors under the soil surface
 n = nSF + nUF  #total number of floors above the base level we add 1 the ground floor and we 
 # remove the last underneath floor which is the base floor  
 fc28,fe = 30,400
 Lx,Ly= 4.5,4.5 
 S1 = Lx * Ly
 S2,S3 = S1/2, S1/4 
 # dead loads G and live loads Q
 GRT,GCF = 787,665
 QRT,QCF = 100,150
 T2 = RC_column(fc28,fe,S1,n,GCF,GRT,QRT,QCF)
 T3 = RC_column(fc28,fe,S2,n,GCF,GRT,QRT,QCF)
 T4 = RC_column(fc28,fe,S3,n,GCF,GRT,QRT,QCF)
 #RC shear force units are in mm and N
 At,b,d,alpha = 452,250,500,0.85/1.2
 Vu_reduced = 179000
 ft28,up,down,stmin=\
 RC_shear_force(fe,At,alpha,b,Vu_reduced,fc28,d)
 T5 = pd.DataFrame({"ft28": [ft28],"up": [up],"down": [down],"stmin": [stmin]})
 # export results
 tables = [T1,T2,T3,T4,T5]
 names = ["stairs","RC_column1","RC_column2","RC_column3","RC_shear_force"]
 exptxt(tables, names, "tall building/elements.txt", 12)

def geometry():
 print("Running case 2: geometry_attributes")
 # your code here
 #shape1
 a1 = [0.4, 0.2, 0.4]
 b1 = [0.4, 3.8, 0.4]
 xg1 = [0.2, 0.2, 0.2]
 yg1 = [0.2, 2.3, 4.4]
 T_scalar1, T_vec1 = shape_geometry_attributes(a1, b1, xg1, yg1)

 #shape2
 a2 = [0.4, 0.2]
 b2 = [0.4, 2.3]
 xg2 = [0.2, 0.2]
 yg2 = [0.2, 1.55]
 T_scalar2, T_vec2 = shape_geometry_attributes(a2, b2, xg2, yg2)

 #shape3
 a3 = [0.4, 2.1]
 b3 = [0.4, 0.2]
 xg3 = [0.2, 1.45]
 yg3 = [0.2, 0.2]
 T_scalar3, T_vec3 = shape_geometry_attributes(a3, b3, xg3, yg3)

 #shape4
 a4 = [5.75]
 b4 = [0.2]
 xg4 = [2.875]
 yg4 = [0.1]
 T_scalar4, T_vec4 = shape_geometry_attributes(a4, b4, xg4, yg4)

 # general scheme RC walls coordinates
 # centre of mass vectors 
 xg3g = T_scalar3["xg_global"].iloc[0]
 yg1g = T_scalar1["yg_global"].iloc[0]
 yg2g = T_scalar2["yg_global"].iloc[0]

 Lx,Ly = 21.77,15.7 
 # X
 X = [0.2, Lx-0.2, 0.2, Lx-0.2,                #i=0:4
 4.7, Lx-4.7, 4.7, Lx-4.7,                     #i=4:8
 4.5+xg3g, Lx-4.5-xg3g, 4.5+xg3g, Lx-4.5-xg3g, #i=8:12
 4.7, Lx-4.7, 4.7, Lx-4.7,                     #i=12:16     
]

 # Y
 Y = [1+yg1g, 1+yg1g, Ly-1-yg1g, Ly-1-yg1g,    #i=0:4
 1+yg2g, 1+yg2g, Ly-1-yg2g, Ly-1-yg2g,         #i=4:8
 5.4, 5.4, Ly-5.4, Ly-5.4,                     #i=8:12
 0.1, 0.1, Ly-0.1, Ly-0.1,                     #i=12:16     
]

 T_sectorial,T_sectorial_scalars = sectorial(T_scalar1,T_scalar2,T_scalar3,T_scalar4,X,Y)

# export results
 tables = [T_vec1,T_scalar1, T_vec2,T_scalar2, T_vec3,T_scalar3, T_vec4,T_scalar4,
 T_sectorial, T_sectorial_scalars]
 names = ["vectors1","scalars1", "vectors2","scalars2", "vectors3","scalars3","vectors4","scalars4",
 "sectorial_attributes","sectorial_attributes_scalars"]
 exptxt(tables, names, "tall building/geometry.txt", 12)

def masses():
 print("running case 3: masses")
 #your code here
 geometry = read_tables_txt3("tall building/geometry.txt")
 Lx,Ly = 23.05,19.25 #building dimension x y
 h_story,h_beam = 3.06,0.4 
 DC = 2.5 #concrete density
 # roof top barricade
 G_RTB = 211.1 #kg/m
 #RC columns
 n_RC_columns,a_RC_column = 48,0.45
 T_RTB,T_RC_walls,T_RC_columns = \
 building_masses(geometry,Lx,Ly,G_RTB,h_story,h_beam,a_RC_column,n_RC_columns,DC)
# export results
 tables = [T_RTB,T_RC_walls, T_RC_columns]
 names = ["roof_top_barricade","RC_walls", "RC_columns"]
 exptxt(tables, names, "tall building/masses.txt", 12)
 
def dynamic():
 print("Running case 4: dynamic analysis")
 # your code here
 n = 9 #number of floors above the base floor
 M1, M2, M3 = 710.02, 703.74, 705.94 #masses
 Lx, Ly = 45.2, 17.4
 # SA and mass matrices and Elasticity module
 h = 3.24 #m story height
 # case there is only "with bricks" or "no bricks"
 case = "with bricks"
 SA, M, MR, E, TSA, TM, T_imperial = dynamic1(n,M1,M2,M3,h,case,Lx,Ly)
 Ix, Iy, Iw = 97.133, 808.81, 374955.3
 fx, TSx, TDx, eigen_valuesx, Teigen_vectors, periods_x = dynamic2(h,E,Iy,SA,M) 
 fy, TSy, TDy, eigen_valuesy, _, periods_y = dynamic2(h,E,Ix,SA,M) 
 fw, TSw, TDw, eigen_valuesw, _, periods_w = dynamic2(h,E,Iw,SA,MR) 
 names = ["SA","M","Sx","Dx","eigen_vectors","Sy","Dy","MR","Sw","Dw"]
 matrices = [TSA, TM, TSx, TDx, Teigen_vectors, TSy, TDy, MR, TSw, TDw]
 #float_format = "{:.3f}".format
 export_matrices_txt2(matrices, names, "tall building/dynamic.txt")
 T = pd.DataFrame({"eigen_valuesx": eigen_valuesx,"eigen_valuesy": eigen_valuesy,"eigen_valuesw": eigen_valuesw,
 "periods_x_s": periods_x,"periods_y_s": periods_y,"periods_w_s": periods_w})
 T2 = pd.DataFrame({"Elasticity_module": [E],"Iy": [Iy],"Ix": [Ix],"fx": [fx],"fy": [fy],"fw": [fw],
 "T_imperial":[T_imperial]})
 #export results
 tables = [T,T2]
 names = ["periods_secondes","scalars"]
 exptxt(tables, names, "tall building/dynamic2.txt", 12)

def plot():
 print("Running case 2: building upper vue ground level XY")
 # your code here
 nx,ny,Lx,Ly = 6,6,4.5,4.5
 nodes,_=generate_grid(nx, ny, Lx, Ly)
 plot_grid(nodes, nx, ny, "tall building", "ground_level_XY.png")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a case: dynamic, columns,geometry,test")
    else:
        command = sys.argv[1]

        if command == "elements":
            elements()
        elif command == "geometry":
            geometry()
        elif command == "masses":
            masses()
        elif command == "dynamic":
            dynamic()
        elif command == "plot":
            plot()
        else:
            print("Unknown case")
            


#with open("tall building/dynamic.txt","w") as f:
#    f.write("SA:\n")
#    f.write(np.array2string(SA, precision=0)+ "\n\n")
#    f.write("Stiffness matrix:\n")
#    f.write(np.array2string(S, precision=2)+ "\n\n")
#    f.write("Mass matrix:\n")
#    f.write(np.array2string(M, precision=2)+ "\n\n")
#    f.write("Dynamic matrix:\n")
#    f.write(np.array2string(D, precision=2)+ "\n\n")
#    f.write("eigenvalues:\n")
#    f.write(np.array2string(eigenvalues, precision=2)+ "\n\n")
#    f.write("eigenvectors:\n")
#    f.write(np.array2string(eigenvectors, precision=2)+ "\n")
