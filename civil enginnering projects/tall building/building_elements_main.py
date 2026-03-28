import pandas as pd
from modules.building_elements import stairs,RC_column,RC_shear_force
from modules.io import exptxt
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
fc28,fe = 30,400 #MN/m2 or MPA
S,n= 13.035,7
G_current_floor,G_roof_top = 665,802 #kg
Q_current_floor,Q_roof_top,Q_ground_floor = 150,100,0 #kg
Smaj,NG,NQ,Nu,alpha,Brmin,Nd,Bcmin,amin,a,Bc,Br=\
RC_column(fc28,fe,S,n,G_current_floor,G_roof_top,Q_roof_top,Q_current_floor,Q_ground_floor)
T2 = pd.DataFrame({"Smaj": [Smaj],"NG": [NG],"NQ": [NQ],"Nu": [Nu],"alpha": [alpha],
"Brmin": [Brmin],"Nd": [Nd],"Bcmin": [Bcmin],"amin": [amin],"a": [a],"Bc": [Bc],"Br": [Br]})
#RC shear force units are in mm and N
At,b,d = 452,250,400
Vu_reduced = 179000
ft28,up,down,stmin=\
RC_shear_force(fe,At,alpha,b,Vu_reduced,fc28,d)
T3 = pd.DataFrame({"ft28": [ft28],"up": [up],"down": [down],"stmin": [stmin]})
tables = [T1,T2,T3]
names = ["stairs","RC_column","RC_shear_force"]
# export results
exptxt(tables, names, "tall building/tall building.txt", 12)
