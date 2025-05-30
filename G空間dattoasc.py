import pandas as pd
import os
import arcpy
from osgeo import gdal
import numpy as np

folder_path = arcpy.GetParameterAsText(0)
ex_xls = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)

dat_files = [f for f in os.listdir(folder_path) if f.endswith((".dat"))]
aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap
for dt in dat_files:
    opath = dt.replace(".dat", ".asc")
    aspath = os.path.join(output, opath)
    area = dt[-11:-4]
    sn = dt[-11:-7] + "m"
    df = pd.read_excel(ex_xls, sheet_name=sn, index_col=None, header = None)
    ao =  df[1]
    ind = ao[ao == area].index[0]
    ncols, nrows, xll, yll, cell = df[9][ind], df[10][ind], df[3][ind], df[4][ind], df[2][ind]
    rbpath = os.path.join(folder_path, dt)
    with open(rbpath, encoding="cp932") as f:
        data = f.read()
        data = data.replace("-", " -")
    f.close()
    with open(aspath, 'w') as asc_file:
        asc_file.write(f"ncols         {ncols}\n")
        asc_file.write(f"nrows         {nrows}\n")
        asc_file.write(f"xllcorner     {xll}\n")
        asc_file.write(f"yllcorner     {yll}\n")
        asc_file.write(f"cellsize      {cell}\n")
        asc_file.write(f"NODATA_value    -99\n")
        asc_file.write(f"{data}") 
    asc_file.close()
    if "ir" not in dt:
        m.addDataFromPath(aspath)
    else:
        raster = gdal.Open(aspath)
        data = raster.GetRasterBand(1).ReadAsArray()
        data1 = np.where(data != 0, np.round(data // 100000), -99)
        data2 = np.where(data != 0, np.round(data % 100000 / 100, 2), -99)
        flg = dt.replace(".dat", "_flg.asc")
        ften = dt.replace(".dat", "_ften.asc")
        flgpath = os.path.join(output, "flg", flg)
        ftenpath = os.path.join(output, "ften", ften)
        flgf = os.path.join(output, "flg")
        ftenf = os.path.join(output, "ften")
        os.makedirs(flgf, exist_ok=True)
        os.makedirs(ftenf, exist_ok=True)
        for ff , dd in zip([flgpath, ftenpath], [data1, data2]):
            
            with open(ff, 'w') as asc_file:
                asc_file.write(f"ncols         {ncols}\n")
                asc_file.write(f"nrows         {nrows}\n")
                asc_file.write(f"xllcorner     {xll}\n")
                asc_file.write(f"yllcorner     {yll}\n")
                asc_file.write(f"cellsize      {cell}\n")
                asc_file.write(f"NODATA_value     -99\n")
                np.savetxt(asc_file, dd, fmt="%g") 
            asc_file.close()
            m.addDataFromPath(ff)
        raster = None
        os.remove(aspath)
        
        
        
