import os
from osgeo import gdal
import pandas as pd
import shapefile

ascf = arcpy.GetParameterAsText(0)
shp = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)
delec = arcpy.GetParameterAsText(3) #option
touei = arcpy.GetParameterAsText(4)
asc_files = ascf.split(";")
shp_path = arcpy.Describe(shp).catalogPath



arcpy.SetProgressor("step", "処理を開始します...", len(asc_files), 1)

sr = shapefile.Reader(shp_path)
sh = sr.shapes()

a = 0
for n in asc_files:
    arcpy.SetProgressorLabel(f"ステップ {a+1}/{len(asc_files)} 実行中...")
    arcpy.SetProgressorPosition(a+1)
    rbpath = arcpy.Describe(n).catalogPath
    raster = gdal.Open(rbpath)

    geotransform = raster.GetGeoTransform()
    
    ncols = raster.RasterXSize
    nrows = raster.RasterYSize
    cellsize = geotransform[1]
    xllcorner = geotransform[0]
    yllcorner = geotransform[3] + nrows * geotransform[5]
    data = raster.GetRasterBand(1).ReadAsArray()
    id = []
    ii = 1
    datafl = []
    xx, yy = [], []
    for shpm in sh:
        for m in range(len(shpm.points)):
            
            x = shpm.points[m][0]
            y = shpm.points[m][1]
            xi = int((x - (geotransform[0] + 0.5 * geotransform[1])) / geotransform[1] + 1)
            yi = int((y - (geotransform[3] + geotransform[5] * raster.RasterYSize + 0.5 * (geotransform[1])) ) / geotransform[1] + 1)
            fl = data[yi * (-1)][xi - 1]
            datafl.append(fl)
            id.append(ii)
            xx.append(x)
            yy.append(y)
            ii = ii + 1
            
    fll = str(n).replace(".asc", "").replace(".tif", "")
    if delec:
        de = delec.split(";")
        for i in de:
            fll = fll.replace(i, "")
    if a == 0:
        df = pd.DataFrame({"x" : xx, "y" : yy, "id" : id, fll : datafl})
    else:
        df[fll] = datafl
    a = a + 1
with shapefile.Writer(output, shapeType=shapefile.POINT) as w:
    
    for field_name in list(df.columns)[2:]:
        w.field(field_name, "F",decimal = 5)
    
    for i, row in df.iterrows():
    
        w.point(row["x"], row["y"])  # x, y の取得
        record_values = [row[field] for field in list(df.columns)[2:]]
        w.record(*record_values)  # 属性データの書き込み

w.close()

rprj = output.replace("shp", "prj")

with open(rprj,  'w') as prj:

    prj.write(touei)

prj.close()

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
arcpy.ResetProgressor()


