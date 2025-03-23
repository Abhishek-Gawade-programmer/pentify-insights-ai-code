from agents import agent_knowledge
from agno.utils.log import logger


def load_knowledge(recreate: bool = True):
    logger.info("Loading Collaborate Global knowledge base.")
    agent_knowledge.load(recreate=recreate)
    logger.info("Collaborate Global knowledge base loaded.")


if __name__ == "__main__":
    load_knowledge()
