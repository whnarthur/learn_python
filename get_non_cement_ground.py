import sys
import json

if __name__ == '__main__':
    with open("/Users/weihainan/Documents/road_distress_frame_measure.json") as fp:
        j = json.load(fp)
        result = []
        for key in j.keys():
            # print(key)
            if "patch_repairs" not in j[key].keys():
                continue
            pairs = j[key]["patch_repairs"]
            for p in pairs:
                if p["measure_type"]:
                    # print(p["3d_contour"])
                    coords = p["3d_contour"]
                    new_coords = []
                    for coord in coords:
                        new_coord = []
                        new_coord.append(coord[1])
                        new_coord.append(coord[0])
                        new_coord.append(coord[2])
                        new_coords.append(new_coord)
                    result.append(new_coords)

        j_result = {}
        geometrys = []
        for r in result:
            geometry = {}
            coord = []
            coord.append(r)
            geometry["coordinates"] = coord
            geometry["type"] = "Polygon"
            feature = {}
            feature["geometry"] = geometry
            feature["type"] = "Feature"
            geometrys.append(feature)

        j_result["features"] = geometrys
        j_result["type"] = "FeatureCollection"

        with open("/Users/weihainan/Documents/non_cement_ground.geojson", "w") as fp1:
            fp1.write(json.dumps(j_result))


