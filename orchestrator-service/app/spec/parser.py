def parse_openapi(spec_dict: dict) -> dict:
    info = spec_dict.get("info", {})
    servers = spec_dict.get("servers", [])
    paths = spec_dict.get("paths", {})
    components = spec_dict.get("components", {})
    security_schemes = components.get("securitySchemes", {})

    endpoints = []

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options"):
                continue

            endpoint = {
                "path": path,
                "method": method.upper(),
                "operation_id": details.get("operationId"),
                "summary": details.get("summary"),
                "description": details.get("description"),
                "tags": details.get("tags", []),
                "parameters": details.get("parameters", []),
                "request_body": details.get("requestBody"),
                "responses": details.get("responses", {}),
                "security": details.get("security"),
            }
            endpoints.append(endpoint)

    return {
        "info": {
            "title": info.get("title", "Unknown API"),
            "version": info.get("version", "0.0.0"),
            "description": info.get("description"),
        },
        "servers": servers,
        "endpoints": endpoints,
        "security_schemes": security_schemes,
        "total_endpoints": len(endpoints),
    }