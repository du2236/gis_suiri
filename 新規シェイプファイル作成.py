import shapefile
import arcpy
import os

folder_path = arcpy.GetParameterAsText(0)
feature_name = arcpy.GetParameterAsText(1)
geometry_type = arcpy.GetParameterAsText(2)
field = arcpy.GetParameterAsText(3)
ftype = arcpy.GetParameterAsText(4)
spatial = arcpy.GetParameterAsText(5)

path = os.path.join(folder_path, feature_name) + ".shp"
if ";" in field:
    field_list = field.split(';')
    ftype_list = ftype.split(";")
else:
    field_list = [field]
    ftype_list = [ftype]
    
ftype_p = {
    "Short(単整数)":  {"shp_type": "N", "size": 5, "decimal": 0}, 
    "Long(長整数)":   {"shp_type": "N", "size": 10, "decimal": 0}, 
    "Float(単精度浮動小数点数)":  {"shp_type": "F", "size": 19, "decimal": 6},  
    "Double(倍精度浮動小数点数)": {"shp_type": "F", "size": 19, "decimal": 6},  
    "Text(文字)":   {"shp_type": "C", "size": 50, "decimal": 0}
}
geometry_list = {"POLYGON" : shapefile.POLYGON, "POLYLINE" : shapefile.POLYLINE, "POINT" : shapefile.POINT}
st = geometry_list[geometry_type]

with shapefile.Writer(path, shapeType = st) as w:
    for i, j in zip(field_list, ftype_list):
         w.field(i, ftype_p[j]["shp_type"], ftype_p[j]["size"], ftype_p[j]["decimal"]) 

w.close()    

rprj = path.replace("shp", "prj")

with open(rprj,  'w') as prj:

    prj.write(spatial)

prj.close()

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(path)
