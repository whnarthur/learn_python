import subprocess
import sys

if __name__ == '__main__':
    pipe = subprocess.Popen("cat /Users/weihainan/Documents/test.json", stdout=subprocess.PIPE)
    for line in iter(pipe.stdout.readline, ''):
        print (line.rstrip())