import arcpy
import numpy as np
import os
import tempfile
import time
raster1 = arcpy.GetParameterAsText(0)
minVal = arcpy.GetParameter(1)
maxVal = arcpy.GetParameter(2)
sel = arcpy.GetParameterAsText(3)
num_classes = arcpy.GetParameter(4)
interval = arcpy.GetParameter(5)

temp_dir = tempfile.gettempdir()
if sel == "interval":
    class_breaks = np.arange(minVal, maxVal + interval, interval, dtype = "f8")
    num_classes = len(class_breaks)
    bd = np.arange(minVal + interval/2, maxVal + interval, interval, dtype = "f8")
elif sel == "number":
    class_breaks = np.linspace(minVal, maxVal, num_classes, dtype = "f8")
    bd = np.linspace(minVal+(maxVal - minVal)/ (num_classes - 1) / 2, maxVal, num_classes, dtype = "f8")
    
data =bd.reshape(-1, 1) 

header = f"""ncols         {data.shape[1]}
nrows         {data.shape[0]}
xllcorner     0
yllcorner     0
cellsize      1
NODATA_value  -9999
"""
output_asc = os.path.join(temp_dir, "dummy_raster.asc")

with open(output_asc, "w") as f:
    f.write(header)
    np.savetxt(f, data, fmt="%.2f")
f.close()

p = arcpy.mp.ArcGISProject('CURRENT')
m = p.activeMap
m.addDataFromPath(output_asc)

lyr  = m.listLayers("dummy_raster.asc")[0]
lyr1 = m.listLayers(raster1)[0]
#set symbology (color ramp, labels, stretch type)
sym = lyr.symbology
sym.updateColorizer('RasterClassifyColorizer')
cr = p.listColorRamps('Bathymetric Scale')[0]
sym.colorizer.colorRamp = cr
sym.colorizer.classificationMethod = "ManualInterval"

sym.colorizer.breakCount = num_classes
lyr.symbology = sym

cim_lyr = lyr.getDefinition('V2')

for i in range(num_classes):
    cim_lyr.colorizer.classBreaks[i].upperBound = class_breaks[i]
    if i == 0:
        cim_lyr.colorizer.classBreaks[i].label = f"-{class_breaks[i]:.1f}"
    else:
        cim_lyr.colorizer.classBreaks[i].label = f"{class_breaks[i-1]:.1f}-{class_breaks[i]:.1f}"

# 変更を適用
lyr.setDefinition(cim_lyr)

aa = arcpy.management.ApplySymbologyFromLayer(in_layer =raster1, in_symbology_layer = r"dummy_raster.asc")
arcpy.SetParameter(6, aa)