import random_patching.code_commit_statistic_analysis as ccsa
import random_patching.auto_patch_llm as patchllm
from random_patching.data_loader import JLoader


# commit_sec_list, non_commit_sec_list, non_sec_list = ccsa.rev_back_dataset()


jld = JLoader("test_project.json")
j_test_data = jld.load_dataset()
j_dict = JLoader("CVE_dict.json")
j_dict_data = j_dict.load_dataset()

patchllm.predict_vcode_vpatch(j_test_data, j_dict_data)