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
    except Exception as e:
        print(e)
    return rslt.json()


if __name__ == '__main__':
    project_ids = sys.argv[1]
    task_ids = sys.argv[2]
    name = sys.argv[3]
    #
    print("project_ids=", project_ids)
    print("task_ids=", task_ids)
    print("name=", name)
    #
    projects = project_ids.split(',')
    tasks = task_ids.split(',')
    full_fusions = get_full_fusions(projects)
    print(full_fusions)
    #
    create_post_diff(tasks, full_fusions, "test_automap_{0}_{1}".format(name, time.time()))
