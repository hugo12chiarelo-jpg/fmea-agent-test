#!/usr/bin/env python3
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, 'scripts')

from run_agent import (
    _read_csv_with_fallback_cached,
    DEFAULT_LEVITY_REFERENCE_VENDOR,
    build_mi_list_from_ems_and_catalog,
    create_chat_completion_with_model_fallback,
    estimate_usage_cost,
    load_instruction_entries,
    pick_manual_text,
    pick_scope_from_ems,
    read_csv_with_fallback,
    resolve_model_name,
    search_manual_with_levity,
    should_use_levity_manual_lookup,
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
                        "text": "Pump centrifugal manual section A",
                        "url": "https://example.com/manual-a",
                    },
                    {
                        "content": "Pump operation section B",
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

    assert "Pump centrifugal manual section A" in text
    assert "Pump operation section B" in text
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
            return {"text": "Diesel engine manual section override"}

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

    assert "Diesel engine manual section override" in text
    assert captured["json"]["reference_vendor"] == "Wartsila"
    assert captured["json"]["equipment_context"] == "offshore power generation"
    assert "Wartsila" in captured["json"]["query"]
    assert "offshore power generation" in captured["json"]["query"]


def test_search_manual_with_levity_skips_irrelevant_results(monkeypatch):
    class DummyResponse:
        status_code = 200

        def json(self):
            return {
                "results": [
                    {"text": "Wind turbine troubleshooting chapter"},
                    {"content": "Solar inverter maintenance summary"},
                ]
            }

    monkeypatch.setattr("run_agent.httpx.post", lambda *args, **kwargs: DummyResponse())

    text, source = search_manual_with_levity(
        api_key_levity="levity-token",
        item_class="Pump, Centrifugal",
        item_class_description="Centrifugal process pump",
        scope="Transfer fluid",
    )

    assert text is None
    assert source is None


def test_should_use_levity_manual_lookup_requires_opt_in(monkeypatch):
    monkeypatch.delenv("ENABLE_LEVITY_MANUAL_LOOKUP", raising=False)
    assert should_use_levity_manual_lookup("levity-token") is False
    assert should_use_levity_manual_lookup(None) is False


def test_should_use_levity_manual_lookup_accepts_truthy_values(monkeypatch):
    monkeypatch.setenv("ENABLE_LEVITY_MANUAL_LOOKUP", "true")
    assert should_use_levity_manual_lookup("levity-token") is True

    monkeypatch.setenv("ENABLE_LEVITY_MANUAL_LOOKUP", "1")
    assert should_use_levity_manual_lookup("levity-token") is True


def test_pick_manual_text_returns_none_when_no_relevant_file(tmp_path, monkeypatch):
    manual_dir = tmp_path / "inputs" / "Manual"
    manual_dir.mkdir(parents=True)
    (manual_dir / "diesel_engine_manual.txt").write_text("Diesel engine details", encoding="utf-8")
    (manual_dir / "compressor_handbook.txt").write_text("Compressor details", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    assert pick_manual_text("Pump, Centrifugal") is None


def test_pick_manual_text_returns_none_when_manual_folder_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert pick_manual_text("Pump, Centrifugal") is None


def test_pick_manual_text_selects_relevant_file(tmp_path, monkeypatch):
    manual_dir = tmp_path / "inputs" / "Manual"
    manual_dir.mkdir(parents=True)
    relevant_path = manual_dir / "pump_centrifugal_manual.txt"
    relevant_path.write_text("Pump manual details", encoding="utf-8")
    (manual_dir / "diesel_engine_manual.txt").write_text("Diesel engine details", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    assert pick_manual_text("Pump, Centrifugal").resolve() == relevant_path.resolve()


def test_pick_scope_from_ems_returns_matching_scope(tmp_path):
    ems_path = tmp_path / "EMS.csv"
    ems_path.write_text(
        "Item Class;Item Class Name;Scope\n"
        "PUMP;Pump, Centrifugal;Transfers process fluid in FPSO\n"
        "COMP;Compressor, Screw;Compresses fuel gas\n",
        encoding="utf-8",
    )

    assert pick_scope_from_ems(ems_path, "Pump, Centrifugal") == "Transfers process fluid in FPSO"
    assert pick_scope_from_ems(ems_path, "PUMP") == "Transfers process fluid in FPSO"


def test_pick_scope_from_ems_returns_empty_when_scope_missing(tmp_path):
    ems_path = tmp_path / "EMS.csv"
    ems_path.write_text(
        "Item Class;Item Class Name;Boundaries\n"
        "PUMP;Pump, Centrifugal;Includes casing\n",
        encoding="utf-8",
    )

    assert pick_scope_from_ems(ems_path, "Pump, Centrifugal") == ""


def test_pick_scope_from_ems_returns_first_non_empty_scope_when_multiple_rows_match(tmp_path):
    ems_path = tmp_path / "EMS.csv"
    ems_path.write_text(
        "Item Class;Item Class Name;Scope\n"
        "PUMP;Pump, Centrifugal;\n"
        "PUMP;Pump, Centrifugal;First non-empty scope\n"
        "PUMP;Pump, Centrifugal;Another scope\n",
        encoding="utf-8",
    )

    assert pick_scope_from_ems(ems_path, "Pump, Centrifugal") == "First non-empty scope"


def test_read_csv_with_fallback_uses_cache(tmp_path, monkeypatch):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("col1,col2\n1,2\n", encoding="utf-8")

    _read_csv_with_fallback_cached.cache_clear()

    original_read_csv = pd.read_csv
    calls = {"count": 0}
    call_kwargs = []

    def counting_read_csv(*args, **kwargs):
        calls["count"] += 1
        call_kwargs.append(kwargs)
        return original_read_csv(*args, **kwargs)

    monkeypatch.setattr("run_agent.pd.read_csv", counting_read_csv)

    df_first = read_csv_with_fallback(csv_path)
    df_second = read_csv_with_fallback(csv_path)
    df_third = read_csv_with_fallback(csv_path, skip_bad_lines=True)

    assert calls["count"] == 2
    assert df_first.equals(df_second)
    assert df_first.equals(df_third)
    assert df_first is not df_second
    assert "on_bad_lines" not in call_kwargs[0]
    assert call_kwargs[1].get("on_bad_lines") == "skip"


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


def test_create_chat_completion_uses_default_when_model_empty_or_whitespace():
    class MockCompletions:
        def __init__(self):
            self.calls = []

        def create(self, model=None, messages=None):
            self.calls.append(model)
            return {"model": model, "messages": messages}

    class MockClient:
        def __init__(self):
            self.chat = type("Chat", (), {})()
            self.chat.completions = MockCompletions()

    client = MockClient()
    response, used_model = create_chat_completion_with_model_fallback(client, "   ", [{"role": "user", "content": "x"}])

    assert used_model == "deepseek-chat"
    assert client.chat.completions.calls == ["deepseek-chat"]
    assert response["model"] == "deepseek-chat"


def test_create_chat_completion_retries_when_model_does_not_exist():
    class MockAPIError(Exception):
        def __init__(self):
            super().__init__("Error code: 400 - {'error': {'message': 'Model Not Exist'}}")
            self.status_code = 400
            self.body = {"error": {"message": "Model Not Exist", "code": "invalid_request_error"}}

    class MockCompletions:
        def __init__(self):
            self.calls = []

        def create(self, model=None, messages=None):
            self.calls.append(model)
            if model == "invalid-model":
                raise MockAPIError()
            return {"model": model, "messages": messages}

    class MockClient:
        def __init__(self):
            self.chat = type("Chat", (), {})()
            self.chat.completions = MockCompletions()

    client = MockClient()
    response, used_model = create_chat_completion_with_model_fallback(client, "invalid-model", [{"role": "user", "content": "x"}])

    assert used_model == "deepseek-chat"
    assert client.chat.completions.calls == ["invalid-model", "deepseek-chat"]
    assert response["model"] == "deepseek-chat"


def test_resolve_model_name_fallbacks():
    assert resolve_model_name("  ") == "deepseek-chat"
    assert resolve_model_name(None) == "deepseek-chat"
    assert resolve_model_name("deepseek-reasoner") == "deepseek-reasoner"
