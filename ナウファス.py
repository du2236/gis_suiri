import pandas as pd
from datetime import datetime

input_file = arcpy.GetParameterAsText(0)
start = arcpy.GetParameter(1)
goal = arcpy.GetParameter(2)
output = arcpy.GetParameterAsText(3)

startd = start.strftime("%Y%m%d%H%M")
goald = goal.strftime("%Y%m%d%H%M")
def replace_spaces_in_datetime(line):

    datetime_part = line[:12].replace(" ", "0")  
    remaining_part = line[12:]  
    return datetime_part + remaining_part  


a_file = input_file.replace(".txt", "_.txt")  

with open(input_file, "r") as f_in, open(a_file, "w") as f_out:
    for line in f_in:
        new_line = replace_spaces_in_datetime(line)
        f_out.write(new_line + "\n")  
f_out.close()

df = pd.read_csv(a_file, 
                 delim_whitespace=True, encoding="shift-jis", skiprows = 1, 
                 names = ("年月日時", "フラグ", "波数(波)", "平均波波高(m)", "平均波周期(sec)", "有義波波高(m)", "有義波周期(sec)", "1/10波波高(m)", "1/10波周期(sec)", "最高波波高(m)", "最高波周期(sec)", "波向(度)" ))

df2 = df[(df["年月日時"] <= int(goald)) & (df["年月日時"] >= int(startd))]
df2.to_csv(output, index = False, encoding = "shift-jis")
os.remove(a_file)