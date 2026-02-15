import json

import yaml
from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError


class SpecValidationError(Exception):
    pass


def parse_raw_content(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            return data
    except yaml.YAMLError:
        pass

    raise SpecValidationError("Не удалось распарсить (контент не является валидным JSON или YAML)")


def validate_openapi(spec_dict: dict) -> None:
    if "openapi" not in spec_dict:
        raise SpecValidationError("Отсутствует поле 'openapi' — это не OpenAPI спецификация")

    if "paths" not in spec_dict:
        raise SpecValidationError("Отсутствует поле 'paths' — нет эндпоинтов для генерации тестов")

    try:
        validate(spec_dict)
    except OpenAPIValidationError as e:
        raise SpecValidationError(f"Невалидная OpenAPI спецификация: {e.message}")