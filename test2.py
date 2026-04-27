import numpy as np
x = np.array([0, 3.9, 7.75, 12.25, 18.8, 23.2])
y = np.array([0, 3.7, 7.4, 13.8, 18.6])
# SA matrix
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
print(Lx)
print(Ly)
print(S)
