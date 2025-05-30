import os
import shapefile
import numpy as np

shp_path = arcpy.GetParameterAsText(0)
extent = arcpy.GetParameterAsText(1)
cellsize = arcpy.GetParameter(2)
extent = extent.split(" ")
extent = extent[0:4]
stp = arcpy.GetParameter(3)
output = arcpy.GetParameterAsText(4)

shp_path = arcpy.Describe(shp_path).catalogPath

def create_raster_from_polylines(shp_path, extent, cellsize, asc_path, stp):#extent = [left, botm, right, top]

    left, botm, right, top =  extent
    left, botm, right, top = float(left), float(botm), float(right), float(top)
    xsize = int((right - left) / cellsize)
    ysize = int((top - botm) / cellsize)
    data = np.zeros((ysize, xsize), dtype=int)  
    
    sf = shapefile.Reader(shp_path)
    
    for shape in sf.shapes():
        for i in range(len(shape.points) - 1):
            x1, y1 = shape.points[i]
            x2, y2 = shape.points[i + 1]
            r1 = (top - y1) / cellsize
            c1 = (x1 - left) / cellsize
            r2 = (top - y2) / cellsize
            c2 = (x2 - left) / cellsize
            
            data = create_raster(data, r1, c1, r2, c2, stp)
    	
    save_asc(data, left, botm, cellsize, output)
def create_raster(data, r1, c1, r2, c2, stp):
    
    r1, c1, r2, c2 = float(r1), float(c1), float(r2), float(c2)
    
    steps = int(max(abs(r2 - r1), abs(c2 - c1)) * stp)  
    
    for t in np.linspace(0, 1, steps):
        r = r1 + t * (r2 - r1)
        c = c1 + t * (c2 - c1)
        ri, ci = int((r)), int((c)) 
        if 0 <= ri < data.shape[0] and 0 <= ci < data.shape[1]:
            data[ri, ci] = 1
    return data

def save_asc(raster, x_min, y_min, resolution, asc_path):
    rows, cols = raster.shape
    header = f"NCOLS {cols}\nNROWS {rows}\nXLLCORNER {x_min}\nYLLCORNER {y_min}\n"
    header += f"CELLSIZE {resolution}\nNODATA_VALUE 0\n"
    
    with open(asc_path, "w") as f:
        f.write(header)
        np.savetxt(f, raster, fmt="%.0f",delimiter=" ")
        
create_raster_from_polylines(shp_path, extent, cellsize, output, stp)

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(output)
