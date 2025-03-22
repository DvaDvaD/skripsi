import json
from src_IR_prediction import Config as cf

class JLoader:
    def __init__(self, filename):
        self.fpath = cf.path + filename
        return

    def load_dataset(self):
        with open(self.fpath) as fopen:
            # line = fopen.readline()
            f_input = json.load(fopen)
        fopen.close()
        # for f_item in f_input:
        #     print(f_item)
        return f_input


if __name__ == "__main__":
    jld = JLoader("test_project.json")
    jld.load_dataset()