from pydantic import BaseModel


class GeneratedTest(BaseModel):
    endpoint_method: str
    endpoint_path: str
    test_code: str


class GenerationResult(BaseModel):
    api_title: str
    total_tests: int
    tests: list[GeneratedTest]