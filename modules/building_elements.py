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

 T_vec = pd.DataFrame({"A": A.reshape(-1),"ex": ex.reshape(-1),"ey": ey.reshape(-1),
 "Ix_local": Ix_local.reshape(-1),"Iy_local": Iy_local.reshape(-1),"Ix": Ix.reshape(-1),
 "Iy": Iy.reshape(-1)})
 return T_scalar, T_vec

def sectorial(T_scalar1,T_scalar2,T_scalar3,T_scalar4,T_scalar5):
#X axis
 Ix_total1 = T_scalar1["Ix_total"].iloc[0]
 Ix_total2 = T_scalar2["Ix_total"].iloc[0]
 Ix_total3 = T_scalar3["Ix_total"].iloc[0]
 Ix_total4 = T_scalar4["Ix_total"].iloc[0]
 Ix_total5 = T_scalar5["Ix_total"].iloc[0]
 Ix_total = [Ix_total1, Ix_total2, Ix_total3, Ix_total4, Ix_total5,
 Ix_total1, Ix_total2, Ix_total3, Ix_total4, Ix_total5]

#Y axis
 Iy_total1 = T_scalar1["Iy_total"].iloc[0]
 Iy_total2 = T_scalar2["Iy_total"].iloc[0]
 Iy_total3 = T_scalar3["Iy_total"].iloc[0]
 Iy_total4 = T_scalar4["Iy_total"].iloc[0]
 Iy_total5 = T_scalar5["Iy_total"].iloc[0]
 Iy_total = [Iy_total1, Iy_total2, Iy_total3, Iy_total4, Iy_total5,
 Iy_total1, Iy_total2, Iy_total3, Iy_total4, Iy_total5]
 Ix_scalar,Iy_scalar = np.sum(Ix_total),np.sum(Iy_total)

 RC_walls = ["RC_wall1","RC_wall2","RC_wall3","RC_wall4","RC_wall5",
 "RC_wall6","RC_wall7","RC_wall8","RC_wall9","RC_wall10"]
 T_sectorial = pd.DataFrame({"RC_walls": RC_walls,"Ix": Ix_total,"Iy": Iy_total})
 T_sectorial_scalar = pd.DataFrame({"geometry_attribute": "value","Ix": [Ix_scalar],"Iy": [Iy_scalar]})

 return T_sectorial, T_sectorial_scalar

def factor(h,E,I):
 f= h**3 / (6 * E * I) #m/KN

 return f