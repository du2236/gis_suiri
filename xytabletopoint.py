import pandas as pd
import shapefile
import arcpy
import chardet
from pyproj import CRS
import pyproj

cs = arcpy.GetParameterAsText(0)
x_field = arcpy.GetParameterAsText(1)
y_field = arcpy.GetParameterAsText(2)
btouei = arcpy.GetParameterAsText(3)
atouei = arcpy.GetParameterAsText(4)
output = arcpy.GetParameterAsText(5)
css = arcpy.Describe(cs).catalogPath

df = pd.read_csv(css, skiprows = 0, encoding = "cp932")


crsp = CRS(btouei)
crst = CRS(atouei)
epsg_codep = "epsg:" + crsp.to_authority(min_confidence=50)[1]
epsg_codet = "epsg:" + crst.to_authority(min_confidence=50)[1]
transformer = pyproj.Transformer.from_crs(epsg_codep, epsg_codet, always_xy=True)

df['x'], df['y'] = transformer.transform(df[x_field].values, df[y_field].values)
if x_field == "x" or y_field == "y":
	flist = [i for i in list(df.columns) if (i != x_field and i != y_field)]
else:
	flist = df.columns
tt = []
for ttt in flist:
	tt.append(type(df[ttt][0]))
a = 0
with shapefile.Writer(output, shapeType=shapefile.POINT) as w:

    for field_name in flist:
        if tt == str:
        
            w.field(field_name, "C")
            
        else:
        
            w.field(field_name, "F", decimal = 5)
            
    for i, row in df.iterrows():
        arcpy.SetProgressorLabel(f"step {a+1}/{len(df)} Loading...")
        arcpy.SetProgressorPosition(a+1)    
        w.point(row["x"], row["y"])
        record_values = [row[field] for field in flist]
        w.record(*record_values)

        a = a + 1
w.close()

rprj = output.replace("shp", "prj")

with open(rprj,  'w') as prj:

    prj.write(atouei)
    
prj.close()

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
arcpy.ResetProgressor()
