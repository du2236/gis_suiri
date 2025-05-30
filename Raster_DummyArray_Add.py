import os
from osgeo import gdal
import pandas as pd
import numpy as np

ras = arcpy.GetParameterAsText(0)


aup = arcpy.GetParameter(1)
adown = arcpy.GetParameter(2)
aleft = arcpy.GetParameter(3)
aright = arcpy.GetParameter(4)
output = arcpy.GetParameterAsText(5)

ras_path = arcpy.Describe(ras).catalogPath

raster = gdal.Open(ras_path)
geotransform = raster.GetGeoTransform()

ncols = raster.RasterXSize + aleft + right
nrows = raster.RasterYSize + aup + down
cellsize = geotransform[1]
xllcorner = geotransform[0] - aleft * geotransform[1]
yllcorner = geotransform[3] + (nrows + adown) * geotransform[5]
data = raster.GetRasterBand(1).ReadAsArray()

df = pd.DataFrame(data)

dfl = [df.iloc[:, [0]]]  *a left
dfr = [df.iloc[:, [-1]]]  *a right


df = pd.concat(dfl + [df] + dfr, axis=1)

dfu = [df.iloc[[0], :]]  * aup
dfd = [df.iloc[[-1], :]] *adown

df = pd.concat(dfu + [df] + dfd, ignore_index=True)

