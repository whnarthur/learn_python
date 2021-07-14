# coding:utf-8

import sys
import os
import json
import requests
import time


# import xlrd


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
            "autohdmap_multi_merge_diff_cli": "osm_diff_v1.3.5_20210617"
        },
        "linkParams": {
            "autohdmap_multi_merge_diff_cli": [{"k": "checkShape", "v": "true"},
                                               {"k": "shapeMatchThreshhold", "v": "1.5"},
                                               {"k": "stasScene", "v": "other"}]
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


def get_diff_task_id(diff_project_id):
    req = requests.get("http://kts.gzproduction.com/kts/task/v2/findByProjectId?projectIds=%s" % diff_project_id)
    # print(req.text)
    jsonData = json.loads(req.text)
    # print(jsonData["result"][1]["id"])
    return jsonData["result"][1]["id"]


if __name__ == '__main__':
    all_diff_ids = []
    new_all_diff_ids = []
    input = str(sys.argv[1])
    prefix = str(sys.argv[2])
    output = str(sys.argv[3])
    with open(input) as fp:
        for line in fp.readlines():
            line = line.strip()
            if len(line) <= 0: continue
            line = line.split(',')
            name = line[0]
            project_ids = line[1]
            task_ids = line[2]
            #
            projects = project_ids.split(',')
            tasks = task_ids.split(',')
            full_fusions = get_full_fusions(projects)
            print(full_fusions)
            #
            diff_project_id = create_post_diff(tasks, full_fusions,
                                               "{0}_pos_diff_{1}_{2}".format(prefix, name, time.time()))
            all_diff_ids.append(diff_project_id)
            #
            diff_task_id = get_diff_task_id(diff_project_id)
            task_info = (name, projects[0], tasks[0], diff_project_id, diff_task_id)
            new_all_diff_ids.append(task_info)

    with open(output, "w") as fp_w:
        for task_info in new_all_diff_ids:
            fp_w.write("%s,%s,%s,%s,%s\n" % (task_info[0], task_info[1], task_info[2], task_info[3], task_info[4]))
