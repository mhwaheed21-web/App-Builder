from dotenv import load_dotenv
load_dotenv()


from agent.states import *
from agent.prompts import *
from agent.tools import *
from langchain_groq import ChatGroq
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

# (specify your model name here)

llm=ChatGroq(model="llama-3.3-70b-versatile")
#ChatGroq(model="openai/gpt_oss-120b")

def planner_agent(state:dict)->dict:
    user_prompt=state["user_prompt"]
    resp=llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    if resp is None:
        raise ValueError("Planner doesnot return a valid response")
    return{"plan":resp}

def architect_agent(state:dict)->dict:
    plan:Plan=state["plan"]
    resp=llm.with_structured_output(TaskPlan).invoke(planner_prompt(plan))
    if resp is None:
        raise ValueError("Architect doesnot return a valid response")
    
    resp.plan=plan
    return{"task_plan":resp}

def coder_agent(state:dict)->dict:
    coder_state=state.get("coder_state")
    if coder_state is None:
        coder_state=CoderState(task_plan=state["task_plan"],current_step_idx=0,current_file_content=None)
    
    steps=coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx>=len(steps):
        return{"coder_state":coder_state,"status":"DONE"}
    
    current_task=steps[coder_state.current_step_idx]

    existing_content=read_file.run(current_task.filepath)
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )
    system_prompt=coder_system_prompt()

    coder_tools=[read_file,write_file,list_files,get_current_directory]
    react_agent = create_react_agent(llm, coder_tools)

    react_agent.invoke({"messages":[{"role":"system","content":system_prompt},
                                    {"role":"user","content":user_prompt}]})
    coder_state.current_step_idx+=1
    return{"coder_state":coder_state}



graph= StateGraph(dict)
graph.add_node("planner",planner_agent)
graph.add_node("architect",architect_agent)
graph.add_node("coder",coder_agent)

graph.add_edge(start_key="planner",end_key="architect")
graph.add_edge(start_key="architect",end_key="coder")
graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)

graph.set_entry_point("planner")
agent=graph.compile()
if __name__ == "__main__":
    result = agent.invoke({"user_prompt": "Create a simple calculator web applicaton"},
                          {"recursion_limit": 100})
    print("Final State:", result)