import sys
import pandas as pd
import os
from modules.wind.wind import wind,dimensions
from modules.io import exptxt,read_tables_txt3
from modules.purlin import purlin
from modules.girt_internal_column import girt,internal_column
from modules.truss import roof_bracing,wall_bracing
from modules.frame import frame 


def chapterI():
 print("Running case 1: chapterI")
 # your code here
 eurocode = read_tables_txt3("hangar/txt/eurocode.txt")
 chI = read_tables_txt3("hangar/txt/chapterI.txt")
 hangar = read_tables_txt3("hangar/txt/hangar.txt")
 ba = hangar["building_attributes"]
 Lx = ba["Lx_m"].iloc[0]
 Ly = ba["Ly_m"].iloc[0]
 direction1='wind1'
 direction2='wind2'
 b,d=dimensions(Lx,Ly,direction1)
 bt=ba["bt"].iloc[0]
 bt2=ba["bt2"].iloc[0]
 geo = hangar["geography_attributes"]
 wzs = eurocode["wind_zones"]
 gcs = eurocode["ground_categories"]
 T1,T2,T3,T4,T5,Troof1,Twall=wind(ba,Lx,Ly,direction1,geo,wzs,gcs)
 T6,T7,T8,T9,T10,Troof2,_=wind(ba,Lx,Ly,direction2,geo,wzs,gcs)
 Tables = [T1,T2,T3,T4,T5,Troof1,Twall,T6,T7,T8,T9,T10,Troof2]
 Names = ["T1", "T2", "T3", "T4", "T5", "Troof1", "Twall",
              "T6", "T7", "T8", "T9", "T10", "Troof2"]
 exptxt(Tables, Names, "hangar/txt/chapterI.txt", 12)

def chapterII_1():
 print("Running case 1: chapterII_1")
 # your code here
 steel = read_tables_txt3("hangar/txt/steel.txt")
 chI = read_tables_txt3("hangar/txt/chapterI.txt")
 hangar = read_tables_txt3("hangar/txt/hangar.txt")
 ba = hangar["building_attributes"]
 row = ba.squeeze()
 bt2 = row["bt2"]   
 Lx = row["Lx_m"]   
 Ly = row["Ly_m"]   
 b1=Ly
 b2=Lx
 Tpurlin,T2,loads,acp,combdel,combV,combM,T8,T9,T10=purlin(b1,b2,hangar,chI,steel)
 Tables = [Tpurlin,T2,loads,acp,combdel,combV,combM,T8,T9,T10]
 Names = ["Tpurlin","T2","loads","acp","combdel","combV","combM","T8","T9","T10"]
 exptxt(Tables, Names, "hangar/txt/chapterII-1.txt",15)

def chapterII_2():
 print("Running case 1: chapterII_2")
 # your code here
 steel = read_tables_txt3("hangar/txt/steel.txt") # beam tables
 chI = read_tables_txt3("hangar/txt/chapterI.txt")
 hangar = read_tables_txt3("hangar/txt/hangar.txt")
 Tgirt, T2, T3, T4=girt(hangar, chI, steel)
 T5, Tinter_column, T6, T7, T8, T9 = internal_column(Tgirt, hangar, chI, steel)
 Tables = [Tgirt, T2, T3, T4, T5, Tinter_column, T6, T7, T8, T9]
 Names = ["Tgirt", "T2", "T3", "T4", "T5", "Tinter_column", "T6", "T7", "T8", "T9"]
 exptxt(Tables, Names, "hangar/txt/chapterII-2.txt",12)

def chapterIII_1():
 print("Running case 1: chapterIII_1")
 # your code here
 beamT = read_tables_txt3("hangar/txt/steel.txt") # beam tables
 chI = read_tables_txt3("hangar/txt/chapterI.txt")
 chII_1 = read_tables_txt3("hangar/txt/chapterII-1.txt")
 hangar = read_tables_txt3("hangar/txt/hangar.txt")
 T1, T2, Trafter, Tcolumn, Tdiagonal, T6, T7, T8, T9, T10, T11, T12, T13,FV1,FV2,Ld=\
 roof_bracing(hangar, beamT, chI, chII_1)
 # If you want to export:
 Tables = [T1, T2, Trafter, Tcolumn, Tdiagonal, T6, T7, T8, T9, T10, T11, T12, T13]
 Names = ["T1","T2","Trafter","Tcolumn","Tdiagonal","T6","T7","T8","T9","T10","T11","T12","T13"]
 #expxlsx(Tables, os.path.join(excelDir,"chapterIII-1.xlsx"), sheetNames)
 exptxt(Tables, Names, "hangar/txt/chapterIII-1.txt",12)

def chapterIII_2():
 print("Running case 1: chapterIII_2")
 # your code here
 beamT = read_tables_txt3("hangar/txt/steel.txt") # beam tables
 chIII_1 = read_tables_txt3("hangar/txt/chapterIII-1.txt")
 hangar = read_tables_txt3("hangar/txt/hangar.txt")
 T1, T2, TEave_purlin, Tdiagonal, T3, T4, T5 = wall_bracing(beamT, chIII_1, hangar)
 Tables = [T1, T2, TEave_purlin, Tdiagonal, T3, T4, T5]
 Names = ["T1", "T2", "TEave_purlin", "Tdiagonal", "T3", "T4", "T5"]
 exptxt(Tables, Names, "hangar/txt/chapterIII-2.txt",12)

def chapterIV_1():
 print("Running case 1: chapterIV_1")
 # your code here
 beamT = read_tables_txt3("hangar/txt/steel.txt") # beam tables
 chI = read_tables_txt3("hangar/txt/chapterI.txt")
 chII_1 = read_tables_txt3("hangar/txt/chapterII-1.txt")
 chII_2 = read_tables_txt3("hangar/txt/chapterII-2.txt")
 chIII_1 = read_tables_txt3("hangar/txt/chapterIII-1.txt")
 chIII_2 = read_tables_txt3("hangar/txt/chapterIII-2.txt")
 hangar = read_tables_txt3("hangar/txt/hangar.txt")
 E=210e6 #Kpa
 (Tdistributed_loadG,Tnodal_loadG,T_axial_forces,T_shear_forces,
 T_bending_moments,T_displacements_reactions)=frame(hangar,chI,chII_1,chII_2,chIII_1,chIII_2)
 Tables = [Tdistributed_loadG,Tnodal_loadG,T_axial_forces,T_shear_forces,T_bending_moments,T_displacements_reactions]
 Names = ["Tdistributed_loadG","Tnodal_loadG","T_axial_forces","T_shear_forces","T_bending_moments","T_displacements_reactions"]
 exptxt(Tables, Names, "hangar/txt/chapterIV-1.txt",12)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a case: chapterI, chapterII_1, chapterII_2, chapterIII_1, chapterIII_2, chapterIV_1")
    else:
        command = sys.argv[1]

        if command == "chapterI":
            chapterI()
        elif command == "chapterII_1":
            chapterII_1()
        elif command == "chapterII_2":
            chapterII_2()
        elif command == "chapterIII_1":
            chapterIII_1()
        elif command == "chapterIII_2":
            chapterIII_2()
        elif command == "chapterIV_1":
            chapterIV_1()
        else:
            print("Unknown case")
