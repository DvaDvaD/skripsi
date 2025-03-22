import json
import csv
import random_patching.code_patch_statistic_analysis as cpanalysis
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm, trange
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

os.environ["http_proxy"] = "127.0.0.1:7890"
os.environ["https_proxy"] = "127.0.0.1:7890"

'''
* Compare the submit time of github issues
'''
cve_with_patch, cve_with_issue_wo_patch, cve_disclosure_list = cpanalysis.ret_list_commit("data/CVE_dict.json")
# ref_list_of_issues = [("->".join([url_link for url_link in item["References_String"].split("->") if
#                                   ("issues" in url_link)]),
#                        "->".join([url_link for url_link in item["References_String"].split("->") if
#                                   ("commit" in url_link)])) for item in cve_with_commit]

with open("data/test_project.json", encoding="utf-8") as test_content:
    test_list = json.load(test_content)
    test_sec_list = [item for item in test_list if item['Security_Issue_Full'] == 1]
    test_non_sec_list = [item for item in test_list if item['Security_Issue_Full'] == 0]
    test_content.close()
with open("data/train_project.json", "r", encoding="utf-8") as train_content:
    train_list = json.load(train_content)
    train_sec_list = [item for item in train_list if item['Security_Issue_Full'] == 1]
    train_non_sec_list = [item for item in train_list if item['Security_Issue_Full'] == 0]
    train_content.close()

'''
* Extract commit url from Ref-Strings
'''


def commit_url_extract(ref_str):
    ref_str_list = ref_str.split("->")
    commit_message_url = [commit_str for commit_str in ref_str_list if "TPatch" in commit_str]
    return commit_message_url


'''
* Track back the cve-ids with its IR description
'''


def rev_back_dataset():
    sec_list = test_sec_list + train_sec_list
    non_sec_list = test_non_sec_list + train_non_sec_list
    cve_patch_ids, cve_wo_patch_ids = [item['CVE_ID'] for item in cve_with_patch], \
                                      [item['CVE_ID'] for item in cve_with_issue_wo_patch]
    cve_dataset_ids = [item['CVE_ID'] for item in sec_list]

    # Sec&Ins IR items extraction.
    non_patch_sec_list = [non_commit_item for non_commit_item in sec_list if
                          non_commit_item['CVE_ID'] in cve_wo_patch_ids]
    commit_patch_list = [sec_commit_item for sec_commit_item in sec_list if sec_commit_item['CVE_ID'] in cve_patch_ids]

    # Commit extraction in commit_sec_list.
    for i in range(len(commit_patch_list)):
        commit_patch_list[i]['Commit_Url'] = commit_url_extract(
            cve_disclosure_list[commit_patch_list[i]['CVE_ID']]['References_String'])

    print("IR with Patch: {}, IR w/o Patch: {}".format(len(commit_patch_list), len(non_patch_sec_list)))

    non_patch_time_lag_list, _ = time_diff_calculate(non_patch_sec_list, patch=0)
    patch_time_lag_list, time_patch_list_ret = time_diff_calculate(commit_patch_list, patch=1)
    '''
    * patch_time_lag_list: Time Publish - Time IR Created (IR has patch)
    * time_patch_list_ret: Time Patch - Time IR Created
    * non_patch_time_lag_list: Time Publish - Time IR Created (IR has no patch)
    '''
    print("Average Time Lags: Patched {} Days; Non-Patched {} Days; Patch After {} Days".format(
        sum(patch_time_lag_list) / len(patch_time_lag_list),
        sum(non_patch_time_lag_list) / len(non_patch_time_lag_list),
        sum(time_patch_list_ret) / len(time_patch_list_ret)))

    time_store_res = {}
    time_store_res['Type'] = ['Time_Lag of PatchIR Disclosure'] * len(patch_time_lag_list) + \
                             ['Time_Lag of PatchIR Patching'] * len(time_patch_list_ret) + \
                             ['Time_Lag of UnpatchIR Disclosure'] * len(non_patch_time_lag_list)
    time_store_res['Time_Lag'] = patch_time_lag_list + time_patch_list_ret + non_patch_time_lag_list
    df_time_store_res = pd.DataFrame(time_store_res)
    df_time_store_res.to_csv('data/patch_time_gap/time_lag_res.csv', index=False)
    plt.figure(dpi=120)
    sns.violinplot(df_time_store_res, x='Type', y='Time_Lag')
    plt.show()
    # for commit_patch_item in commit_patch_list:
    #     date_publish = datetime.strptime(commit_patch_item["Published_Date"], "%Y-%m-%dT%H:%MZ")
    #     date_commit = datetime.strptime(commit_patch_item["Issue_Created_At"], "%Y-%m-%dT%H:%M:%SZ")
    #     delta_lag_publish = date_publish - date_commit
    #     hours = delta_lag_publish.total_seconds() / 3600

    print("----------Process dataset finished.----------")
    return commit_patch_list, non_patch_sec_list, non_sec_list


'''
time_diff_list_ret: Time Publish - Time IR Created
time_patch_list_ret: Time Patch - Time IR Created
'''
def time_diff_calculate(item_list, patch=0):
    time_diff_list_ret = []
    time_patch_list_ret = []
    loop = tqdm(range(len(item_list)), desc='Processing')
    for i in loop:
        commit_patch_item = item_list[i]
        date_publish = datetime.strptime(commit_patch_item["Published_Date"], "%Y-%m-%dT%H:%MZ")
        date_commit = datetime.strptime(commit_patch_item["Issue_Created_At"], "%Y-%m-%dT%H:%M:%SZ")
        delta_lag_publish = date_publish - date_commit
        hours = delta_lag_publish.total_seconds() / 86400
        if patch:
            patch_url_github = [patch_item for patch_item in commit_patch_item['Commit_Url'] if 'github' in patch_item]
            if patch_url_github:
                time_element_list = [find_time_element(item_patch_url, date_commit) for item_patch_url in patch_url_github]
                if len(time_element_list) == 1 and time_element_list[0] == 0.0:
                    continue
                time_element_list += [0.0]
                time_patch_list_ret.append(max(time_element_list))
                time_diff_list_ret.append(hours)
        else:
            time_diff_list_ret.append(hours)
        # time_diff_list_ret.append(hours)
    return time_diff_list_ret, time_patch_list_ret


def find_time_element(item_patch_url, date_commit):
    delta_hours_patch_publish = 0
    url_patch = item_patch_url[:item_patch_url.index("~~TPatch")]
    r = requests.get(url_patch)
    soup = BeautifulSoup(r.text, "html.parser")
    time_element = soup.find("relative-time", {"class": "no-wrap"})
    if time_element:
        date_patch = datetime.strptime(time_element.attrs['datetime'], "%Y-%m-%dT%H:%M:%SZ")
        delta_hours_patch_publish = (date_patch - date_commit).total_seconds() / 86400
    return delta_hours_patch_publish


def time_res_plot():
    time_gaps, time_lags_plot = {"Type": [], "Time_Lag": []}, {}
    with open("data/patch_time_gap/patch_time_lags.txt", 'r') as patch_read:
        data = patch_read.readlines()
        patch_read.close()
    ir_created_disclosure = data[0][data[0].index("[") + 1:data[0].index("]")].split(', ')
    ir_patched_disclosure = data[1][data[1].index("[") + 1:data[1].index("]")].split(', ')

    time_gaps["Type"] += ['Time_Lag of Patched IR'] * len(ir_created_disclosure)
    time_gaps["Time_Lag"] += [float(item) for item in ir_created_disclosure]
    time_gaps["Type"] += ['Time_Lag after IR Patched'] * len(ir_patched_disclosure)
    time_gaps["Time_Lag"] += [float(item) for item in ir_patched_disclosure]

    time_lags_plot['Time_Lag of Patched IR'] = ir_created_disclosure[:700]
    time_lags_plot['Time_Lag after IR Patched'] = ir_patched_disclosure[:700]

    # time_gaps['Time_Lag of Patched IR'], time_gaps[
    #     'Time_Lag after IR Patched'] = ir_created_disclosure, ir_patched_disclosure
    with open("data/patch_time_gap/non_patch_time_lags.txt", 'r') as patch_read:
        data_unpatched = patch_read.readlines()
        patch_read.close()
    ir_unpatched_disclosure = data_unpatched[0][data_unpatched[0].index("[") + 1:data_unpatched[0].index("]")].split(', ')
    time_gaps["Type"] += ['Time_Lag of Unpatched IR'] * len(ir_unpatched_disclosure)
    time_gaps["Time_Lag"] += [float(item) for item in ir_unpatched_disclosure]

    time_lags_plot['Time_Lag of Unpatched IR'] = ir_unpatched_disclosure[:700]
    df_patch = pd.DataFrame(time_gaps)
    df_plot_patch = pd.DataFrame(time_lags_plot)
    # df_patch.to_csv('data/patch_time_gap/patch_lag.csv', index=False)

    plt.figure(dpi=120)
    sns.violinplot(df_patch, x='Type', y='Time_Lag')
    plt.show()
    return


if __name__ == "__main__":
    rev_back_dataset()
    # time_res_plot()

# print(ref_list_of_issues)
