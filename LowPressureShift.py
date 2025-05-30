import pandas as pd
import shapefile
import arcpy
import chardet
from pyproj import CRS
import pyproj
import time
folder = arcpy.GetParameterAsText(0)
input_path = arcpy.GetParameterAsText(1)
xidou = arcpy.GetParameter(2)
yidou = arcpy.GetParameter(3)
angle = arcpy.GetParameter(4)
dis = arcpy.GetParameter(5)
atouei = arcpy.GetParameterAsText(6)
output_path = arcpy.GetParameterAsText(7)
clip = arcpy.GetParameterAsText(8)
output_path2 = arcpy.GetParameterAsText(9)
tbx = arcpy.ImportToolbox(r"C:\home\ueda\ツールボックス\python作成ツール.atbx")

list_c = [f for f in os.listdir(folder) if f.endswith((".csv"))]
for cs in list_c:
    ccs = os.path.join(folder, cs)
    sh = cs.replace("csv", "shp")
    input = os.path.join(input_path, sh)
    output = os.path.join(output_path, sh)
    output2 = os.path.join(output_path2, sh)

    arcpy.management.SelectLayerByLocation(
    	in_layer=sh,
    	overlap_type="INTERSECT",
    	select_features=clip,
    	search_distance=None,
    	selection_type="NEW_SELECTION",
    	invert_spatial_relationship="INVERT"
    )
    arcpy.conversion.ExportFeatures(
        in_features=input,
        out_features=output,
        where_clause="",
        use_field_alias_as_name="NOT_USE_ALIAS",
        sort_field=None
    )
    tbx.FeatureShift(
        shp=output,
        xidou=xidou,
        yidou=yidou,
        angle=angle,
        dis=dis,
        btouei=atouei,
        atouei=atouei,
        output=output2
    )

arcpy.ResetProgressor()
