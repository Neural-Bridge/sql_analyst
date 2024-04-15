"""This module contains SQLAgent Class."""
import os
from config import EXAMPLE, Config
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from typing import Any, Dict, Optional

from agent_utils.extra_tools import visualize_data


def set_env_vars(env_file_path='.env'):
  """Read the file and set environment variables."""
  with open(env_file_path, 'r') as file:
    for line in file:
      key, value = line.strip().split('=', 1)
      if not value:
        raise ValueError(
          f"Invalid value for environment variable: {key}\n Please double check the .env file.")
      os.environ[key] = value


set_env_vars('.env')

set_llm_cache(SQLiteCache(database_path="data/.langchain.db"))


class SQLAgent():
  """
  Agent to convert user queries into sql queries and process results.

  Attributes:
    config (Config): The configuration settings for the agent.
  """

  def __init__(self, config: Config):
    """
    Initializes the SQLAgent.

    Args:
      config (Config): The configuration for processing queries.
    """
    self.agent_executor = create_sql_agent(llm=config.llm,
                                           toolkit=config.sql_connector,
                                           agent_type=config.agent_type,
                                           max_iterations=10,
                                           prompt=config.prompt,
                                           verbose=True,
                                           extra_tools=[
                                             visualize_data] if config.enable_chart else [],
                                           agent_executor_kwargs={
                                               "return_intermediate_steps": True,
                                               "handle_parsing_errors": True,
                                           })

  def run(self, user_query: str,
          st_callback: Optional[StreamlitCallbackHandler] = None) -> Dict[str, Any]:
    """
    Processes a user query and returns a list of processing steps.

    Args:
      user_query (str): The user query to process.

    Returns:
      Result of the agent invocation.
    """
    if st_callback:
      return self.agent_executor.invoke(user_query, config=RunnableConfig(callbacks=[st_callback]))

    return self.agent_executor.invoke(user_query)


# DEMO
if __name__ == "__main__":
  demo_config = Config.create_custom_openai_custom_sqllite_with_chart()
  demo_sql_agent = SQLAgent(config=demo_config)
  demo_sql_agent.run(EXAMPLE.query)
