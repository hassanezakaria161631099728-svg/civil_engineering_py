import sys
import numpy as np
import pandas as pd
from modules.building_elements import (stairs,RC_columns,RC_shear_force,shape_geometry_attributes,
sectorial,masses1,dynamic1,dynamic2)
from modules.FEM import generate_grid,plot_grid
from modules.io import matrix_to_table,export_matrices_txt2,exptxt,read_tables_txt3

def elements():
 print("Running case 1: elements")
 # your code here
 #stairs
 story_height = 3.06 # m
 vertical_step = 18 # cm
 horizontal_step = 25 # cm
 T1 = stairs(story_height, vertical_step, horizontal_step)
 #reinforced concrete column
 # number of floors above the base level
 #in general case the base level isn't necessary the ground floor but the last underneath floor
 # the last floor under the surface of soil
 nSF = 9 # number of floors above the soil surface
 nUF = 0 # number of floors under the soil surface
 n = nSF + nUF  #total number of floors above the base level we add 1 the ground floor and we 
 # remove the last underneath floor which is the base floor  
 fc28,fe = 30,400
 # dead loads G and live loads Q
 x = np.array([0, 3.9, 7.75, 12.25, 18.8, 23.2])
 y = np.array([0, 3.7, 7.4, 13.8, 18.6])
 tables,names = RC_columns(x,y)
 exptxt(tables, names, "tall building/RC_columns.txt", 12)
 #RC shear force units are in mm and N
 At,b,d,alpha = 452,250,500,0.85/1.2
 Vu_reduced = 179000
 ft28,up,down,stmin=\
 RC_shear_force(fe,At,alpha,b,Vu_reduced,fc28,d)
 T5 = pd.DataFrame({"ft28": [ft28],"up": [up],"down": [down],"stmin": [stmin]})
 # export results
 tables = [T1,T5]
 names = ["stairs","RC_shear_force"]
 exptxt(tables, names, "tall building/elements.txt", 12)

def geometry():
 print("Running case 2: geometry_attributes")
 # your code here
 #shape1
 a,Lx,Ly,e = 0.45,4.5,4.5,0.2
 a1 = [a, Lx-a,  a,    e, a]
 b1 = [a,    e,  a, Ly-a, a]
 xg1 = [a/2, (Lx-a)/2+a, Lx+a/2,        a/2,      a/2]
 yg1 = [a/2,        a/2,    a/2, (Ly-a)/2+a,   a/2+Ly]
 T_scalar1, T_vec1 = shape_geometry_attributes(a1, b1, xg1, yg1)

 # general scheme RC walls coordinates
 # centre of mass vectors 
 xg1g = T_scalar1["xg_global"].iloc[0]
 yg1g = T_scalar1["yg_global"].iloc[0]

 Lbx,Lby = 22.5, 22.5 
 # X
 X = [xg1g, Lbx-xg1g, xg1g, Lbx-xg1g]

 # Y
 Y = [yg1g, yg1g, Lby-yg1g, Lby-yg1g]

 T_sectorial,T_sectorial_scalars = sectorial(T_scalar1,X,Y)

# export results
 tables = [T_vec1,T_scalar1,T_sectorial, T_sectorial_scalars]
 names = ["vectors1","scalars1", "sectorial_attributes","sectorial_attributes_scalars"]
 exptxt(tables, names, "tall building/geometry.txt", 12)

def masses():
 print("running case 3: masses")
 #your code here
 geometry = read_tables_txt3("tall building/geometry.txt")
 Lx,Ly = 22.5,22.5 #building dimension x y
 h_story,h_beam,b_beam = 3.06,0.4,0.3 
 nx,ny = 5,5
 CD = 2.5 #concrete density
 # roof top barricade
 #RC columns
 n_columns,a_column = 36,0.45
 T_RTB,T_RC_walls,T_columns,T_beams,T_floor,T_loads_on_beams,T_tiles,m_RT,m_BLF = \
 masses1(geometry,Lx,Ly,h_story,a_column,n_columns,CD,nx,ny,b_beam,h_beam)
 print(m_RT)
 print(m_BLF)
 #export results
 tables = [T_RTB,T_RC_walls,T_columns,T_beams,T_floor,T_loads_on_beams,T_tiles]
 names = ["roof_top_barricade","RC_walls", "RC_columns","RC_beams","floor",
 "loads_on_beams","tiles"]
 exptxt(tables, names, "tall building/masses.txt", 18)
 
def dynamic():
 print("Running case 4: dynamic analysis")
 # your code here
 n = 9 #number of floors above the base floor
 M1, M2, M3 = 549.56, 549.56, 524.36 #masses
 Lx, Ly = 22.5, 22.5
 # SA and mass matrices and Elasticity module
 h = 3.06 #m story height
 # case there is only "with bricks" or "no bricks"
 case = "with bricks"
 SA, M, MR, E, TSA, TM, T_imperial = dynamic1(n,M1,M2,M3,h,case,Lx,Ly)
 Ix, Iy, Iw = 23.865, 23.865, 4581.9
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
