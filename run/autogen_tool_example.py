# FROM: https://microsoft.github.io/autogen/0.2/docs/tutorial/code-executors/
import os
import tempfile
import socket
# from autogen.coding import LocalCommandLineCodeExecutor
from autogen import ConversableAgent, UserProxyAgent

from dotenv import load_dotenv
load_dotenv()

message_manager_system_message = """You are a tool that is able to resolve domain names to IP addresses. 
User will provide you with a domain name, and you are able to resolve it to an IP address.
Append with 'TERMINATE' when you are done.
"""

# Create a temporary directory to store the code files.
# Is destroyed when the program ends
temp_dir = tempfile.TemporaryDirectory()

# Create an agent with code executor configuration that uses docker.
user_proxy = UserProxyAgent(
    name="user_proxy",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config=False, 
    max_consecutive_auto_reply=5, # Number of auto replies before asking for human input
    # NOTE: this specifies Callable condition when to stop the loop between agents
    is_termination_msg=lambda msg: msg.get("content") is not None and msg.get("content", "").strip().endswith("TERMINATE"),
    human_input_mode="TERMINATE",
)

message_manager = ConversableAgent(
    name="message_manager",
    system_message=message_manager_system_message,
    llm_config={"config_list": [{
        # GEMINI
        "model": "gemini-1.5-flash-latest",
        "api_key": os.environ["GEMINI_API_KEY"],
        "api_type": "google"
    }]},
    code_execution_config=False,  # Turn off code execution for this agent.
)


@user_proxy.register_for_execution()
@message_manager.register_for_llm(description="resolve domain name to IP address")
def resolve_domain_to_ip(domain: str) -> str:
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return f"Could not resolve domain {domain}"


# initiate chat with message manager
chat_result = user_proxy.initiate_chat(
    recipient=message_manager,
    message="Resolve: localhost",
)


# NOTE: this bootstraps the following loop:
# graph LR
#     A[Human] --> B[UserProxyAgent]
#     B --> C[MessageManager]
#     C --> [Callable] B
#     B --> [Output] C
#     C --> [Output and TERMINATE] A
