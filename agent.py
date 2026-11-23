import json
from langchain_ollama import ChatOllama
from prompts import AGENT_ANALYSIS_PROMPT
from test_case_generator import clean_json_response, generate_test_cases


def run_test_case_agent(requirement: str, selected_categories: list = None, model_name: str = "llama3.2") -> dict:
    """
    Agent workflow:
    1. Validate requirement is not empty.
    2. Analyze requirement intent, clarity, assumptions, and scenario categories.
    3. Generate and validate structured test cases.
    """
    if not requirement or not requirement.strip():
        return {
            "status": "error",
            "message": "Please enter a software requirement before generating test cases."
        }

    try:
        llm = ChatOllama(model=model_name, temperature=0.1)
        analysis_chain = AGENT_ANALYSIS_PROMPT | llm
        raw_analysis = analysis_chain.invoke({"requirement": requirement.strip()})
        cleaned_analysis = clean_json_response(raw_analysis.content)
        analysis = json.loads(cleaned_analysis)
    except Exception:
        # Safe fallback if analysis JSON fails to parse
        analysis = {
            "is_clear": len(requirement.strip().split()) >= 3,
            "clarification_message": "Your requirement seems too short or unclear. Please describe the software feature and expected behavior in a complete sentence.",
            "feature_name": "Software Feature",
            "feature_summary": requirement.strip(),
            "assumptions": [],
            "scenario_categories": ["Positive", "Negative", "Edge Case"]
        }

    if not analysis.get("is_clear", True):
        return {
            "status": "clarification_needed",
            "message": analysis.get(
                "clarification_message",
                "The requirement is unclear. Please provide more details about the feature, inputs, and expected behavior."
            )
        }

    categories = selected_categories if selected_categories else analysis.get(
        "scenario_categories", ["Positive", "Negative", "Edge Case"]
    )
    feature_name = analysis.get("feature_name", "Software Feature")
    feature_summary = analysis.get("feature_summary", requirement.strip())
    assumptions = analysis.get("assumptions", [])

    try:
        test_cases = generate_test_cases(
            requirement=requirement.strip(),
            feature_summary=feature_summary,
            scenario_categories=categories,
            model_name=model_name
        )
        return {
            "status": "success",
            "feature_name": feature_name,
            "feature_summary": feature_summary,
            "assumptions": assumptions,
            "scenario_categories": categories,
            "test_cases": test_cases
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Local LLM error while generating test cases: {str(e)}. Make sure Ollama is running with '{model_name}'."
        }