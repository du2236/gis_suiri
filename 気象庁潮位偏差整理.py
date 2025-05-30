import pandas as pd
import re
from datetime import datetime
import arcpy

input_file = arcpy.GetParameterAsText(0)
start = arcpy.GetParameter(1)
goal = arcpy.GetParameter(2)
output = arcpy.GetParameterAsText(3)

startd = start.strftime("%Y%m%d%H")
goald = goal.strftime("%Y%m%d%H")

def parse_tide_data(file_path, target_year_month):

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = []

    for line in lines:

        match = re.search(rf"({target_year_month}\d{{2}})", line) 
        
        if match:
            date_part = match.group(1)  
            tide_values_part = line[:match.start()]  
        else:
            continue  

        
        tide_values = [tide_values_part[i:i+4] for i in range(0, len(tide_values_part), 4)]

        
        tide_values = [float(v.strip()) if v.strip() else -99900 for v in tide_values]

       
        for hour, value in enumerate(tide_values):
            timestamp = f"{date_part}{hour:02d}"  
            data.append([timestamp, value])

    df = pd.DataFrame(data, columns=["datetime", "value(m)"])
    df["value(m)"] = df["value(m)"] /100
    df = df[(df["datetime"].astype('int') < int(goald)) & (df["datetime"].astype('int') >= int(startd))]

    return df

df = parse_tide_data(input_file, resa)

df.to_csv(output, index = False)