import pandas as pd
import shapefile
import arcpy
import chardet
import os
from pyproj import CRS, Transformer
import math

shp = arcpy.GetParameterAsText(0)
xidou = arcpy.GetParameter(1)
yidou = arcpy.GetParameter(2)
angle = arcpy.GetParameter(3)
dis = arcpy.GetParameter(4)
btouei = arcpy.GetParameterAsText(5)
atouei = arcpy.GetParameterAsText(6)
output = arcpy.GetParameterAsText(7)
shp_path = arcpy.Describe(shp).catalogPath

def detect_encoding(dbf_path):
    with open(dbf_path, "rb") as f:
        raw_data = f.read(10000)  
        result = chardet.detect(raw_data)
    return result['encoding']

# 文字コードの判定
dbf_path = shp_path.replace(".shp", ".dbf")
cpg_path = shp_path.replace(".shp", ".cpg")
prj_path = shp_path.replace(".shp", ".prj")

if os.path.exists(cpg_path):
    with open(cpg_path, "r") as cpg_file:
        encoding = cpg_file.read().strip()
else:
    encoding = detect_encoding(dbf_path) or "shift_jis"

if os.path.exists(prj_path):
    with open(prj_path, "r") as prj_file:
        prjj = prj_file.read().strip()

# パラメータのデフォルト値
xidou = xidou or 0
yidou = yidou or 0
dis = dis or 0
angle = angle or 0

# 座標変換の設定
crsp = CRS(btouei)
crst = CRS(atouei)
epsg_codep = crsp.to_authority(min_confidence=50)[1]
epsg_codet = crst.to_authority(min_confidence=50)[1]
transformer = Transformer.from_crs(f"epsg:{epsg_codep}", f"epsg:{epsg_codet}", always_xy=True)

# シェープファイルの読み込み
sf = shapefile.Reader(shp_path, encoding=encoding)
sh = sf.shapes()
sr = sf.records()
fields = sf.fields[1:]
field_names = [field[0] for field in fields]
x1, y1 = 0,0
row_data = []
ii = 0
geometry_list = {"POLYGON": shapefile.POLYGON, "POLYLINE": shapefile.POLYLINE, "POINT": shapefile.POINT}

for shp, rec in zip(sh, sr):
    geo = []
    if ii == 0:
        shptype = shp.shapeTypeName
        st = geometry_list[shptype] 

    parts = list(shp.parts) + [len(shp.points)]  # パーツのインデックスを取得
    if len(parts) == 1:
        pp = 2 
    for p in range(pp - 1):  
        sub_geo = []
        if len(parts) != 1:
            for i in range(parts[p], parts[p + 1]):
                x, y = shp.points[i]
                x, y = transformer.transform(x, y)
                
                x1 = x + xidou + (math.cos(math.radians(angle)) * dis)
                y1 = y + yidou + (math.sin(math.radians(angle)) * dis)
                sub_geo.append([x1, y1])
            geo.append(sub_geo)  
        else:
            for i in range(parts[p]):
                x, y = shp.points[i]
                x, y = transformer.transform(x, y)
                
                x1 = x + xidou + (math.cos(math.radians(angle)) * dis)
                y1 = y + yidou + (math.sin(math.radians(angle)) * dis)
                sub_geo.append([x1, y1])
            geo.append(sub_geo)  
    attr_dict = {field_name: rec[field_name] for field_name in field_names}
    
    if st == shapefile.POINT: 
        row_data.append({**attr_dict, "x": x1, "y": y1})
    else:
        row_data.append({**attr_dict, "geometry": geo})
    
    ii += 1

df = pd.DataFrame(row_data)

# フィールドの型判定
flist = [col for col in df.columns if col != "geometry"]
field_types = [type(df[col][0]) for col in flist]

# 出力シェープファイルの作成
with shapefile.Writer(output, shapeType=st) as w:
    for field_name, field_type in zip(flist, field_types):
        if field_type == str:
            w.field(field_name, "C")
        else:
            w.field(field_name, "F", decimal=5)

    for i, row in df.iterrows():
        arcpy.SetProgressorLabel(f"step {i+1}/{len(df)} Loading...")
        arcpy.SetProgressorPosition(i+1)
        if st == shapefile.POINT: 
            w.point(row["x"], row["y"])
        elif st == shapefile.POLYLINE:
            w.line(row["geometry"])
        elif st == shapefile.POLYGON:
            w.poly(row["geometry"])
        w.record(*[row[field] for field in flist])

# PRJファイルの出力
with open(output.replace(".shp", ".prj"), 'w') as prj:
    prj.write(atouei)

# ArcGIS に追加
aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
arcpy.ResetProgressor()