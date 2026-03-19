import math

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

def RC_column(fc28,fe,S,n,G_current_floor,G_roof_top,Q_roof_top,
Q_current_floor,Q_ground_floor):
  Smaj = 1.1 * S #m
  NG = 1.1 * ((n-1) * G_current_floor + G_roof_top) * Smaj / 100 #converting Kg to KN 
  NQ = (Q_roof_top + Q_current_floor * (1+0.9+0.8+0.7+0.6+(n-7)*0.5)+ Q_ground_floor) * Smaj / 100 #KN
  Nu = (1.35 * NG + 1.5 * NQ) / 1000 # converting KN to MN
  alpha = 0.85 / 1.2
  Brmin = Nu / (alpha * (fc28 / (0.9 * 1.5) + 0.01 * fe / 1.15)) #m2
# gamma c is 1.5 and gamma s is 1.15 
  return Smaj,NG,NQ,Nu,alpha,Brmin
    