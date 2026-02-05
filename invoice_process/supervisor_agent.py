
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END

from read_mail import mail_tools, mail_tools_by_name
from langchain_ollama import ChatOllama
from read_invoice import invoice_tools, invoice_tools_by_name
from langgraph.graph import MessagesState
#Graph
LLM_NODE = "llm_node"
HUMAN_DECISION_NODE = "decision_node"
EXTRACT_INVOICE_DETAILS_NODE = "extract_invoice_details_node"
#POST_NODE = "post_node"

#Nodes
llm = ChatOllama(model="llama3.2", system_prompt="You are a helpful assistant. You can read emails and extract invoice details.")

def invoke_llm_agent(state: MessagesState):
    print(state["messages"])
    print("\n\n")
    llm_with_tools = llm.bind_tools(mail_tools)
    ai_msg = llm_with_tools.invoke(state["messages"][-1].content)
    print(ai_msg)
    print("\n\n")
    
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            print(f"Tool Name: {tool_call['name']}")
            tool_output = mail_tools_by_name[tool_call['name']].invoke(tool_call['args'])
            print(f"Tool Output: {tool_output}")    
    return {"messages": [ai_msg]}

def extract_invoice_details(state: MessagesState):
    print(state["messages"])
    print("\n\n")
    llm_with_tools = llm.bind_tools(invoice_tools)
    ai_msg = llm_with_tools.invoke(state["messages"][-1].content)
    print(ai_msg)
    print("\n\n")
    
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            print(f"Tool Name: {tool_call['name']}")
            tool_output = invoice_tools_by_name[tool_call['name']].invoke(tool_call['args'])
            print(f"Tool Output: {tool_output}")    
    return {"messages": [ai_msg]}


def decision_node(state: MessagesState):
    result = state["messages"][-1].content
    print(result)

    decision = input("Do want to proceed? (yes/no)")

    if(decision.lower() == "yes"):
        state["messages"].append(HumanMessage(content="extract invoice details"))
        return EXTRACT_INVOICE_DETAILS_NODE
    else:
        return END

#def post_node(state: MessagesState):
#    return {"messages": [llm.invoke(state["messages"])]}

GRAPH = StateGraph(MessagesState)
GRAPH.add_node(LLM_NODE,invoke_llm_agent)
GRAPH.add_node(HUMAN_DECISION_NODE,decision_node)
GRAPH.add_node(EXTRACT_INVOICE_DETAILS_NODE,extract_invoice_details)
#GRAPH.add_node(POST_NODE,post_node)

GRAPH.set_entry_point(LLM_NODE)
GRAPH.add_conditional_edges(LLM_NODE,decision_node)
GRAPH.add_edge(EXTRACT_INVOICE_DETAILS_NODE,END)
#GRAPH.add_edge(POST_NODE,END)
app = GRAPH.compile()

if __name__ == "__main__":
    result = app.invoke({"messages":[HumanMessage("content=read last 24 hours emails")]})
    print(result["messages"][-1].content)