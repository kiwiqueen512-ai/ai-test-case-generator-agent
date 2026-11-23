import json
import re
from langchain_ollama import ChatOllama
from prompts import TEST_CASE_GENERATION_PROMPT

VALID_PRIORITIES = {"High", "Medium", "Low"}
VALID_SCENARIOS = {"Positive", "Negative", "Edge Case"}


def clean_json_response(raw_text: str) -> str:
    """Strip markdown code fences if the LLM includes them."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*$", "", cleaned)
    return cleaned.strip()


def validate_and_normalize_test_cases(raw_list: list) -> list:
    """Validate required fields, normalize IDs, scenarios, and priorities."""
    if not isinstance(raw_list, list) or len(raw_list) == 0:
        raise ValueError("Model did not return a valid list of test cases.")

    validated = []
    seen_titles = set()

    for idx, item in enumerate(raw_list, start=1):
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", f"Test Case {idx}")).strip()
        if not title or title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())

        scenario = str(item.get("scenario_type", "Positive")).strip().title()
        if scenario == "Edgecase" or scenario == "Edge-Case":
            scenario = "Edge Case"
        if scenario not in VALID_SCENARIOS:
            scenario = "Positive"

        priority = str(item.get("priority", "Medium")).strip().title()
        if priority not in VALID_PRIORITIES:
            priority = "Medium"

        preconditions = str(item.get("preconditions", "System is accessible.")).strip()
        test_steps = str(item.get("test_steps", "1. Execute action")).strip()
        test_data = str(item.get("test_data", "N/A")).strip()
        expected_result = str(item.get("expected_result", "Expected behavior occurs.")).strip()

        validated.append({
            "test_case_id": f"TC-{len(validated) + 1:02d}",
            "title": title,
            "scenario_type": scenario,
            "preconditions": preconditions,
            "test_steps": test_steps,
            "test_data": test_data,
            "expected_result": expected_result,
            "priority": priority
        })

    if not validated:
        raise ValueError("No valid test cases remained after validation.")

    return validated


def generate_test_cases(requirement: str, feature_summary: str, scenario_categories: list, model_name: str = "llama3.2") -> list:
    """Invoke local Ollama LLM via LangChain to generate and validate test cases."""
    llm = ChatOllama(model=model_name, temperature=0.2)
    chain = TEST_CASE_GENERATION_PROMPT | llm

    categories_str = ", ".join(scenario_categories)
    last_error = None

    # Safe retry up to 2 attempts in case of invalid JSON formatting from local LLM
    for attempt in range(2):
        try:
            response = chain.invoke({
                "requirement": requirement,
                "feature_summary": feature_summary,
                "scenario_categories": categories_str
            })
            cleaned_text = clean_json_response(response.content)
            parsed_data = json.loads(cleaned_text)
            return validate_and_normalize_test_cases(parsed_data)
        except Exception as e:
            last_error = e

    raise RuntimeError(f"Failed to generate valid test cases from local LLM: {last_error}")