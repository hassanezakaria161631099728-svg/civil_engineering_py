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

#RC shear force units are in mm and N
At,b,d,alpha = 452,250,400,0.85/1.2
Vu_reduced = 179000
ft28,up,down,stmin=\
RC_shear_force(fe,At,alpha,b,Vu_reduced,fc28,d)
T3 = pd.DataFrame({"ft28": [ft28],"up": [up],"down": [down],"stmin": [stmin]})
tables = [T1,T2,T3]
names = ["stairs","RC_column","RC_shear_force"]
# export results
exptxt(tables, names, "tall building/tall building.txt", 12)
