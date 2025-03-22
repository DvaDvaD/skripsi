api_key = "sk-proj-1guzJL6gGVe3L0ORzJV3T3BlbkFJ74d24GUbawXHkROCP22e" # Your ChatGPT API Key
path = "data/"
prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

compare:
e.g. compare: Issue Title (Multiple XSS in APITAG Gallery by Photocrati Version NUMBERTAG), and CVE (CVE-2015-9537)
Returns the comparison result of whether the issue report of such title is matched to the content of CVE-ID

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

issue_search:
e.g. issue_search: Issue Title (Multiple XSS in APITAG Gallery by Photocrati Version NUMBERTAG)
Returns the details of issue, including the analysis of codes and screenshots.

comment_search:
e.g. comment_search: Issue Title (Multiple XSS in APITAG Gallery by Photocrati Version NUMBERTAG)
Returns the details of issue comments, including the analysis of codes and screenshots.

Always compare the issue report with CVE-ID first the issue_search.

Example session:

Question: Is the following issue report matches the CVE?
Issue Title (Multiple XSS in APITAG Gallery by Photocrati Version NUMBERTAG)
Issue Body (Details Word Press Product Bugs Report Bug Name XSS APITAG Site Scripting) Software...)
Matched CVE (CVE-2015-9537)(The NextGEN Gallery plugin before 2.1.10 for WordPress has multiple XSS issues...)
Thought: I need to compare the "Multiple XSS in APITAG Gallery by Photocrati Version NUMBERTAG" with CVE-2015-9537
Action: compare: Can the Issue Report (Multiple XSS in APITAG Gallery by Photocrati Version NUMBERTAG, Details Word Press Product Bugs Report Bug Name XSS APITAG Site Scripting) Software...) matches the CVE (CVE-2015-9537, The NextGEN Gallery plugin before 2.1.10 for WordPress has multiple XSS issues...)?
PAUSE

You will be called again with this:

Observation: No, the issue report does not contain the vulnerability.
You then output:
Answer: The issue report need the {action name} to support the analysis.
"""

alpha = 0.3
root = 2
max_depth = 5

content = """
Please generate Top K (K value is {}) potential vulnerable code and patches for the following issue report (IR).
The following IR has vulnerability, and you must recommend code and patch for the IR"
If the IR lacks the details, please generate the most relevant code and patch, and do not leave it blank!
The detail of IR: \"Title of IR\": \"{}\"; \"Body of IR\": \"{}\".
Note that, the \"Title of IR\" may not correspond to the \"Body of IR\",
so title can only be used as reference, and you should mainly focus on the body.
The format of your response should be the JSON format, and the format of output is as follows:
* Generation 1: \"Vulnerable Code\": The generated vulnerable code; \"Patch\": The generated patch for the code.
* Generation 2: \"Vulnerable Code\": The generated vulnerable code; \"Patch\": The generated patch for the code.
...
* Generation K: \"Vulnerable Code\": The generated vulnerable code; \"Patch\": The generated patch for the code.
"""

content_sec_issue_analysis = """
Please identify whether this following issue report has the security issues, which need to be disclosed in CVE.
The detail of IR: \"Title of IR\": {}; \"Body of IR\": {}.
The format of your response should be the json format, and the components are as follows: \"Identification Result\": Yes or No, \"CWE-ID\": the predicted CWE-ID, \"Description\": A short description of why it relates/not-relates to security
"""