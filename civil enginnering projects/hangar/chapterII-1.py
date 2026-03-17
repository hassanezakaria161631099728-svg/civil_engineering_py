# ---- Chapter II-1 ----
import pandas as pd
import os
# Directory where hangar.py lives
baseDir = os.path.dirname(__file__)
# Excel folder is inside this directory
excelDir = os.path.join(baseDir, "hangar/txt")
beamT = os.path.join(excelDir, "steel.xlsx")
chI = os.path.join(excelDir, "chapterI.xlsx")
hangarf = os.path.join(excelDir, "hangar.xlsx")
from modules.purlin import purlin
from modules.exptxt import exptxt
ba = pd.read_excel(hangarf,sheet_name="building attributes")
row = ba.squeeze()
bt2 = row["bt2"]   
Lx = row["Lx_m"]   
Ly = row["Ly_m"]   
b1=Ly
b2=Lx
Tpurlin,T2,loads,acp,combdel,combV,combM,T8,T9,T10=purlin(b1,b2,hangarf,chI,beamT)
Tables = [Tpurlin,T2,loads,acp,combdel,combV,combM,T8,T9,T10]
Names = ["Tpurlin","T2","loads","acp","combdel","combV","combM","T8","T9","T10"]
#expxlsx(Tables, os.path.join(excelDir, "chapterII-1.xlsx"), sheetNames)
exptxt(Tables, Names, "hangar/txt/chapterII-1.txt")
