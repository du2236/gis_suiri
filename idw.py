point = arcpy.GetParameterAsText(0)
extent = arcpy.GetParameterAsText(1)
field = arcpy.GetParameterAsText(2)
cellsize = arcpy.GetParameterAsText(3)
output = arcpy.GetParameterAsText(4)
#touei = arcpy.GetParameterAsText(5)
with arcpy.EnvManager(extent=extent):
    arcpy.ddd.Idw(
        in_point_features=point,
        z_field=field,
        out_raster=output,
        cell_size=cellsize,
        power=3,
        search_radius="VARIABLE 9",
        in_barrier_polyline_features=None
    )
aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)