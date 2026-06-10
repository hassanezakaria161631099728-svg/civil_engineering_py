import sys
import numpy as np
import pandas as pd
from modules.building_elements import (stairs,RC_structure,RC_shear_force,masses,dynamic1,dynamic2,seismic,geometry,moments_from_shear)
from modules.FEM import (generate_Z,prepare_fem_inputs,generate_elements2,plot_from_above_view,
plot_structure)
from modules.wind.wind import wind,dimensions
from modules.io import matrix_to_table,export_matrices_txt2,exptxt,read_tables_txt3,matrices_to_tables2,matrices_to_tables4

#here we define the building from scratch starting by the columns mass centers coordinates in x and y so we define surface then we use the input base floor heigth and current floor height and number of floors to define the total height to the building then we define the surface of each floor using x and y 
#and we complete the rest of this segment
def elements():
 print("Running case 1: elements")
 # your code here
 #stairs
 story_height = 3.06 # m
 vertical_step = 17 # cm
 horizontal_step = 30 # cm
 platform_length1,platform_length2 = 110,160 #cm
 platform_width = 4
 slope_width = 1.25 #m
 tables1,names1,slope_surface1,slope_surface2,platform_surface1,platform_surface2 = \
 stairs(story_height, vertical_step, horizontal_step,platform_length1,platform_length2,platform_width,slope_width)
 #reinforced concrete columns
 fc28,fe = 30,500
 x = np.array([0, 4.4, 8.2, 12, 16.6, 20.4, 24.2, 28.6])
 y = np.array([0, 2, 8, 13.1, 18.2, 24.2, 26.2])
 n_floors,fc28,fe = 8,30,500
 tables2, names2, a, S_columns, Lbeamx, Lbeamy, Sbeamx, Sbeamy, hbeamx, hbeamy, S_RCwalls = \
 RC_structure(x,y,n_floors,fc28,fe) 
 #RC shear force units are in mm and N
 # At,b,d,alpha = 452,250,500,0.85/1.2
 # Vu_reduced = 179000
 # ft28,up,down,stmin=\
 # RC_shear_force(fe,At,alpha,b,Vu_reduced,fc28,d)
 # T2 = pd.DataFrame({"ft28": [ft28],"up": [up],"down": [down],"stmin": [stmin]})
 #masses
 S_RCwalls,L_RCwalls,L_balcony,w_balcony,n_balconies,L_columns = S_RCwalls-24*0.16,44,4.25,1.2,4,7.6
 L_slope,w_slope,L_platform,w_platform,beam_heigth= 2.4,1.25,2.2,3,0.4
 tables3, names3 = \
 masses(x,y,a,story_height,S_columns,Sbeamx,Sbeamy,hbeamx,hbeamy,L_RCwalls,L_columns,S_RCwalls,
 slope_surface1,slope_surface2,platform_surface1,platform_surface2,
 L_balcony,w_balcony,n_balconies,L_slope,w_slope,L_platform,w_platform,beam_heigth)
 # export results
 tables, names = tables1 + tables2 + tables3, names1 + names2 + names3
 exptxt(tables, names, "tall building/elements.txt", 12)

#this segment dynamic() is used to study the mouvement of the building due to it's proper mass without any external forces and this by using the functions dynamic1 and dynamic2 and then 
#studying the mouvement of the building due to external forces and we mean seismic analysis and in this code we use the algerian regulation made at 2024 we refer to it as APR24 Algerian paraseimic regulation
  
def dynamic():
 print("Running case 4: dynamic analysis")
 # your code here
 n = 8 #number of floors above the base floor
 M1, M2, M3 = 805, 802.66, 795.6 #masses
 Lx, Ly = 29, 21
 # SA and mass matrices and Elasticity module
 h = 3.06 #m story height
 # case there is only "with bricks" or "no bricks"
 case = "with bricks"
 fc28 = 30
 SA, M, M_vec, W_vec, MR, E, building_weight, building_height, imperial_period = \
 dynamic1(n,M1,M2,M3,h,case,Lx,Ly,fc28)
 Ix, Iy, Iw = 15.379, 15.72, 4581.9
 fx, Sx, Dx, eigen_valuesx, eigen_vectors, periods_x = dynamic2(h,E,Iy,SA,M) 
 fy, Sy, Dy, eigen_valuesy, _, periods_y = dynamic2(h,E,Ix,SA,M) 
 fw, Sw, Dw, eigen_valuesw, _, periods_w = dynamic2(h,E,Iw,SA,MR) 
 T = pd.DataFrame({"eigen_valuesx": eigen_valuesx,"eigen_valuesy": eigen_valuesy,"eigen_valuesw": eigen_valuesw,
 "periods_x_s": periods_x,"periods_y_s": periods_y,"periods_w_s": periods_w})
 beta = eigen_vectors @ M_vec / (eigen_vectors**2 @ M_vec)
 betaup1 = eigen_vectors * W_vec
 betadown1 = eigen_vectors**2 * W_vec
 betaup2 = np.sum(betaup1, axis=1)
 betadown2 = np.sum(betadown1, axis=1)
 alpha = betaup2**2 / betadown2 * (1/building_weight)
 sum_alpha = np.sum(alpha)
 T2 = pd.DataFrame({"Elasticity_module": [E],"Iy": [Iy],"Ix": [Ix],"fx": [fx],"fy": [fy],"fw": [fw],
 "imperial_period":[imperial_period],"building_weight":building_weight,"building_height":building_height,
 "sum_alpha":sum_alpha})
 period1,period2,period3 = 0.1,0.5,2 #APR24 table3.4 
 #response spectrum
 Q = 1
 periods_new_x,SadT0x, V_vecx, Fx, Fsrssx, Vx, Vsrssx = \
 seismic(periods_x,imperial_period,period1,period2,period3,building_weight,beta,eigen_vectors,M_vec,Q)
 periods_new_y,SadT0y, V_vecy, Fy, Fsrssy, Vy, Vsrssy = \
 seismic(periods_y,imperial_period,period1,period2,period3,building_weight,beta,eigen_vectors,M_vec,Q)
 T3 = pd.DataFrame({"sadT0x": SadT0x,"sadT0y": SadT0y,"Vx": V_vecx,"Vy": V_vecy,"beta":beta,
 "periods_new_x":periods_new_x,"periods_new_y":periods_new_y,
 "betaup2":betaup2,"betadown2":betadown2,"alpha":alpha})
 T4 = pd.DataFrame({"Fx":Fsrssx,"Fy":Fsrssy,"Vx":Vsrssx,"Vy":Vsrssy,"M":M_vec,"W":W_vec,})
 matrices = [SA, M, Sx, Dx, eigen_vectors, Sy, Dy, MR, Sw, Dw, Fx,Fy,Vx,Vy,betaup1,betadown1]
 names1 = ["SA","M","Sx","Dx","eigen_vectors","Sy","Dy","MR","Sw","Dw","forces_x","forces_y",
 "Vx","Vy","betaup","betadown"]
 tables1 = matrices_to_tables2(matrices)
 tables2 = [T,T2,T3,T4]
 names2 = ["periods_secondes","scalars","vectors1","vectors2"]
 #beta = beta.reshape(1, -1)      # (1, n_modes)
 #SadT0x    = SadT0x.reshape(1, -1)       # (1, n_modes)
 #m_vec     = m_vec.reshape(-1, 1)        # (n_floors, 1)
 #g = 10
 #F = eigen_vectors * beta * SadT0x * g * M_vec
 #export results
 tables = tables1 + tables2
 names = names1 + names2 
 exptxt(tables, names, "tall building/dynamic.txt", 12)

#this segment plot() is used to draw the building scheme in three axis systems X length Y width Z heigth
#the upper view in XY axis where Z=0 
#the elevation view XZ
#the elevation view YZ
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

def steel():
 print("Running case 5: steel")
 N,M,B,l = 0.5439, 0.5657, 1.15, 5.75
 I = 3.1684
 segmat_negative = (N / B) - (M * l / 2 / I)
 segmat_positive = (N / B) + (M * l / 2 / I)
 lc = segmat_positive / (segmat_positive + segmat_negative) * l
 lt = l - lc
 print(segmat_negative)
 print(segmat_positive)
 print(lc)
 print(lt)

def horizontal_loads():
 print("Running case 6: horizontal loads")
 #RC walls
 Lbx,Lby = 29.4,27
 tables1, names1, S_RCwalls, Ix_total, Iy_total, dx, dy, Iw_scalar = geometry(Lbx,Lby)
 e = 1.45 #m 
 Fx = np.array([2080.371, 1301.305, 1240.7, 1377.8, 1382.648, 1404.712, 1354.783, 970.515, 357.536])
 Fy = np.array([2074.35, 1294.428, 1235.761, 1374.982, 1384.167, 1404.017, 1354.295, 970.114, 357.361])

 # inertia ratios
 Ix_ratios = Ix_total / Ix_total.sum()
 Iy_ratios = Iy_total / Iy_total.sum()

 # outer product
 # translation forces matrix
 trans_forces_x,trans_forces_y = np.outer(Fx, Ix_ratios),np.outer(Fy,Iy_ratios) # translation forces matrix 
 # rotation forces matrix
 rot_forces_x,rot_forces_y = np.outer(Fx, e * Ix_total * dx / Iw_scalar),np.outer(Fy, e * Iy_total * dy / Iw_scalar) # translation forces matrix 
 # sum 
 forces_x,forces_y = trans_forces_x + rot_forces_x, trans_forces_y + rot_forces_y
 # shear forces
 Vx,Vy = np.cumsum(forces_x, axis=0),np.cumsum(forces_y, axis=0)
 # moments
 Mx,My = moments_from_shear(Vx, h=3.06),moments_from_shear(Vy, h=3.06)

 matrices = [trans_forces_x,rot_forces_x,forces_x,Vx,Mx,trans_forces_y,rot_forces_y,forces_y,Vy,My]
 tables2 = matrices_to_tables4(matrices, row_prefix='floor', col_prefix='wall')
 names2 = ["translation_forces_x","rotation_forces_x","forces_x","shear_forces_x","moments_x",
 "translation_forces_y","rotation_forces_y","forces_y","shear_forces_y","moments_y"] 
 tables = tables1 + tables2
 names = names1 + names2 
 #print(IxXFx.shape)
 #print(IxXFx)
 exptxt(tables, names, "tall building/horizontal_loads.txt", 12)
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a case: dynamic, columns,geometry,test")
    else:
        command = sys.argv[1]

        if command == "elements":
            elements()
        elif command == "masses":
            masses()
        elif command == "dynamic":
            dynamic()
        elif command == "plot":
            plot()
        elif command == "wind_analysis":
            wind_analysis()
        elif command == "steel":
            steel()
        elif command == "horizontal_loads":
            horizontal_loads()
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
