import sys
import numpy as np
import pandas as pd
from modules.building_elements import compute_NQ,compute_NG,RC_column,inertia,factor
from modules.io import matrix_to_table,export_matrices_txt2,exptxt
def dynamic():
 print("Running case 1: dynamic analysis")
 # your code here
 n = 9
 M1 = 580.8
 M2 = 575.48
 M3 = 500.37
 M = np.zeros((n+1,n+1))
 for i in range(n-1): M[i,i] = M1 #fill diagonal for i=1 to n-2 
 M[n-1,n-1] = M2 #element (n-1,n-1)
 M[n,n] = M3 #element (n,n)

 SA=np.zeros((n+1,n+1))
 for i in range(n+1):
    for j in range(n+1):
        if i<j: SA[i,j] = (i+1)**2 * (3*(j+1)-(i+1))
        elif i==j: SA[i,j] = 2*(i+1)**3
        else : SA[i,j] = (j+1)**2 * (3*(i+1)-(j+1)) # i>j

 h = 3.06 #m
 fc28 = 25 #MPA or MN/m2
 E=11000 * fc28 **(1/3) * 1000 #MN/m2 to KN/m2 we multiply on 10**3
 t,by1,by2,by3 = 0.25,3.95,4.4,2.5 
 bx1,bx2,bx3 = 3.05,2.5,3.95
 Iy1,Iy2,Iy3 = inertia(t,by1),inertia(t,by2),inertia(t,by3), 
 Ix1,Ix2,Ix3 = inertia(t,bx1),inertia(t,bx2),inertia(t,bx3), 

 IY,IX= 4 * Iy1 + 2 * Iy2 + 4 * Iy3, 4 * Ix1 + 4 * Ix2 + 2* Ix3 #m**4
 fx = factor(h,E,IY)
 fy = factor(h,E,IX)

 Sx= fx * SA 
 Dx =  Sx @ M #matrix product
 TSA = matrix_to_table(SA)
 TM = matrix_to_table(M)
 TS = matrix_to_table(Sx)
 TD = matrix_to_table(Dx)
 eigenvalues, eigenvectors = np.linalg.eig(Dx)
 #print(eigenvectors)
 Teigvec = matrix_to_table(eigenvectors) 
 matrices = [TSA,TM,TS,TD,Teigvec]
 names = ["SA","M","Sx","Dx","eigen_vectors"]
 float_format = "{:.3f}".format
 export_matrices_txt2(matrices, names, "tall building/dynamic.txt")
 T = pd.DataFrame({"Iy1": [Iy1],"Iy2": [Iy2],"Iy3": [Iy3],"Ix1": [Ix1],"Ix2": [Ix2],"Ix3": [Ix3],
 "IY": IY,"IX": IX,"fx":[fx],"fy":[fy]})

#showing on terminal
# print(T)  
# export results
 tables = [T]
 names = ["geometry_attributes"]
 exptxt(tables, names, "tall building/geometry attributes.txt", 12)


def columns():
 print("Running case 2: columns analysis")
 # your code here
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

#showing on terminal
# print(T2)  
# export results
 tables = [T2]
 names = ["RC_column"]
 exptxt(tables, names, "tall building/RC column.txt", 12)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a case: case1, case2")
    else:
        command = sys.argv[1]

        if command == "dynamic":
            dynamic()
        elif command == "columns":
            columns()
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
