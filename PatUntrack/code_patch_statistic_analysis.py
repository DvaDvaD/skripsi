import json
import csv

'''
* Extract the CVE lists with GitHub issues.
'''


def ret_list_commit(CVE_link):
    with open(CVE_link, "r", encoding="utf-8") as read_content:
        cve_disclosure_list = json.load(read_content)
        read_content.close()

    issue_cve_github = []

    for item in cve_disclosure_list:
        ref_str = cve_disclosure_list[item]["References_String"]
        if (ref_str is not None) and ("https://github.com/" in ref_str) and ("/issues/" in ref_str):
            url_link_list = ref_str.split("->")
            # issue_link_list = [item for item in url_link_list if ("https://github.com/" in item)]
            # commit_link_list = [item for item in url_link_list if ("https://github.com/" in item)]
            # cve_disclosure_list[item]["References_String"] = ref_str.split("->")
            issue_cve_github.append(cve_disclosure_list[item])
    # print(issue_cve_github)
    cve_with_commit = [item for item in issue_cve_github if ("commit" in item["References_String"])]
    cve_with_patch = [item for item in issue_cve_github if ("TPatch" in item["References_String"])]
    cve_wo_patch = [item for item in issue_cve_github if ("TPatch" not in item["References_String"])]
    cve_with_issue_wo_commit = [item for item in issue_cve_github if ("commit" not in item["References_String"]) and (
                "TPatch" not in item["References_String"])]
    print("GitHub Issues: {}, Issue with Commits: {}, Issue with Patch: {}".
          format(len(issue_cve_github), len(cve_with_commit), len(cve_with_patch)))

    ref_list_of_issues = [("->".join([url_link for url_link in item["References_String"].split("->") if
                                      ("issues" in url_link)]),
                           "->".join([url_link for url_link in item["References_String"].split("->") if
                                      ("commit" in url_link)])) for item in cve_with_commit]
    # ref_list_of_commits = [[url_link for url_link in item["References_String"].split("->") if
    #                     ("commit" in url_link)] for item in cve_with_commit]
    csv_list_commit = [[each_key for each_key in cve_with_commit[0].keys()]] + \
                      [[item[each_key] for each_key in item.keys()] for item in cve_with_commit]

    # Analyze the exploit of such vulnerability
    cve_with_patch_exploit = [item for item in cve_with_patch if ("TExploit" in item["References_String"])]
    cve_wo_patch_exploit = [item for item in cve_wo_patch if ("TExploit" in item["References_String"])]

    return cve_with_patch, cve_wo_patch, cve_disclosure_list


'''
* Store the CVE lists with GitHub issues to *.csv file.
'''
if __name__ == "__main__":
    cve_with_commit, cve_with_issue_wo_commit, cve_disclosure_list = ret_list_commit("data/CVE_dict.json")
    # print(len(cve_with_commit), len(cve_with_issue_wo_commit))
    # with open("data/cve_with_commit_patch/issue_cve_with_commit.csv", "w", newline="") as write_content:
    #     csv_writer = csv.writer(write_content)
    #     csv_writer.writerows(csv_list_commit)
    #     write_content.close()
