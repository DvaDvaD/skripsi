import os
import random_patching.Config as cf
os.environ["http_proxy"]="127.0.0.1:7890"
os.environ["https_proxy"]="127.0.0.1:7890"

import openai
openai.api_key = cf.api_key

# list models
models = openai.Model.list()

# print the first model's id
# print(models.data[0].id)

content = "Find the most frequently-used library in {}".format("Java")

# create a chat completion
chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])

# print the chat completion
print(chat_completion.choices[0].message.content)