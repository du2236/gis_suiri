aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.activeMap 
symbol = arcpy.GetParameterAsText(0)
addly = arcpy.GetParameterAsText(1)
addli = addly.split(";")
for i in addli:
    layer = m.listLayers(symbol)[0]
    layer1 = m.listLayers(i)[0]
    sym = layer.symbology
    layer1.symbology = sym