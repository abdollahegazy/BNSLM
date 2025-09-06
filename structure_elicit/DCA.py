import logging

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

from prompts import system_prompts,inference_prompts

def llm_query(prompt, role):
    full_prompt = ''.join(prompt)

    messages = [
        {"role": "system", "content": system_prompts[role]},
        {"role": "user", "content": full_prompt}
    ]

    response = get_client().chat.completions.create(
        model="gpt-4o-mini-2024-07-18", 
        messages=messages,
        max_tokens=1500,
        temperature=0.3,
    )

    return response.choices[0].message.content


_client = None  

def get_client():
    from openai import OpenAI
    import os 
    from dotenv import load_dotenv

    load_dotenv()
    global _client
    if _client is None:  # lazy init
        _client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.getenv("OPENAI_ORG_ID"),
        )
    return _client


def decider(nodes: str ,nodes_desc: dict[str:str]):
    role = 'decider'
    query = (
        inference_prompts[role]  
        + f"\n NODES: {nodes}\n" 
        + f"NODE_DESCRIPTIONS: {nodes_desc}\n"
    )
    response = llm_query(query,role)
    # print(response)
    return response

def critique(nodes, nodes_desc, decider_response):
    role = 'critique'
    query = (
        inference_prompts[role]  
        + f"\n NODES: {nodes}\n" 
        + f"NODE_DESCRIPTIONS: {nodes_desc}\n"
        + "DECIDER_JUDGMENTS:\n"
        + decider_response
    )
    response = llm_query(query,role)
    # print(response)
    return response

def arbiter(nodes,nodes_desc,decider_response,critique_response):
    role = 'arbiter'
    query = (
        inference_prompts[role]  + 
        f"\n NODES {nodes}\n" + 
        f"NODE_DESCRIPTIONS: {nodes_desc}\n"  + 
        f"DECIDER: \n{decider_response}\n" + 
        f"CRITIQUE:\n {critique_response}\n")
    response = llm_query(query,role)
    print(response)
    return response

def dca_round(nodes: str, nodes_desc: dict[str:str]):
    
    decider_response = decider(nodes,nodes_desc)
#     decider_response = """
# {
#   "judgments": {
#     "(Bronchitis,Dyspnea)": "->",
#     "(Dyspnea,Lung_Cancer)": "None",
#     "(Lung_Cancer,Bronchitis)": "->"
#   }
# """

    critique_response = critique(nodes,nodes_desc,decider_response)

    if critique_response == "YES":
        return decider_response
    
    arbiter_response = arbiter(nodes,nodes_desc,decider_response,critique_response)

    return decider_response, critique_response,arbiter_response
    # arbiter_response = 
    




