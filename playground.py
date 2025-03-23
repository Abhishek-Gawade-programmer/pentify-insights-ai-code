from agno.playground import Playground, serve_playground_app

from agents import get_sql_agent


app = Playground(agents=[get_sql_agent()]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
