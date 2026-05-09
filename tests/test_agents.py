import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import agents


def test_call_uses_hermes_subprocess_with_combined_prompt(monkeypatch):
    calls = []

    def fake_run(cmd, input=None, capture_output=None, text=None, encoding=None, timeout=None):
        calls.append(
            {
                "cmd": cmd,
                "input": input,
                "capture_output": capture_output,
                "text": text,
                "encoding": encoding,
                "timeout": timeout,
            }
        )
        return subprocess.CompletedProcess(cmd, 0, stdout="result\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    output = agents._call("SYSTEM PROMPT", "USER MESSAGE", "test-model")

    assert output == "result"
    assert calls[0]["cmd"][:3] == ["hermes", "chat", "-q"]
    assert "claude" not in calls[0]["cmd"]
    assert "--model" in calls[0]["cmd"]
    assert "test-model" in calls[0]["cmd"]
    assert "SYSTEM PROMPT" in calls[0]["cmd"][3]
    assert "USER MESSAGE" in calls[0]["cmd"][3]
    assert calls[0]["input"] is None


def test_call_raises_backend_specific_error_on_failure(monkeypatch):
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 2, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        agents._call("system", "user", "")
    except RuntimeError as exc:
        assert "Hermes CLI error" in str(exc)
        assert "boom" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
