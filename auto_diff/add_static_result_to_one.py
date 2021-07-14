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
    task_info_path = str(sys.argv[1])
    # task_info_path = "/Users/weihainan/Downloads/new_beijing_info_0705.txt"
    out_path = "/home/kddev/all_result.csv"
    map_task_info = {}

    with open(task_info_path) as fp:
        for line in fp.readlines():
            line = line.strip()
            task_ids = line.split(',')
            auto_task_id = task_ids[1]
            human_task_id = task_ids[2]
            diff_project_id = task_ids[3]
            diff_task_id = task_ids[4]
            map_task_info[diff_task_id] = [auto_task_id, human_task_id, diff_task_id, diff_project_id]

    with open(out_path, "w") as fp_w:
        fp_w.write(
            "autoTaskId,humanTaskId,diffProjectId,diffTaskID,model,xyz,类型,标答总数,[0~1]cm,(1~5]cm,(5~20]cm,(20~50]cm,>50cm,缺失,冗余\n")
        files = os.listdir(path)
        for fi in files:
            fi_d = os.path.join(path, fi)
            if not os.path.isdir(fi_d):
                fullpath = os.path.join(path, fi_d)
                if fullpath.find(".csv") == -1:
                    continue
                if fullpath.find("all") != -1:
                    continue

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
                        diff_task_id = static_num[0]
                        if diff_task_id=="2039593" :
                            print("")
                        task_info = map_task_info[diff_task_id]
                        static_num.insert(0, task_info[3])
                        static_num.insert(0, task_info[1])
                        static_num.insert(0, task_info[0])

                        total = int(static_num[7]) * 1.0
                        static_num[7] = "1.0"
                        if total != 0:
                            for j in range(8, 15):
                                static_num[j] = str(round(int(static_num[j]) / total, 2))
                        else:
                            continue
                            static_num[7] = "0.0"


                        fp_w.write(','.join(static_num) + "\n")
