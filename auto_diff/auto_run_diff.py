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
    shapeMatchThreshhold = "3.8"
    task_info = {}
    with open("input_task.txt") as fp:
        for line in fp.readlines():
            line = line.strip().split(' ')
            task_info[line[1]] = line[0]
        # print(task_info)

        for (task_id, project_id) in task_info.items():
            path = "/data/wei/data/" + task_id
            cmd = "cd " + path
            os.system(cmd)
            task_info_path = path + "/taskInfo32_all.json"
            json_str = ""
            with open(task_info_path) as fp_r:
                json_str = fp_r.read()
            jsonData = json.loads(json_str)
            params = jsonData["input"]["params"]
            for p in params:
                if p["k"] == "shapeMatchThreshhold":
                    p["v"] = shapeMatchThreshhold
                    break
            json_str = json.dumps(jsonData, indent=4)
            with open(task_info_path, "w") as fp_w:
                fp_w.write(json_str)
            cmd = "docker run --rm -v /data:/data -a stdout -a stderr -u $(id -u) op-01.gzproduction.com/kd-ad/autohdmap_multi_merge_diff_cli:osm_diff_v1.3.5_20210617 /bin/bash -c \'umask 0000 && /compiler/build/bin/autohdmap_multi_merge_diff_cli /data/wei/data/%s/taskInfo32_all.json\'" % task_id
            os.system(cmd)
            cmd = "cp /data/wei/data/%s/output/diff_stat.csv /data/wei/data/diff_output/%s.csv" % (task_id, project_id)
            os.system(cmd)

