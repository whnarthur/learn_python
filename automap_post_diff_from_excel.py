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
    xlsx = xlrd.open_workbook('beijing.xlsx')
    print('All sheets: %s' % xlsx.sheet_names())
    sheet_num = len(xlsx.sheets())
    for sheet_index in range(sheet_num):
        sheet1 = xlsx.sheets()[sheet_index]  # 获得第1张sheet，索引从0开始
        sheet1_name = sheet1.name  # 获得名称
        sheet1_cols = sheet1.ncols  # 获得列数
        sheet1_nrows = sheet1.nrows  # 获得行数
        print('Sheet1 Name: %s\nSheet1 cols: %s\nSheet1 rows: %s' % (sheet1_name, sheet1_cols, sheet1_nrows))

        task_infos = []
        for i in range(sheet1_nrows):
            print("process %d" %i)
            if i == 0:
                continue
            auto_project_id = str(int(sheet1.row(i)[4].value))  # 查看第3行第4列数据
            human_task_id = str(int(sheet1.row(i)[6].value))  # 查看第3行第4列数据
            task_name = sheet1.row(i)[2].value
            print(
                'row: %d, auto_project_id: %s, human_task_id: %s, task_name:%s' % (i, auto_project_id, human_task_id, task_name))

            project_ids = auto_project_id
            task_ids = human_task_id
            name = sheet1_name
            #
            projects = project_ids.split(',')
            tasks = task_ids.split(',')
            full_fusions = get_full_fusions(projects)
            print(full_fusions)
            #
            diff_project_id = create_post_diff(tasks, full_fusions, "test_automap_{0}_{1}".format(name, time.time()))
            task_info = (task_name, projects[0], tasks[0], diff_project_id)
            task_infos.append(task_info)

        with open(sheet1_name + "_task_info.txt", "w") as fp:
            for id in task_infos:
                fp.write("%s,%s,%s,%s\n" % (id[0], id[1], id[2], id[3]))
