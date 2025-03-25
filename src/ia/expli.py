from langchain_community.llms import GPT4All
import getpass
import os
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
#from gpt4all import GPT4All
from langchain_community.llms import GPT4All
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, trim_messages



#print(GPT4All.list_models())

model_path=r"C:\Users\etien\AppData\Local\nomic.ai\GPT4All\mistral-7b-instruct-v0.1.Q4_0.gguf"

llm=GPT4All(model=model_path)

trimmer = trim_messages(
    max_tokens=650,
    strategy="last",
    token_counter=llm,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

messages=[]

prompt_template = ChatPromptTemplate.from_messages(
    [
     SystemMessage(content=
 """You are a cybersecurity assistant specialized in phishing detection.

The user will provide you with an email and a list of its key elements along with importance scores (positive meaning suspicious, negative meaning benign). Your task is to analyze the email holistically and construct a concise, factual paragraph explaining whether it is suspicious in a phishing context.

When generating the paragraph:

Consider all elements and their scores to determine the overall likelihood of phishing.

If multiple elements have a strong positive score, emphasize their contribution to suspicion.

If certain elements have a negative score, acknowledge them as mitigating factors but do not overrule the suspicious elements if they dominate.

Highlight whether the email contains an HTTP link rather than HTTPS, as the absence of HTTPS can be a security concern in phishing attempts.

Integrate the elements naturally in a flowing paragraph rather than listing them separately.

Do not assume or invent information beyond what is provided.

Be clear, educational, and factual, without giving security tips or recommendations."""
),
        MessagesPlaceholder(variable_name="messages"),
    ]
)






# Define the function that calls the model
def call_model(state: MessagesState):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke(trimmed_messages)
    prompt_text = prompt.to_string() 
    response = llm.invoke(prompt_text).strip()

    return {"messages": state["messages"] + [AIMessage(content=response)]}

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


config = {"configurable": {"thread_id": "abc123"}}


if __name__ == "__main__":
    # Charger la base de données et FAISS

    print("🤖 Chatbot prêt ! Donnez un mot en entrée (tapez 'exit' pour quitter).")
    while True:
        word = input("Mot : ").strip()
        if word.lower() in ["exit", "quit", "stop"]:
            print("🤖 Fin de la session. À bientôt !")
            break
        
        user_message = [HumanMessage(content=word)]
        output = app.invoke({"messages": user_message}, config)
        response = output["messages"][-1]
        if isinstance(response, AIMessage):
            print(f"🤖 {response.content}")