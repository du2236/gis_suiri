import os

folder_path = arcpy.GetParameterAsText(0)
file = arcpy.GetParameter(1)
fold = arcpy.GetParameter(2)
kaku = arcpy.GetParameterAsText(3)

if kaku != None:
    kaku_list = [f".{ext.strip()}" for ext in kaku.split(";")]
if file:
    kakup = "file_list.txt"
else:
    if fold:
        if kaku == None:
            kakup = "folder_list.txt"
        else:
            kakup = "fol_" +  "_".join(kaku_list).replace(".", "") + "_list.txt"
    else:
        kakup = "_".join(kaku_list).replace(".", "") + "_list.txt"

output = os.path.join(folder_path, kakup)
if file:
    fol = [f for f in os.listdir(folder_path)]
else:
    if fold:
        if kaku == None:
            fol = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder, f))]
        else:
            fol = [
                f for f in os.listdir(folder_path)
                if os.path.isdir(os.path.join(folder_path, f)) or any(f.endswith(ext) for ext in kaku_list)
            ]
    else:
        fol = [f for f in os.listdir(folder_path) if any(f.endswith(ext) for ext in kaku_list)]
         
with open(output, "w") as tt:
    for filename in fol:
        tt.write(f"{filename} \n")
tt.close()