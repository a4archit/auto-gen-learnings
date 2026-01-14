from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
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









# ************************************ News letter sender agent ******************************

# File to attach
file_path = Path("newsletter.pdf")  # change filename
mime_type, _ = mimetypes.guess_type(file_path)
mime_type, mime_subtype = mime_type.split("/")




def send_mail(
        email_content: str, 
        email_address: str, 
        email_subject: str
    ) -> Literal['newsletter_sent_successfully','newsletter_not_sent_due_to_some_error']:
    
    """
    By the use of this tool agent is able to send email to the provided email address

    Args:
        email_content (str): content body of email, may be content of news letter
        email_address (str): email address on which newsletter/email will be sent
        email_subject (str): subject to the email

    """

    try: 
        msg = EmailMessage()
        msg.set_content(email_content)
        msg['Subject'] = email_subject
        msg['From'] = os.getenv("SENDER_EMAIL")
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
            server.login(
                os.getenv("SENDER_EMAIL"), 
                os.getenv("GOOGLE_APP_PASSWORD")
            )

            server.send_message(msg)
        
    except:
        return "newsletter_not_sent_due_to_some_error"
    
    return "newsletter_sent_successfully"


newsletter_sender_agent = AssistantAgent(
    name="newsletter_sender_agent",
    model_client=client,
    tools=[send_mail],
    description="News letter sender agent.",
    max_tool_iterations=5,
    system_message="""
You are a helpful assistant. 
Your job is to write a cool email (yourself) and sent it using your tool(s).
Email not more than 150 words.
Don't add subject in the email body.
Don't use markdown content in email body.
Use name 'agento bhai' iff you adding 'regards' below the email body.
"""
)

















# ****************************** news letter builder agent ***********************************

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




newsletter_builder_agent = AssistantAgent(
    name = "newsletter_builder_agent",
    model_client = client,
    tools = [get_news_headlines, save_newsletter],
    max_tool_iterations=2,
    description = "This agent is able to build newletter on the given topic.",
    system_message = """
You are an expert news collector and news letter builder.
Your job is to build a newsletter and save it.
You have 2 tools which helps you to done your task:
    1) `get_news_headlines`: it helps you to collect news
    2) `save_newsletter`: it saves the newsletter

Important: You can call a tool only single time.
"""
)
















# ************************************** Assistant agent ************************************8


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

    response = newsletter_builder_agent.run(task=task)

    return response 









# --------------------------------------- giant agent ----------------------------------


assistant_agent = AssistantAgent(
    name = "assistant_agent",
    model_client = client,
    tools = [tavily],
    max_tool_iterations=2,
    description = "This agent helps to answer general queries.",
    system_message = """
You are a helpful agent.
You always chat like a helpful friend.
Your reponses always polite and unambiguous.
"""
)





# ********************************* Main: selector agent <orchestrator> ****************************


# Define a termination condition that stops the task if the critic approves.
team_termination = TextMentionTermination("newsletter_sent_successfully") | MaxMessageTermination(25)


orchestrator_prompt = """Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Make sure the planner agent has assigned tasks before other agents start working.
Only select one agent.
"""

orchestrator = SelectorGroupChat(
    participants = [assistant_agent, newsletter_builder_agent, newsletter_sender_agent],
    model_client = client,
    name = "orchestrator",
    selector_prompt = orchestrator_prompt,
    allow_repeated_speaker = True,
    termination_condition = team_termination
)











async def running_selector_group_chat_team() -> None:
    task = """ Write a newsletter about spacex mars mission (future goals with timelines) 
    and send it to my collegues, their emails are digvijaykhapran@gmail.com and spacegyan00@gmail.com
    """
    await Console(orchestrator.run_stream(task=task))



# async def main():

#     # When running inside a script, use a async main function and call it from `asyncio.run(...)`.
#     await orchestrator.reset()  # Reset the team for a new task.
#     async for message in orchestrator.run_stream(task="Write a newsletter about tesla mars mission and send it on email conceptclearhelp@gmail.com"):  # type: ignore
#         if isinstance(message, TaskResult):
#             print("Stop Reason:", message.stop_reason)
#         else:
#             print(message)







if __name__ == "__main__":

    # asyncio.run(running_round_robin_team()) 

    asyncio.run(running_selector_group_chat_team())

    # send_mail("hello ji (from python), email sending test passed!", email_address="archittyagi599@gmail.com")
    



