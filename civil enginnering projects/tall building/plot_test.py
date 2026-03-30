import sys
from modules.FEM import generate_grid,plot_grid_elevation_view_XZ,plot_grid 

def case1():
    print("Running case 1: building vertical vue XZ")
    # your code here
    nx = 7 
    nz = 8
    Lx=5
    h=3

    nodes,elements=generate_grid(nx, nz, Lx, h)
 #wall_bracing=[[0,9],[9,16],[16,25],[25,32],[32,41],[41,48],[48,57],[57,64],
 #              [1,8],[8,17],[17,24],[24,33],[33,40],[40,49],[49,56],[56,65]]
 #elements1=elements+wall_bracing
    plot_grid_elevation_view_XZ(nodes, elements, nx, nz,"hangar/PNG images","elevation_view_XZ.png")

def case2():
    print("Running case 2: building upper vue ground level XY")
    # your code here
    nx,ny,Lx,Ly = 6,5,5,4
    nodes,_=generate_grid(nx, ny, Lx, Ly)
    plot_grid(nodes, nx, ny, "tall building", "ground_level_XY.png")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a case: case1, case2")
    else:
        command = sys.argv[1]

        if command == "case1":
            case1()
        elif command == "case2":
            case2()
        else:
            print("Unknown case")
            