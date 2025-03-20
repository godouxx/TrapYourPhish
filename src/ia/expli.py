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

model_path=r"C:\Users\r0man\AppData\Local\nomic.ai\GPT4All\mistral-7b-instruct-v0.2.Q4_0.gguf"

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
        SystemMessage(content="You are a cybersecurity assistant. The user will give you one word, and you must explain why this word could be malicious in a phishing context."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)



# Define a new graph
workflow = StateGraph(state_schema=MessagesState)


# Define the function that calls the model
def call_model(state: MessagesState):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke(trimmed_messages)
    response = llm.invoke(prompt).strip()

    return {"messages": state["messages"] + [AIMessage(content=response)]}


# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


config = {"configurable": {"thread_id": "abc123"}}

#query = "What's my name?"

#input_messages = [HumanMessage(query)]
#output = app.invoke({"messages": input_messages}, config)
#output["messages"][-1].pretty_print()


#embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L-12-v2")
#vector_store = FAISS(embedding_function=embeddings)

if __name__ == "__main__":
    # Charger la base de données et FAISS

    print("🤖 Chatbot prêt ! Donnez un mot en entrée (tapez 'exit' pour quitter).")
    while True:
        word = input("Mot : ").strip()
        if word.lower() in ["exit", "quit", "stop"]:
            print("🤖 Fin de la session. À bientôt !")
            break
        
        messages.append(HumanMessage(content=word))
        output = app.invoke({"messages": messages}, config)
        response = output["messages"][-1]
        if isinstance(response, AIMessage):
            print(f"🤖 {response.content}")
        messages.append(response)
