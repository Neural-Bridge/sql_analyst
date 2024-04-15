
"""This module contains SQLAgent Class."""
from ast import literal_eval
import ast
from langchain.agents import tool
import pandas as pd
import re

SAFE_IMPORTS = set(["matplotlib.pyplot",
                    "pandas",
                    "BytesIO",
                    "base64"])


def parse_to_df_and_code(data_and_charting_code: str) -> tuple:
  """
  This is corresponding to visualize_data tool description.

  Args:
    data_and_charting_code (str): The input string containing data and charting code.

  Returns:
    tuple: A tuple containing a pandas DataFrame and the extracted code block.

  Raises:
    ValueError: If the input string contains more than one dataframe or code block,
      or if the data is not in dictionary format.
  """
  # Transform Data
  datas = re.findall(r"<df>(.*?)</df>", data_and_charting_code, re.DOTALL)
  if len(datas) != 1:
    raise ValueError(f"Error: Generated {len(datas)} dataframes but expected 1.")
  data = literal_eval(datas[0])
  if not isinstance(data, dict):
    return ValueError("Error: Input is not data in dictionary format.")
  df = pd.DataFrame(data)

  # Transform Code block
  code_blocks = re.findall(r"```python(.*?)```", data_and_charting_code, re.DOTALL)
  if len(code_blocks) != 1:
    return ValueError(f"Error: Generated {len(code_blocks)} codeblocks but expected 1.")
  return df, code_blocks[0].strip()


def validate_imports(chart_code):
  tree = ast.parse(chart_code)
  for node in ast.walk(tree):
    if not isinstance(node, ast.Import) and not isinstance(node, ast.ImportFrom):
      continue
    for alias in node.names:
      if alias.name not in SAFE_IMPORTS:
        raise Exception(f"Use of {alias.name} module is not allowed")


@tool
def visualize_data(data_and_charting_code: str) -> str:
  """ Visualize the data with matplotlib via python_charting_code, return an html as string.

  This should usually be run after a successful query of the database.

  Example Input:

  <df>{dict_str_of_dataframe}</df>

  <chart>```python
  import matplotlib.pyplot as plt
  import pandas as pd
  import base64
  from io import BytesIO

  # Assume `df` is initialized already
  {python_charting_code}

  html_str = ...
  ```
  </chart>


  Args:
    data_and_charting_code (str): a string that has two xml objects following the example input.
      - dict_str_of_dataframe (dict): A string representation of a dictionary of the dataframe.
      - python_charting_code (str): The python that uses provided imports in example input to create chart.
          - Do not create `df` again in the python code, `df` is already initialized.
          - Do not show the chart with plt.show(), save it to a svg_buffer then put it in an `html_str` variable
          - fig size should not exceed 7x7
  """
  try:
    df, code = parse_to_df_and_code(data_and_charting_code)
    validate_imports(code)
    namespace = {'df': df}
    exec(code, namespace, namespace)
    html_output = namespace['html_str']
  except Exception as e:
    return f"Error: {e}"
  return html_output
