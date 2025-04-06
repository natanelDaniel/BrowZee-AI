from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

async def update_memory(llm, text: str, memory_manager) -> list[str]:
    existing_memory = memory_manager.as_system_message()

    prompt = f"""
    You are a memory agent. Your task is to extract any important new facts about the user or the world that should be remembered long term.
    
    Existing memory:
    \"\"\"{existing_memory}\"\"\"
    
    New text:
    \"\"\"{text}\"\"\"
    
    Return only new facts that are not already known. Respond with a list of concise facts. If nothing new, return an empty list.
    """
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    try:
        facts = response.content.strip().splitlines()
        facts = [f.strip('- ').strip() for f in facts if f.strip()]
        if facts:
            memory_manager.update_long_term_memory({f"fact_{i}": fact for i, fact in enumerate(facts)})
        return facts
    except Exception as e:
        print(f"❌ Error updating memory: {e}")
        return []