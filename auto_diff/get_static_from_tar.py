# coding:utf-8

import sys
import os
import json
import requests
import time
import tarfile


if __name__ == '__main__':
    input = str(sys.argv[1])
    new_all_diff_ids = []
    with open(input) as fp:
        for line in fp.readlines():
            line = line.strip()
            if len(line) <= 0: continue
            # print(line)
            line = line.split(',')
            name = line[0]
            project_ids = line[1]
            tasks = line[2]
            diff_project_id = line[3]
            diff_task_id = line[4]
            #
            cmd = "cd ~"
            os.system(cmd)
            cmd = "/opt/hadoop-3.1.2/bin/hdfs dfs -get /tmp/fusion_diff/%s.tar" % diff_task_id
            os.system(cmd)

            # tar_file_path = "%s/%s.tar" % (work_dir, diff_task_id)
            tar_file_path = "/home/kddev/%s.tar" % (diff_task_id)
            with tarfile.open(tar_file_path, "r") as file:
                for i in file.getmembers():
                    if i.name == "diff_stat.csv":
                        f = file.extractfile(i.name)
                        content = f.read()
                        # print("$$$$$$"+diff_project_id)
                        with open(diff_project_id+".csv", "wb") as fp_w:
                            # print(content)
                            fp_w.write(content)



