import pandas as pd
import shapefile
import chardet
from pyproj import CRS
import pyproj

ipath = arcpy.GetParameterAsText(0)
shp_path = arcpy.Describe(ipath).catalogPath
touei = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)

def detect_encoding(dbf_path):
    with open(dbf_path, "rb") as f:
        raw_data = f.read(10000)  
        result = chardet.detect(raw_data)
    return result['encoding']
    
dbf_path = shp_path.replace(".shp", ".dbf")
cpg_path = shp_path.replace(".shp", ".cpg")
prj_path = shp_path.replace(".shp", ".prj")

if os.path.exists(cpg_path):
    with open(cpg_path, "r") as cpg_file:
        encoding = cpg_file.read().strip()
else:
    encoding = detect_encoding(dbf_path)

if os.path.exists(prj_path):
    with open(prj_path, "r") as prj_file:
        prjj = prj_file.read().strip()
    prj_file.close()

src = shapefile.Reader(shp_path, encoding=encoding) 
sf = src.shapes()  
rf = src.records() 


fields = src.fields[1:]  
fn = [field[0] for field in fields]
fty = [field[1] for field in fields]
fsi = [field[2] for field in fields]
fde = [field[3] for field in fields]

row_data = []

for shp, rec in zip(sf, rf):

    for i in range(len(shp.points)):
        if os.path.exists(prj_path):
            if prjj == touei:
                x, y = shp.points[i]
            else:
                crsp = CRS(prjj)
                crst = CRS(touei)
                epsg_codep = "epsg:" + crsp.to_authority(min_confidence=50)[1]
                epsg_codet = "epsg:" + crst.to_authority(min_confidence=50)[1]
                transformer = pyproj.Transformer.from_crs(epsg_codep, epsg_codet, always_xy=True)
                x, y = transformer.transform(shp.points[i][0], shp.points[i][1])
                
        else:
                x, y = shp.points[i]
        
        point_data = {"x": x, "y": y}
        for field_name, value in zip(fn, rec):
            point_data[field_name] = value
        
        row_data.append(point_data)
nf = pd.DataFrame(row_data)

with shapefile.Writer(output, shapeType=shapefile.POINT) as w:
    
    for field_name, ty, si, de in zip(fn, fty, fsi, fde):
        w.field(field_name, ty, si, de)
         
    total = len(nf)

    for i, row in enumerate(nf.itertuples(index=False), start=1):
        if i % 100 == 0 or i == total:  
            arcpy.SetProgressorLabel(f"ステップ {round(i / total * 100)}/{100} 実行中...")
            arcpy.SetProgressorPosition(i)
        w.point(row.x, row.y)  
        w.record(*[getattr(row, field) for field in fn])  

w.close()

rprj = output.replace("shp", "prj")

with open(rprj,  'w') as prj:

    prj.write(touei)

prj.close()

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
arcpy.ResetProgressor()