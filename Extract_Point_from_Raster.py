import os
from osgeo import gdal
import pandas as pd
import shapefile

folder_path = arcpy.GetParameterAsText(0)
shp = arcpy.GetParameterAsText(1)
outpath = arcpy.GetParameterAsText(2)
delec = arcpy.GetParameterAsText(3) #option

shp_path = arcpy.Describe(shp).catalogPath

asc_files = [f for f in os.listdir(folder_path) if f.endswith((".asc", ".tif"))]

arcpy.SetProgressor("step", "処理を開始します...", 0, len(asc_files), 1)

sr = shapefile.Reader(shp_path)
sh = sr.shapes()

a = 0
for n in asc_files:
    arcpy.SetProgressorLabel(f"ステップ {a+1}/{len(asc_files)} 実行中...")
    arcpy.SetProgressorPosition(a+1)
    rbpath = os.path.join(folder_path, n)
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
    for shpm in sh:
        for m in range(len(shpm.points)):
            
            x = round(shpm.points[m][0])
            y = round(shpm.points[m][1])
            xi = int((x - (geotransform[0] + 0.5 * geotransform[1])) / geotransform[1] + 1)
            yi = int((y - (geotransform[3] + geotransform[5] * raster.RasterYSize + 0.5 * (geotransform[1])) ) / geotransform[1] + 1)
            fl = data[yi * (-1)][xi - 1]
            datafl.append(fl)
            id.append(ii)
            ii = ii + 1
            
    fll = str(n).replace(".asc", "").replace(".tif", "")
    if delec:
        de = delec.split(";")
        for i in de:
            fll = fll.replace(i, "")
    if a == 0:
        df = pd.DataFrame({"id" : id, fll : datafl})
    else:
        df[fll] = datafl
    a = a + 1
df.to_csv(outpath, index = False)
arcpy.ResetProgressor()