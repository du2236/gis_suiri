import pandas as pd
import shapefile
import arcpy
import chardet
from pyproj import CRS
import pyproj

param_text = arcpy.GetParameterAsText(0)
iden = arcpy.GetParameterAsText(1)
maxf = arcpy.GetParameterAsText(2)
touei = arcpy.GetParameterAsText(3)
output = arcpy.GetParameterAsText(4)
param_list = param_text.split(";")
def detect_encoding(dbf_path):
    with open(dbf_path, "rb") as f:
        raw_data = f.read(10000)  
        result = chardet.detect(raw_data)
    return result['encoding']

df1 = pd.DataFrame(columns=['geometry', iden, maxf])
data_dict = {}

for ly in param_list:
    shp_path = arcpy.Describe(ly).catalogPath
    dbf_path = shp_path.replace(".shp", ".dbf")
    cpg_path = shp_path.replace(".shp", ".cpg")
    prj_path = shp_path.replace(".shp", ".prj")
    
    if os.path.exists(cpg_path):
        with open(cpg_path, "r") as cpg_file:
            encoding = cpg_file.read().strip()
        cpg_file.close()
    else:
        encoding = detect_encoding(dbf_path)
        
    if os.path.exists(prj_path):
        with open(prj_path, "r") as prj_file:
            prjj = prj_file.read().strip()
        prj_file.close()
    sf = shapefile.Reader(shp_path, encoding = encoding)
    sh = sf.shapes()
    sr = sf.records()
    fields = sf.fields[1:]
    
    field_names = [field[0] for field in fields]
    shptype = shp.shapeTypeName
    geometry_list = {"POLYGON" : shapefile.POLYGON, "POLYLINE" : shapefile.POLYLINE, "POINT" : shapefile.POINT}
    st = geometry_list[shptype] 
    for i, j in zip(field_names, range(len(field_names))):
        if i == maxf:
            a = j
        if i == iden:
            b = j
    for shp, rec in zip(sh, sr):
        geo = []
        sub_geo = []
        
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
                
            sub_geo.append([x, y])
            geo.append(sub_geo)
        fid = rec[b]
        fl = rec[a]
        key = (fid)
        if key in data_dict:
            if fl > data_dict[key][maxf]:
                if st == shapefile.POINT:
                    data_dict[key] = {"x" : x, "y" : y, iden : fid, maxf : fl}
                else:
                    data_dict[key] = {"geometry" : geo, iden : fid, maxf : fl}
        else:
            if st == shapefile.POINT:
                data_dict[key] = {"x" : x, "y" : y, iden : fid, maxf : fl}
            else:
                data_dict[key] = {"geometry" : geo, iden : fid, maxf : fl}
     
df1 = pd.DataFrame.from_dict(data_dict, orient='index').reset_index(drop=True)

with shapefile.Writer(output, shapeType=st) as w:
    w.field(iden, 'N') 
    w.field(maxf, 'F', decimal = 5) 
    for _, row in df1.iterrows():
        if st == shapefile.POINT:
            w.point(row["x"], row["y"])
        if st == shapefile.POLYLINE:
            w.line(row["geometry"])
        if st == shapefile.POLYGON:
            w.poly(row['geometry'])
        w.record(row[iden], row[maxf])
w.close()


rprj = output.replace("shp", "prj")
with open(rprj,  'w') as prj:
    prj.write(touei)
prj.close()
aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap
m.addDataFromPath(output)