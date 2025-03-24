from langchain_community.llms import GPT4All
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, trim_messages

# Modèle local
model_path = r"C:\Users\r0man\AppData\Local\nomic.ai\GPT4All\mistral-7b-instruct-v0.2.Q4_0.gguf"
llm = GPT4All(model=model_path)

# Trimming
trimmer = trim_messages(
    max_tokens=650,
    strategy="last",
    token_counter=llm,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# Prompt
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
You are a cybersecurity assistant specialized in phishing detection.

The user will give you a word, phrase, email address, or email element. 
Your task is to explain clearly and simply why this item might be suspicious or commonly used in phishing emails.

Focus only on the explanation — do not give any advice or safety tips. Do not include checklists or instructions on what to do.

Your goal is to help regular users understand why this element raises red flags in a phishing context, using accessible and educational language.

Highlight how attackers use emotional manipulation (urgency, fear, reward), technical tricks (fake links, spoofed addresses), and common language patterns in phishing.

If the element is especially suspicious (e.g., "urgent", "verify your account", "support@paypal-security.com"), emphasize why it’s often used in phishing, and what it triggers psychologically.

If the element is probably safe, explain that too — just stick to the explanation.

Keep the tone informative and focused on understanding, not on action.
"""),
    MessagesPlaceholder(variable_name="messages"),
])

# LangGraph
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    trimmed = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke(trimmed)
    response = llm.invoke(prompt).strip()
    return {"messages": state["messages"] + [AIMessage(content=response)]}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}


def get_explanation_from_llm(word: str) -> str:
    messages = [HumanMessage(content=word)]
    output = app.invoke({"messages": messages}, config)
    response = output["messages"][-1]
    if isinstance(response, AIMessage):
        return response.content.strip()
    return "Erreur : pas de réponse du LLM"
