"""
agent/core.py — LangGraph stateful agent for Profundus-Comet
Nodes: load_project -> retrieve_memory -> plan -> act -> synthesize -> persist
"""
from __future__ import annotations
import os, yaml, operator, uuid, datetime
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agent.memory.chroma_store import get_collection, query_memory, upsert_memory

class AgentState(TypedDict):
    messages:        Annotated[list, operator.add]
    project_context: str
    system_prompt:   str
    memory_chunks:   list
    plan:            str
    artifacts:       Annotated[list, operator.add]
    iteration:       int

def _cfg() -> dict:
    with open(os.getenv("PROJECT_CONFIG", "./project_config.yaml")) as f:
        return yaml.safe_load(f)

def load_project(state):
    c = _cfg()
    with open(c.get("system_prompt", "./agent/prompts/system_prompt.md")) as f:
        sp = f.read()
    ctx = f"Project: {c['project_name']} | Model: {c['model']}"
    return {**state, "project_context": ctx, "system_prompt": sp}

def retrieve_memory(state):
    c = _cfg()
    if not state["messages"]: return state
    q = getattr(state["messages"][-1], "content", str(state["messages"][-1]))
    try:
        col = get_collection(c["project_id"], c["memory_path"])
        chunks = query_memory(col, q, 5).get("documents", [[]])[0]
    except Exception: chunks = []
    return {**state, "memory_chunks": chunks}

def plan_step(state):
    c = _cfg()
    llm = ChatOllama(model=c["model"], base_url=c["ollama_url"])
    mem = "\n".join(state.get("memory_chunks", []))
    msgs = [SystemMessage(content=state["system_prompt"])] + state["messages"] + \
           [HumanMessage(content=f"Memory:\n{mem}\n\nProduce a concise 3-5 step plan.")]
    return {**state, "plan": llm.invoke(msgs).content}

def act_with_tools(state):
    return {**state, "artifacts": [], "iteration": state.get("iteration", 0) + 1}

def synthesize_response(state):
    c = _cfg()
    llm = ChatOllama(model=c["model"], base_url=c["ollama_url"])
    ctx = f"Plan:\n{state.get('plan','')}\nMemory:\n{''.join(state.get('memory_chunks',[]))}"
    msgs = [SystemMessage(content=state["system_prompt"])] + state["messages"] + \
           [HumanMessage(content=ctx)]
    return {**state, "messages": [AIMessage(content=llm.invoke(msgs).content)]}

def persist_to_memory(state):
    c = _cfg()
    if not state["messages"]: return state
    summary = getattr(state["messages"][-1], "content", "")[:500]
    try:
        col = get_collection(c["project_id"], c["memory_path"])
        upsert_memory(col, str(uuid.uuid4()), summary,
                      {"type": "session", "ts": datetime.datetime.utcnow().isoformat()})
    except Exception as e: print(f"[persist] {e}")
    return state

def build_graph():
    g = StateGraph(AgentState)
    for name, fn in [("load_project", load_project), ("retrieve_memory", retrieve_memory),
                     ("plan", plan_step), ("act", act_with_tools),
                     ("synthesize", synthesize_response), ("persist", persist_to_memory)]:
        g.add_node(name, fn)
    g.set_entry_point("load_project")
    for a, b in [("load_project","retrieve_memory"),("retrieve_memory","plan"),
                 ("plan","act"),("act","synthesize"),("synthesize","persist"),("persist",END)]:
        g.add_edge(a, b)
    return g.compile()

if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    agent = build_graph()
    state = {"messages":[], "project_context":"", "system_prompt":"",
             "memory_chunks":[], "plan":"", "artifacts":[], "iteration":0}
    console.print("[bold green]Profundus-Comet[/] ready. Ctrl+C to exit\n")
    while True:
        try:
            ui = console.input("[cyan]You:[/] ")
            state["messages"] = state["messages"] + [HumanMessage(content=ui)]
            state = agent.invoke(state)
            console.print(f"\n[yellow]Agent:[/] {state['messages'][-1].content}\n")
        except KeyboardInterrupt:
            break
