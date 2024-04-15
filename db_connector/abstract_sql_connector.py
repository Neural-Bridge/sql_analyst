from abc import ABC, abstractmethod
import pprint
import re
from langchain_community.agent_toolkits.sql.toolkit import BaseToolkit
from langchain_community.tools import BaseTool
from langchain.agents import tool
import pandas as pd
import sqlparse


def maybe_extract_sql(query: str) -> str:
  """Extracts the SQL code from the given query."""
  if "```sql" not in query:
    return query
  return re.findall(r"```sql(.*?)```", query, re.DOTALL)[0].strip()


def validate_sql_statement(sql_code):
  """Check if the SQL code contains only SELECT statements."""
  for statement in sqlparse.parse(sql_code):
    # Check if the parsed statement is not a SELECT statement
    if statement.get_type() != 'SELECT':
      raise ValueError(f"Only SELECT statements are allowed, got: {statement.get_type()}")


class AbstractSQLConnector(BaseToolkit, ABC):
  """
  An abstract base class for SQL connectors.

  This class defines the interface for interacting with SQL databases.
  Subclasses of this class should implement the abstract methods to provide
  specific functionality for a particular SQL database.
  """

  @abstractmethod
  def initialize(self, **kwargs):
    """Initialize the connector. This method will be called before using the connector."""
    pass

  @property
  @abstractmethod
  def dialect(self) -> str:
    """The SQL dialect of the database. This should be a string that represents the SQL dialect of the database."""
    pass

  @abstractmethod
  def table_names(self) -> list[str]:
    """List the allowed names of the tables in the database."""
    pass

  @abstractmethod
  def query(self, query: str) -> pd.DataFrame:
    """Execute the specified query and return the result as a string."""
    pass

  class Config:
    """override pydantic validation to allow implementaions to have extra fields."""
    arbitrary_types_allowed = True
    extra = 'allow'

  @classmethod
  def create(cls, **kwargs):
    """Create an instance of the connector. This method should be used to create an instance of the connector."""
    obj = cls()
    obj.initialize(**kwargs)
    return obj

  def get_tools(self) -> list[BaseTool]:
    """Returns a list of tools that can be used with this connector for AI Agent.

    Note that for the @tool functions below
     - doc will be used by the agent through prompt to understand how this tool works.
     - function name will be passed to agent as tool name.
    """

    @tool
    def list_table_names(args={}) -> str:
      """Comma separated list of the names of the tables in the database."""
      return ",".join(self.table_names())

    @tool
    def get_table_info_and_sample_rows(comma_separated_table_names: str) -> str:
      """ Retrieves information and sample about the specified tables. """
      tables = comma_separated_table_names.split(",")
      result = "Following are the tables with sample data, where the dictionary key is column name, and data is limited to 3 rows:\n\n"
      for table in tables:
        result += f"#### Table: {table}\n\n"
        result += query_database(f"SELECT * FROM {table} LIMIT 3")
        result += "\n\n\n"
      return result

    @tool
    def query_database(query: str) -> str:
      """ Queries the database with the specified query. """
      try:
        query = maybe_extract_sql(query)
        validate_sql_statement(query)
        return pprint.pformat(self.query(query).to_dict('list'), indent=2)
      except Exception as e:
        return f"Error: {e}"
    return [
        list_table_names,
        get_table_info_and_sample_rows,
        query_database
    ]
