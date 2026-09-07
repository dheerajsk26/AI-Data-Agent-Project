from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

def pick_llm(level: str):
    """
    Picks the appropriate Claude LLM based on the level of the question.
    Args:
        level (str): The level of the question, can be "low", "medium", or "high".
    Returns:
        ChatAnthropic: The LLM instance to be used.
    """
    if level.lower() == "low":
        llm = ChatAnthropic(model_name="claude-haiku-4-5-20251001", temperature=0)
    elif level.lower() == "medium":
        # temperature/top_p/top_k are removed on claude-sonnet-5 (400 if sent) - omit entirely
        llm = ChatAnthropic(model_name="claude-sonnet-5")
    elif level.lower() == "high":
        # temperature/top_p/top_k are removed on claude-opus-5 (400 if sent) - omit entirely
        llm = ChatAnthropic(model_name="claude-opus-5")
    else:
        raise ValueError(f"Unsupported level: {level}")
    return llm

if __name__ == "__main__":
    llm_obj = pick_llm("low")
    print(llm_obj.invoke("What is the capital of France?"))