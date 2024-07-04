import openai
import os
import json

from gradio_client import Client

base ='folder_dir' # Change this to folder containing folders with prompt and example folder
openai.api_key = "key" #and this to a valid openai
experiments = ["NoShotGeneral","FewShotGeneral","OneShotGeneral", "NoShotCoT", "OneShotCoT", "FineTuned"]
experiments_to_do = [0]

# Query a model fine-tuned for APT generation. Please contact the authors of https://aclanthology.org/2023.emnlp-main.746/ for access.
def query_fine_tuned(sentence:str, type:str):
    if type == "Semantic based": # Map APT naming to usage from fine-tuned model
        type = "Semantic-based"
    opt =  [('AdditionDeletion','Addition/Deletion'),('Syntheticanalytic substitution','Synthetic/analytic substitution'),('Same Polarity Substitution (contextual)','Same Polarity Substitution (contextual)'),('Derivational Changes', 'Derivational Changes'), ('Inflectional Changes', 'Inflectional Changes'), ('Modal Verb Changes', 'Modal Verb Changes'), ('Spelling changes', 'Spelling changes'), ('Change of format', 'Change of format'), ('Same Polarity Substitution (contextual)', 'Same Polarity Substitution (contextual)'), ('Same Polarity Substitution (habitual)', 'Same Polarity Substitution (habitual)'), ('Same Polarity Substitution (named ent.)', 'Same Polarity Substitution (named ent.)'), ('Converse substitution', 'Converse substitution'), ('Opposite polarity substitution (contextual)', 'Opposite polarity substitution (contextual)'), ('Opposite polarity substitution (habitual)', 'Opposite polarity substitution (habitual)'), ('Synthetic/analytic substitution', 'Synthetic/analytic substitution'), ('Coordination changes', 'Coordination changes'), ('Diathesis alternation', 'Diathesis alternation'), ('Ellipsis', 'Ellipsis'), ('Negation switching', 'Negation switching'), ('Subordination and nesting changes', 'Subordination and nesting changes'), ('Direct/indirect style alternations', 'Direct/indirect style alternations'), ('Punctuation changes', 'Punctuation changes'), ('Syntax/discourse structure changes', 'Syntax/discourse structure changes'), ('Entailment', 'Entailment'), ('Identity', 'Identity'), ('Non-paraphrase', 'Non-paraphrase'), ('Addition/Deletion', 'Addition/Deletion'), ('Change of order', 'Change of order'), ('Semantic-based', 'Semantic-based')]

    find = filter(lambda tup: tup[0] == type, opt)
    fine_tuned_type = next(find,"Not found")
    if fine_tuned_type == "Not found":
        print("Unknown type for fine tuned chat gpt")
        quit(1)
    
    messages = [
            {
                "role": "user",
                "content": (
                    "Given the following sentence, generate a paraphrase with"
                    f" the following types. Sentence: {sentence}. Paraphrase"
                    f" Types: {type}"
                ),
            }]
    response = openai.ChatCompletion.create(

        model="ft:gpt-3.5-turbo-0613:personal::7xbU0xQ2",

        messages=messages,

        max_tokens=1024,

        n=1,

        stop=None,

        temperature=1,

    )
    answer = response.choices[0].message["content"]
    return answer.strip().replace("\n","")

    
def query_sentences(prompt:str, extract_answer:bool=False):
    preprompt = "You are a helpful linguist."
    messages = [{"role":"system", "content": preprompt},
                {"role":"user", "content":prompt}]
    response = openai.ChatCompletion.create(

        model="gpt-3.5-turbo",

        messages=messages,

        max_tokens=1024,

        n=1,

        stop=None,

        temperature=1,

    )
    answer = response.choices[0].message["content"]

    if extract_answer:
        answer = answer.split("Output:")[1]

    return answer.strip().replace("\n","")

definition = {}
examples = {}

with open("definitions.json","r") as f:
    definition = json.load(f)

exampleFormat = 'Sentence: {Original} \n Output: {Changed}'




prompt_files = {
    experiments[0]:"prompt.txt",
    experiments[1]:"prompt_multi.txt",
    experiments[2]:"prompt_single.txt",
    experiments[3]:"prompt_chain.txt",
    experiments[4]:"prompt_chain_single.txt"
}



for ex in experiments_to_do:
    experiment = experiments[ex]
    examples_original = {}
    examples_transformed = {}
    examples_explanation = {}
    if experiment == "OneShotGeneral":
        with open(base + f"CleanedExamples\\CleanedExamplesSingle.txt") as file:
           exampleFile = file.readlines()
           for i in range(0,len(exampleFile),3):
               key = exampleFile[i].strip()
               examples_original[key] = []
               examples_transformed[key] = []
               examples_original[key].append(exampleFile[i+1].strip())
               examples_transformed[key].append(exampleFile[i+2].strip())

    if experiment == "FewShotGeneral":
        with open(base + f"CleanedExamples\\CleanedExamplesMulti.txt","r") as file:
            exampleFile = file.readlines()
            for i in range(0,len(exampleFile),11):
                key = exampleFile[i].strip()
                examples_original[key] = []
                examples_transformed[key] = []
                for k in range(5):
                    examples_original[key].append(exampleFile[i+k*2+1].strip())
                    examples_transformed[key].append(exampleFile[i+k*2+2].strip())
    if experiment == "OneShotCoT":
         with open(base + f"CleanedExamples\\CleanedExamplesCoTSingle.txt","r") as file:
            exampleFile = file.readlines()
            for i in range(0,len(exampleFile),4):
                key = exampleFile[i].strip()
                examples_original[key] = []
                examples_transformed[key] = []
                examples_explanation[key] = []
                examples_original[key].append(exampleFile[i+1].strip())
                examples_transformed[key].append(exampleFile[i+2].strip())
                examples_explanation[key].append(exampleFile[i+3].strip())
    
    if experiment != "FineTuned":
        prompt_file = prompt_files[experiment] 
        with open(base+ f"Prompts\\{prompt_file}", 'r') as file:
            prompt_template = file.read()

    for atomic_p in definition.keys():
        # Uncomment following and adapt the already done categories in case run gets cancelled for some reason
        #if atomic_p in ["Converse substitution"]:#,"Converse substitution","Spelling changes","Punctuation changes", "Subordination and nesting changes", "Change of order", "Inflectional Changes"]:
        #  continue 
        with open(base + f"Sentences\\{atomic_p}_base_1.txt") as file: # Get base sentence
            file_content =file.readlines()
            category = file_content[:1]
            sentences = file_content[1:]

        with open(base + f"Extract\\{atomic_p}_base_2.txt") as file: # Get paraphrase from ETPC dataset as reference
            file_content =file.readlines()
            results  = file_content   

        examples = []
        if examples_original:
            examples = examples_original[atomic_p]
            example_transformed = examples_transformed[atomic_p]
            if experiment == "OneShotCoT":
                example_explanation = examples_explanation[atomic_p]
        sentences = sentences[1:11]
        results = results[1:]

        example_str = ""
        for index, example in enumerate(examples):
            if experiment == "OneShotCoT":
                example_str = example_str + f"""Input: '''{example}'''
Thoughts: {example_explanation[index]}
Output: {example_transformed[index]}\n"""
            else:
                example_str = example_str + f"""Input: '''{example}'''
Output: {example_transformed[index]}\n"""
        print(atomic_p) 
        print(example_str)
        output_file = base + f"Output\\{experiment}\\{atomic_p}.csv"
        os.makedirs(os.path.dirname(output_file),exist_ok=True)
        with open(output_file,"w", encoding="utf-8") as f:
            print(f"prompt_none",file=f)
            print("Input|Output|ETPC",file=f)
            i = 0
            for sentence in sentences:
                sentence = sentence.strip()
                if experiment == "FineTuned":
                    answer = query_fine_tuned(sentence,atomic_p)
                else:
                    prompt=prompt_template.format(definition=definition[atomic_p],example=example_str,sentence=sentence.strip())
                    extract_answer = False
                    if experiment=="NoShotCoT" or experiment=="OneShotCoT":
                        extract_answer=True
                    answer = query_sentences(prompt, extract_answer)
                print(f"{sentence}|{answer}|{results[i]}", file=f) #Output corresponds to Base-sentence, Paraphrased by GPT, Paraphrase given in the ETPC
                i=i+1

