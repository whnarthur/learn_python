# coding:utf-8

import sys
import os
import json
import requests
import time
import xlrd


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
    path = "/Users/weihainan/Documents/diff_new"
    sum = []
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            fullpath = os.path.join(dirpath, file)
            print(fullpath)
            with open(fullpath) as fp:
                lines = fp.readlines()
                for i in range(len(lines)):
                    if i == 0:
                        continue

                    line = lines[i].strip()
                    # print(line)
                    static_num = line.split(',')
                    if len(sum) != 18:
                        single_sum = []
                        single_sum.append(int(static_num[3]))
                        single_sum.append(int(static_num[4]))
                        single_sum.append(int(static_num[5]))
                        single_sum.append(int(static_num[6]))
                        single_sum.append(int(static_num[7]))
                        single_sum.append(int(static_num[8]))
                        single_sum.append(int(static_num[9]))
                        single_sum.append(int(static_num[10]))
                        sum.append(single_sum)
                    else:
                        sum[i - 1][0] += int(static_num[3])
                        sum[i - 1][1] += int(static_num[4])
                        sum[i - 1][2] += int(static_num[5])
                        sum[i - 1][3] += int(static_num[6])
                        sum[i - 1][4] += int(static_num[7])
                        sum[i - 1][5] += int(static_num[8])
                        sum[i - 1][6] += int(static_num[9])
                        sum[i - 1][7] += int(static_num[10])

    table_head = ["BARRIER_GEOMETRY,x,", "BARRIER_GEOMETRY,y,", "BARRIER_GEOMETRY,z,", "DIVIDER,x,", "DIVIDER,y,", "DIVIDER,z,", "OBJECT_PG,x,", "OBJECT_PG,y,", "OBJECT_PG,z,", "OBJECT_PL,x,", "OBJECT_PL,y,", "OBJECT_PL,z,", "ROAD_FACILITIES,x,", "ROAD_FACILITIES,y,", "ROAD_FACILITIES,z,", "TRAFFICSIGN,x,", "TRAFFICSIGN,y,", "TRAFFICSIGN,z,"]
    for i in range(len(sum)):
        single_sum = sum[i]
        str_single_sum = map(lambda x: str(x), single_sum)
        # print(str_single_sum)
        print(table_head[i] + ','.join(str_single_sum))

