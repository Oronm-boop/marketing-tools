from app.json_utils import extract_json_payload


def test_extract_json_payload_from_markdown_fence():
    payload = extract_json_payload('```json\n{"items":[{"keyword":"SEO"}]}\n```')

    assert payload == {"items": [{"keyword": "SEO"}]}


def test_extract_json_payload_from_thinking_and_array():
    payload = extract_json_payload('<think>hidden</think>\n[{"keyword":"长尾词"}]')

    assert payload == [{"keyword": "长尾词"}]


def test_extract_json_payload_repairs_unescaped_quotes_in_string_value():
    payload = extract_json_payload('{"items":[{"content":"最惊喜的是它的“物理 AI"属性。"}]}')

    assert payload == {"items": [{"content": '最惊喜的是它的“物理 AI"属性。'}]}
