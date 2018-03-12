"""Utils tests."""
from utils.memory_consumption import get_memory_consumption


def test_send_slack_message():
    assert get_memory_consumption() > 0
