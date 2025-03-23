from gpt4all import GPT4All
import json
import os
import re




NUM_VALUES = 20
SYSTEM_PROMPT = "You are an AI assistant for REST API testing. The user will ask for parameter values to assign to HTTP parameters for requests to an API. Please generate valid, plausible, and diverse values, that are in the context of the API and endpoint being invoked. Take into account constraints from the user such type, format, minimum and maximum. Your response should be only contains the generated values, one per line, and no other text."




# Build prompt starting from a template and the provided information
def get_prompt_from_template(operation, operation_description, parameter_name, parameter_type, parameter_format, parameter_min, parameter_max, parameter_description):

    # Strip strings
    operation_description = operation_description.strip()
    parameter_description = parameter_description.strip()

    # Intro
    prompt = f"Please provide at least {NUM_VALUES} plausible and diverse values for the parameter called '{parameter_name}' of the endpoint '{operation}' of the API '{input.removesuffix('.json')}'. "

    # Operation description
    if len(operation_description) > 3:
        prompt += f"Documentation describes this endpoint: {operation_description}"
        if not operation_description.endswith('.'):
            prompt += "."
        prompt += "\n"
    
    # Type, format and contraints
    prompt += f"The parameter to generate values for is called '{parameter_name}', and is of type {parameter_type}"
    if len(parameter_format) > 2 and parameter_format != 'missing':
        prompt += f" with {parameter_format} format"
    prompt += ". "

    # Min and max
    if parameter_type == 'string':
        if len(parameter_min) > 0 and parameter_min.isdigit() and int(parameter_min) > 0:
            prompt += f"The minimum length of values must be {parameter_min}. "
        if len(parameter_max) > 0:
            prompt += f"The maximum length of values must be {parameter_max}. "
    else:
        if len(parameter_min) > 0:
            prompt += f"Values must be greater than {parameter_min}. "
        if len(parameter_max) > 0:
            prompt += f"Values must be lower than {parameter_max}. "

    # Parameter description
    if len(parameter_description) > 2:
        prompt += f"Consider this description for the parameter when generating values: {parameter_description}"
        if not parameter_description.endswith('.'):
            prompt += "."
        prompt += " "

    return prompt


# Parse LLM response (remove ordered or unordered lists)
def parse_llm_response(response):
    values = []

    lines = response.split('\n')
    for line in lines:
        line = re.sub(r'(\d+\.?|-)\s(.*)$', r'\2', line)
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        values.append(line)

    return values

# Main
if __name__ == '__main__':

    model = GPT4All('wizardlm-13b-v1.2.Q4_0.gguf', n_threads=120)
    os.makedirs('./output', exist_ok=True)

    inputs = os.listdir('./input')
    for input in inputs:
        print(f" => Processing {input}.")
        gpt_output = {}
        with open(f'./input/{input}', 'r') as fr:
            with model.chat_session(system_prompt=SYSTEM_PROMPT):
                data = json.load(fr)
                count = 1
                total = len(data)
                for d in data:
                    print(f" => => ({count}/{total}) Processing parameter '{d['parameter_name']}' of operation {d['operation']}.")
                    prompt = get_prompt_from_template(operation=d['operation'], operation_description=d['operation_description'], parameter_name=d['parameter_name'], parameter_type=d['parameter_type'], parameter_format=d['parameter_format'], parameter_max=d['parameter_max'], parameter_min=d['parameter_min'], parameter_description=d['parameter_description'])

                    response = model.generate(prompt=prompt, temp=0, max_tokens=800)

                    # Create dictionary for operation
                    if d['operation'] not in gpt_output:
                        gpt_output[d['operation']] = {}
                    
                    gpt_output[d['operation']][d['parameter_name']] = parse_llm_response(response)
                    count += 1
    
        with open(f'./output/{input}', 'w') as fw:
            json.dump(gpt_output, fw)
