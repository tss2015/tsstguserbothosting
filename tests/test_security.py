from utils.security import valid_chat_id, redact

def test_chat_id():
    assert valid_chat_id("-1001234567890")
    assert not valid_chat_id("abc")

def test_redact():
    assert "secret" not in redact("session=secret")
