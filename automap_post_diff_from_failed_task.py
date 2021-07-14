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
            "fusion_diff": ""
        },
        "linkParams": {
            "fusion_diff": [{"k": "checkShape", "v": "true"}]
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
    task_infos = {}
    with open("21G1北京_task_info.txt") as fp:
        for ids in fp.readlines():
            res = ids.strip().split(',')
            diff_project_id = res[3]
            task_infos[diff_project_id]  = res

    new_task_infos = []
    failed_diff_project_ids = []
    with open("failed_task.txt") as fp1:
        for diff_project_id in fp1.readlines():
            diff_project_id = diff_project_id.strip()
            failed_diff_project_ids.append(diff_project_id)
            if diff_project_id not in task_infos.keys():
                continue
            task_info = task_infos[diff_project_id]

            project_ids = task_info[1]
            task_ids = task_info[2]
            name = task_info[0]
            #
            projects = project_ids.split(',')
            tasks = task_ids.split(',')
            full_fusions = get_full_fusions(projects)
            print(full_fusions)
            #
            diff_project_id = create_post_diff(tasks, full_fusions, "20210531_test_automap_{0}_{1}".format(name, time.time()))
            new_task_info = (name, projects[0], tasks[0], diff_project_id)
            new_task_infos.append(new_task_info)

    for key in task_infos.keys():
        diff_project_id = key
        ids = task_infos[key]
        if diff_project_id not in failed_diff_project_ids:
            new_task_info = (ids[0], ids[1], ids[2], ids[3])
            new_task_infos.append(new_task_info)

    with open("new_beijing.txt", "w") as fp2:
        for id in new_task_infos:
            fp2.write("%s,%s,%s,%s\n" % (id[0], id[1], id[2], id[3]))
