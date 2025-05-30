import pandas as pd
import shapefile
import chardet
import os
import arcpy
import pyproj
from pyproj import CRS, Transformer

pd.options.mode.chained_assignment = None

ipath = arcpy.GetParameterAsText(0)
prjj = arcpy.GetParameterAsText(1)
touei = arcpy.GetParameterAsText(2)
output = arcpy.GetParameterAsText(3)

shp_path = arcpy.Describe(ipath).catalogPath

def detect_encoding(dbf_path):
    with open(dbf_path, "rb") as f:
        raw_data = f.read(10000)  
        result = chardet.detect(raw_data)
    return result['encoding']

dbf_path = shp_path.replace(".shp", ".dbf")
cpg_path = shp_path.replace(".shp", ".cpg")

# 文字コードを取得
if os.path.exists(cpg_path):
    with open(cpg_path, "r") as cpg_file:
        encoding = cpg_file.read().strip()
else:
    encoding = detect_encoding(dbf_path)

# シェープファイル読み込み
src = shapefile.Reader(shp_path, encoding=encoding)  
sf = src.shapes()
rf = src.records()

# フィールド情報取得
fields = src.fields[1:] 
fn = [field[0] for field in fields]
fty = [field[1] for field in fields]
fsi = [field[2] for field in fields]
fde = [field[3] for field in fields]

# 変換オブジェクトを事前作成
crsp = CRS(prjj)
crst = CRS(touei)
epsg_codep = "epsg:" + crsp.to_authority(min_confidence=50)[1]
epsg_codet = "epsg:" + crst.to_authority(min_confidence=50)[1]
transformer = pyproj.Transformer.from_crs(epsg_codep, epsg_codet, always_xy=True)

# 変換後データリスト
new_row = []
geometry_list = {"POLYGON": shapefile.POLYGON, "POLYLINE": shapefile.POLYLINE, "POINT": shapefile.POINT}

for shp, rec in zip(sf, rf):
    sub_geo = [[transformer.transform(x, y) for x, y in shp.points]]
    shptype = shp.shapeTypeName
    shptype = "POINT"
    st = geometry_list[shptype]

    row_data = {"geometry": sub_geo} if st != shapefile.POINT else {"x": sub_geo[0][0][0], "y": sub_geo[0][0][1]}
    row_data.update({field_name: rec[field_name] for field_name in fn})

    new_row.append(row_data)

# 出力シェープファイル作成
with shapefile.Writer(output, shapeType=st) as w:
    w.fields = [(field_name, ty, si, de) for field_name, ty, si, de in zip(fn, fty, fsi, fde)]

    total = len(new_row)
    for i, row in enumerate(new_row, start=1):
        if i % 100 == 0 or i == total:  
            arcpy.SetProgressorLabel(f"ステップ {round(i / total * 100)}/{100} 実行中...")
            arcpy.SetProgressorPosition(i)

        if st == shapefile.POINT:
            w.point(row["x"], row["y"])
        elif st == shapefile.POLYLINE:
            w.line(row["geometry"])  
        else:
            w.poly(row["geometry"])

        w.record(*[row[field] for field in fn])  

# 座標系ファイル（.prj）を保存
rprj = output.replace(".shp", ".prj")
with open(rprj, 'w') as prj:
    prj.write(CRS(touei).to_wkt())

# マップに追加
aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
