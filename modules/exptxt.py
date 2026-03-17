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
