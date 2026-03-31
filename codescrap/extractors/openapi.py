import json
import logging

import yaml

from ..networking import fetch_with_retry

logger = logging.getLogger(__name__)


async def extract_openapi(session, api_url: str, config) -> str:
    try:
        data = await fetch_with_retry(session, api_url, config.max_retries)
        text = data.decode("utf-8")

        if api_url.endswith((".yaml", ".yml")):
            spec = yaml.safe_load(text)
        else:
            try:
                spec = json.loads(text)
            except json.JSONDecodeError:
                spec = yaml.safe_load(text)

        return _spec_to_markdown(spec, api_url)

    except Exception as e:
        logger.error(f"Failed to extract OpenAPI spec {api_url}: {e}")
        return (
            f"## Source URL: {api_url}\n"
            f"*Failed to extract OpenAPI spec: {e}*\n\n---\n\n"
        )


def _spec_to_markdown(spec: dict, url: str) -> str:
    lines = [f"## Source URL: {url} (OpenAPI Specification)\n"]

    info = spec.get("info", {})
    title = info.get("title", "API Documentation")
    version = info.get("version", "1.0")
    description = info.get("description", "")

    lines.append(f"### API Name: {title} (Version: {version})\n")
    if description:
        lines.append(f"{description}\n\n")

    paths = spec.get("paths", {})
    if paths:
        lines.append("### Endpoints\n")
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() not in [
                    "get", "post", "put", "delete", "patch", "options", "head"
                ]:
                    continue

                summary = details.get("summary", "No summary provided")
                lines.append(f"#### `{method.upper()}` {path}")
                lines.append(f"**Summary:** {summary}")

                if "description" in details:
                    lines.append(f"**Description:** {details['description']}")

                parameters = details.get("parameters", [])
                if parameters:
                    lines.append("\n**Parameters:**")
                    for param in parameters:
                        if "$ref" in param:
                            lines.append(
                                f"- *(Reference: {param['$ref']})*"
                            )
                            continue
                        name = param.get("name", "Unknown")
                        in_loc = param.get("in", "query")
                        required = "Required" if param.get("required") else "Optional"
                        param_desc = param.get("description", "")
                        lines.append(
                            f"- `{name}` ({in_loc}, {required}): {param_desc}"
                        )

                lines.append("\n")

    lines.append("---\n\n")
    return "\n".join(lines)
