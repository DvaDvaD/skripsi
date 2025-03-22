import csv
import pandas as pd
import numpy as np


def calculate_time_of_patches():
    csv_data = pd.read_csv('data/patch_time_gap/time_lag_res.csv')
    csv_df = pd.DataFrame(csv_data)
    type_list = list(csv_df['Type'])
    time_gap_list = list(csv_df['Time_Lag'])
    time_patch = [time_gap_each for type_each, time_gap_each in zip(type_list, time_gap_list) if
                  type_each == 'Time_Lag of PatchIR Disclosure']
    time_unpatch = [time_gap_each for type_each, time_gap_each in zip(type_list, time_gap_list) if
                    type_each == 'Time_Lag of UnpatchIR Disclosure']
    time_gap_plot_list = [time_step for time_step in range(0, 1000, 50)]
    ratio_gap_plot_list_patch, ratio_gap_plot_list_unpatch = [], []
    for time_step in time_gap_plot_list:
        num_patch_time = [time_gap_each for time_gap_each in time_patch if time_gap_each <= time_step]
        num_unpatch_time = [time_gap_each for time_gap_each in time_unpatch if time_gap_each <= time_step]
        ratio_gap_plot_list_patch.append(len(num_patch_time) / len(time_patch))
        ratio_gap_plot_list_unpatch.append(len(num_unpatch_time) / len(time_unpatch))
    dict_res = {"Time Gap": time_gap_plot_list, "Ratio_of_Patched": ratio_gap_plot_list_patch,
                "Ratio_of_Unpatched": ratio_gap_plot_list_unpatch}
    df_res = pd.DataFrame(dict_res)
    df_res.to_csv('data/patch_time_gap/patch_or_unpatch_time_lag.csv', index=False)
    return


if __name__ == "__main__":
    calculate_time_of_patches()
