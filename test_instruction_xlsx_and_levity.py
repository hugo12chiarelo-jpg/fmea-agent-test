#!/usr/bin/env python3
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, 'scripts')

from run_agent import load_instruction_entries, search_manual_with_levity, slugify_for_filename


def test_load_instruction_entries_from_xlsx(tmp_path, monkeypatch):
    instructions_dir = tmp_path / "inputs" / "Instructions"
    instructions_dir.mkdir(parents=True)

    df = pd.DataFrame(
        [
            {
                "Item Class": "Pump, Centrifugal",
                "Item Class Description": "Centrifugal process pump",
                "Scope": "Transfer process fluid",
                "Vendor": "ACME",
                "Model": "P-1000",
            },
            {
                "Item Class": "Compressor, Screw",
                "Item Class Description": "Gas compression package",
                "Scope": "Compress fuel gas",
                "Vendor": "TurboCo",
                "Model": "SC-200",
            },
        ]
    )
    xlsx_path = instructions_dir / "instructions.xlsx"
    df.to_excel(xlsx_path, index=False)

    monkeypatch.chdir(tmp_path)
    entries = load_instruction_entries()

    assert len(entries) == 2
    assert entries[0]["item_class"] == "Pump, Centrifugal"
    assert entries[0]["vendor"] == "ACME"
    assert entries[1]["item_class"] == "Compressor, Screw"
    assert entries[1]["model"] == "SC-200"


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
        vendor="ACME",
        model="P-1000",
    )

    assert "Manual section A" in text
    assert "Manual section B" in text
    assert source == "https://example.com/manual-a"
    assert captured["url"] == "https://levity.example/search"
    assert captured["headers"]["Authorization"] == "Bearer levity-token"
    assert "Pump, Centrifugal" in captured["json"]["query"]


def test_slugify_for_filename_edge_cases():
    assert slugify_for_filename("Pump, Centrifugal") == "pump_centrifugal"
    assert slugify_for_filename("  ") == "item_class"
    assert slugify_for_filename("Mótör #1 / A") == "m_t_r_1_a"
