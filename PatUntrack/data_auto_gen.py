import pandas as pd
import numpy as np
import random
csv_file = pd.read_csv("data/data_am.csv")
df = pd.DataFrame(csv_file)
RNG = 2

def random_change(data_change):
    return random.uniform(data_change-RNG,data_change+RNG)


if __name__=="__main__":
    l_df = df.values.tolist()
    # for index_row in range(len(l_df)):
    #     for index_elem in range(len(l_df[index_row])):

    elements = [random_change(elem) for row in l_df for elem in row]
    elements_change = np.array(elements).reshape(len(l_df),len(l_df[0])).tolist()
    # print(elements)

    df_change = pd.DataFrame(elements_change)
    df_change.to_csv("data/data_change_am.csv")