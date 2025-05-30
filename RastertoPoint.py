import os
from osgeo import gdal
import pandas as pd
import shapefile

ras = arcpy.GetParameterAsText(0)
touei = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)
f = arcpy.GetParameterAsText(3)
ras_path = arcpy.Describe(ras).catalogPath

raster = gdal.Open(ras_path)
nodata = raster.GetRasterBand(1).GetNoDataValue()
geotransform = raster.GetGeoTransform()
ncols = raster.RasterXSize
nrows = raster.RasterYSize
cellsize = geotransform[1]
xllcorner = geotransform[0]
yllcorner = geotransform[3] + nrows * geotransform[5]
data = raster.GetRasterBand(1).ReadAsArray()
arcpy.SetProgressor("step", "処理を開始します...", 0, ncols * nrows, 1)

with shapefile.Writer(output, shapeType=shapefile.POINT) as w:
    w.field("dp", 'F', decimal=3)
    
    total = 0
     
    for y in range(nrows):
        for x in range(ncols):
            dt = data[y][x]
            if dt != nodata:
                xx = x * geotransform[1] + geotransform[0] + geotransform[1] / 2
                yy = y * geotransform[5] + geotransform[3] + geotransform[5] / 2
                w.point(xx, yy)
                w.record(float(dt))  # 値を float に変換して書き込み
                
            total += 1
            if total % 100 == 0:
                arcpy.SetProgressorLabel(f"ステップ {round(total / (ncols * nrows) * 100)}% 実行中...")
                arcpy.SetProgressorPosition(total)
                    
w.close()

rprj = output.replace("shp", "prj")

with open(rprj,  'w') as prj:

    prj.write(touei)

prj.close()

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
arcpy.ResetProgressor()
