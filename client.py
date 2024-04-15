from config import EXAMPLE, Config
from streamlit_lib.constants import HIDE_STREAMLIT_STYLE, FAVICON_B64
from agent import SQLAgent
from streamlit_lib.streamlit_handler import CallbackHandlerWithVisualization
import streamlit as st

# Update config here for the web App
config = Config.create_custom_openai_custom_sqllite_with_chart()

st.set_page_config(page_title="SQL Agent",
                   page_icon=f"data:image/png;base64,{FAVICON_B64}")
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

st.title("SQL Agent")

query = st.text_input("Query", EXAMPLE.query)

if st.button("Submit"):
  if not query:
    st.warning("Please enter a query.")
  else:
    with st.spinner("Processing..."):
      try:
        sql_agent = SQLAgent(config=config)
        st_callback = CallbackHandlerWithVisualization(st.container())
        sql_agent.run(user_query=query, st_callback=st_callback)
      except Exception as e:
        st.error(f"An error occured, please try again\n {e}")
