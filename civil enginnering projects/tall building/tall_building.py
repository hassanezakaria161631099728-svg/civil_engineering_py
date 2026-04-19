import sys
import numpy as np
import pandas as pd
from modules.building_elements import (RC_column,shape_geometry_attributes,sectorial,
building_masses,dynamic1,dynamic2)
from modules.io import matrix_to_table,export_matrices_txt2,exptxt,read_tables_txt3

def columns():
 print("Running case 2: columns analysis")
 # your code here
 # number of floors above the base level
 #in general case the base level isn't necessary the ground floor but the last underneath floor
 # the last floor under the surface of soil
 nSF = 7 # number of floors above the soil surface
 nUF = 1 # number of floors under the soil surface
 n = nSF + nUF  #total number of floors above the base level we add 1 the ground floor and we 
 # remove the last underneath floor which is the base floor  
 fc28,fe = 25,400
 S = 13.035
# dead loads G and live loads Q
 GRT,GCF = 802,665
 QRT,QCF = 100,150
 Smaj,NG,NQ,Nu,alpha,Brmin,Nd,Bcmin,amin,a,Bc,Br=\
 RC_column(fc28,fe,S,n,GCF,GRT,QRT,QCF)
 T2 = pd.DataFrame({"Smaj": Smaj.reshape(-1),"NG": NG.reshape(-1),"NQ": NQ.reshape(-1),
 "Nu": Nu.reshape(-1),"alpha": alpha.reshape(-1),"Brmin": Brmin.reshape(-1),"Nd": Nd.reshape(-1),
 "Bcmin": Bcmin.reshape(-1),"amin": amin.reshape(-1),"a": a.reshape(-1),
 "Bc": Bc.reshape(-1),"Br": Br.reshape(-1)})

#showing on terminal
# print(T2)  
# export results
 tables = [T2]
 names = ["RC_column"]
 exptxt(tables, names, "tall building/RC column.txt", 12)

def geometry():
 print("Running geometry_attributes")
 # your code here
 # RC wall 1 
 a1 = [0.45, 3.95, 0.45, 0.2] 
 b1 = [0.45, 0.2, 0.45, 2.075] 
 xg1 = [0.225, 2.425, 4.625, 0.225]
 yg1 = [0.225, 0.225, 0.225, 1.4875]

 T_scalar1, T_vec1 = shape_geometry_attributes(a1, b1, xg1, yg1)

 # RC wall 2 
 a2 = [0.45, 0.2, 0.45] 
 b2 = [0.45, 3.05, 0.45] 
 xg2 = [0.225, 0.225, 0.225]
 yg2 = [0.225, 1.975, 3.725]

 T_scalar2, T_vec2 = shape_geometry_attributes(a2, b2, xg2, yg2)

 # RC wall 3 
 a3 = [0.45, 0.2, 0.45] 
 b3 = [0.45, 3.95, 0.45] 
 xg3 = [0.225, 0.225, 0.225]
 yg3 = [0.225, 2.425, 4.625]

 T_scalar3, T_vec3 = shape_geometry_attributes(a3, b3, xg3, yg3)

 # RC wall 4 
 a4 = [0.45, 2.075] 
 b4 = [0.45, 0.2] 
 xg4 = [0.225, 1.2625]
 yg4 = [0.225, 0.225]

 T_scalar4, T_vec4 = shape_geometry_attributes(a4, b4, xg4, yg4)

 # RC wall 5 
 a5 = [4.4] 
 b5 = [0.2] 
 xg5 = [2.2]
 yg5 = [0.2]

 T_scalar5, T_vec5 = shape_geometry_attributes(a5, b5, xg5, yg5)
 T_sectorial,T_sectorial_scalars = sectorial(T_scalar1,T_scalar2,T_scalar3,T_scalar4,T_scalar5)

# export results
 tables = [T_vec1,T_scalar1, T_vec2,T_scalar2, T_vec3,T_scalar3, T_vec4,T_scalar4, T_vec5,T_scalar5,
 T_sectorial, T_sectorial_scalars]
 names = ["vectors1","scalars1", "vectors2","scalars2", "vectors3","scalars3",
 "vectors4","scalars4","vectors5","scalars5","sectorial_attributes","sectorial_attributes_scalars"]
 exptxt(tables, names, "tall building/geometry attributes.txt", 12)

def masses():
 print("running masses")
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
 
def test():
 print("Running case 2: testing")
 # your code here
 n = 16
 Ix_total,Iy_total = np.zeros((n)), np.zeros((n))
 Ix_total[0:4], Iy_total[0:4] = 1, 1
 Ix_total[4:8], Iy_total[4:8] = 2, 2
 Ix_total[8:10], Iy_total[8:10] = 3, 3
 Ix_total[10:14], Iy_total[10:14] = 4, 4
 Ix_total[14:16], Iy_total[14:16] = 5, 5

 print(Ix_total)

def dynamic():
 print("Running case 1: dynamic analysis")
 # your code here
 n = 9
 M1, M2, M3 = 710.021, 703.74, 705.94 #masses
 # SA and mass matrices and Elasticity module
 SA, M, E, TSA, TM = dynamic1(n,M1,M2,M3)
 h = 3.24 #m story height
 Ix, Iy = 97.13, 808.809
 fx, TSx, TDx, eigen_valuesx, Teigen_vectors, periods_x = dynamic2(h,E,Iy,SA,M) 
 fy, TSy, TDy, eigen_valuesy, _, periods_y = dynamic2(h,E,Ix,SA,M) 
 names = ["SA","M","Sx","Dx","eigen_vectors","Sy","Dy"]
 matrices = [TSA, TM, TSx, TDx, Teigen_vectors, TSy, TDy]
# float_format = "{:.3f}".format
 export_matrices_txt2(matrices, names, "tall building/dynamic.txt")
 T = pd.DataFrame({"eigen_valuesx": eigen_valuesx,"eigen_valuesy": eigen_valuesy,
 "periods_x_s": periods_x,"periods_y_s": periods_y})
 T2 = pd.DataFrame({"Elasticity_module": [E],"Iy": [Iy],"Ix": [Ix],"fx": [fx],"fy": [fy]})
# export results
 tables = [T,T2]
 names = ["periods_secondes","scalars"]
 exptxt(tables, names, "tall building/dynamic2.txt", 12)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a case: dynamic, columns,geometry,test")
    else:
        command = sys.argv[1]

        if command == "columns":
            columns()
        elif command == "geometry":
            geometry()
        elif command == "masses":
            masses()
        elif command == "dynamic":
            dynamic()
        elif command == "test":
            test()
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
