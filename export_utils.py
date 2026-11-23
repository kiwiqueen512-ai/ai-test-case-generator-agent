import pandas as pd


def test_cases_to_dataframe(test_cases: list) -> pd.DataFrame:
    """Convert list of test case dictionaries into a structured Pandas DataFrame."""
    if not test_cases:
        return pd.DataFrame(columns=[
            "test_case_id", "title", "scenario_type",
            "preconditions", "test_steps", "test_data",
            "expected_result", "priority"
        ])

    df = pd.DataFrame(test_cases)
    expected_cols = [
        "test_case_id", "title", "scenario_type",
        "preconditions", "test_steps", "test_data",
        "expected_result", "priority"
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    return df[expected_cols]


def convert_df_to_csv(test_cases: list) -> bytes:
    """Convert test cases into UTF-8 encoded CSV bytes for Streamlit download."""
    df = test_cases_to_dataframe(test_cases)
    df_export = df.rename(columns={
        "test_case_id": "Test Case ID",
        "title": "Test Case Title",
        "scenario_type": "Scenario Type",
        "preconditions": "Preconditions",
        "test_steps": "Test Steps",
        "test_data": "Test Data",
        "expected_result": "Expected Result",
        "priority": "Priority"
    })
    return df_export.to_csv(index=False).encode("utf-8")