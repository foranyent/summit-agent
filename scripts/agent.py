import anthropic
import json
import os
from dotenv import load_dotenv
from tools import TOOL_DEFINITIONS, TOOL_MAP

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are Sierra, a friendly and knowledgeable customer support agent for Summit Outfitters, an outdoor gear company. You help customers with order questions, returns, product information, and store policies.

You have access to four tools:
- get_order_status: look up any order by ID
- check_return_eligibility: check if an order can be returned
- search_products: search the product catalog
- escalate_to_human: hand off to a human agent when needed

Guidelines:
- Always be warm, helpful, and concise
- If a customer gives you an order number, look it up proactively
- If a question is about a product, search for it before answering
- Escalate to a human if: the customer is upset, the issue is complex, or you can't resolve it with your tools
- Never make up information — use your tools to get accurate data
- When you escalate, briefly explain what you've already done to help
- Keep responses conversational, not overly formal"""


def run_agent(conversation_history: list) -> str:
    """
    Run one turn of the agent loop.
    Handles tool calls automatically until a final text response is ready.
    Returns the assistant's final text response.
    """
    messages = conversation_history.copy()

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages
        )

        # If Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Add Claude's response (which includes tool use blocks) to history
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    # Call the actual tool function
                    tool_fn = TOOL_MAP.get(tool_name)
                    if tool_fn:
                        result = tool_fn(**tool_input)
                    else:
                        result = {"error": f"Unknown tool: {tool_name}"}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            # Add tool results back into the conversation
            messages.append({"role": "user", "content": tool_results})

        # Claude is done — extract and return the text response
        elif response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        else:
            return "Something unexpected happened. Please try again."
