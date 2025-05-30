import pandas as pd
import shapefile
import chardet
pd.options.mode.chained_assignment = None
from pyproj import CRS
import pyproj

ipath = arcpy.GetParameterAsText(0)
angle_t = arcpy.GetParameter(1)
distance_t = arcpy.GetParameter(2)
touei = arcpy.GetParameterAsText(3)
shp_path = arcpy.Describe(ipath).catalogPath

def detect_encoding(dbf_path):
    with open(dbf_path, "rb") as f:
        raw_data = f.read(10000)  
        result = chardet.detect(raw_data)
    return result['encoding']

def distance_point_to_line(x0, y0, x1, y1, x2, y2):
    """
    点 (x0, y0) が直線 (x1, y1) - (x2, y2) からどれだけ離れているかを計算
    """
    if x1 == x2:  # 垂直な直線の場合
        return abs(x0 - x1)
    else:
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        return abs(a * x0 - y0 + b) / ((a**2 + 1) ** 0.5)

def calculate_angle(p1, p2, p3):
    """
    3点 (p1, p2, p3) を通る角度変化を計算
    p1 → p2 → p3 の角度差を [-180, 180] の範囲で返す
    """
    v1 = (p1[0] - p2[0], p1[1] - p2[1])  # ベクトル p2→p1
    v2 = (p3[0] - p2[0], p3[1] - p2[1])  # ベクトル p2→p3

    dot = v1[0] * v2[0] + v1[1] * v2[1]  # 内積
    det = v1[0] * v2[1] - v1[1] * v2[0]  # 外積

    angle = math.atan2(det, dot)  # 角度 (ラジアン)
    return math.degrees(angle)  # 角度 (度数法)

def simplify_polyline(points, angle_threshold, buffer_dist):
    """
    角度と距離の条件を両方満たす場合に点を保持するポリライン簡略化
    :param points: ポリラインの座標点 [(x1, y1), (x2, y2), ..., (xn, yn)]
    :param angle_threshold: 角度の閾値（この値以上の角度変化がある場合のみ保持）
    :param buffer_dist: バッファ距離（閾値、線分からの距離がこれ以上なら保持）
    :return: 簡略化されたポリラインの座標点リスト
    """
    if len(points) < 3:
        return points  # 3点未満ならそのまま

    simplified = [points[0]]  # 最初の点を追加
    p1 = points[0]  # 始点を固定
    i = 1  # p2 のインデックス

    while i < len(points) - 1:
        p2 = points[i]
        p3 = points[i + 1]

        angle = calculate_angle(p1, p2, p3)
        distance = distance_point_to_line(p2[0], p2[1], p1[0], p1[1], p3[0], p3[1])

        # 角度が閾値以上 OR 距離が閾値以上なら p2 を保持
        if abs(angle) - 180 < angle_threshold * (-1) or distance > buffer_dist:
            simplified.append(p2)  # 判定を満たした点を追加
            p1 = p2  # 次の始点を更新

        i += 1  # 次の判定へ進む

    simplified.append(points[-1])  # 最後の点を追加
    return simplified


dbf_path = shp_path.replace(".shp", ".dbf")
cpg_path = shp_path.replace(".shp", ".cpg")
prj_path = shp_path.replace(".shp", ".prj")
if os.path.exists(cpg_path):
    with open(cpg_path, "r") as cpg_file:
        encoding = cpg_file.read().strip()
    cpg_file.close()
else:
    encoding = detect_encoding(dbf_path)
    
if os.path.exists(prj_path):
    with open(prj_path, "r") as prj_file:
        prjj = prj_file.read().strip()
    prj_file.close()
src = shapefile.Reader(shp_path, encoding = encoding)  
sf = src.shapes()  
rf = src.records()  

fields = src.fields[1:] 
fn = [field[0] for field in fields]
fty = [field[1] for field in fields]
fsi = [field[2] for field in fields]
fde = [field[3] for field in fields]
new_row = []

for shp, rec in zip(sf, rf):

    sub_geo = []
    geo = []

    for i in range(len(shp.points)):
        if os.path.exists(prj_path):
            if prjj == touei:
                x = shp.points[i][0]
                y = shp.points[i][1]   
            else:
                crsp = CRS(prjj)
                crst = CRS(touei)
                epsg_codep = "epsg:" + crsp.to_authority(min_confidence=50)[1]
                epsg_codet = "epsg:" + crst.to_authority(min_confidence=50)[1]
                transformer = pyproj.Transformer.from_crs(epsg_codep, epsg_codet, always_xy=True)
                x, y = transformer.transform(shp.points[i][0], shp.points[i][1])
        else:
            x = shp.points[i][0]
            y = shp.points[i][1]           
        sub_geo.append([x, y])  
    geo.append(sub_geo)

    row_data = {"geometry": geo}
    for field_name in fn:
        row_data[field_name] = rec[field_name]

    new_row.append(row_data)

# DataFrame作成
nf = pd.DataFrame(new_row)
shptype = shp.shapeTypeName
geometry_list = {"POLYGON" : shapefile.POLYGON, "POLYLINE" : shapefile.POLYLINE, "POINT" : shapefile.POINT}
st = geometry_list[shptype] 
nr = []
dd = 0
for j in range(len(nf)):
    polyline = nf["geometry"][j][0]
    row_data = {"geometry": [simplify_polyline(polyline, angle_t, distance_t)]}
    dec = len(polyline) - len(simplify_polyline(polyline, angle_t, distance_t))
    dd = dec + dd
    for field_name in fn:
        row_data[field_name] = nf[field_name][j]
    nr.append(row_data)
nnf = pd.DataFrame(nr)
rpath = shp_path.replace(".shp", "_simple.shp")
with shapefile.Writer(rpath, shapeType=st) as w:
    
    for field_name, ty, si, de in zip(fn, fty, fsi, fde):
        w.field(field_name, ty, si, de)
         
    total = len(nnf)

    for i, row in enumerate(nnf.itertuples(index=False), start=1):
        if i % 100 == 0 or i == total:  # 100 ステップごとに更新
            arcpy.SetProgressorLabel(f"ステップ {round(i / total * 100)}/{100} 実行中...")
            arcpy.SetProgressorPosition(i)
        if st == shapefile.POLYLINE:
            w.line(row.geometry)  # ラインデータの追加（リストで囲む必要あり）
        else:
            w.poly(row.geometry)
        w.record(*[getattr(row, field) for field in fn])  # 属性データを追加

w.close()

rprj = rpath.replace("shp", "prj")

with open(rprj,  'w') as prj:

    prj.write(touei)

prj.close()
    
aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.activeMap  
m.addDataFromPath(rpath)

arcpy.AddMessage(f"{dd}個の座標が減りました.")