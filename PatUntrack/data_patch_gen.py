import json
import csv

with open("data/patch_db.json", "r", encoding="utf-8") as read_content:
    patch_list = json.load(read_content)
    read_content.close()

with open("data/test_project.json", encoding="utf-8") as test_content:
    test_list = json.load(test_content)
    test_content.close()

with open("data/train_project.json", "r", encoding="utf-8") as train_content:
    train_list = json.load(train_content)
    train_content.close()

patch_url_list = ["https://github.com/{}/{}".format(item_patch_url["owner"], item_patch_url["repo"]) for item_patch_url in patch_list]
train_url_list = [item_train_url["Issue_Url"] for item_train_url in train_list]
test_url_list = [item_test_url["Issue_Url"] for item_test_url in test_list]

repo_url_list = [item_repo[:item_repo.index("issues")-1] for item_repo in train_url_list] + \
            [item_repo[:item_repo.index("issues")-1] for item_repo in test_url_list]
# print(repo_url_list)

set_repo = set(repo_url_list)
set_patch_repo = set(patch_url_list)
intsec = set_repo.intersection(set_patch_repo)

common_elements = list(intsec)
print(len(common_elements))

# with open("data/test_project.csv", "w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(["URL", "ISSUE_TITLE", "ISSUE_BODY"])
    # print(content_list)