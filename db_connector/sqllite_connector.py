from typing import Optional

import pandas as pd
from db_connector.abstract_sql_connector import AbstractSQLConnector
from sqlalchemy import create_engine, MetaData, Engine
from sqlalchemy import text


class SQLLiteConnector(AbstractSQLConnector):
  """A class representing a SQLLite database connector."""

  engine: Optional[Engine]
  metadata: Optional[MetaData]

  def initialize(self, db_url: str):
    self.engine = create_engine(db_url)
    self.metadata = MetaData()

  def dialect(self) -> str:
    return 'sqlite'

  def table_names(self) -> list[str]:
    """Uses the sql lite db metadata to return all the tables."""
    self.metadata.reflect(bind=self.engine)
    table_names = list(self.metadata.tables.keys())
    return table_names

  def query(self, query: str) -> pd.DataFrame:
    """Run the query and compile the results into a pandas dataframe."""
    with self.engine.connect() as connection:
      result = connection.execute(text(query))
      return pd.DataFrame(result.fetchall(), columns=result.keys())
