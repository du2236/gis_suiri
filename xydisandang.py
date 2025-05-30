import os
from osgeo import gdal
import pandas as pd
import numpy as np

ascx = arcpy.GetParameterAsText(0)
ascy = arcpy.GetParameterAsText(1)

output_tif = arcpy.GetParameterAsText(2)
lyfile = arcpy.GetParameterAsText(3)

rbpathx = arcpy.Describe(ascx).catalogPath
rbpathy = arcpy.Describe(ascy).catalogPath
rasterx = gdal.Open(rbpathx)
rastery = gdal.Open(rbpathy)
geotransformx = rasterx.GetGeoTransform()
geotransformy = rastery.GetGeoTransform()
ncols = rasterx.RasterXSize
nrows = rasterx.RasterYSize
cellsize = geotransformx[1]
xllcorner = geotransformx[0]
yllcorner = geotransformx[3] + nrows * geotransformx[5]
datax = rasterx.GetRasterBand(1).ReadAsArray()
datay = rastery.GetRasterBand(1).ReadAsArray()
if datax.shape != datay.shape:
    arcpy.AddError("ラスタのカラム数とコラム数をそろえてください")

dfx = pd.DataFrame(datax)
dfy = pd.DataFrame(datay)
df1 = (dfx * dfx + dfy * dfy) ** (1 / 2)
df1 = np.array(df1)
df2 = ((270 - np.degrees(np.arctan2(np.array(dfy), np.array(dfx)))) + 360) % 360

driver = gdal.GetDriverByName("GTiff")
dataset = driver.Create(output_tif, ncols, nrows, 2, gdal.GDT_Float32) 
geoTransform = [xllcorner, cellsize, 0, yllcorner + nrows * cellsize, 0, -cellsize]
dataset.SetGeoTransform(geoTransform)

band1 = dataset.GetRasterBand(1)
band1.WriteArray(df1)
band1.SetDescription("U Component")

# バンド 2 (V 成分)
band2 = dataset.GetRasterBand(2)
band2.WriteArray(df2)
band2.SetDescription("V Component")

metadata = {
    "TIFFTAG_SOFTWARE": "GDAL Custom Script",
    "DataType": "Vector-UV",
    "AREA_OR_POINT": "Area"
}
dataset.FlushCache()
dataset = None
aprx = arcpy.mp.ArcGISProject("CURRENT") 

m = aprx.activeMap 
file_name = os.path.basename(output_tif)
sy = arcpy.management.ApplySymbologyFromLayer(in_layer =output_tif, in_symbology_layer = lyfile)
syl = sy.getOutput(0)
ss = syl.name
syl.name = ss.replace("_Layer1", "").replace("_Layer2", "").replace("_Layer3", "").replace("_Layer4", "").replace("_Layer5", "")
arcpy.AddMessage(syl)
m.addLayer(syl)
arcpy.ResetProgressor()