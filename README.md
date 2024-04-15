# sql_analyst


## Installation

Ensure you have Python 3.8+ installed on your system. Follow these steps to set up your environment:

1. **Clone the repository:**

   ```sh
   git clone https://github.com/Neural-Bridge/sql_analyst.git
   cd sql_analyst
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Environment Variables:**

   Duplicate the `env.example` file, rename it to `.env`, and fill in your configuration details such as API keys.
   STREAMLIT_PORT is needed for Docker to start the web app on the given port, it's preset with default port.

   `OPENAI_API_KEY` is required to make the default custom app work but it's not needed for your implementation,
   please remove the row `OPENAI_API_KEY=` in your `.env` file

## Implementing Custom Database Connectors

To integrate a custom database connector, extend the abstract base class provided in the `db_connector` directory.

[Example Implementation](https://github.com/Neural-Bridge/sql_analyst/blob/main/db_connector/sqllite_connector.py)

1. **Create Custom Connector Class:**

   ```python
   # custom_db_connector.py
   from db_connector.abstract_sql_connector import AbstractSQLConnector

   class CustomDBConnector(AbstractSQLConnector):
       ...
   ```

2. **Implement Required Methods:**

   Define the `initialize`, `dialect`, `table_names`, and `query` methods.

   - **Important**: `query` must return a pandas dataframe where the column names are set based on sql query result schema.


## Implementing Custom LLMs

To implement a custom LLM, you will extend the abstract base class provided in the `llms` directory.

[Example Implementation](https://github.com/Neural-Bridge/sql_analyst/blob/main/llms/openai_llm.py)

1. **Create Custom LLM Class:**

   ```python
   # custom_llm.py
   from llms.abstract_llm import AbstractLLM

   class CustomLLM(AbstractLLM):
       ...
   ```

2. **Implement Abstract Methods:**

   Flesh out the `initialize_client` and `call_internal` methods with your custom logic.

## Using the Custom Implementations


1. **Create an agent config:**

   In `config.py`, instantiate your Custom LLM:

   ```python
   # config.py
   from llms.custom_llm import CustomLLM
   from db_connector.custom_db_connector import CustomDBConnector

   ...

   def create_my_config(cls):
     # TODO: Initialize the custom llm and connector, decide if chart should be enabled
     llm = CustomLLM()
     connector = CustomDBConnector.create()
     enable_chart=True

     # Most general prompt and agent type.
     prompt = zero_shot_prompt()
     agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION

     return cls(llm=llm, prompt=prompt, sql_connector=connector, agent_type=agent_type, enable_chart=enable_chart)
   ```

2. **Test Your Config**

    By making following change in `agent_py`.
    ```python
    # agent.py
    ...
    if __name__ == "__main__":
        demo_config = create_my_config()
        ...
    ```
    Then run the following command, make sure the log does not show error, and ends with message "Finished chain."

    ```sh
    python agent.py
    ```

3. **Use Your Config in Web App**

    In the `client.py` update the config to your own config
    ```python
    config = Config.create_my_config()
    ```

## Deployment

### Building the Application

Build the Docker image for your application using the Dockerfile provided in your repository.

```sh
docker build -t yourappname .
```

Replace `yourappname` with the name you prefer for your Docker image.

### Running the Application

Once the image is built, you can run it as a container. To deploy the Streamlit app:

```sh
docker run --env-file .env -p 8501:8501 yourappname
```

This command starts a container instance of your application, forwarding your local port 8501 to the container's port 8501, which is the default for Streamlit apps. It also specifies the `.env` file you prepared earlier to set up the environment variables within the container.

### Accessing the Streamlit App

After running the container, you can access the Streamlit app in your web browser:

```
http://localhost:8501
```

You should now see your SQL Analyst Streamlit application running and ready to accept user queries.

## Generated Code Safety

In our approach to ensuring the safety of dynamically generated code, we employ specific validation techniques for SQL and Python, respectively.
- For Generated SQL, we utilize the `sqlparse` library to analyze and ensure that only `SELECT` type statements are executed. This method helps in preventing unintended data modifications or deletions through SQL operations.

- For Generated Python code, we leverage the `ast` (Abstract Syntax Tree) library to make sure only allowlisted modules are imported.
