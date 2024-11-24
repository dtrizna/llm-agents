# FROM: https://microsoft.github.io/autogen/0.2/docs/tutorial/code-executors/
import os
import tempfile
from autogen.coding import DockerCommandLineCodeExecutor, LocalCommandLineCodeExecutor
from autogen import ConversableAgent, AssistantAgent, UserProxyAgent

from dotenv import load_dotenv
load_dotenv()

code_writer_system_message = """You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or 
shell script (in a sh coding block) for the user to execute.

1. When you need to collect info, use the code to output the info you need, 
for example, browse or search the web, download/read a file, print the content of a webpage or a file, 
get the current date/time, check the operating system. After sufficient info is printed and 
the task is ready to be solved based on your language skill, you can solve the task by yourself.

2. When you need to perform some task with code, use the code to perform the task and output the result. 
Finish the task smartly. Solve the task step by step if you need to. 
If a plan is not provided, explain your plan first. 
Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. 
The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. 
The user can't modify your code. So do not suggest incomplete code which requires users to modify. 
Don't use a code block if it's not intended to be executed by the user.

If you want the user to save the code in a file before executing it, 
put # filename: <filename> inside the code block as the first line. 

Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. 
Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. 
Suggest the full code instead of partial code or code changes. 
If the error can't be fixed or if the task is not solved even after the code is executed successfully, 
analyze the problem, revisit your assumption, collect additional info you need, 
and think of a different approach to try.
When you find an answer, verify the answer carefully. 
Include verifiable evidence in your response if possible.

When you see no input, reply with just 'TERMINATE'.
"""

# Create a temporary directory to store the code files.
# Is destroyed when the program ends
temp_dir = tempfile.TemporaryDirectory()

# NOTE: It's possible to use a command line code executor in docker:
# executor = DockerCommandLineCodeExecutor(..)
executor = LocalCommandLineCodeExecutor(
    work_dir=temp_dir.name,
)

# Create an agent with code executor configuration that uses docker.
code_executor_agent = ConversableAgent(
    name="code_executor_agent",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor},  # Use the command line code executor.
    max_consecutive_auto_reply=5, # Number of auto replies before asking for human input
    # NOTE: this specifies Callable condition when to stop the loop between agents
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
    human_input_mode="TERMINATE",
    # NOTE on 'human_input_mode' (str): whether to ask for human inputs every time a message is received.
    # (1) When "ALWAYS", the agent prompts for human input every time a message is received.
    #     Under this mode, the conversation stops when the human input is "exit",
    #     or when is_termination_msg is True and there is no human input.
    # (2) When "TERMINATE", the agent only prompts for human input only when a termination message is received or
    #     the number of auto reply reaches the max_consecutive_auto_reply.
    # (3) When "NEVER", the agent will never prompt for human input. Under this mode, the conversation stops
    #     when the number of auto reply reaches the max_consecutive_auto_reply or when is_termination_msg is True.
)

code_writer_agent = ConversableAgent(
    name="code_writer_agent",
    system_message=code_writer_system_message,
    llm_config={"config_list": [{
        # GEMINI
        "model": "gemini-1.5-flash-latest",
        "api_key": os.environ["GEMINI_API_KEY"],
        "api_type": "google"
    }]},
    code_execution_config=False,  # Turn off code execution for this agent.
)

chat_result = code_executor_agent.initiate_chat(
    recipient=code_writer_agent,
    message="Write a Python script to calculate the 14th Fibonacci number.",
)

# NOTE: this bootstraps the following loop:
# graph LR
#     A[Human] --> B[code_executor_agent]
#     B --> C[code_writer_agent]
#     C -->|Writes Code| B
#     B -->|Asks Permission| A
#     A -->|Approves Execution| B
#     B -->|Executes Code| B
