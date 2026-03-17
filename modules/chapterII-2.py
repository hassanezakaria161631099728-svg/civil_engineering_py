#%% ---- Chapter II-2 ----
import pandas as pd
import os
from modules.girt_internal_column import girt,internal_column
from modules.exptxt import export_tables_txt 
# Directory where hangar.py lives
baseDir = os.path.dirname(__file__)
# Excel folder is inside this directory
excelDir = os.path.join(baseDir, "excel")
beamT = os.path.join(excelDir, "tableaudesprofiles.xlsx")
chI = os.path.join(excelDir, "chapterI.xlsx")
hangarf = os.path.join(excelDir, "hangar.xlsx")
Tgirt, T2, T3, T4=girt(hangarf, chI, beamT)
T5, Tinter_column, T6, T7, T8, T9 = internal_column(Tgirt, hangarf, chI, beamT)
Tables = [Tgirt, T2, T3, T4, T5, Tinter_column, T6, T7, T8, T9]
Names = ["Tgirt", "T2", "T3", "T4", "T5", "Tinter_column", "T6", "T7", "T8", "T9"]
#expxlsx(Tables, os.path.join(excelDir, "chapterII-2.xlsx"), sheetNames)
export_tables_txt(Tables, Names, "hangar/txt/chapterII-2.txt")
