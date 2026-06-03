from app.json_utils import extract_json_payload


def test_extract_json_payload_from_markdown_fence():
    payload = extract_json_payload('```json\n{"items":[{"keyword":"SEO"}]}\n```')

    assert payload == {"items": [{"keyword": "SEO"}]}


def test_extract_json_payload_from_thinking_and_array():
    payload = extract_json_payload('<think>hidden</think>\n[{"keyword":"长尾词"}]')

    assert payload == [{"keyword": "长尾词"}]

