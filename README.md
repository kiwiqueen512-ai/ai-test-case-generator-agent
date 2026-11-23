# 🧪 AI Test Case Generator Agent

An Agentic AI web application built with *Python, Streamlit, Ollama (llama3.2), LangChain, SQLite, and Pandas* that converts plain-language software requirements into structured *Positive, Negative, and Edge-Case* test scenarios.

## 🚀 Features
- *Requirement Analysis & Clarity Check:* Detects unclear/vague inputs and asks for clarification before generating test cases.
- *Scenario Selection:* Generates Positive, Negative, and Edge-Case test scenarios with High, Medium, or Low priority.
- *Response Validation:* Validates JSON structure, normalizes test case IDs (TC-01, TC-02, ...), removes duplicates, and retries safely on invalid model responses.
- *Interactive Review & Edit:* Double-click to edit test case fields or delete rows directly inside the UI table.
- *Persistent SQLite History:* Save generated test cases and reload them anytime even after restarting the app.
- *CSV Export:* Export finalized test cases as a clean .csv file using Pandas.

## 🛠️ Tech Stack
- *Frontend:* Streamlit
- *Agent & Orchestration:* LangChain
- *Local LLM:* Ollama (llama3.2)
- *Database:* SQLite3
- *Data Processing & Export:* Pandas

## ⚙️ Setup & Run Instructions
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1