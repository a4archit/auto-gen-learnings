from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination, ExternalTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console

from email.message import EmailMessage
from typing import Literal, List, Dict
from tavily import TavilyClient
from dotenv import load_dotenv
from weasyprint import HTML
from pathlib import Path

import mimetypes
import markdown
import asyncio
import smtplib
import os





load_dotenv()








# ----------------------------------- Clients ----------------------------------------

client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",  # or mistralai/mistral-7b-instruct, google/gemma-7b-it
    api_key=None,                # uses OPENROUTER_API_KEY env var
    base_url="https://openrouter.ai/api/v1",
)


# tavily client
tavily_client = TavilyClient(api_key=None)











# File to attach
file_path = Path("newsletter.pdf")  # change filename
mime_type, _ = mimetypes.guess_type(file_path)
mime_type, mime_subtype = mime_type.split("/")




def send_mail(email_content: str, email_address: str):
    """
    By the use of this tool agent is able to send email to the provided email address

    Args:
        email_content (str): content body of email, may be content of news letter
        email_address (str): email address on which newsletter/email will be sent

    """

    msg = EmailMessage()
    msg.set_content(email_content)
    msg['Subject'] = 'SMTP Test'
    msg['From'] = 'help.atd@gmail.com'
    msg['To'] = email_address

    # Read file and attach
    with open(file_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype=mime_type,
            subtype=mime_subtype,
            filename=file_path.name,
        )


    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('help.atd@gmail.com', os.getenv("GOOGLE_APP_PASSWORD"))
        server.send_message(msg)
        


newsletter_sender_agent = AssistantAgent(
    "newsletter_sender_agent",
    model_client=client,
    tools=[send_mail],
    description="News letter sender agent",
    system_message="""
You are a helpful assistant agent, you can send the newsletter (pdf) through email.
You have a tool that helps you to complete your task.
"""
)

















# ----------------------------------------- sub agents -----------------------------------------

def get_news_headlines(topic: str, number_of_headlines: int = 3) -> List[str]:
    """
    Collect latest news healines.

    Args:
        topic (str): topic of News
        number_of_headlines (int): total number of news headlines

    Returns:
        List(str): list of latest news of given topic 
    """

    print(f"Collecting news about `{topic}`... ", end="")
    news = tavily(query=topic, max_results=number_of_headlines)
    print("Done.")

    return [x['content'] for x in news]



def save_newsletter(news_headlines: str) -> Literal['newsletter saved', 'newsletter not saved due to some error']:
    """
    This tool MUST be called after news collection.
    It saves the final formatted newsletter.
    The task is INCOMPLETE until this tool is executed.
    Input must be the collected news content.

    Args:
        news_headlines (str): news headlines as mardown content

    Returns:
        Literal['newsletter saved', 'newsletter not saved due to some error']: message
    
    """

    print("Saving Newsletter... ", end="")
    try:
        html_content = markdown.markdown(news_headlines)
        complete_content = html_content
        # converting to the pdf
        HTML(string=complete_content).write_pdf("newsletter.pdf")
    except: 
        return 'newsletter not saved due to some error'
    
    print("Saved.")
    return 'newsletter saved'




newsletter_agent = AssistantAgent(
    name = "newsletter_agent",
    model_client = client,
    tools = [get_news_headlines, save_newsletter],
    max_tool_iterations=2,
    description = "A subagent that able to collect latest news and save them in a pdf.",
    system_message = """
        You are an autonomous agent.
        You must complete tasks by calling tools.
        If multiple tools are relevant, you MUST call them in logical order.
        Do NOT stop after the first tool.
        Confirm task completion only after all required tools are used.
        """
)

















# -------------------------------- tools --------------------------------------------------

def tavily(query: str, max_results: int = 5) -> List[Dict]:
    """
    Perform a web search using Tavily.

    Args:
        query (str): Search query
        max_results (int): Number of results to return

    Returns:
        List[Dict]: Search results with title, url, and content
    """

    response = tavily_client.search(
        query=query,
        max_results=max_results
    )
    
    return response["results"]



def newsletter_subagent(task: str):
    """ 
    This is able to create a newsletter and save it.

    Args:
        task (str): task
    """

    response = newsletter_agent.run(task=task)

    return response 









# --------------------------------------- giant agent ----------------------------------


assistant = AssistantAgent(
    name = "assistant",
    model_client = client,
    tools = [tavily],
    max_tool_iterations=2,
    description = "Main Assistant agent",
    system_message = "You are a helpful agent, you have access of some tools, your always return your responses like a human."
)








# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

# Create a team with the primary and critic agents.
team = RoundRobinGroupChat(
    [assistant, newsletter_agent, newsletter_sender_agent], 
    termination_condition=text_termination,
    max_turns=4,
    name="round_robin_team"
)








async def running_round_robin_team() -> None:

    # await Console(
    #     assistant.on_messages_stream(
    #         messages= [TextMessage(content='Create a newsletter about tesla',source='User')],
    #         cancellation_token=CancellationToken()
    #     ),
    #     output_stats=True # Enable stats Printing
    # )

    # while True:

    #     user = input("user: ")

    #     if user.strip().lower() == "/bye":
    #         print("\n\n\tBYE BYE :)\n\n")

    await team.reset()

    print("Agent is thinking...")
    result = await team.run(task="hi")

    print(result)




async def main():

    # When running inside a script, use a async main function and call it from `asyncio.run(...)`.
    await team.reset()  # Reset the team for a new task.
    async for message in team.run_stream(task="Write a newsletter about humanoid robots and send it on email spacegyan00@gmail.com"):  # type: ignore
        if isinstance(message, TaskResult):
            print("Stop Reason:", message.stop_reason)
        else:
            print(message)







if __name__ == "__main__":

    # asyncio.run(running_round_robin_team()) 

    asyncio.run(main())

    # send_mail("hello ji (from python), email sending test passed!", email_address="archittyagi599@gmail.com")
    



