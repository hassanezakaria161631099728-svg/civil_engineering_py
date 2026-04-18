import math
import numpy as np
import pandas as pd
# stairs
def stairs(story_height, vertical_step, horizontal_step):
 if 16 <=vertical_step <= 19 and 23 <= horizontal_step <= 32: # cm
   statement= "vertical and horizontal step are within accepted segment "
 else:      
   statement= "either vertical or horizontal step is out accepted segment or both"

 stairs_height = story_height / 2 * 100 # converting to cm 
 n_stairs = math.ceil(stairs_height / vertical_step)

 stairs_length = n_stairs * horizontal_step

 slope_angle = math.atan(vertical_step / horizontal_step)
 slope_angle_deg = math.degrees(slope_angle)
 return (statement,story_height,stairs_height,vertical_step,n_stairs,
 horizontal_step,stairs_length,slope_angle,slope_angle_deg)

def RC_column(fc28,fe,S,n,G_current_floor,G_roof_top,Q_roof_top,Q_current_floor):
  Smaj = 1.1 * S #m
#  NG = 1.1 * (n * G_current_floor + G_roof_top) * Smaj / 100 #converting Kg to KN 
#  NQ = (Q_roof_top + Q_current_floor * (1+0.9+0.8+0.7+0.6+(n-5)*0.5)+Q_ground_floor) * Smaj / 100 #KN
  NQ = compute_NQ(n+1,Q_current_floor,Q_roof_top,Smaj) 
  NG = compute_NG(n+1,G_current_floor,G_roof_top,Smaj) 
  Nu = (1.35 * NG + 1.5 * NQ) / 1000 # converting KN to MN
  Smaj = np.full((n+1, 1), Smaj)
  alpha = 0.85 / 1.2
  alpha = np.full((n+1, 1), alpha)
  Brmin = Nu / (alpha * (fc28 / (0.9 * 1.5) + 0.01 * fe / 1.15)) #m2
#gamma c is 1.5 and gamma s is 1.15 
  Nd = (NG + NQ) / 1000 
  Bcmin = Nu / (0.3 * fc28)
  amin = Bcmin**0.5
  a = np.ceil(amin*20)/20
  Bc = a*a # we have a rectangular column
  Br = (a - 0.02)**2
  return Smaj,NG,NQ,Nu,alpha,Brmin,Nd,Bcmin,amin,a,Bc,Br

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

def sectorial(T_scalar1,T_scalar2,T_scalar3,T_scalar4,T_scalar5):
# we define geometrical attributes for reinforced concrete walls
#inertia X axis
 Ix_total1 = T_scalar1["Ix_total"].iloc[0]
 Ix_total2 = T_scalar2["Ix_total"].iloc[0]
 Ix_total3 = T_scalar3["Ix_total"].iloc[0]
 Ix_total4 = T_scalar4["Ix_total"].iloc[0]
 Ix_total5 = T_scalar5["Ix_total"].iloc[0]

#inertia Y axis
 Iy_total1 = T_scalar1["Iy_total"].iloc[0]
 Iy_total2 = T_scalar2["Iy_total"].iloc[0]
 Iy_total3 = T_scalar3["Iy_total"].iloc[0]
 Iy_total4 = T_scalar4["Iy_total"].iloc[0]
 Iy_total5 = T_scalar5["Iy_total"].iloc[0]
# surfaces 
 A_total1 = T_scalar1["A_total"].iloc[0]
 A_total2 = T_scalar2["A_total"].iloc[0]
 A_total3 = T_scalar3["A_total"].iloc[0]
 A_total4 = T_scalar4["A_total"].iloc[0]
 A_total5 = T_scalar5["A_total"].iloc[0]
 n = 16
# inertia vectors
 Ix_total,Iy_total,A_total = np.zeros((n)), np.zeros((n)), np.zeros((n))
 Ix_total[0:4], Iy_total[0:4], A_total[0:4] = Ix_total1, Iy_total1, A_total1 
 Ix_total[4:8], Iy_total[4:8], A_total[4:8] = Ix_total2, Iy_total2, A_total2
 Ix_total[8:10], Iy_total[8:10], A_total[8:10] = Ix_total3, Iy_total3, A_total3
 Ix_total[10:14], Iy_total[10:14], A_total[10:14] = Ix_total4, Iy_total4, A_total4
 Ix_total[14:16], Iy_total[14:16], A_total[14:16] = Ix_total5, Iy_total5, A_total5
# centre of mass vectors
 xg1 = T_scalar1["xg_global"].iloc[0]
 xg4 = T_scalar1["xg_global"].iloc[0]
 yg1 = T_scalar1["yg_global"].iloc[0]
 yg2 = T_scalar1["yg_global"].iloc[0]
 yg3 = T_scalar1["yg_global"].iloc[0]

 Lx,Ly = 23.05, 19.25
 X = [xg1, Lx-xg1, xg1, Lx-xg1,            #i=0:4
 9.925, Lx-9.925, 9.925, Lx-9.925,         #i=4:8
 6.525, Lx-6.525,                          #i=8:10
 10.15-xg4,12.9+xg4, 10.15-xg4,12.9+xg4,   #i=10:14
 2.425,Lx-2.425                           #i=14:16 
 ]
 Y = [yg1, yg1, Ly-yg1, Ly-yg1,            #i=0:4
 yg2, yg2, Ly-yg2, Ly-yg2,                 #i=4:8
 3.5+yg3, 10.9+yg3,                        #i=8:10
 8.125,8.125, Ly-8.125,Ly-8.125,           #i=10:14
 Ly/2,Ly/2                                #i=14:16 
 ]

 A_scalar,Ix_scalar,Iy_scalar = np.sum(A_total),np.sum(Ix_total),np.sum(Iy_total)

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
 T_sectorial = pd.DataFrame({"RC_walls": RC_walls,"A": A_total,"Ix": Ix_total,"Iy": Iy_total,"X": X,"Y": Y,
 "dx": dx,"dy": dy,"Iw":Iw_vec})
 T_sectorial_scalar = pd.DataFrame({"geometry_attribute": "value","A": [A_scalar],"Ix": [Ix_scalar],
 "Iy": [Iy_scalar],"XC": [XC],"YC": [YC],"Iw":Iw_scalar})

 return T_sectorial, T_sectorial_scalar

def building_masses(geometry,Lx,Ly,G_RTB,h_story,h_beam,a_RC_column,n_RC_columns,DC):
 geometry_attributes = geometry["sectorial_attributes_scalars"]
 geometry_attributes["A"] = geometry_attributes["A"].astype(float)
 A_RC_walls = geometry_attributes["A"].iloc[0]
 #roof top barricade 
 L_RTB = (Lx + Ly) * 2 #m
 m_RTB = G_RTB * L_RTB / 1000
 T_RTB = pd.DataFrame({"G_kg/m": [G_RTB],"L_m": [L_RTB],"m_tonnes": [m_RTB]})
 # RC walls
 h_RC_wall = h_story - h_beam
 v_RC_walls = A_RC_walls * h_RC_wall          
 m_RC_walls = v_RC_walls * DC           
 T_RC_walls = pd.DataFrame({"height_m": [h_RC_wall],"volume_m3": [v_RC_walls],"m_tonnes": [m_RC_walls]})
 # RC columns
 S_RC_column = a_RC_column * a_RC_column
 m_RC_columns = h_story * n_RC_columns * S_RC_column *  DC 
 T_RC_columns = pd.DataFrame({"n_columns": [n_RC_columns],"a_m": [a_RC_column],"S_m2": [S_RC_column],
 "m_tonnes": [m_RC_columns]})
 return T_RTB,T_RC_walls,T_RC_columns

def factor(h,E,I):
 f= h**3 / (6 * E * I) #m/KN

 return f