from ast import literal_eval
import re
import pandas as pd
import sqlparse
from langchain.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler
from langchain_core.agents import AgentFinish
from langchain_core.outputs import LLMResult
from typing import Any, Dict, Optional, Union

from agent_utils.extra_tools import parse_to_df_and_code
from db_connector.abstract_sql_connector import maybe_extract_sql


THOUGHT_PREFIX = "Thought: "


def get_first_thought(text):
  for line in text.strip().split('\n'):
    if line.startswith(THOUGHT_PREFIX):
      return line[len(THOUGHT_PREFIX):]
  raise ValueError("No line starting with 'Thought' found")


def to_markdown_table(d: Union[str, dict, pd.DataFrame]) -> str:
  if isinstance(d, pd.DataFrame):
    df = d
  elif isinstance(d, dict):
    df = pd.DataFrame(d)
  else:
    df = pd.DataFrame(literal_eval(d))

  html = df.to_html(index=False)
  return "<div style = \"overflow-x: auto; font-size: 12px;\" >" + html + "</div>"


def replace_dict_to_markdown_table(text: str) -> str:
  dict_strings = re.findall(r"\{[^}]*\}", text)
  markdown_strings = [to_markdown_table(d) for d in dict_strings]
  for i, d in enumerate(dict_strings):
    text = text.replace(d, markdown_strings[i])
  return text


def format_input_str_based_on_tool(tool_name: str, input_str: str) -> str:
  if tool_name == 'query_database':
    input_str = maybe_extract_sql(input_str)
    return f"```sql\n{sqlparse.format(input_str, reindent=True, keyword_case='upper')}\n```"
  elif tool_name == 'visualize_data':
    try:
      df, code = parse_to_df_and_code(input_str)
      return f"#### Data\n\n{to_markdown_table(df)}\n\n#### Code\n\n```python\n{code}\n```"
    except Exception as e:
      return f"Error: {e}"
  else:
    return f"```\n{input_str}\n```\n"


def center_chart_html(chart_html):
  return f"""<div style="display: flex; justify-content: center; align-items: center;">{chart_html}</div>"""


class CallbackHandlerWithVisualization(StreamlitCallbackHandler):
  """A custom callback handler that renders the agent output."""

  def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
    """Add thoughts to the block"""
    thought_str = f"### Thought\n\n{get_first_thought(response.generations[0][0].text)}\n\n"
    self._require_current_thought()._container.markdown(thought_str)
    self._prune_old_thought_containers()

  def on_tool_start(
      self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
  ) -> None:
    """Parses input block and renders sql code."""
    self._require_current_thought().on_tool_start(serialized, input_str, **kwargs)
    tool_name = serialized["name"]
    input_str = f"### Input\n{format_input_str_based_on_tool(tool_name,input_str)}\n"
    self._require_current_thought()._container.markdown(input_str, unsafe_allow_html=True)
    self._prune_old_thought_containers()

  def on_tool_end(
          self,
          output: Any,
          color: Optional[str] = None,
          observation_prefix: Optional[str] = None,
          llm_prefix: Optional[str] = None,
          **kwargs: Any,):
    """Renders the tool outptu to markdown tables."""
    if self._current_thought._last_tool.name == 'visualize_data':
      output_str = center_chart_html(output)
    else:
      output_str = replace_dict_to_markdown_table(str(output))

    self._require_current_thought()._container.markdown(
      f"### Output\n\n{output_str}\n\n___", unsafe_allow_html=True)
    self._complete_current_thought()

  def on_agent_finish(
      self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
  ) -> None:
    """Adds the final answer."""
    super().on_agent_finish(finish, color, **kwargs)
    self._parent_container.markdown(f"## Answer\n\n{finish.return_values['output']}\n___")
