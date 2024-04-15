from llms.abstract_llm import AbstractLLM
import openai


class OpenAILLM(AbstractLLM):
  """
  This class extends the AbstractLLM class and calls the openai models expclicitly.
  """

  def initialize_client(self):
    """Initialize but actually do nothing here."""
    print('openai model initialized')

  def call_internal(self, messages: list, **kwargs):
    """calls the openai api and returns the response.

    Args:
      messages (list): list of the messages in the conversation. Generally just one.

    The message dict will generally have two keys: role and content. e.g.
        [{'role': 'user', 'content': 'Hello, how are you?'}]

    """
    client = openai.Client()
    print([m.keys()for m in messages])
    # In this case it already matches the openai format therefore no need to convert.
    openai_messages = messages
    completion = client.chat.completions.create(model="gpt-4-turbo",
                                                messages=openai_messages,
                                                temperature=0)
    return completion.choices[0].message.content


# DEMO
if __name__ == "__main__":

  openai_llm: OpenAILLM = OpenAILLM()

  res = openai_llm.invoke("hello how are you")

  print(res)
