def export_tables_txt(tables, names, filename):
    
    with open(filename, "w") as f:
        
        for table, name in zip(tables, names):
            
            f.write(f"{name}\n")
            f.write("-"*60 + "\n")
            
            f.write(table.to_string(index=False))
            
            f.write("\n\n")

def exptxt(tables, names, filename, col_space):

    if len(tables) != len(names):
        raise ValueError("Number of tables and names must match")

    with open(filename, "w") as f:

        for table, name in zip(tables, names):

            f.write(f"{name}\n")
            f.write("-"*70 + "\n")

            table_str = table.to_string(
                index=False,
                col_space=col_space
               #float_format="{:.3f}".format
            )

            f.write(table_str)
            f.write("\n\n")

import pandas as pd

def read_tables_txt(filename):

    tables = {}
    current_name = None
    rows = []

    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "-" not in line and len(line.split()) == 1:
            if current_name and rows:
                df = pd.DataFrame(rows[1:], columns=rows[0])
                tables[current_name] = df
                rows = []

            current_name = line
            continue

        if "-" in line:
            continue

        rows.append(line.split())

    if current_name and rows:
        df = pd.DataFrame(rows[1:], columns=rows[0])
        tables[current_name] = df

    return tables

def read_tables_txt2(filename):

    tables = {}
    current_name = None
    rows = []

    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if "-" not in line and len(line.split()) == 1:
            if current_name and rows:
                header = rows[0]
                clean_rows = []

                for r in rows[1:]:
                    if len(r) == len(header):
                        clean_rows.append(r)
                    else:
                        print("Skipping bad row:", r)

                df = pd.DataFrame(clean_rows, columns=header)
                tables[current_name] = df
                rows = []

            current_name = line
            continue

        if "-" in line:
            continue

        rows.append(line.split())

    if current_name and rows:
        header = rows[0]
        clean_rows = []

        for r in rows[1:]:
            if len(r) == len(header):
                clean_rows.append(r)
            else:
                print("Skipping bad row:", r)

        df = pd.DataFrame(clean_rows, columns=header)
        tables[current_name] = df

    return tables

def read_tables_txt3(filename):

    tables = {}
    current_name = None
    rows = []

    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Empty line = end of table
        if not line:
            if current_name and rows:
                header = rows[0]
                data = rows[1:]

                df = pd.DataFrame(data, columns=header)

                # Convert numeric columns automatically
                for col in df.columns[1:]:
                    try:
                        df[col] = df[col].astype(float)
                    except:
                        pass

                tables[current_name] = df
                rows = []
                current_name = None
            continue

        # Skip dashed line
        if set(line) == {"-"}:
            continue

        # If table name not defined yet → first line is table name
        if current_name is None:
            current_name = line
            continue

        rows.append(line.split())

    return tables

import pandas as pd

def matrix_to_table(A):
    n = len(A)

    # Generate labels
    rows = [f"floor{i}" for i in range(1, n+1)]
    cols = [f"mode{i}" for i in range(1, n+1)]

    # Create DataFrame
    df = pd.DataFrame(A, index=rows, columns=cols)

    return df

def export_matrices_txt(matrices, names, filename):

    if len(matrices) != len(names):
        raise ValueError("Matrices and names must have same length")

    with open(filename, "w") as f:

        for A, name in zip(matrices, names):

            n = len(A)

            # Generate labels
            rows = [f"floor{i}" for i in range(1, n+1)]
            cols = [f"mode{i}" for i in range(1, n+1)]

            # Convert to DataFrame
            df = pd.DataFrame(A, index=rows, columns=cols)
#="{:.3f}".format
            # Write table name
            f.write(f"{name}\n")
            f.write("-"*60 + "\n")

            # Write table
#            f.write(df.to_string(col_space, float_format))
            f.write(df.to_string())
            f.write("\n\n")

def export_matrices_txt2(matrices, names, filename):

    if len(matrices) != len(names):
        raise ValueError("Matrices and names must have same length")

    with open(filename, "w") as f:

        for A, name in zip(matrices, names):

            n = len(A)

            rows = [f"floor{i}" for i in range(1, n+1)]
            cols = [f"mode{i}" for i in range(1, n+1)]

            df = pd.DataFrame(A, index=rows, columns=cols)

            f.write(f"{name}\n")
            f.write("-"*60 + "\n")

            f.write(df.to_string(
                float_format="{:.3e}".format,
                col_space=12,
                justify="center"
            ))

            f.write("\n\n")

"""
Python equivalent of expxlsx.m
expxlsx(Tables, filename, sheetNames)
- Tables: list of pandas DataFrames [T1, T2, ...]
- filename: string, Excel file name (e.g. "chapterI.xlsx")
- sheetNames: list of strings for each sheet ["T1", "T2", ...]
The Excel file will be saved in the "excel" folder under the project root.
"""
import os
import pandas as pd
def expxlsx(Tables, filename, sheetNames):
    # --- Step 1: Get project root (2 levels up from shared_functions)
    here = os.path.dirname(os.path.abspath(__file__))  # shared_functions folder
    rootDir = os.path.abspath(os.path.join(here, "..", ".."))
    # --- Step 2: Define excel folder ---
    excelDir = os.path.join(rootDir, "excel")
    os.makedirs(excelDir, exist_ok=True)
    # --- Step 3: Build full path ---
    filepath = os.path.join(excelDir, filename)
    # --- Step 4: Write tables ---
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        for tbl, sheet in zip(Tables, sheetNames):
            tbl.to_excel(writer, sheet_name=sheet, index=False)
    # --- Step 5: Adjust column widths (like MATLAB AutoFit) ---
    from openpyxl import load_workbook
    wb = load_workbook(filepath)
    for sheet in sheetNames:
        ws = wb[sheet]
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter  # e.g. 'A'
            for cell in col:
                try:
                    val = str(cell.value)
                    if val:
                        max_length = max(max_length, len(val))
                except:
                    pass
            adjusted_width = max_length + 2  # padding
            ws.column_dimensions[col_letter].width = adjusted_width
    wb.save(filepath)
    wb.close()

