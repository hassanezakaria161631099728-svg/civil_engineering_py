import sys
import numpy as np
import pandas as pd
from modules.building_elements import (stairs,RC_columns,RC_shear_force,shape_geometry_attributes,
sectorial,masses1,dynamic1,dynamic2,static_equivalent)
from modules.FEM import (generate_Z,prepare_fem_inputs,generate_elements2,plot_from_above_view,
plot_structure)
from modules.wind.wind import wind,dimensions
from modules.io import matrix_to_table,export_matrices_txt2,exptxt,read_tables_txt3

def elements():
 print("Running case 1: elements")
 # your code here
 #stairs
 story_height = 3.06 # m
 vertical_step = 18 # cm
 horizontal_step = 25 # cm
 T1 = stairs(story_height, vertical_step, horizontal_step)
 #reinforced concrete columns
 fc28,fe = 30,400
 x = np.array([0, 4, 4*2, 4*3, 4*4, 4*5, 4*6, 4*7])
 y = np.array([0, 5, 5*2, 5*3, 5*4])
 tables1,names1 = RC_columns(x,y)
 #RC shear force units are in mm and N
 At,b,d,alpha = 452,250,500,0.85/1.2
 Vu_reduced = 179000
 ft28,up,down,stmin=\
 RC_shear_force(fe,At,alpha,b,Vu_reduced,fc28,d)
 T5 = pd.DataFrame({"ft28": [ft28],"up": [up],"down": [down],"stmin": [stmin]})
 # export results
 tables2 = [T1,T5]
 names2 = ["stairs","RC_shear_force"]
 tables, names = tables1 + tables2, names1 + names2
 exptxt(tables, names, "tall building/elements.txt", 12)

def geometry():
 print("Running case 2: geometry_attributes")
 # your code here
 #shape1
 a,Lx,Ly,e = 0.3,4,4,0.2
 a1 = [a, Lx-a,  a,    e, a]
 b1 = [a,    e,  a, Ly-a, a]
 xg1 = [a/2, (Lx-a)/2+a, Lx+a/2,        a/2,      a/2]
 yg1 = [a/2,        a/2,    a/2, (Ly-a)/2+a,   a/2+Ly]
 T_scalar1, T_vec1 = shape_geometry_attributes(a1, b1, xg1, yg1)

 # general scheme RC walls coordinates
 # centre of mass vectors 
 xg1g = T_scalar1["xg_global"].iloc[0]
 yg1g = T_scalar1["yg_global"].iloc[0]

 Lbx,Lby = 28, 20 
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
 Lx,Ly = 28,20 #building dimension x y
 h_story,h_beam,b_beam = 3.06,0.4,0.3 
 nx,ny = 7,4 #number of spans on x and y
 CD = 2.5 #concrete density
 # roof top barricade
 #RC columns
 a_column = 0.55
 T_RTB,T_RC_walls,T_columns,T_beams,T_floor,T_loads_on_beams,T_tiles,m_RT,m_BLF = \
 masses1(geometry,Lx,Ly,h_story,a_column,CD,nx,ny,b_beam,h_beam)
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
 Lx, Ly = 28, 20
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

def seismic():
 print("Running case : seismic analysis")
 # your code here
 T1,T2,T3,T4 = 0.1,0.5,2,4 #APR24 table3.4 
 h_building = 30.6  
 T_imperial = 0.05 * h_building ** 0.75
 Tx,Ty = 0.914,1.021
 sagx = static_equivalent(Tx,T_imperial,T1,T2,T3,T4)
 sagy = static_equivalent(Ty,T_imperial,T1,T2,T3,T4)
 print(T_imperial)
 print(sagx)
 print(sagy)

def plot():
 print("Running case 2: building upper vue ground level XY")
 # your code here
 x = np.array([0, 4, 4*2, 4*3, 4*4, 4*5, 4*6, 4*7])
 y = np.array([0, 5, 5*2, 5*3, 5*4])
 n, h_base, h_story = 9, 3.06, 3.06
 z = generate_Z(n+2, h_base, h_story)
 # Cartesian product
 nodes_xy = np.array([[xi, zj] for zj in y for xi in x])
 nodes_xz = np.array([[xi, zj] for zj in z for xi in x])
 nodes_yz = np.array([[xi, zj] for zj in z for xi in y])
 A_beam = 0.3 * 0.5
 I_beam = (0.3 * 0.5**3) / 12
 A_col = 0.4 * 0.4
 I_col = (0.4 * 0.4**3) / 12
 E = 30e9  # Pa
 elements_xz = generate_elements2(x, z, A_beam, I_beam, A_col, I_col, E, q_beam=0)
 elements_yz = generate_elements2(y, z, A_beam, I_beam, A_col, I_col, E, q_beam=0)
 show_node_ids = True
 nodal_loads = []
 constraints = []
 nx = len(x)
 for i in range(nx):
    node = i  # first row (z=0)
    constraints.extend([3*node, 3*node+1, 3*node+2])
 title1, title2, title3, folder = "view_from_above_XY_Z=0", "elevation_view_XZ", "elevation_view_YZ", "tall building"  
 filename1, filename2, filename3 = "ground_level_XY2.png", "elevation_view_XZ.png", "elevation_view_YZ.png"
 elem_conn_xz, elem_props_xz = prepare_fem_inputs(elements_xz)
 elem_conn_yz, elem_props_yz = prepare_fem_inputs(elements_yz)
 plot_from_above_view(nodes_xy, x, y, folder, filename1, title1, "X", "Y")
 plot_structure(nodes_xz,elements_xz,constraints,show_node_ids,folder,filename2,title2,"X","Z")
 plot_structure(nodes_yz,elements_yz,constraints,show_node_ids,folder,filename3,title3,"Y","Z")

def wind_analysis():
 print("Running case 6: wind_analysis")
 # your code here
 #python tall_building.py wind_analysis
 eurocode = read_tables_txt3("tall building/eurocode.txt")
 wind_entry = read_tables_txt3("tall building/wind_entry.txt")
 ba = wind_entry["building_attributes"]
 Lx = ba["Lx_m"].iloc[0]
 Ly = ba["Ly_m"].iloc[0]
 direction1='wind1'
 direction2='wind2'
 geo = wind_entry["geography_attributes"]
 wzs = eurocode["wind_zones"]
 gcs = eurocode["ground_categories"]
 T1,T2,T3,T4,T5,Troof1,Twall=wind(ba,Lx,Ly,direction1,geo,wzs,gcs)
 T6,T7,T8,T9,T10,Troof2,_=wind(ba,Lx,Ly,direction2,geo,wzs,gcs)
 Tables = [T1,T2,T3,T4,T5,Troof1,Twall,T6,T7,T8,T9,T10,Troof2]
 Names = ["T1", "T2", "T3", "T4", "T5", "Troof1", "Twall",
 "T6", "T7", "T8", "T9", "T10", "Troof2"]
 exptxt(Tables, Names, "tall building/wind.txt", 12)

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
        elif command == "seismic":
            seismic()
        elif command == "wind_analysis":
            wind_analysis()
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
