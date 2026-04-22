#!/usr/bin/env python3
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, 'scripts')

from run_agent import (
    DEFAULT_LEVITY_REFERENCE_VENDOR,
    build_mi_list_from_ems_and_catalog,
    create_chat_completion_with_model_fallback,
    estimate_usage_cost,
    load_instruction_entries,
    search_manual_with_levity,
    slugify_for_filename,
)


def test_load_instruction_entries_from_xlsx(tmp_path, monkeypatch):
    instructions_dir = tmp_path / "inputs" / "Instructions"
    instructions_dir.mkdir(parents=True)

    df = pd.DataFrame(
        [
            {
                "Item Class": "Pump, Centrifugal",
                "Item Class Description": "Centrifugal process pump",
                "Scope": "Transfer process fluid",
            },
            {
                "Item Class": "Compressor, Screw",
                "Item Class Description": "Gas compression package",
                "Scope": "Compress fuel gas",
            },
        ]
    )
    xlsx_path = instructions_dir / "instructions.xlsx"
    df.to_excel(xlsx_path, index=False)

    monkeypatch.chdir(tmp_path)
    entries = load_instruction_entries()

    assert len(entries) == 2
    assert entries[0]["item_class"] == "Pump, Centrifugal"
    assert entries[0]["item_class_description"] == "Centrifugal process pump"
    assert entries[1]["item_class"] == "Compressor, Screw"
    assert entries[1]["scope"] == "Compress fuel gas"


def test_search_manual_with_levity_parses_results(monkeypatch):
    class DummyResponse:
        status_code = 200

        def json(self):
            return {
                "results": [
                    {
                        "text": "Manual section A",
                        "url": "https://example.com/manual-a",
                    },
                    {
                        "content": "Manual section B",
                        "url": "https://example.com/manual-b",
                    },
                ]
            }

    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("run_agent.httpx.post", fake_post)
    monkeypatch.setenv("LEVITY_API_URL", "https://levity.example/search")

    text, source = search_manual_with_levity(
        api_key_levity="levity-token",
        item_class="Pump, Centrifugal",
        item_class_description="Centrifugal process pump",
        scope="Transfer fluid",
    )

    assert "Manual section A" in text
    assert "Manual section B" in text
    assert source == "https://example.com/manual-a"
    assert captured["url"] == "https://levity.example/search"
    assert captured["headers"]["Authorization"] == "Bearer levity-token"
    assert "Pump, Centrifugal" in captured["json"]["query"]
    assert DEFAULT_LEVITY_REFERENCE_VENDOR in captured["json"]["query"]
    assert captured["json"]["reference_vendor"] == DEFAULT_LEVITY_REFERENCE_VENDOR


def test_search_manual_with_levity_uses_env_overrides(monkeypatch):
    class DummyResponse:
        status_code = 200

        def json(self):
            return {"text": "Manual section override"}

    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["json"] = json
        return DummyResponse()

    monkeypatch.setattr("run_agent.httpx.post", fake_post)
    monkeypatch.setenv("LEVITY_REFERENCE_VENDOR", "Wartsila")
    monkeypatch.setenv("LEVITY_EQUIPMENT_CONTEXT", "offshore power generation")

    text, _ = search_manual_with_levity(
        api_key_levity="levity-token",
        item_class="Engine, Diesel",
        item_class_description="Diesel Engine",
        scope="Main propulsion backup",
    )

    assert "Manual section override" in text
    assert captured["json"]["reference_vendor"] == "Wartsila"
    assert captured["json"]["equipment_context"] == "offshore power generation"
    assert "Wartsila" in captured["json"]["query"]
    assert "offshore power generation" in captured["json"]["query"]


def test_slugify_for_filename_edge_cases():
    assert slugify_for_filename("Pump, Centrifugal") == "pump_centrifugal"
    assert slugify_for_filename("  ") == "item_class"
    assert slugify_for_filename("Mótör #1 / A") == "m_t_r_1_a"


def test_estimate_usage_cost_with_env_rates(monkeypatch):
    monkeypatch.setenv("INPUT_TOKEN_COST_PER_MILLION", "1.5")
    monkeypatch.setenv("OUTPUT_TOKEN_COST_PER_MILLION", "2.5")
    cost = estimate_usage_cost(2_000_000, 1_000_000)
    assert cost == 5.5


def test_estimate_usage_cost_invalid_inputs(monkeypatch):
    monkeypatch.setenv("INPUT_TOKEN_COST_PER_MILLION", "x")
    monkeypatch.setenv("OUTPUT_TOKEN_COST_PER_MILLION", "1")
    assert estimate_usage_cost(100, 100) is None

    monkeypatch.setenv("INPUT_TOKEN_COST_PER_MILLION", "-1")
    monkeypatch.setenv("OUTPUT_TOKEN_COST_PER_MILLION", "1")
    assert estimate_usage_cost(100, 100) is None
    assert estimate_usage_cost(None, 100) is None
    assert estimate_usage_cost(100, None) is None


def test_build_mi_list_returns_empty_when_item_class_not_found(tmp_path):
    ems_path = tmp_path / "ems.csv"
    catalog_path = tmp_path / "mi_catalog.csv"

    ems_path.write_text(
        "Item Class;Item Class Name;Boundaries\nDRDE;Diesel Engine;Include rotor and stator\n",
        encoding="utf-8",
    )
    catalog_path.write_text("Maintainable Item\nRotor\nStator\n", encoding="utf-8")

    result = build_mi_list_from_ems_and_catalog(ems_path, "CEDS", catalog_path)
    assert result == []


def test_create_chat_completion_uses_default_when_model_empty():
    class DummyCompletions:
        def __init__(self):
            self.calls = []

        def create(self, model=None, messages=None):
            self.calls.append(model)
            return {"model": model, "messages": messages}

    class DummyClient:
        def __init__(self):
            self.chat = type("Chat", (), {})()
            self.chat.completions = DummyCompletions()

    client = DummyClient()
    response, used_model = create_chat_completion_with_model_fallback(client, "   ", [{"role": "user", "content": "x"}])

    assert used_model == "deepseek-chat"
    assert client.chat.completions.calls == ["deepseek-chat"]
    assert response["model"] == "deepseek-chat"


def test_create_chat_completion_retries_when_model_not_exist():
    class DummyCompletions:
        def __init__(self):
            self.calls = []

        def create(self, model=None, messages=None):
            self.calls.append(model)
            if model == "invalid-model":
                raise RuntimeError("Error code: 400 - {'error': {'message': 'Model Not Exist'}}")
            return {"model": model, "messages": messages}

    class DummyClient:
        def __init__(self):
            self.chat = type("Chat", (), {})()
            self.chat.completions = DummyCompletions()

    client = DummyClient()
    response, used_model = create_chat_completion_with_model_fallback(client, "invalid-model", [{"role": "user", "content": "x"}])

    assert used_model == "deepseek-chat"
    assert client.chat.completions.calls == ["invalid-model", "deepseek-chat"]
    assert response["model"] == "deepseek-chat"
