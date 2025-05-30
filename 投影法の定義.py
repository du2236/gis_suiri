import shapefile
import arcpy
import os

feature_name = arcpy.GetParameterAsText(0)
spatial = arcpy.GetParameterAsText(1)

shp_path = arcpy.Describe(feature_name).catalogPath

prj_path = shp_path.replace(".shp", ".prj")

with open(prj_path,  'w') as prj:

    prj.write(spatial)

prj.close()