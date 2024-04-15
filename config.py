
from typing import Literal, Union, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_community.agent_toolkits.sql.base import SQLDatabaseToolkit
from langchain_core.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain.agents.agent_types import AgentType
from llms.openai_llm import OpenAILLM
from langchain.sql_database import SQLDatabase
from pydantic.v1 import BaseModel
from db_connector.sqllite_connector import SQLLiteConnector
from agent_utils.prompts import zero_shot_prompt
# Model Names
GPT4_TURBO = "gpt-4-0125-preview"
GPT35_TURBO = "gpt-3.5-turbo-0125"
CLAUDE_3_OPUS = "claude-3-opus-20240229"

# Tool Names
AGENT_TYPE_OPENAI_TOOLS = "openai-tools"


class SqlliteExample(BaseModel):
  db_url: str
  query: str


_CHINOOK_SQL_EXAMPLE = SqlliteExample(
  db_url="sqlite:///data/Chinook.db",
  query="Count the number of tracks in each album by \"Queen\" and rank the albums by track count.")

# Test Sqlite Paths
EXAMPLE = _CHINOOK_SQL_EXAMPLE


class Config(BaseModel):
  """
  A configuration class for SQLAgent that encapsulates the settings
  and components required for its operation.

  Attributes:
    llm (BaseLanguageModel): The language model to be used by the SQLAgent.
    prompt: Optional[PromptTemplate]: An optional template for generating prompts.
    sql_connector (BaseToolkit): The SQL database connector used by the SQLAgent.
    agent_type (Union[AgentType, Literal["openai-tools"]]): Specifies the type of agent.
  """
  llm: BaseLanguageModel
  prompt: Optional[PromptTemplate] = None
  sql_connector: BaseToolkit
  agent_type: Union[AgentType, Literal["openai-tools"]]
  enable_chart: Optional[bool] = False

  @classmethod
  def create_default(cls):
    llm = ChatOpenAI(model=GPT4_TURBO, temperature=0)
    sql_connector = SQLDatabaseToolkit(llm=llm, db=SQLDatabase.from_uri(EXAMPLE.db_url))
    agent_type = AGENT_TYPE_OPENAI_TOOLS
    return cls(llm=llm, sql_connector=sql_connector, agent_type=agent_type)

  @classmethod
  def create_default_openai_custom_sqllite(cls):
    llm = ChatOpenAI(model=GPT4_TURBO, temperature=0)
    sql_connector = SQLLiteConnector.create(db_url=EXAMPLE.db_url)
    agent_type = AGENT_TYPE_OPENAI_TOOLS
    return cls(llm=llm, sql_connector=sql_connector, agent_type=agent_type)

  @classmethod
  def create_default_anthropic_custom_sqlite(cls):
    llm = ChatAnthropic(temperature=0, model_name=CLAUDE_3_OPUS)
    prompt = zero_shot_prompt()
    sql_connector = SQLLiteConnector.create(db_url=EXAMPLE.db_url)
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
    return cls(llm=llm, prompt=prompt, sql_connector=sql_connector, agent_type=agent_type)

  @classmethod
  def create_custom_openai_default_sqllite(cls):
    llm = OpenAILLM()
    prompt = zero_shot_prompt()
    sql_connector = SQLDatabaseToolkit(llm=llm, db=SQLDatabase.from_uri(EXAMPLE.db_url))
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
    return cls(llm=llm, prompt=prompt, sql_connector=sql_connector, agent_type=agent_type)

  @classmethod
  def create_custom_openai_custom_sqllite(cls):
    llm = OpenAILLM()
    prompt = zero_shot_prompt()
    sql_connector = SQLLiteConnector.create(db_url=EXAMPLE.db_url)
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
    return cls(llm=llm, prompt=prompt, sql_connector=sql_connector, agent_type=agent_type)

  @classmethod
  def create_custom_openai_custom_sqllite_with_chart(cls):
    llm = OpenAILLM()
    prompt = zero_shot_prompt()
    sql_connector = SQLLiteConnector.create(db_url=EXAMPLE.db_url)
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
    return cls(llm=llm, prompt=prompt, sql_connector=sql_connector, agent_type=agent_type, enable_chart=True)
