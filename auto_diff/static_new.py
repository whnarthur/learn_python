# coding:utf-8

import sys
import os
import json
import requests
import time


def get_full_fusions(projects):
    muses = "http://srv-04.gzproduction.com:13440"
    fusion_task_ids = []
    try:
        header = {'Content-Type': 'application/json'}
        for id in projects:
            data = {"type": "full_fusion", "projectId": id}
            url = muses + "/muses/task/query"
            rslt = requests.post(url, json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=header)
            # print(rslt.json())
            info = rslt.json()
            if info['code'] != "0":
                raise "failed to get fusion {0}".format(info)
            fusion_task_id = info['result']['result'][0]['id']
            fusion_task_ids.append("{0}".format(fusion_task_id))
        return fusion_task_ids
    except Exception as e:
        print("error get full fusions")
        print(e)


def create_post_diff(tasks, full_fusions, task_name):
    header = {'Content-Type': 'application/json'}
    data = {
        "category": 6,
        "engineVersions": {
            "fusion_diff": "osm_diff_v1.3.4.3_20210611"
        },
        "linkParams": {
            "fusion_diff": [{"k": "checkShape", "v": "true"}, {"k": "shapeMatchThreshhold", "v": "0.5"}]
        },
        "rangeType": "64",
        "createBy": "edit_lead1",
        "tags": [
            {
                "k": "currentLibraryData",
                "v": ','.join(tasks)
            },
            {
                "k": "comparativeLibraryData",
                "v": ','.join(full_fusions)
            }
        ],
        # "priority": 4,
        "description": "",
        "name": task_name,
        "linkCode": "fusion_diff"
    }
    kts = "http://kts.gzproduction.com"
    url = kts + "/kts/project/create/v2"
    try:
        print("url={0}, data={1}".format(url, data))
        rslt = requests.post(url, json.dumps(data), headers=header)
        print(rslt.json())

        diff_project_id = rslt.json()["result"]
        print(diff_project_id)
    except Exception as e:
        print(e)
    return rslt.json()["result"]


if __name__ == '__main__':
    # path = "/Users/weihainan/Downloads/2"
    path = "/home/kddev"
    map_sum = {}
    sum = []
    files = os.listdir(path)
    for fi in files:
        fi_d = os.path.join(path, fi)
        if not os.path.isdir(fi_d):
            fullpath = os.path.join(path, fi_d)
            if fullpath.find(".csv") == -1:
                continue
            print(fullpath)
            with open(fullpath) as fp:
                lines = fp.readlines()
                for i in range(len(lines)):
                    if i == 0:
                        continue

                    line = lines[i].strip()
                    if line.find(",,,,,,,,,,,") != -1:
                        continue

                    # print(line)
                    static_num = line.split(',')
                    # print(static_num)
                    key = "%s,%s,%s" % (static_num[1], static_num[2], static_num[3])
                    if key in map_sum.keys():
                        map_sum[key][0] += int(static_num[4])
                        map_sum[key][1] += int(static_num[5])
                        map_sum[key][2] += int(static_num[6])
                        map_sum[key][3] += int(static_num[7])
                        map_sum[key][4] += int(static_num[8])
                        map_sum[key][5] += int(static_num[9])
                        map_sum[key][6] += int(static_num[10])
                        map_sum[key][7] += int(static_num[11])
                    else:
                        value = [int(static_num[4]), int(static_num[5]), int(static_num[6]), int(static_num[7]),
                                 int(static_num[8]), int(static_num[9]), int(static_num[10]), int(static_num[11])]
                        map_sum[key] = value

    with open("result_detail.csv", "w") as fp_w:
        fp_w.write("model,xyz,类型,标答总数,[0~1]cm,(1~5]cm,(5~20]cm,(20~50]cm,>50cm,缺失,冗余" + "\n")
        for key in map_sum.keys():
            str_single_sum = map(lambda x: str(x), map_sum[key])
            # print(str_single_sum)
            fp_w.write(key + "," + ','.join(str_single_sum) + "\n")

    with open("result.csv", "w") as fp_w:
        fp_w.write(
            "model,xyz,类型,标答总数,[0~1]cm(百分比),(1~5]cm(百分比),(5~20]cm(百分比),(20~50]cm(百分比),>50cm(百分比),缺失(百分比),冗余(百分比)" + "\n")
        for key in map_sum.keys():
            total = map_sum[key][0]
            if (total != 0):
                map_sum[key][0] = round(map_sum[key][0] * 1.0 / total, 2)
                map_sum[key][1] = round(map_sum[key][1] * 1.0 / total, 2)
                map_sum[key][2] = round(map_sum[key][2] * 1.0 / total, 2)
                map_sum[key][3] = round(map_sum[key][3] * 1.0 / total, 2)
                map_sum[key][4] = round(map_sum[key][4] * 1.0 / total, 2)
                map_sum[key][5] = round(map_sum[key][5] * 1.0 / total, 2)
                map_sum[key][6] = round(map_sum[key][6] * 1.0 / total, 2)
                map_sum[key][7] = round(map_sum[key][7] * 1.0 / total, 2)
            str_single_sum = map(lambda x: str(x), map_sum[key])
            fp_w.write(key + "," + ','.join(str_single_sum) + "\n")
