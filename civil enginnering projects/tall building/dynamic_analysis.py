import numpy as np
n=10
M1=710.02
M2=703.74
M3=705.94
M=np.zeros((n,n))
for i in range(n-2): M[i,i]=M1 #fill diagonal for i=1 to n-2 
M[n-2,n-2]=M2 #element (n-1,n-1)
M[n-1,n-1]=M3 #element (n,n)

SA=np.zeros((n,n))
for i in range(n):
    for j in range(n):
        if i<j: SA[i,j] = (i+1)**2 * (3*(j+1)-(i+1))
        elif i==j: SA[i,j] = 2*(i+1)**3
        else : SA[i,j]=(j+1)**2 * (3*(i+1)-(j+1)) # i>j

h=3.06
E=11000 * 25 **(1/3)
IY=808 #m**4
f= h**3 / (6 * E * IY)
S= f * SA 
D = S * M 

eigenvalues, eigenvectors = np.linalg.eig(D)

with open("tall building/dynamic.txt","w") as f:
    f.write("SA:\n")
    f.write(np.array2string(SA, precision=0)+ "\n\n")
    f.write("Stiffness matrix:\n")
    f.write(np.array2string(S, precision=2)+ "\n\n")
    f.write("Mass matrix:\n")
    f.write(np.array2string(M, precision=2)+ "\n\n")
    f.write("Dynamic matrix:\n")
    f.write(np.array2string(D, precision=2)+ "\n\n")
    f.write("eigenvalues:\n")
    f.write(np.array2string(eigenvalues, precision=2)+ "\n\n")
    f.write("eigenvectors:\n")
    f.write(np.array2string(eigenvectors, precision=2)+ "\n")
