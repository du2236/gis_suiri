import arcpy

aprx = arcpy.mp.ArcGISProject("CURRENT")

layout_name = arcpy.GetParameterAsText(0)
output_file = arcpy.GetParameterAsText(1)
cte = arcpy.GetParameterAsText(2)
reso = arcpy.GetParameter(3)

layout = aprx.listLayouts(layout_name)[0]

layout.exportToJPEG(output_file, resolution=reso, clip_to_elements=cte)