from pydantic import BaseModel


class TestScenario(BaseModel):
    name: str
    description: str
    scenario_type: str
    priority: str
    expected_status_code: int
    request_body: dict | None = None
    request_params: dict | None = None
    request_headers: dict | None = None
    notes: str | None = None


class EndpointTestPlan(BaseModel):
    method: str
    path: str
    summary: str
    scenarios: list[TestScenario]


class AnalysisResult(BaseModel):
    api_title: str
    api_version: str
    base_url: str | None = None
    total_endpoints: int
    total_scenarios: int
    endpoints: list[EndpointTestPlan]