import os
import random_patching.Config as cf
import random_patching.code_commit_statistic_analysis as ccsa
import json

from tqdm import tqdm, trange

os.environ["http_proxy"]="127.0.0.1:7890"
os.environ["https_proxy"]="127.0.0.1:7890"

import openai
openai.api_key = cf.api_key

# list models
models = openai.Model.list()

# print the first model's id
# print(models.data[0].id)


commit_sec_list, non_commit_sec_list, non_sec_list = ccsa.rev_back_dataset()
count_pos, count_neg = 0, 0
pos_non_sec_list, neg_non_sec_list = [], []
loop = tqdm(range(len(non_sec_list)), desc='Processing')
for i in loop:
    item = non_sec_list[i]
    # print("----- URL of IR:{} -----\n".format(item['Issue_Url']))
    # print(">> Issue Title: {}\n >> Issue Body: {}".format(item['Issue_Title'], item['Issue_Body']))
    content = cf.content_sec_issue_analysis.format(5, item['Issue_Title'], item['Issue_Body'])

    # create a chat completion
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
    resp_content = chat_completion.choices[0].message.content

    # print the chat completion
    if "Yes" in resp_content:
        count_pos += 1
        pos_ir_dict = {"ID": count_pos, "IR": item['Issue_Url'],
                       "IR_Create_Time": item["Issue_Created_At"], "Desc": resp_content}
        pos_non_sec_list.append(pos_ir_dict)
    else:
        count_neg += 1
        neg_ir_dict = {"ID": count_neg, "IR": item['Issue_Url'],
                       "IR_Create_Time": item["Issue_Created_At"], "Desc": resp_content}
        neg_non_sec_list.append(neg_ir_dict)
    sec_ratio = count_pos/(count_pos + count_neg)
    loop.set_postfix(url=item['Issue_Url'], create_at=item["Issue_Created_At"],
                     pos_issue=count_pos, neg_issue=count_neg, sec_ratio=sec_ratio)
    with open("data/non_cve_sec_issues/pos_non_sec.json", 'w') as f_sec:
        f_sec.write(json.dumps(pos_non_sec_list))
        f_sec.close()
    with open("data/non_cve_sec_issues/neg_non_sec.json", 'w') as f_neg:
        f_neg.write(json.dumps(neg_non_sec_list))
        f_neg.close()