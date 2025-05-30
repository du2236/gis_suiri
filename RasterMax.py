import os
from osgeo import gdal
import pandas as pd
import shapefile
import numpy as np

ras = arcpy.GetParameterAsText(0)
touei = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)
f = arcpy.GetParameterAsText(3)
ras_path = arcpy.Describe(ras).catalogPath

raster = gdal.Open(ras_path)

geotransform = raster.GetGeoTransform()
ncols = raster.RasterXSize
nrows = raster.RasterYSize
cellsize = geotransform[1]
xllcorner = geotransform[0]
yllcorner = geotransform[3] + nrows * geotransform[5]
data = raster.GetRasterBand(1).ReadAsArray()
nr = []
y, x = np.unravel_index(np.argmax(data), data.shape)
xx = x * geotransform[1] + geotransform[0] + geotransform[1] / 2
yy = y * geotransform[5] + geotransform[3] + geotransform[5] / 2
dt = data[y][x]
nr.append({"x": xx, "y" : yy, "dp" : dt})
df = pd.DataFrame(nr)

with shapefile.Writer(output, shapeType=shapefile.POINT) as w:
    w.field("dp", 'F', decimal=3)

    records = []  
    total = len(df)

    for i, row in enumerate(df.itertuples(index=False), start=1):

        w.point(row.x, row.y) 
        w.record(row.dp if f == "True" else 0)

w.close()

rprj = output.replace("shp", "prj")

with open(rprj,  'w') as prj:

    prj.write(touei)

prj.close()

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
arcpy.ResetProgressor()