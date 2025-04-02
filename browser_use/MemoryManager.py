from langchain.memory import ConversationBufferMemory
import os
import json
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
class MemoryManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.short_term_memory = ConversationBufferMemory(return_messages=True)
        path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Chromium", "User Data", "Memory")
        if not os.path.exists(path):
            os.makedirs(path)
        self.long_term_file = os.path.join(path, f"{user_id}_long_term_memory.json")
        self._ensure_long_term_memory_file()

    def _ensure_long_term_memory_file(self):
        if not os.path.exists(self.long_term_file):
            with open(self.long_term_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def as_system_message(self) -> str:
        """
        Converts long-term memory into a string suitable for use as a SystemMessage.
        """
        memory = self.get_long_term_memory()
        if not memory:
            return "No known user information."

        lines = [f"- {v}" for k, v in memory.items()]
        return "Known user information:\n" + "\n".join(lines)

    def get_short_term_messages(self):
        return self.short_term_memory.chat_memory.messages

    def append_user_input(self, message: str):
        self.short_term_memory.chat_memory.add_user_message(message)

    def append_ai_output(self, message: str):
        self.short_term_memory.chat_memory.add_ai_message(message)

    def get_long_term_memory(self) -> dict:
        with open(self.long_term_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_long_term_memory(self, updates: dict):
        data = self.get_long_term_memory()
        data.update(updates)
        with open(self.long_term_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def update_memory(self, llm, text: str):
        existing_memory = self.as_system_message()

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
                self.update_long_term_memory({f"fact_{i}": fact for i, fact in enumerate(facts)})
        except Exception as e:
            print(f"❌ Error updating memory: {e}")