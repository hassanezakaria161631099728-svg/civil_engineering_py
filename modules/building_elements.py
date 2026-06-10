import math
import numpy as np
import pandas as pd
from modules.io import matrix_to_table,matrices_to_tables4,exptxt
# stairs
def stairs(story_height, vertical_step, horizontal_step,platform_length1,platform_length2,platform_width,slope_width):
 if 16 <=vertical_step <= 19 and 23 <= horizontal_step <= 32: # cm
   print("vertical and horizontal step are within accepted segment")
 else:      
   print("either vertical or horizontal step is out accepted segment or both")

 stairs_height = story_height / 2 * 100 # converting to cm 
 n_stairs = math.ceil(stairs_height / vertical_step)
 slope_length = n_stairs * horizontal_step
 slope_angle = math.atan(vertical_step / horizontal_step)
 slope_angle_deg = math.degrees(slope_angle)
 total_length2 = slope_length / math.cos(slope_angle) + 2 * platform_length1
 total_length3 = (slope_length  + 2 * platform_length1) / 100 
 thickness_min = total_length2 / 30
 thickness_max = total_length2 / 20
 platform_surface1,platform_surface2 = platform_length1 * platform_width / 100, platform_length2 * platform_width / 100
 slope_surface1,slope_surface2 = slope_length * slope_width / 100, slope_length * platform_width / 100
 T1 = pd.DataFrame({"story_height": [story_height],"stairs_height": [stairs_height],
 "vertical_step": [vertical_step],"n_stairs": [n_stairs],"horizontal_step": [horizontal_step],
 "stairs_length": [slope_length],"slope_angle": [slope_angle],"slope_angle_deg": [slope_angle_deg]})
 T2 = pd.DataFrame({"total_lenght2_cm": [total_length2],"total_lenght3_m": [total_length3],
 "thickness_min":[thickness_min],"thickness_max":[thickness_max],"slope_surface1":[slope_surface1],
 "slope_surface2":[slope_surface2],"platform_surface1":[platform_surface1],
 "platform_surface2":[platform_surface2]})
 tables = [T1,T2]
 names = ["stairs1","stairs2"]
 return tables,names,slope_surface1,slope_surface2,platform_surface1,platform_surface2

def RC_column(fc28,fe,S,n):
 #note: the input S is a matrix value 
 Smaj = 1.1 * S #m # this is the majorated surface held by column
 Q_current_floor,Q_roof_top,G_current_floor,G_roof_top = 150,100,665,787.6
 NQ = compute_NQ(n+1,Q_current_floor,Q_roof_top,Smaj) 
 NG = compute_NG(n+1,G_current_floor,G_roof_top,Smaj) 
 Nu = (1.35 * NG + 1.5 * NQ) / 1000 # converting KN to MN
 Smaj = np.full((n+1, 1), Smaj)
 alpha = 0.85 / 1.2
 alpha = np.full((n+1, 1), alpha)
 Brmin = Nu / (alpha * (fc28 / (0.9 * 1.5) + 0.01 * fe / 1.15)) #m2
 #gamma c is 1.5 and gamma s is 1.15 
 Bcmin = Nu / (0.3 * fc28)
 amin = Bcmin**0.5
 a = np.ceil(amin*20)
 Bc = a**2 # we have a rectangular column
 Br = (a - 0.02)**0.5
 T = pd.DataFrame({"Smaj": Smaj.reshape(-1),"NG": NG.reshape(-1),"NQ": NQ.reshape(-1),
 "Nu": Nu.reshape(-1),"alpha": alpha.reshape(-1),"Brmin": Brmin.reshape(-1),
 "Bcmin": Bcmin.reshape(-1),"amin": amin.reshape(-1),"a": a.reshape(-1),
 "Bc": Bc.reshape(-1),"Br": Br.reshape(-1)})
 return T

def RC_columns(x,y,spansx,spansy,n_floors,fc28,fe):
 n,p = len(x),len(y)
 Lx,Ly,S = np.zeros((n)), np.zeros((p)), np.zeros((n,p))
 i,j = np.arange(1, n-1),np.arange(1, p-1)
 Lx[i] = x[i+1]-x[i-1]
 Lx[0] = x[1]-x[0]
 Lx[n-1] = x[n-1]-x[n-2]
 Ly[j] = y[j+1]-y[j-1]
 Ly[0] = y[1]-y[0]
 Ly[p-1] = y[p-1]-y[p-2]
 S = np.outer(Ly, Lx) / 4
 Smaj = S * 1.1 
 GRT,GCF,QRT,QCF = 787.6, 665, 100, 150
 NG = 1.1 * (GRT + GCF * n_floors) * Smaj / 100
 if n_floors < 5: NQ = (QRT + n_floors * QCF) * Smaj / 100
 else: NQ = (QRT + (4 + (n_floors-5)*0.5) * QCF) * Smaj / 100

 Nu = (1.35 * NG + 1.5 * NQ) / 1000 # converting KN to MN
 alpha = 0.85 / 1.2
 Brmin = Nu / (alpha * (fc28 / (0.9 * 1.5) + 0.01 * fe / 1.15)) #m2
 #gamma c is 1.5 and gamma s is 1.15 
 Bcmin = Nu / (0.3 * fc28)
 amin = Bcmin**0.5
 a = np.ceil(amin*20) / 20
 Bc = a**2 # we have a rectangular column
 Br = (a - 0.02)**0.5 
 return S, Smaj, NG, NQ, Nu, Brmin, Bcmin, amin, a, Bc, Br

def RC_structure(x,y,n_floors,fc28,fe):
 spansx, spansy = x[1:] - x[:-1], y[1:] - y[:-1]
 #RC columns
 S, Smaj, NG, NQ, Nu, Brmin, Bcmin, amin, a, Bc, Br = RC_columns(x,y,spansx,spansy,n_floors,fc28,fe)
 #support beams
 Lbeamx,Lbeamy = beam_clear_lengths(a, spansx, spansy)
 #hbeamxmax,hbeamymax = Lbeamx/10,Lbeamy/10  
 hbeamx = beam_heights(Lbeamx)
 hbeamy = beam_heights(Lbeamy)
 wbeamx = beam_width(hbeamx)
 wbeamy = beam_width(hbeamy)
 Sbeamx, Sbeamy = Lbeamx * wbeamx, Lbeamy * wbeamy
 matrices = [S, Smaj, NG, NQ, Nu, Brmin, Bcmin, amin, a, Bc, Br, Lbeamx, Lbeamy,
hbeamx, hbeamy, wbeamx, wbeamy, Sbeamx, Sbeamy] 
 #RC walls
 #tables, names, S_RCwalls, Ix_total, Iy_total, dx, dy, Iw_scalar 
 tables2, names2, S_RCwalls, Ix_total, Iy_total, dx, dy, Iw_scalar = geometry(x[-1]+a[0,0],y[-1]+a[0,0])
 tables1 = matrices_to_tables4(matrices,"x","y")
 names1 = ["surface_held_by_column","surface_held_by_column * 1.1",
"NG","NQ","Nu","Brmin","Bcmin","amin","a","Bc","Br","Lbeamx","Lbeamy",
"hbeamx","hbeamy","wbeamx", "wbeamy","Sbeamx", "Sbeamy"]
 tables, names = tables1 + tables2, names1 + names2 
 return tables, names, a, Bc, Lbeamx, Lbeamy, Sbeamx, Sbeamy, hbeamx, hbeamy, S_RCwalls 

def masses(x,y,a,h_story,S_columns,Sbeamx,Sbeamy,hbeamx,hbeamy,L_RCwalls,L_columns,S_RCwalls,
 slope_surface1,slope_surface2,platform_surface1,platform_surface2,          
 L_balcony,w_balcony,n_balconies,L_slope,w_slope,L_platform,w_platform,beam_heigth):
 CD = 2.5
 #roof top barricade 
 G_RTB = 211.1
 L_RTB = (x[-1] + y[-1] + a[0,0] * 2) * 2 #m
 m_RTB = G_RTB * L_RTB / 1000
 # RC walls
 h_RC_wallx,h_RC_wally = h_story - hbeamx[0,0], h_story - hbeamy[0,0]
 v_RC_walls = S_RCwalls/2 * h_RC_wallx + S_RCwalls/2 * h_RC_wally 
 m_RC_walls = v_RC_walls.sum() * CD           
 # RC columns
 m_columns = h_story * S_columns.sum() *  CD 
 # RC beams
 v_beamsx,v_beamsy = Sbeamx * hbeamx, Sbeamy * hbeamy  
 m_beams = (v_beamsx.sum()+v_beamsy.sum()) * CD 
 T1 = pd.DataFrame({"length_roof_top_barricade":[L_RTB],"mass_roof_top_barricade": [m_RTB],
 "v_RCwalls": [v_RC_walls.sum()],"m_RCwalls": [m_RC_walls],"m_columns": [m_columns],"m_beams": [m_beams]})
 Q_RTF,Q_CF,G_RTF,G_CF = 100,150,787.6,665  
 #stairs
 G_slope,G_platform,Q_stairs = 766.76,571,250
 #stairs slope
 m_slope = slope_surface1 * G_slope / 1000
 #stairs platform
 m_platform = platform_surface2 * G_platform / 1000
 m_stairs_BLF = m_slope + m_platform
 m_stairs_CF = 2 * m_slope + m_platform 
 S_stairs2 = slope_surface2 + platform_surface2 
 T2 = pd.DataFrame({"m_slope":[m_slope],"m_platform": [m_platform],"m_stairs_BLF":[m_stairs_BLF],
 "m_stairs_CF": [m_stairs_CF],"surface_stairs2": [S_stairs2]})
 #floor rooftop and current floor
 S_floor_rooftop = x[-1] * y[-1] - (S_columns.sum() + Sbeamx.sum() + Sbeamy.sum() + S_RCwalls) 
 S_floor_current = x[-1] * y[-1] - (S_columns.sum() + Sbeamx.sum() + Sbeamy.sum() + S_RCwalls + S_stairs2) # same as surface of the floor before last floor
 m_RTF = G_RTF * S_floor_rooftop / 1000 
 m_CFF = G_CF * S_floor_current / 1000 
 #loads on beams
 m_loads_on_beams_RT = (G_RTF - 400) * (Sbeamx.sum() + Sbeamy.sum()) / 1000 #rooftop
 m_loads_on_beams_CF = (G_CF - 400) * (Sbeamx.sum() + Sbeamy.sum()) / 1000  #current floor
 #total mass rooftop
 m_RT = m_RTF + m_beams + 0.5 * (m_columns + m_RC_walls) + m_RTB + m_loads_on_beams_RT 
 + 0.3 * Q_RTF * S_floor_rooftop 
 T3 = pd.DataFrame({"S_floor_rooftop": [S_floor_rooftop],"S_floor_current": [S_floor_current],
 "rooftop_floor_mass": [m_RTF],"current_floor_mass": [m_CFF], "m_loads_on_beams_rooftop":[m_loads_on_beams_RT],
 "m_loads_on_beams_current_floor":[m_loads_on_beams_CF],"rooftop_mass":[m_RT]})
 #tiles
 G_tile = 299
 h_tiles = h_story - beam_heigth
 L_tiles = 2 * (x[-1] + y[-1] + 0.4 + 0.25) - L_RCwalls - L_columns
 m_tiles = G_tile * h_tiles * L_tiles / 1000 
 #balcony
 G_balcony,Q_balcony = 589,250 # kg/m2
 S_balcony = L_balcony * w_balcony * n_balconies 
 m_balcony = G_balcony * S_balcony / 1000
 #balcony protection
 G_balcony_protection = 180
 m_balcony_protection = G_balcony_protection * S_balcony / 1000
 T4 = pd.DataFrame({"G_tile": [G_tile],"h_tiles": [h_tiles],"L_tiles": [L_tiles],"m_tiles": [m_tiles],
 "s_balcony": [S_balcony],"m_balcony": [m_balcony],"m_balcony_protection":[m_balcony_protection]})
 m_BLF = m_CFF + m_beams + m_columns + m_RC_walls + m_loads_on_beams_RT + m_stairs_BLF + m_balcony
 + 0.3 * (Q_CF * S_floor_current + Q_stairs * S_stairs2 + Q_balcony * S_balcony) 
 m_CF = m_CFF + m_beams + m_columns + m_RC_walls + m_loads_on_beams_RT + m_stairs_CF
 + 0.3 * (Q_CF * S_floor_current + Q_stairs * S_stairs2 + Q_balcony * S_balcony) 
 T5 = pd.DataFrame({"mass_before_last_floor":[m_BLF],"mass_current_floor":[m_CF]})
 tables = [T1,T2,T3,T4,T5]
 names = ["T1","T2","T3","T4","T5"]
 return tables,names

def geometry(Lbx,Lby):
 #shape1
 #a1,L,a2,e = 0.3,4,0.4,0.2
# L_rcwall = L - (a1+a2)/2
# a =  [a1,        L_rcwall,               a2,               e]
# b =  [a1,               e,               a2,        L_rcwall]
# xg = [a1/2, L_rcwall/2+a1, a1+L_rcwall+a2/2,            a1/2]
# yg = [a2/2,          a2/2,             a2/2, L_rcwall/2 + a2]
 #shape1
 a1 = [0.4, 4, 0.4]
 b1 = [0.4, 0.2, 0.4]
 xg1 = [0.2, 2.4, 4.6]
 yg1 = [0.2, 0.3, 0.2] 
 T_scalar1, T_vec1 = shape_geometry_attributes(a1, b1, xg1, yg1)
 #shape2
 a2 = [0.4, 0.2, 0.4, 0.2]
 b2 = [0.4, 1.6, 0.4, 2.4]
 xg2 = [0.2, 0.1, 0.2, 0.1]
 yg2 = [0.2, 1.2, 2.2, 3.6] 
 T_scalar2, T_vec2 = shape_geometry_attributes(a2, b2, xg2, yg2)
 #shape3
 a3 = [0.2, 0.4]
 b3 = [4, 0.4]
 xg3 = [0.3, 0.2]
 yg3 = [2, 4.2] 
 T_scalar3, T_vec3 = shape_geometry_attributes(a3, b3, xg3, yg3)
 #shape4
 a4 = [0.2, 0.4]
 b4 = [3.3, 0.4]
 xg4 = [0.3, 0.2]
 yg4 = [1.65, 3.5] 
 T_scalar4, T_vec4 = shape_geometry_attributes(a4, b4, xg4, yg4)

 # general scheme RC walls coordinates
 # centre of mass vectors 
 xgg1,xgg2,xgg3 = T_scalar1["xg_global"].iloc[0],T_scalar2["xg_global"].iloc[0],T_scalar3["xg_global"].iloc[0]
 ygg1,ygg2,ygg3 = T_scalar1["yg_global"].iloc[0],T_scalar2["yg_global"].iloc[0],T_scalar3["yg_global"].iloc[0]
 xgg4 = T_scalar4["xg_global"].iloc[0]
 ygg4 = T_scalar4["yg_global"].iloc[0]

 #Lbx,Lby = 28, 20 #building dimensions on x and y 
 # X
 X = [xgg1,Lbx-xgg1,xgg1,Lbx-xgg1,xgg1,Lbx-xgg1, 8.2+xgg2,Lbx-8.2-xgg2, xgg3,Lbx-xgg3,xgg3,Lbx-xgg3, xgg4,Lbx-xgg4,xgg4,Lbx-xgg4]
 # Y
 Y = [ygg1,ygg1,Lby-ygg1,Lby-ygg1,Lby/2,Lby/2, ygg2,Lby-ygg2, 2+ygg3,2+ygg3,Lby-2-ygg3,Lby-2-ygg3, 8+ygg4,8+ygg4,Lby-8-ygg4,Lby-8-ygg4]
 n = 16
 T_sectorial,T_sectorial_scalars,A_scalar, Ix_total, Iy_total, dx, dy, Iw_scalar = \
 RC_walls(T_scalar1,T_scalar2,T_scalar3,T_scalar4,X,Y,n)
 #export results
 tables = [T_vec1,T_scalar1,T_vec2,T_scalar2,T_vec3,T_scalar3,T_vec4,T_scalar4,
 T_sectorial, T_sectorial_scalars]
 names = ["vectors1","scalars1","vectors2","scalars2","vectors3","scalars3","vectors4","scalars4",
 "sectorial_attributes","sectorial_attributes_scalars"]

 return tables, names, A_scalar, Ix_total, Iy_total, dx, dy, Iw_scalar 

def moments_from_shear(V, h=3.06):

    M = np.zeros_like(V, dtype=float)

    for k in range(1, V.shape[0]):
        M[k] = M[k-1] + V[k] * h

    return M

def RC_walls(T_scalar1,T_scalar2,T_scalar3,T_scalar4,X,Y,n):
# we define geometrical attributes for reinforced concrete walls
#inertia X axis
 Ix_total1,Ix_total2 = T_scalar1["Ix_total"].iloc[0],T_scalar2["Ix_total"].iloc[0]
 Ix_total3,Ix_total4 = T_scalar3["Ix_total"].iloc[0],T_scalar4["Ix_total"].iloc[0]
# Ix_total5 = T_scalar5["Ix_total"].iloc[0]
#inertia Y axis
 Iy_total1,Iy_total2 = T_scalar1["Iy_total"].iloc[0],T_scalar2["Iy_total"].iloc[0]
 Iy_total3,Iy_total4 = T_scalar3["Iy_total"].iloc[0],T_scalar4["Iy_total"].iloc[0]
# Iy_total5 = T_scalar5["Iy_total"].iloc[0]
# surfaces 
 A_total1,A_total2 = T_scalar1["A_total"].iloc[0],T_scalar2["A_total"].iloc[0]
 A_total3,A_total4 = T_scalar3["A_total"].iloc[0],T_scalar4["A_total"].iloc[0]
# inertia vectors
 Ix_total,Iy_total,A_total = np.zeros((n)), np.zeros((n)), np.zeros((n))
 Ix_total[0:6], Iy_total[0:6], A_total[0:6] = Ix_total1, Iy_total1, A_total1 
 Ix_total[6:8], Iy_total[6:8], A_total[6:8] = Ix_total2, Iy_total2, A_total2 
 Ix_total[8:12], Iy_total[8:12], A_total[8:12] = Ix_total3, Iy_total3, A_total3 
 Ix_total[12:16], Iy_total[12:16], A_total[12:16] = Ix_total4, Iy_total4, A_total4 

 A_scalar,Ix_scalar,Iy_scalar = np.sum(A_total), np.sum(Ix_total),np.sum(Iy_total)
 #global torsion center
 XC = np.sum(Ix_total * X) / Ix_scalar
 YC = np.sum(Iy_total * Y) / Iy_scalar
 # Distances (broadcasting)
 dx = X - XC
 dy = Y - YC
 # sectorial inertia (parallel axis theorem)
 Iw_vec = Ix_total * dx**2 + Iy_total * dy**2
 Iw_scalar = np.sum(Iw_vec)

 RC_walls = ["RC_wall1","RC_wall2","RC_wall3","RC_wall4","RC_wall5","RC_wall6","RC_wall7","RC_wall8",
 "RC_wall9","RC_wall10","RC_wall11","RC_wall12","RC_wall13","RC_wall14","RC_wall15","RC_wall16"]
 T_sectorial = pd.DataFrame({"RC_walls": RC_walls,"A": A_total,"Ix": Ix_total,
"Iy": Iy_total,"X": X,"Y": Y,"dx": dx,"dy": dy,"Iw":Iw_vec})
 T_sectorial_scalar = pd.DataFrame({"geometry_attribute": "value","A": [A_scalar],
"Ix": [Ix_scalar],"Iy": [Iy_scalar],"XC": [XC],"YC": [YC],"Iw":Iw_scalar})

 return T_sectorial, T_sectorial_scalar, A_scalar, Ix_total, Iy_total, dx, dy, Iw_scalar


def beam_clear_lengths(A, Lx, Ly):

    A = np.asarray(A)

    ny, nx = A.shape
    # -----------------------------------
    # Horizontal beams
    # shape = (ny, nx-1)
    # -----------------------------------
    Lbeamx = np.zeros((ny, nx-1))

    for i in range(ny):
        for j in range(nx-1):

            Lbeamx[i,j] = (
                Lx[j]
                - (A[i,j] + A[i,j+1]) / 2
            )
    # -----------------------------------
    # Vertical beams
    # shape = (ny-1, nx)
    # -----------------------------------
    Lbeamy = np.zeros((ny-1, nx))

    for i in range(ny-1):
        for j in range(nx):

            Lbeamy[i,j] = (
                Ly[i]
                - (A[i,j] + A[i+1,j]) / 2
            )

    return Lbeamx, Lbeamy

def beam_heights(Lbeam):

    Lbeam = np.asarray(Lbeam)

    # -----------------------------------
    # Target preliminary sizing
    # -----------------------------------
    Hbeam = Lbeam / 12

    # -----------------------------------
    # Round UP to nearest 0.05 m
    # -----------------------------------
    Hbeam = 0.05 * np.ceil(Hbeam / 0.05)

    # -----------------------------------
    # Bounds
    # -----------------------------------
    Hmin = Lbeam / 15
    Hmax = Lbeam / 10

    # enforce limits
    Hbeam = np.maximum(Hbeam, Hmin)
    Hbeam = np.minimum(Hbeam, Hmax)

    # -----------------------------------
    # Final rounding again
    # -----------------------------------
    Hbeam = 0.05 * np.ceil(Hbeam / 0.05)

    return Hbeam

def beam_width(hbeam):

    hbeam = np.asarray(hbeam)

    # -----------------------------------
    # Target preliminary sizing
    # -----------------------------------
    wbeam = hbeam * 0.55

    # -----------------------------------
    # Round UP to nearest 0.05 m
    # -----------------------------------
    wbeam = 0.05 * np.ceil(wbeam / 0.05)

    # -----------------------------------
    # Bounds
    # -----------------------------------
    wmin = hbeam * 0.3
    wmax = hbeam * 0.8

    # enforce limits
    wbeam = np.maximum(wbeam, wmin)
    wbeam = np.minimum(wbeam, wmax)

    # -----------------------------------
    # Final rounding again
    # -----------------------------------
    wbeam = 0.05 * np.ceil(wbeam / 0.05)

    return wbeam

def RC_shear_force(fe,At,alpha,b,Vu_reduced,fc28,d): #units mm and N
  ft28 = 0.06 * fc28 + 0.6 
  up = 0.9 * fe * At * ((math.cos(math.radians(alpha)))+(math.sin(math.radians(alpha))))
  down = b *  (Vu_reduced/(b*d) - 0.3 * ft28)
  stmin = up / down
  return ft28,up,down,stmin

def compute_NQ(n, QCF, QRT, Smaj):
    base = QRT * Smaj / 100
    delta = QCF * Smaj / 100

    increments = np.zeros(n)  # initialize properly

    if n < 5:
        increments[1:] = delta

    else:
        # first segment: i = 1 → 4
        i = np.arange(1, 5)
        increments[1:5] = (1 - (i - 1) * 0.1) * delta

        # second segment: i ≥ 5
        increments[5:] = 0.5 * delta

    # cumulative sum
    NQ = base + np.cumsum(increments)

    return NQ.reshape(-1, 1)

def compute_NG(n,GCF,GRT,Smaj): 
 base = GRT * Smaj / 100
 increment = GCF * Smaj / 100
 i = np.arange(n)
 NG = 1.1 * (base + i * increment)# cumulative sum handles recursion efficiently
 NG = NG.reshape(-1, 1) 
 return NG

def inertia_composite(a, b, xg, yg):
    a = np.array(a)
    b = np.array(b)
    xg = np.array(xg)
    yg = np.array(yg)

    # Areas
    A = a * b

    # Global centroid
    A_total = np.sum(A)
    xgg = np.sum(A * xg) / A_total
    ygg = np.sum(A * yg) / A_total

    # Distances (broadcasting)
    ex = xg - xgg
    ey = yg - ygg

    # Local inertias
    Ix_local = a * b**3 / 12
    Iy_local = b * a**3 / 12

    # Global inertias (parallel axis theorem)
    Ix = Ix_local + A * ey**2
    Iy = Iy_local + A * ex**2

    # Total inertia
    Ix_total = np.sum(Ix)
    Iy_total = np.sum(Iy)

    return xgg, ygg,  A_total, Ix_total, Iy_total, A, Ix, Iy ,ex, ey, Ix_local, Iy_local

def shape_geometry_attributes(a, b, xg, yg):
 xgg, ygg,  A_total, Ix_total, Iy_total, A, Ix, Iy ,ex, ey, Ix_local, Iy_local =\
  inertia_composite(a, b, xg, yg)
 T_scalar = pd.DataFrame({"A_total": [A_total],"xg_global": [xgg],"yg_global": [ygg],
 "Ix_total": [Ix_total],"Iy_total": [Iy_total]})
 T_vec = pd.DataFrame({"a": a,"b": b,"A": A,"xg": xg,"yg": yg,"ex": ex,"ey": ey,
 "Ix_local": Ix_local,"Iy_local": Iy_local,"Ix": Ix,"Iy": Iy})
 return T_scalar, T_vec

def dynamic1(n,M1,M2,M3,h,case,Lx,Ly,fc28):
 #mass matrix
 M = np.zeros((n+1,n+1))
 for i in range(n-1): M[i,i] = M1 #fill diagonal for i=1 to n-2 
 M[n-1,n-1] = M2 #element (n-1,n-1)
 M[n,n] = M3 #element (n,n)
 Mk = np.zeros((n+1))
 for i in range(n-1): Mk[i] = M1 #fill diagonal for i=1 to n-2 
 Mk[n-1] = M2 #element (n-1,n-1)
 Mk[n] = M3 #element (n,n)
 # SA matrix
 SA=np.zeros((n+1,n+1))
 for i in range(n+1):
    for j in range(n+1):
        if i<j: SA[i,j] = (i+1)**2 * (3*(j+1)-(i+1))
        elif i==j: SA[i,j] = 2*(i+1)**3
        else : SA[i,j] = (j+1)**2 * (3*(i+1)-(j+1)) # i>j
 MR = M * (Lx**2 + Ly**2) / 12
 # Elasticity module
 E=11000 * fc28 **(1/3) * 1000 #MN/m2 to KN/m2 we multiply on 10**3
 #TSA = matrix_to_table(SA)
 #TM = matrix_to_table(M)
 if case == "no bricks": CT = 0.075
 elif case == "with bricks": CT = 0.05
 else: raise ValueError("specify the case")
 building_weight = ((n-1) * M1 + M2 + M3) * 10
 building_height = h * (n+1)  
 imperial_period = CT * building_height ** 0.75
 g = 10 #m/s2
 Wk = Mk * g 
 return SA, M, Mk, Wk, MR, E, building_weight, building_height, imperial_period

def dynamic2(h,E,I,SA,M): 
 f= h**3 / (6 * E * I) #m/KN factor
 S= f * SA # flexibility matrix
 D =  S @ M #matrix product dynamic matrix
 eigen_values, eigen_vectors = np.linalg.eig(D) #eigen values are lambdas
 #TS = matrix_to_table(S)
 #TD = matrix_to_table(D)
 #Teigen_vectors = matrix_to_table(eigen_vectors)
 periods = eigen_values ** 0.5 * 2 * 3.14
 return f, S, D, eigen_values, eigen_vectors, periods

def seismic(periods,imperial_period,period1,period2,period3,building_weight,beta,
eigen_vectors,M_vec,Q):
    # convert to numpy array
    periods = np.asarray(periods, dtype=float)
    # capped periods according to RPA
    periods_new = np.minimum(periods, 1.3 * imperial_period)
    # coefficients
    A, I, S, R, = 0.3, 1, 1.2, 4.5
    # initialize spectral acceleration vector
    SadT0 = np.zeros_like(periods_new)
    # interval 1
    mask1 = (periods_new > 0) & (periods_new < period1)
    SadT0[mask1] = (A * I * S *(2/3+(periods_new[mask1] / period2)*(2.5 * Q / R - 2/3)))
    # interval 2
    mask2 = (periods_new >= period1) & (periods_new < period2)
    SadT0[mask2] = (A * I * S * 2.5 * Q / R)
    # interval 3
    mask3 = (periods_new >= period2) & (periods_new < period3)
    SadT0[mask3] = (A * I * S * 2.5 * Q / R* period2 / periods_new[mask3])
    # interval 4
    mask4 = (periods_new >= period3) & (periods_new < 4)
    SadT0[mask4] = (A * I * S * 2.5 * Q / R* period2 * period3/ periods_new[mask4]**2)
    # invalid periods
    if np.any(periods_new <= 0) or np.any(periods_new >= 4):
        raise ValueError("Some periods are invalid")
    # damping correction
    lam = 0.85
    # modal base shear vector
    #V = lam * sadT0 * building_weight * beta
    V_vec = lam * SadT0 * building_weight 
    beta_new = beta.reshape(1, -1)      # (1, n_modes)
    SadT0_new    = SadT0.reshape(1, -1)       # (1, n_modes)
    M_vec_new     = M_vec.reshape(-1, 1)        # (n_floors, 1)
    g = 10
    F = eigen_vectors * beta_new * SadT0_new * g * M_vec_new   
    Fsrss = np.sqrt(np.sum(F**2, axis=1))
    V = np.cumsum(F[::-1, :], axis=0)[::-1, :] #or V = np.cumsum(F[::-1], axis=0)[::-1]
    Vsrss = np.sqrt(np.sum(V**2, axis=1))

    return periods_new, SadT0, V_vec, F, Fsrss, V, Vsrss
 
#    F_srss = np.sqrt(np.sum(F**2, axis=0))
 