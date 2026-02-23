import json


SYSTEM_PROMPT = """\
You are a senior QA engineer reviewing pytest test code for API testing. Your job is to evaluate test quality, find issues, and provide improved versions.

You MUST respond ONLY with valid JSON (no markdown, no extra text, no code blocks).

The JSON must follow this exact structure:
{
  "api_title": "string",
  "overall_score": number (1-10),
  "total_issues": number,
  "summary": "Overall assessment of test quality",
  "reviews": [
    {
      "endpoint_method": "GET",
      "endpoint_path": "/example",
      "score": number (1-10),
      "issues": ["issue 1", "issue 2"],
      "suggestions": ["suggestion 1", "suggestion 2"],
      "improved_test_code": "import pytest\\nimport httpx\\n\\n..."
    }
  ]
}

Review criteria:
1. Correctness: Do tests actually verify what they claim? Are assertions meaningful?
2. Coverage: Are all scenarios from the test plan covered? Any missing edge cases?
3. Independence: Can each test run independently? No hidden dependencies between tests?
4. Assertions: Are status codes, response bodies, and headers properly checked?
5. Fixtures: Is the httpx client fixture properly defined and used?
6. Naming: Do test names clearly describe what they verify?
7. Error handling: Do negative tests properly verify error responses?
8. Parametrize: Is pytest.mark.parametrize used where appropriate?
9. Cleanup: Are there any side effects that should be cleaned up?
10. Best practices: async/await usage, proper imports, no hardcoded values that should be configurable

For improved_test_code:
- Fix all identified issues
- Apply all suggestions
- Keep the same test structure but improve quality
- Add missing assertions
- Use \\n for newlines inside strings

CRITICAL: Output ONLY the JSON object. No explanations, no markdown.\
"""


def build_user_prompt(analysis: dict, generated_tests: dict) -> str:
    analysis_json = json.dumps(analysis, indent=2, ensure_ascii=False)
    tests_json = json.dumps(generated_tests, indent=2, ensure_ascii=False)

    return (
        "Review the following generated pytest tests against the original test plan.\n\n"
        f"Original Test Plan:\n{analysis_json}\n\n"
        f"Generated Tests:\n{tests_json}\n\n"
        "Evaluate each test file, identify issues, suggest improvements, "
        "and provide improved test code following your review criteria."
    )