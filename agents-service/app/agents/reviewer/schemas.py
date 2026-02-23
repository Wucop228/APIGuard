from pydantic import BaseModel


class TestReview(BaseModel):
    endpoint_method: str
    endpoint_path: str
    score: int
    issues: list[str]
    suggestions: list[str]
    improved_test_code: str


class ReviewResult(BaseModel):
    api_title: str
    overall_score: int
    total_issues: int
    reviews: list[TestReview]
    summary: str