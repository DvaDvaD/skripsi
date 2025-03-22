# PatUntrack

This is the repository for PatUntrack: Automated Generating Patch Examples for Issue
Reports without Tracked Insecure Code (ASE'24)

## 1. Abstract

Security patches are essential for enhancing the stability and robustness of projects in the open-source software community. 
While vulnerabilities are officially expected to be patched before being disclosed, patching vulnerabilities is complicated and remains a struggle for many organizations. 
To patch vulnerabilities, security practitioners typically track vulnerable issue reports (IRs), and analyze their relevant insecure code to generate potential patches. 
However, the relevant insecure code may not be explicitly specified and practitioners cannot track the insecure code in the repositories, thus limiting their ability to generate patches. 
In such cases, providing examples of insecure code and the corresponding patches would benefit the security developers to better locate and resolve the actual insecure code. 
In this paper, we propose PatUntrack, an automated approach to generating patch examples from IRs without tracked insecure code. PatUntrack utilizes auto-prompting to optimize the Large Language Model (LLM) to make it applicable for analyzing the vulnerabilities described in IRs and generating appropriate patch examples. 
To evaluate the performance of PatUntrack, we conducted experiments on 5,465 vulnerable IRs. The experimental results show that PatUntrack can obtain the highest performance and improve the traditional LLM baselines by +17.7% (MatchFix) and +14.6% (Fix@10) on average in patch example generation. 
Our human evaluation indicates that developers can benefit from these examples for patching the vulnerabilities.

## 2. Prompts of PatUntrack
The prompts in the PatUntrack control the generation of insecure code and patch examples from the IRs.
Note that, the focus list is the essential information, and we will maintain a directory in the [prompt/focus_list](./prompt/focus_list) that store all the information in the focuses of prompt.
All the tasks will refer to the focus list to enhance their performances.

### 2.1 Prompts for Generating Complete VTP Description

In this section, we illustrate the initial prompt for generating VTP descriptions in the PatUntrack.

**P_extract: Pre-defined Prompt for Extracting the VTP Description**


> We define the structure of the VTP description for triggering the vulnerabilities, which
is a graph with operations and transitions:
> 
> * The definition of operations and transitions in the VTP description.
> 
> Please note that each Vul_Type has a CWE type and error type. Different CWE and
error types have different Focus (f) on extracting VTP description.
> * The definition of CWE and error types.
> * Focus List: <Vul_Type_1,f_1>,...,<Vul_Type_n,f_n>
> 
> The input IR is {Title, Body}, where Title is the summarization of vulnerability, and
Body incorporates the content of the vulnerability. Please generate the VTP description
based on the previous definition. 
> 
> You can first predict the vulnerability types based on the CWE and error types, 
> then refer to the Focus List to retrieve the f_i for help.

**P_complete: Pre-defined Prompt for Completing the VTP Description**


> We define the structure of the VTP description for triggering the vulnerabilities, which
is a graph with operations and transitions:
> 
> * The definition of operations and transitions in the VTP description.
> 
> Please note that each Vul_Type has a CWE type and error type. Different CWE and
error types have different Focus (f) on extracting VTP description.
> * The definition of CWE and error types.
> * Focus List: <Vul_Type_1,f_1>,...,<Vul_Type_n,f_n>
> 
> The input VTP description is {JSON-formatted VTP Description}. 
> Please determine whether this VTP description is complete based on the previous definition.
> If the VTP description is not complete, you can generate the missing nodes and edges based on the Focus List.
> 
> The inputted IR is{Title, Body}. After you generate the complete VTP description, you can update the content of IR.
> 
> Based on the predicted vulnerability type {CWE and Vul_Type}, 
> you can refer to the Focus List to retrieve the f_i for help.

### 2.2 Prompts for Correcting Hallucinatory VTP Description

In this section, we illustrate the initial prompt for correcting hallucinatory VTP descriptions in the PatUntrack.
The control of the traversing is in the algorithm. 
For each _OpItem_, we find it connected nodes _OpConn_ and the historical paths.
The path is _HistoricalPath: (Op_1,...,OpItem)_

**P_halDetect: Pre-defined Prompt for Detecting the LLM Hallucination**

> We define the structure of the VTP description for triggering the vulnerabilities, which
is a graph with operations and transitions:
> 
> * The definition of operations and transitions in the VTP description.
> 
> Please note that each Vul_Type has a CWE type and error type. Different CWE and
error types have different Focus (f) on extracting VTP description.
> * The definition of CWE and error types.
> * Focus List: <Vul_Type_1,f_1>,...,<Vul_Type_n,f_n>
> 
> The current node of VTP Description is shown as follows, and this VTP is completed. 
> * Current operation node: {Content of _OpItem_}.
> * The connected operation nodes: {Contents of All _OpConn_}.
> * The historical information of transitions: {JSON-formatted _HistoricalPath_}
> 
> In this task, please correct the hallucinatory in the VTP description with the following two steps.
> 
> STEP-1: You only need to generate the MySQL queries, and wait for the response. 
> The query items are golden knowledge, and we give some examples for the query.
> * Provide some SQL query examples for the golden knowledge retrieval, 
> such as "select * from DB where DB.detail like 'XSS attacks'".
> 
> STEP-2: Based on the current operation node, connected operation nodes, and historical information,
> please compare them with the {Golden Knowledge}, and report whether this node contains the hallucination.
> You just need to tell me which node and edge may contain hallucinations in JSON format.
> * Provide an example list of nodes/edges of hallucination, 
> such as {Nodes: [_OpItem_,_OpConn_1_,_OpConn_3_], Edges: [_OpItem_->_OpConn_1_,_OpItem_->_OpConn_3_]}.
> 
> Based on the predicted vulnerability type {CWE and Vul_Type}, 
> you can refer to the Focus List to retrieve the f_i for help.


Note that, in this prompt, we utilize one prompt to incorporate the two steps: query generation and hallucination detection.
In practical usage, these prompt may separately conduct these two steps.
When we receive the golden knowledge of STEP-1, we will use it in the STEP-2.

**P_halCorrect: Pre-defined Prompt for Correcting the LLM Hallucination**

> We define the structure of the VTP description for triggering the vulnerabilities, which
is a graph with operations and transitions:
> 
> * The definition of operations and transitions in the VTP description.
> 
> Please note that each Vul_Type has a CWE type and error type. Different CWE and
error types have different Focus (f) on extracting VTP description.
> * The definition of CWE and error types.
> * Focus List: <Vul_Type_1,f_1>,...,<Vul_Type_n,f_n>
> 
> The input is the {Original Nodes and Edges}, {Hallucinatory Nodes and Edges} that may contain the LLM hallucination, 
> together with the {Golden Knowledge}.
> You should tell me how to correct the hallucination, and just output the nodes and edges after you correct.
> The output will be the JSON format, and incorporates a field with description of why you correct it into this output.
> 
> * Provide an example outputted nodes and edges after hallucination correction.
> 
> Based on the predicted vulnerability type {CWE and Vul_Type}, 
> you can refer to the Focus List to retrieve the f_i for help.

### 2.3 Prompts for Generating Insecure Code & Patch Example

In this section, we illustrate the initial prompt for generating insecure code & patch examples.


**P_typePredict: Pre-defined Prompt for Predicting Patch Types**

> We define the structure of the VTP description for triggering the vulnerabilities, which
is a graph with operations and transitions:
> 
> * The definition of operations and transitions in the VTP description.
> 
> Please note that each Vul_Type has a CWE type and error type. Different CWE and
error types have different Focus (f) on extracting VTP description.
> * The definition of CWE and error types.
> * Focus List: <Vul_Type_1,f_1>,...,<Vul_Type_n,f_n>
>
> The input is the {JSON-Formatted VTP Description with Corrected LLM Hallucinations}.
> Please predict which patch type of this VTP description will be used.
> * The definition of patch types <Pat_Type_1,...,Pat_Type_n>
> 
> Based on the predicted vulnerability type {CWE and Vul_Type}, 
> you can refer to the Focus List to retrieve the f_i for help.

Note that, the information in focus list f_i will incorporate the historical frequency of vulnerability types to the patch type.
This is controlled by our code and algorithm.

**P_generate: Pre-defined Prompt for Jointly Generating Insecure Code & Patch Examples**

> We define the structure of the VTP description for triggering the vulnerabilities, which
is a graph with operations and transitions:
> 
> * The definition of operations and transitions in the VTP description.
> 
> Please note that each Vul_Type has a CWE type and error type. Different CWE and
error types have different Focus (f) on extracting VTP description.
> * The definition of CWE and error types.
> * Focus List: <Vul_Type_1,f_1>,...,<Vul_Type_n,f_n>
>
> The input is the {JSON-Formatted VTP Description with Corrected LLM Hallucinations},
> and the predicted patch types is {Patch Type}.
> Please generate {K} the potential insecure code and security patch example based on these inputs.
> The format of output will be the JSON-based lists for the code pairs as follows:
> * Provide examples for the generated code pairs, such as
> {CodePair_1: {InsCode: 'InsCodeDetail', PatCode: 'PatCodeDetail'},...,CodePair_K: {InsCode: 'InsCodeDetail', PatCode: 'PatCodeDetail'}}
> 
> Based on the predicted vulnerability type {CWE and Vul_Type}, 
> you can refer to the Focus List to retrieve the f_i for help.


## 3. Auto-Prompting

In the auto-prompting step, we conduct 20 iterations to tune the Focus List in these prompts.
The prompt analyze the examples by adding, modifying, and deleting the original prompts.

> We will auto-prompt the Focus List in the prompt {Inputted Prompt} with the sample {Inputted Item}.
> 
> The three methods for auto-prompting are Inserting, Modifying, and Deleting, which are defined as follows:
> * Inserting: You can insert this sample to the prompt's focus list. The inserted information is how this sample will affect the {Task}.
> * Modifying: The sample is already used in the prompt, and you can modify the content of focus based on the new analysis.
> * Deleting: You can delete this sample from the focus list, which might be redundant.
> 
> Based on the previous three prompts, please re-conduct the prediction with the three new prompts.

Note that, the score function F_s(x,y) is conducted in the source code, and we choose the best prompt after the auto-prompting.
If all the scores are below 0 (i.e., F_s(x,y)<0), we will choose the original prompt as the updated prompt.

## 4. Setup Instructions

The following instructions can help you utilize the artifacts:

### 4.1 Prompts and Dataset

We have open-sourced the Prompts, Focus-Lists, and Datasets for the PatUntrack, and you can directly generate the insecure code\&patch examples with them. Note that, the dataset is too large, and you have to download the dataset in the external links in [data/README.md](data/README.md).


### 4.2 Necessary Python Versions and Packages

This artifact requires the Python with Version>3.8, so you need to update your Python version if it is less than 3.8. We recommend you create a new environment for the _Python 3.8_ because there might be compatibility issues between different versions.
Moreover, you need to know how to install the Python Packages with:

`pip install package-name==package-version`

If you use Anaconda to deploy your Python projects, you can utilize the following command to install the corresponding packages.

`conda install package-name==package-version`

Some other packages are _numpy_, _openai_, _torch_, and _transformers_, etc., and we have listed the packages in the \texttt{requirements.txt}.
You can install the packages with:

`pip install -r requirements.txt`

### 4.3 Setup of OpenAI API-Key and Fine-Tuning

After downloading the artifact on your own PC, you can execute the generation of insecure code\&patch examples with the following command:

`python code_patch_pipeline.py`

* **Setup of OpenAI:** Since PatUntrack is conducted on the LLM, e.g., GPT-3 and ChatGPT, you need to call the OpenAI APIs to enable the usage of such LLM. We have not removed our original _API-Key_ in the file [Config.py](./Config.py) to ensure that the artifact can be executed normally. However, this key might not be permanent, so we recommend you apply for your own keys through the [OpenAI Platform](https://platform.openai.com/account/api-keys) and replace it in the Config.py. 
* **Setup of PyTorch:** Since PatUntrack is also conducted on CodeT5, you also need to ensure that your system contains the basic packages for fine-tuning, e.g., _PyTorch_ and _Transformer_. These packages are incorporated in the [requirements.txt](./requirements.txt), and you can directly install them. We utilize Tsinghua's _OpenPrompt_ library to train the T5 model and the configuration is listed in the file [t5Config.py](./t5Config.py). You need to download the model in the link within [data/README.md](data/README.md), then use this model to generate the insecure code\&patch examples.


### 4.4 Setup for Auto-Prompting

In the directory [prompt/focus\_list](prompt/focus_list), we have listed all the Focus-Lists after the auto-prompting, and you can directly utilize them to generate insecure code\&patch examples.
If you want to know how the auto-prompting is conducted, you can execute the Python file with the following command. 
This file indicates how the PatUntrack is optimized from VTP generation to the patch example generation.

`python auto-prompting.py`
