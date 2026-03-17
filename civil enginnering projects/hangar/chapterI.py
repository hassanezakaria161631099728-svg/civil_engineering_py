# ---- Chapter I ----
import pandas as pd
import os
from modules.wind.wind import wind,dimensions
from modules.exptxt import exptxt
excel_path = os.path.join(os.path.dirname(__file__),"hangar/txt","eurocode.xlsx")
eurocode = pd.ExcelFile(excel_path)
# --- Excel file path (relative to project root) ---
excel_path = os.path.join(os.path.dirname(__file__), "hangar/txt", "hangar.xlsx")
# Load Excel
hangarf = pd.ExcelFile(excel_path)# Read Excel input
geo = pd.read_excel(hangarf,sheet_name="geography attributes")
wzs = pd.read_excel(eurocode,sheet_name="wind zones")
gcs = pd.read_excel(eurocode,sheet_name="ground categories")
ba = pd.read_excel(hangarf,sheet_name="building attributes")
Lx = ba["Lx_m"].iloc[0]
Ly = ba["Ly_m"].iloc[0]
direction1='wind1'
direction2='wind2'
b,d=dimensions(Lx,Ly,direction1)
bt=ba["bt"].iloc[0]
bt2=ba["bt2"].iloc[0]
T1,T2,T3,T4,T5,Troof1,Twall=wind(ba,Lx,Ly,direction1,geo,wzs,gcs)
T6,T7,T8,T9,T10,Troof2,_=wind(ba,Lx,Ly,direction2,geo,wzs,gcs)
#s = snow(geo, ba, Ly, Lx, Lx, Ly)  # daN/m²
# Save Chapter I tables
baseDir = os.path.dirname(__file__)
# Excel folder is inside this directory
#excelDir = os.path.join(baseDir, "hangar/txt")
Tables = [T1,T2,T3,T4,T5,Troof1,Twall,T6,T7,T8,T9,T10,Troof2]
Names = ["T1", "T2", "T3", "T4", "T5", "Troof1", "Twall",
              "T6", "T7", "T8", "T9", "T10", "Troof2"]
#expxlsx(Tables, os.path.join(excelDir, "chapterI.xlsx"), sheetNames)
exptxt(Tables, Names, "hangar/txt/chapterI.txt", 12)
