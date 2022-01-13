# -*- coding:utf-8 -*-

import re
import os
import time
import threading

SS = []
PASS11=0

def walkFile(file):
    path = []
    failr = []
    for root, dirs, files in os.walk(file):
        for f in files:
            p = os.path.join(root, f)
            path.append(p)
    for i in path:
        # print(i)
        if "test_result.xml" in i:
            failr.append(i)
    return len(failr), failr


def While_baogao(path):

    print(path)
    baogao = path.replace(r"tools", r"results", 1)
    len_failr, failr = walkFile(baogao)
    print(len_failr)
    while True:
        len_failr1, failr1 = walkFile(baogao)
        time.sleep(300)
        print(len_failr1)
        if len_failr1 != len_failr:
            retry_results=shuzu(failr1,failr)
            retry_results=retry_results[0]
            #retry_results=retry_results.replace(r"test_result_failures_suite.html", r"test_result.xml", 1)
            time.sleep(60)
            break
    return retry_results,len_failr1  #多出一个的报告


def terminal_PID():
    ss = []
    ii = "ps -U root -u root -N |grep tradefed"
    iii = os.popen(ii).read()
    results = re.findall("[0-9]{3,6}", iii)
    print("terminal_PID:", results)
    return results


def shuzu(a, b):
    PID_cloud = []
    for i in a:
        if i not in b:
            PID_cloud.append(i)

    return PID_cloud

#build_fingerprint="realme/RMX3370/RE5473:12/SKQ1.210216.001/R.202110251917:user/release-keys"
def panduan_PF(result,FP):
    with open(result, 'r', encoding='UTF-8') as f:
        strr = f.read(100000)
        results_FP = re.findall('command_line_args=".*?"', strr)
        if results_FP == []:
            return False
        # print(results_FP)
        uuuu = str(results_FP[0])
        print(uuuu)
        if FP in uuuu:
            print("报告一致")
            return True  # 一致 判断是否有这个设备
        else:
            print("报告bu一致")
            return False

#<Summary pass="0" failed="0" modules_done="0" modules_total="0" />
#a=报告出错  b=再retry  c=结束retry d=跑卡
def results_analysis(result,failed):
    global yes_retry
    yes_retry="b"
    with open(result, 'r', encoding='UTF-8') as f:
        strr = f.read(100000)
        uuuu = re.findall('pass=".*?" failed=".*?" modules_done=".*?" modules_total=".*?"', strr)
        uuuu=str(uuuu)
        uuuuo = re.findall('suite_variant=".*?"', strr)
        uuuuu = uuuuo[0]
        ee = uuuuu[15:-1]
        f.close()
        print(ee)
        Pass = re.findall('\d+', uuuu)
        print(Pass)
        if int(Pass[0]) == 0:
            yes_retry = "a"
            return yes_retry
        if int(Pass[3]) - int(Pass[2]) >= 8:
            yes_retry = "b"
            return yes_retry
        if int(Pass[1]) >= 1000 and ee=="CTS":
            yes_retry = "b"
            return yes_retry
        if int(Pass[1]) >= 250 and ee!="CTS":
            yes_retry = "b"
            return yes_retry
        if int(Pass[1]) >= failed:
            yes_retry = "b"
            return yes_retry
        else:
            yes_retry = "c"
            return yes_retry

def tradefed_find(rr):

    # print(rr)

    path = []
    failru = []
    for root, dirs, files in os.walk(rr):
        for f in files:
            p = os.path.join(root, f)
            path.append(p)
    for i in path:
        # print(i)

        if "-tradefed" in i and "jar" not in i:
            failru.append(i)
    return failru

def set_devices(shebo):
    shebei = []
    s2 = shebo.split()
    print(s2)
    for i in s2:
        if len(i) != 13 and len(i) != 2 and len(i) != 1:
            print(i)
            shebei.append(i)

    for l in shebei:
        os.system("adb -s %s reboot" % l)
    time.sleep(180)
    print("等待2分钟")
    for ll in shebei:
        os.system("adb -s %s shell wm dismiss-keyguard" % ll)
        os.system("adb -s %s shell svc wifi enable" % ll)

def rgj(resulrs_xml,rgj_path,sheb,failed,rr):
    print("日构建")
    rusult_path=resulrs_xml.replace('test_result.xml','')
    rgj_result_path = rgj_path.replace(r"tools", r"results", 1)
    os.system(f"cp -r {rusult_path} {rgj_result_path}")
    time.sleep(120)
    len_failr, failr = walkFile(rgj_result_path)
    rgj_chengxu=tradefed_find(rgj_path)
    rgj_chengxu=rgj_chengxu[0]
    rgj_base_path = os.path.basename(rgj_chengxu)
    rgj_bbase_path = "./" + rgj_base_path
    print(rgj_bbase_path)
    rgj_s=f"{rgj_bbase_path} run retry --retry {len_failr} {sheb}"
    os.system(f"cd {rgj_path} ; gnome-terminal -- {rgj_s}")
    rgj_retry_results, rgj_len_failr1=While_baogao(rgj_path)
    aa=results_analysis(rgj_retry_results,failed)
    rgj_result_path=rgj_retry_results.replace('test_result.xml','')
    result_path_s = rr.replace(r"tools", r"results", 1)
    os.system(f"cp -r {rgj_result_path} {result_path_s}")


def main():
    rr = os.getcwd()
    print(rr)
    chu=tradefed_find(rr)
    retry_xu=[]   #记录retry序号
    retry_shu = input("retry-序号:")
    retry_xu.append(int(retry_shu))
    chengx = chu[0]
    base_path = os.path.basename(chengx)
    bbase_path = "./" + base_path
    print(bbase_path)
    sheb = input("设备：")
    retry = "run retry --retry"
    frist=True
    FP =input("输入其中一个序列号：")
    failed=input("剩余fail：")
    failed=int(failed)
    len_result=None
    retry_shu = str(retry_shu)
    s = chengx + " " + retry + " " + str(retry_xu[-1]) + " " + sheb
    retry_shu = int(retry_shu)
    print(s)
    while True:
        PID_cloud = []
        if frist:
            while True:
                retry_resulrs,len_result=While_baogao(rr)
                retry_shu=retry_shu+1
                if panduan_PF(retry_resulrs,FP):#####
                    retry_shu = retry_shu - 1
                    break
        small = terminal_PID()
        print("开始terminal：", small)
        if frist:
            s = chengx + " " + retry + " " + str(retry_xu[0]) + " " + sheb
        else:
            s = chengx + " " + retry + " " + str(retry_xu[-1]) + " " + sheb
        print(s)
        retry_xu.append(len_result)
        print("retry_序号：",retry_xu)
        #重启，打开WiFi
        set_devices(sheb)
       # rgj()
        os.system("gnome-terminal -- %s" % s)
        time.sleep(20)
        big = terminal_PID()
        print("新增terminal:", big)
        cloud_PID = shuzu(big, small)
        print("需要kill terminal",cloud_PID)
        while True:
            retry_resulrs,len_result=While_baogao(rr)
            retry_shu = retry_shu + 1
            if panduan_PF(retry_resulrs,FP):
                retry_shu = retry_shu - 1
                break
        analysis=results_analysis(retry_resulrs,failed)
        print(analysis)
        if analysis=="a":  #报告出错后
            retry_xu.remove(retry_xu[-1])
        if analysis=="b":  #报告没出错
            pass  #正常数
        if analysis =="c":
            print("end")
            break
        time.sleep(30)
        print(cloud_PID[0])
        os.system("kill %s" % cloud_PID[0])
        print("kill terminal",cloud_PID[0])
        retry_shu = retry_shu + 1
        frist = False


if __name__ == '__main__':

    main()