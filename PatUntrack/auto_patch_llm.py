# import os
# import random_patching.Config as cf
# import random_patching.code_commit_statistic_analysis as ccsa
#
# from tqdm import tqdm, trange
#
# os.environ["http_proxy"]="127.0.0.1:7890"
# os.environ["https_proxy"]="127.0.0.1:7890"
#
# import openai
# openai.api_key = cf.api_key
#
# # list models
# models = openai.Model.list()
#
# # print the first model's id
# # print(models.data[0].id)
#
#
# commit_sec_list, non_commit_sec_list, non_sec_list = ccsa.rev_back_dataset()
# for i in tqdm(range(len(commit_sec_list)), desc='Processing'):
#     item = commit_sec_list[i]
#     print("----- URL of IR:{} -----\n".format(item['Issue_Url']))
#     print(">> Issue Title: {}\n >> Issue Body: {}".format(item['Issue_Title'], item['Issue_Body']))
#     content = cf.content.format(5, item['Issue_Title'], item['Issue_Body'])
#
#     # create a chat completion
#     chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
#
#     # print the chat completion
#     print(">> Recommend Codes and Patches:\n {}".format(chat_completion.choices[0].message.content))


import os
import json
import random_patching.Config as cf
import ast

from tqdm import tqdm, trange

def predict_vcode_vpatch(j_test_data, j_dict_data):
    os.environ["http_proxy"]="127.0.0.1:7890"
    os.environ["https_proxy"]="127.0.0.1:7890"

    import openai
    openai.api_key = cf.api_key

    # list models
    models = openai.Model.list()

    # print the first model's id
    # print(models.data[0].id)
    # commit_sec_list, non_commit_sec_list, non_sec_list = ccsa.rev_back_dataset()

    match_total = 0
    acc = 0.0
    res_mismatch = []
    cal_total = 0

    loop_identify = tqdm(range(len(j_test_data)), desc='Processing')

    for i in loop_identify:
        item = j_test_data[i]
        if item["Security_Issue_Full"] == 0:
            continue
        cwe_truth = j_dict_data[item["CVE_ID"]]["CWE_ID"]
        # print("----- URL of IR:{} -----\n".format(item['Issue_Url']))
        # print(">> Issue Title: {}\n >> Issue Body: {}".format(item['Issue_Title'], item['Issue_Body']))
        content = cf.content_sec_issue_analysis.format(item['Issue_Title'], item['Issue_Body'])

        # create a chat completion
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])

        # print the chat completion
        res = chat_completion.choices[0].message.content
        # print(res)
        try:
            # response_dict = json.loads(res)
            response_result = ast.literal_eval(res)
            if response_result["Identification Result"] == "Yes" and response_result["CWE-ID"] == cwe_truth:
                match_total += 1
            else:
                mis_item = item
                mis_item["predicted_IR"] = response_result["Identification Result"]
                mis_item["predicted_cwe"] = response_result["CWE-ID"]
                mis_item["truth_cwe"] = cwe_truth
                res_mismatch.append(mis_item)
                with open("data/mismatch_newly.json", "w") as f_mismatch:
                    f_mismatch.write(json.dumps(res_mismatch, indent=4))
                    f_mismatch.close()
            cal_total += 1
            acc = match_total / cal_total
            loop_identify.set_postfix(Acc=acc)
        except:
            mis_item = item
            mis_item["predicted_IR"] = res
            mis_item["predicted_cwe"] = "Not Predicted"
            mis_item["truth_cwe"] = cwe_truth
            res_mismatch.append(mis_item)
            with open("data/mismatch_newly.json", "w") as f_mismatch:
                f_mismatch.write(json.dumps(res_mismatch, indent=4))
                f_mismatch.close()
            # print("Cannot transfer to json.")
            pass
        # print(">> Identification Results:\n {}".format(chat_completion.choices[0].message.content))