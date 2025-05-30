import os
from osgeo import gdal
import numpy as np

tif_path = arcpy.GetParameterAsText(0)
output = arcpy.GetParameterAsText(1)
ras_path = arcpy.Describe(tif_path).catalogPath
raster = gdal.Open(ras_path)

data = raster.GetRasterBand(1).ReadAsArray()

geotransform = raster.GetGeoTransform()
ncols = raster.RasterXSize
nrows = raster.RasterYSize
cellsize = geotransform[1]
xllcorner = geotransform[0]
yllcorner = geotransform[3] + nrows * geotransform[5]

with open(output, 'w') as asc_file:
    asc_file.write(f"ncols         {ncols}\n")
    asc_file.write(f"nrows         {nrows}\n")
    asc_file.write(f"xllcorner     {xllcorner}\n")
    asc_file.write(f"yllcorner     {yllcorner}\n")
    asc_file.write(f"cellsize      {cellsize}\n")
    asc_file.write(f"NODATA_value      -9999 \n")
    np.savetxt(asc_file, data, fmt='%g') 
asc_file.close()