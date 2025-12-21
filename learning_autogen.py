from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_core.models import ModelInfo
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage

from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Literal, List, Dict
from weasyprint import HTML

import asyncio
import markdown


load_dotenv()




# ----------------------------------- Clients ----------------------------------------

client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",  # or mistralai/mistral-7b-instruct, google/gemma-7b-it
    api_key=None,                # uses OPENROUTER_API_KEY env var
    base_url="https://openrouter.ai/api/v1",
)


# tavily client
tavily_client = TavilyClient(api_key=None)















# ----------------------------------------- sub agents -----------------------------------------

async def get_news_headlines(topic: str, number_of_headlines: int = 3) -> List[str]:
    """
    Collect latest news healines.

    Args:
        topic (str): topic of News
        number_of_headlines (int): total number of news headlines

    Returns:
        List(str): list of latest news of given topic 
    """

    print(f"Collecting news about `{topic}`... ", end="")
    news = await tavily(query=topic, max_results=number_of_headlines)
    print("Done.")

    return [x['content'] for x in news]



async def save_newsletter(news_headlines: str) -> Literal['newsletter saved', 'newsletter not saved due to some error']:
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

async def tavily(query: str, max_results: int = 5) -> List[Dict]:
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



async def newsletter_subagent(task: str):
    """ 
    This is able to create a newsletter and save it.

    Args:
        task (str): task
    """

    response = await newsletter_agent.run(task=task)

    return response 









# --------------------------------------- giant agent ----------------------------------


assistant = AssistantAgent(
    name = "assistant",
    model_client = client,
    tools = [tavily, newsletter_subagent],
    max_tool_iterations=2,
    description = "Main Assistant agent",
    system_message = "You are a helpful agent, you have access of some tools, your always return your responses like a human."
)





async def assistant_run_stream() -> None:

    await Console(
        assistant.on_messages_stream(
            messages= [TextMessage(content='Create a newsletter about tesla',source='User')],
            cancellation_token=CancellationToken()
        ),
        output_stats=True # Enable stats Printing
    )




async def main():

    await assistant_run_stream()






if __name__ == "__main__":

    asyncio.run(main())
    



