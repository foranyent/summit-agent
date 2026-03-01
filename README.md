# Summit Outfitters AI Support Agent

An AI-powered customer support agent built with the Anthropic API and Streamlit. Demonstrates autonomous tool use, multi-turn conversation, and human escalation logic.

## Features
- Order status lookup
- Return eligibility checking
- Product catalog search
- Automatic escalation to human agents with conversation logging

## Stack
- Python
- Anthropic API (Claude) with tool use
- Streamlit

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Set your Anthropic API key:
```
export ANTHROPIC_API_KEY=your_key_here
```

3. Run the app:
```
streamlit run app.py
```

## Demo Scenarios
- "Can you check on order SO-1042?"
- "I want to return my tent from order SO-1031, is it too late?"
- "What rain jackets do you carry?"
- "I've been waiting 3 weeks and nobody will help me" (triggers escalation)
