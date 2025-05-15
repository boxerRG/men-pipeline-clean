from men_pipeline import qwen_dispatcher

def test_run_prompt_mock(monkeypatch):
    def fake_dispatch(prompt, key_idx=0):
        return {"role": "assistant", "content": "Fake response"}
    monkeypatch.setattr(qwen_dispatcher, "dispatch_to_qwen", fake_dispatch)
    response = qwen_dispatcher.run_prompt("Czym jest grawitacja?")
    assert "content" in response
