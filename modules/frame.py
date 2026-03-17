import numpy as np
import pandas as pd
from shared_functions.FEM import FEM2D_frame,plot_frame
from shared_functions.utils import snow
def frame1(nodes,elements,constraints,chIII_1,q0,q1,q2,q3,q4,q5,loads,distributed_load_reference):
#frame properties 
 Trafter = pd.read_excel(chIII_1,sheet_name="Ttrafter")
 A_rafter = Trafter["A"].iloc[0]*10e-4
 I_rafter = Trafter["Iy"].iloc[0]*10e-8
 Tcolumn = pd.read_excel(chIII_1,sheet_name="Tcolumn")
 A_column = Tcolumn["A"].iloc[0]*10e-4
 I_column = Tcolumn["Iy"].iloc[0]*10e-8
 E=210e6
 if distributed_load_reference=="global": 
  print(" 4 elements ")
  elem_props=[
# element 0: left column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'w':q0},  #KN/m   
#element 1: left rafter
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'w':q1},   #KN/m
#element 2: right rafter
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'w':q2},  #KN/m
#element 3: right column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'w':q3}, #KN/m
 ]
 elif distributed_load_reference=="local": 
  print(" 4 elements ")
  elem_props=[
# element 0: left column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'q':q0},  #KN/m   
#element 1: left rafter
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'q':q1},   #KN/m
#element 2: right rafter
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'q':q2},  #KN/m
#element 3: right column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'q':q3}, #KN/m
 ]
 elif distributed_load_reference=="local_wind1": 
  print("we will have 6 elements in wind1 case")
  elem_props=[
# element 0: left column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'q':q0},  #KN/m   
#element 1: left rafter wFG
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'q':q1},   #KN/m
#element 2: left rafter wH
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'q':q2},   #KN/m
#element 3: right rafter wJ
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'q':q3},  #KN/m
#element 4: right rafter wI
  {'type':'beam','A':A_rafter,'I':I_rafter,'E':E,'q':q4},  #KN/m
#element 5: right column
  {'type':'beam','A':A_column,'I':I_column,'E':E,'q':q5}, #KN/m
 ]
 else: raise ValueError("unidentified distributed_load_reference")
 plot_frame(nodes, elements, elem_props, loads, constraints, load_scale=0.01) 
 u, R, N, V, M=\
 FEM2D_frame(nodes, elements, elem_props, loads, constraints, E)
 ux1=u[3]
 if distributed_load_reference=="local_wind1": 
  ux3=u[5*3]
  uy2=u[3*3+1]
 else:
  ux3=u[3*3]
  uy2=u[2*3+1]
 Vert=R[1]+R[4]
 Horiz=R[0]+R[3]
 RD=np.array([Vert,Horiz,ux1,ux3,uy2])
 if distributed_load_reference=="local_wind1": 
  indices=[0,1,2,5,6,9,10,11]
  N1=N[indices,:]
  V1=V[indices,:]
  M1=M[indices,:]
 else:
  N1,V1,M1=N,V,M
 return N1,V1,M1,RD   

def dead_load(chIII_1,chIII_2,chII_1,chII_2,hangarf):
 ba = pd.read_excel(hangarf,sheet_name="building attributes")
 Lx=ba["Lx_m"].iloc[0]
 Ly=ba["Ly_m"].iloc[0]
 l=Lx/4
 t=Ly/4
#distributed load daN/m
#rafter 
 Trafter = pd.read_excel(chIII_1,sheet_name="Ttrafter")
 q_rafter = Trafter["P"].iloc[0]#rafter daN/m
#purlin
 Tpurlin = pd.read_excel(chII_1,sheet_name="Tpanne")
 if Lx==16 or Lx==18:
  n_purlin=14
 elif Lx==20 or Lx==24:
  n_purlin=18
 else: raise ValueError("this hangar front doesn't exist in our current variantes")
 lm_purlin = Tpurlin["P"].iloc[0]#purlin daN/m
 q_purlin=lm_purlin*n_purlin*t/Lx
#diagonals
 Tdiagonal = pd.read_excel(chIII_1,sheet_name="Tdiagonal")
 ml_diagonal = Tdiagonal["P"].iloc[0] * 2 #diagonal daN/m do not forget there are two corners forming one diagonal
 n_diagonal=8
 lenght_diagonal=(l**2+t**2)**0.5
 q_diagonal=ml_diagonal*n_diagonal*(lenght_diagonal/2)/Lx
#covering
 qgc=15.21 #daN/m2
 q_covering= qgc*t
#sum
 distributed_load=(q_rafter+q_purlin+q_diagonal+q_covering)*1.1
#nodal load on the two columns daN
#colomn
 Tcolumn = pd.read_excel(chIII_1,sheet_name="Tcolumn")
 lm_column = Tcolumn["P"].iloc[0]#column daN/m linear mass
 hc=ba["floor_height_m"].iloc[0]
 q_column=lm_column*hc #daN
#girt
 Tgirt = pd.read_excel(chII_2,sheet_name="Tgirt")
 lm_girt = Tgirt["P"].iloc[0]#girt daN/m linear mass
 n_girt=6
 q_girt=lm_girt*n_girt*t 
#eave purlin
 TEave_purlin = pd.read_excel(chIII_2,sheet_name="TEave_purlin")
 lm_Eave_purlin = TEave_purlin["P"].iloc[0]#Eave_purlin daN/m linear mass
 q_Eave_purlin=lm_Eave_purlin*t  
#cladding
 qgb=11.89
 q_cladding=qgb*(hc-2)*t
#sum
 nodal_load=(q_column+q_girt+q_Eave_purlin+q_cladding)*1.1              
 Tdistributed_load=pd.DataFrame({
"frame_gear":["rafter","purlin","diagonal","covering","sum"],
"distributed_load_daN_m":[q_rafter,q_purlin,q_diagonal,q_covering,distributed_load],
 })
 Tnodal_load=pd.DataFrame({
"frame_gear":["column","girt","Eave_purlin","cladding","sum"],
"nodal_load_daN":[q_column,q_girt,q_Eave_purlin,q_cladding,nodal_load],
 })
 return distributed_load,nodal_load,Tdistributed_load,Tnodal_load

def snow_load(hangarf):
 ba = pd.read_excel(hangarf,sheet_name="building attributes")
 geo = pd.read_excel(hangarf,sheet_name="geography attributes")
 Lx=ba["Lx_m"].iloc[0]
 Ly=ba["Ly_m"].iloc[0]
 qs=snow(geo, ba, Lx, Lx, Ly) #daN/m2 here we take direction 2 to the front b=Lx to get the total load
 t=Ly/4
 snow_load=qs*t #daN/m
 return snow_load

def interpolation(cpe1,cpe2,alpha):
 cpe = (cpe2 - cpe1) / 10 * (alpha - 5) + cpe1    
 return cpe

def cpe_from_s(epf10,epf1,s):
 if s == 0:
  epf = 0
 elif s <= 1:
  epf = epf1
 elif 1 < s < 10:
  epf = epf1 + (epf10 - epf1) * np.log10(s)
 elif s >= 10:
  epf = epf10    
 else: raise ValueError("s needs to be positive")
 return epf

def frame(hangarf,chI,chII_1,chIII_1,chIII_2,chII_2):
 ba = pd.read_excel(hangarf,sheet_name="building attributes")
 floor_height=ba["floor_height_m"].iloc[0]
 hp=ba["hp_m"].iloc[0]
 L=ba["Lx_m"].iloc[0]
 T=ba["Ly_m"].iloc[0]
 alpha=ba["slope_angle_deg"].iloc[0]
 nodes=[[0,0],[0,floor_height],[L/2,floor_height+hp],[L,floor_height],[L,0]]
 elements=[[0,1],[1,2],[2,3],[3,4]]
 constraints = [0,1,2,  4*3, 4*3+1, 4*3+2]   # all DOFs at node 0 and node 4 are fixed on the gound
#dead load G
 distributed_loadG,loadG,Tdistributed_loadG,Tnodal_loadG=\
 dead_load(chIII_1,chIII_2,chII_1,chII_2,hangarf)
 nodal_loadsG = np.array([[4,loadG*-1], [10,loadG*-1]]) 
#frame1(nodes,elements,constraints,chIII_1,q0,q1,q2,q3,q4,q5,loads,distributed_load_reference):
 NG,VG,MG,RDG=frame1(nodes,elements,constraints,chIII_1,0,distributed_loadG,distributed_loadG,0,0,0,
 nodal_loadsG,"global")
#snow1
 qs=snow_load(hangarf)
 nodal_loadss1=[]
 Ns1,Vs1,Ms1,RDs1=frame1(nodes,elements,constraints,chIII_1,0,qs*0.5,qs,0,0,0,nodal_loadss1,"global")
#snow2
 Ns2,Vs2,Ms2,RDs2=frame1(nodes,elements,constraints,chIII_1,0,qs,qs,0,0,0,nodal_loadss1,"global")
#wind1
#for wind1 case we will have additional two nodes intermediate
 t=T/4
 Tin1 = pd.read_excel(chI, sheet_name="T1")
 Tin2 = pd.read_excel(chI, sheet_name="T2")
 Tin3 = pd.read_excel(chI, sheet_name="T3")
 Tin6 = pd.read_excel(chI, sheet_name="T6")
 Tin8 = pd.read_excel(chI, sheet_name="T8")
 e1 = Tin1["e_m"].iloc[0]          
 a=hp/(L/2)
 hfg=(e1/10)*a+hp
 hI=(L/2-e1/10)*a+hp
 nodes1=[[0,0],[0,floor_height],[e1/10,hfg],[L/2,floor_height+hp],[L/2+e1/10,hI],[L,floor_height],[L,0]]
 elements1=[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]]
 constraints1 = [0,1,2,  3*6, 3*6+1, 3*6+2]   # all DOFs at node 0 and node 4 are fixed on the gound
 qpze = Tin2["qpze_N_m_2"].iloc[0]  # table2{1,3}
 ipf1 = Tin3["ipf1"].iloc[0]         # table3{1,3}
 wi1=qpze*ipf1
 weD=qpze*0.8
 weE=qpze*(-0.3)
 qv1D=(weD-wi1)*t/10
 qv1E=(weE-wi1)*t/10
 bF=(e1/5-t/2)
 sF=bF*e1/10
 bG=((3/2)*t-e1/5)
 sG=bG*(L/2-e1/10)
 cpeF10=interpolation(-1.7,-0.9,alpha)
 cpeF1=interpolation(-2.5,-2,alpha)
 cpeG10=interpolation(-1.2,-0.8,alpha)
 cpeG1=interpolation(-2,-1.5,alpha)
 cpeF=cpe_from_s(cpeF10,cpeF1,sF)
 cpeG=cpe_from_s(cpeG10,cpeG1,sG)
 weF=qpze*cpeF
 weG=qpze*cpeG
 qvF=(weF-wi1)*bF
 qvG=(weG-wi1)*bG
 qv1FG=(qvF+qvG)/10
 cpeH=interpolation(-0.6,-0.3,alpha)
 qv1H=(cpeH-wi1)*t/10
 cpeJ=interpolation(-0.6,-0.4,alpha)
 qv1J=(cpeJ-wi1)*t/10
 cpeI=interpolation(-0.6,-1,alpha)
 qv1I=(cpeI-wi1)*t/10
 Nw1,Vw1,Mw1,RDw1=frame1(nodes1,elements1,constraints1,chIII_1,qv1D,-qv1FG,-qv1H,-qv1J,-qv1I,-qv1E,
  nodal_loadss1,"local_wind1")
#wind2
 e2 = Tin6["e_m"].iloc[0]          
 ipf2 = Tin8["ipf1"].iloc[0]
 wi2=qpze*ipf2
 weA=qpze*(-1)
 weB=qpze*(-0.8)
 qv2A=(weA-wi2)*(e2/5-t/2)
 qv2B=(weB-wi2)*((3/2)*t-e2/5)
 qv2AB=(qv2A+qv2B)/10
 cpeH=interpolation(-0.7,-0.6,alpha)
 weH=qpze*cpeH
 qv2H=(weH-wi2)*t/10
 Nw2,Vw2,Mw2,RDw2=frame1(nodes,elements,constraints,chIII_1,-qv2AB,-qv2H,-qv2H,-qv2AB,0,0,
 nodal_loadss1,"local")
#imperfections
 nodal_loadsimp=[[3,50]]
 Nimp,Vimp,Mimp,RDimp=frame1(nodes,elements,constraints,chIII_1,0,0,0,0,0,0,nodal_loadsimp,"global")
#final tables
 T_axial_forces=pd.DataFrame({
 "element":["column1","column1","rafter1","rafter1","rafter2","rafter2","column2","column2"],    
 "node":[0,1,1,2,2,3,3,4],
 "G":NG.reshape(-1),
 "S1":Ns1.reshape(-1),
 "S2":Ns2.reshape(-1),
 "W1":Nw1.reshape(-1),
 "W2":Nw2.reshape(-1),
 "IMP":Nimp.reshape(-1),
 })

 T_shear_forces=pd.DataFrame({
 "element":["column1","column1","rafter1","rafter1","rafter2","rafter2","column2","column2"],    
 "node":[0,1,1,2,2,3,3,4],
 "G":VG.reshape(-1),
 "S1":Vs1.reshape(-1),
 "S2":Vs2.reshape(-1),
 "W1":Vw1.reshape(-1),
 "W2":Vw2.reshape(-1),
 "IMP":Vimp.reshape(-1),
 })
 T_bending_moments=pd.DataFrame({
 "element":["column1","column1","rafter1","rafter1","rafter2","rafter2","column2","column2"],    
 "node":[0,1,1,2,2,3,3,4],
 "G":MG.reshape(-1),
 "S1":Ms1.reshape(-1),
 "S2":Ms2.reshape(-1),
 "W1":Mw1.reshape(-1),
 "W2":Mw2.reshape(-1),
 "IMP":Mimp.reshape(-1),
 })
 T_displacements_reactions=pd.DataFrame({
 "parameter":["vertical reaction V [daN]","horizontal reaction H [daN]","ux1[cm]","ux3[cm]","uy2[cm]"],    
 "G":RDG.reshape(-1),
 "S1":RDs1.reshape(-1),
 "S2":RDs2.reshape(-1),
 "W1":RDw1.reshape(-1),
 "W2":RDw2.reshape(-1),
 "IMP":RDimp.reshape(-1),
 })
 return (Tdistributed_loadG,Tnodal_loadG,T_axial_forces,T_shear_forces,
T_bending_moments,T_displacements_reactions)

