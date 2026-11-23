from langchain_core.prompts import ChatPromptTemplate

AGENT_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert QA Software Testing Agent.
Analyze the user's software requirement and return ONLY a valid JSON object (no markdown, no backticks, no extra text).

Rules:
1. Check if the requirement is clear enough to write software test cases. If it is gibberish, single random word, or completely vague (e.g., "test", "hello", "make app"), set "is_clear" to false and provide a helpful "clarification_message".
2. If clear, set "is_clear" to true, identify the "feature_name", summarize the main testing purpose in "feature_summary", list any reasonable "assumptions" (do not invent strict business rules not stated), and select suitable "scenario_categories" from ["Positive", "Negative", "Edge Case"].

Return strictly this JSON structure:
{{
  "is_clear": true,
  "clarification_message": "",
  "feature_name": "Feature Name",
  "feature_summary": "Brief summary of what needs to be tested",
  "assumptions": ["Assumption 1 if any"],
  "scenario_categories": ["Positive", "Negative", "Edge Case"]
}}"""),
    ("human", "Software Requirement:\n{requirement}")
])

TEST_CASE_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior QA Engineer. Generate structured, non-duplicate software test cases based ONLY on the given requirement and selected scenario categories.

Strict Rules:
1. Return ONLY a valid JSON array of test case objects. No markdown formatting, no ```json wrappers, no introductory text.
2. Cover the selected scenario categories: {scenario_categories}.
3. Do not invent strict rules not mentioned in the requirement; note any assumptions clearly in preconditions.
4. Priority MUST be strictly one of: "High", "Medium", or "Low".
5. Scenario Type MUST be strictly one of: "Positive", "Negative", or "Edge Case".
6. Generate 5 to 8 concise, practical, non-duplicate test cases.

Each object in the JSON array MUST follow this exact schema:
[
  {{
    "test_case_id": "TC-01",
    "title": "Short descriptive title",
    "scenario_type": "Positive",
    "preconditions": "Required initial state or assumptions",
    "test_steps": "1. Step one\\n2. Step two",
    "test_data": "Specific input values used",
    "expected_result": "Clear expected system behavior",
    "priority": "High"
  }}
]"""),
    ("human", """Requirement: {requirement}
Feature Summary: {feature_summary}
Scenario Categories to Cover: {scenario_categories}""")
])