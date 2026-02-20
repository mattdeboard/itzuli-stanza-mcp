import json

from core.types import AnalysisRow, TranslationResult
from core.formatters import (
    format_as_markdown_table,
    format_as_json,
    format_as_dict_list,
    apply_friendly_mappings,
)


class TestFormatAsMarkdownTable:
    def test_formats_basic_translation_result(self):
        rows = [
            AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan"),
            AnalysisRow("mundua", "mundu", "NOUN", "Case=Abs|Definite=Def|Number=Sing"),
        ]
        result = TranslationResult(
            source_text="Kaixo mundua!",
            source_language="eu",
            translated_text="Hello world!",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_markdown_table(result, "en")

        assert "Source: Kaixo mundua! (Basque)" in output
        assert "Translation: Hello world! (English)" in output
        assert "Morphological Analysis:" in output
        assert "| Word | Lemma | Part of Speech | Features |" in output
        assert "|------|-------|---------------|----------|" in output
        assert "| Kaixo | (kaixo) | interjection | inanimate |" in output
        assert "| mundua | (mundu) | noun | absolutive (sub/obj), definite (the), singular |" in output

    def test_formats_with_localized_labels_euskera(self):
        rows = [AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan")]
        result = TranslationResult(
            source_text="Kaixo!",
            source_language="eu",
            translated_text="Hello!",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_markdown_table(result, "eu")

        assert "Jatorria: Kaixo! (euskera)" in output
        assert "Itzulpena: Hello! (ingelesa)" in output
        assert "Analisi Morfologikoa:" in output
        assert "| Hitza | Lema | Hitz Mota | Ezaugarriak |" in output

    def test_formats_with_localized_labels_spanish(self):
        rows = [AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan")]
        result = TranslationResult(
            source_text="Kaixo!",
            source_language="eu",
            translated_text="¡Hola!",
            target_language="es",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_markdown_table(result, "es")

        assert "Origen: Kaixo! (vasco)" in output
        assert "Traducción: ¡Hola! (español)" in output
        assert "Análisis Morfológico:" in output
        assert "| Palabra | Lema | Categoría Gramatical | Características |" in output

    def test_wraps_long_features_at_100_columns(self):
        long_features = "Case=Abs, Definite=Def, Number=Sing, Person=3, Animacy=Inan, Gender=Neut, VerbForm=Fin, Mood=Ind, Tense=Pres"
        rows = [AnalysisRow("test", "(test)", "noun", long_features)]
        result = TranslationResult(
            source_text="test",
            source_language="eu",
            translated_text="test",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_markdown_table(result, "en")
        lines = output.split("\n")

        # Find the data rows (skip headers and separators)
        data_lines = [line for line in lines if line.startswith("| test |")]
        assert len(data_lines) >= 1

        # Check that no line exceeds 100 characters
        for line in lines:
            assert len(line) <= 100, f"Line exceeds 100 chars: {line}"

    def test_handles_empty_features(self):
        rows = [AnalysisRow("test", "test", "NOUN", "")]
        result = TranslationResult(
            source_text="test",
            source_language="eu",
            translated_text="test",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_markdown_table(result, "en")

        assert "| test | (test) | noun | — |" in output

    def test_handles_none_features(self):
        rows = [AnalysisRow("test", "test", "NOUN", None)]
        result = TranslationResult(
            source_text="test",
            source_language="eu",
            translated_text="test",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_markdown_table(result, "en")

        assert "| test | (test) | noun | — |" in output


class TestFormatAsJson:
    def test_formats_translation_result_as_json(self):
        rows = [
            AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan"),
            AnalysisRow("mundua", "mundu", "NOUN", "Case=Abs|Definite=Def|Number=Sing"),
        ]
        result = TranslationResult(
            source_text="Kaixo mundua!",
            source_language="eu",
            translated_text="Hello world!",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_json(result, "en")
        parsed = json.loads(output)

        assert parsed["source_text"] == "Kaixo mundua!"
        assert parsed["source_language"] == "eu"
        assert parsed["translated_text"] == "Hello world!"
        assert parsed["target_language"] == "en"
        assert parsed["translation_id"] == "trans-123"
        assert len(parsed["morphological_analysis"]) == 2

        first_analysis = parsed["morphological_analysis"][0]
        assert first_analysis["word"] == "Kaixo"
        assert first_analysis["lemma"] == "kaixo"
        assert first_analysis["part_of_speech"] == "INTJ"
        assert first_analysis["features"] == "Animacy=Inan"

    def test_handles_empty_analysis_rows(self):
        result = TranslationResult(
            source_text="test",
            source_language="eu",
            translated_text="test",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=[],
        )

        output = format_as_json(result, "en")
        parsed = json.loads(output)

        assert parsed["morphological_analysis"] == []

    def test_preserves_unicode_characters(self):
        rows = [AnalysisRow("ñ", "ñ", "NOUN", "special")]
        result = TranslationResult(
            source_text="ñ",
            source_language="eu",
            translated_text="ñ",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_json(result, "en")

        # Should contain the actual unicode character, not escaped version
        assert '"ñ"' in output
        parsed = json.loads(output)
        assert parsed["source_text"] == "ñ"


class TestFormatAsDictList:
    def test_formats_analysis_rows_as_dict_list(self):
        rows = [
            AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan"),
            AnalysisRow("mundua", "mundu", "NOUN", "Case=Abs|Definite=Def|Number=Sing"),
        ]
        result = TranslationResult(
            source_text="Kaixo mundua!",
            source_language="eu",
            translated_text="Hello world!",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        output = format_as_dict_list(result, "en")

        assert len(output) == 2
        assert output[0] == {
            "word": "Kaixo",
            "lemma": "kaixo",
            "part_of_speech": "INTJ",
            "features": "Animacy=Inan",
        }
        assert output[1] == {
            "word": "mundua",
            "lemma": "mundu",
            "part_of_speech": "NOUN",
            "features": "Case=Abs|Definite=Def|Number=Sing",
        }

    def test_handles_empty_analysis_rows(self):
        result = TranslationResult(
            source_text="test",
            source_language="eu",
            translated_text="test",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=[],
        )

        output = format_as_dict_list(result, "en")

        assert output == []


class TestApplyFriendlyMappings:
    def test_converts_raw_analysis_to_friendly_format(self):
        raw_analysis = [
            ("Kaixo", "kaixo", "INTJ", "Animacy=Inan"),
            ("mundua", "mundu", "NOUN", "Case=Abs|Definite=Def|Number=Sing"),
        ]

        friendly = apply_friendly_mappings(raw_analysis, "en")

        assert len(friendly) == 2
        assert friendly[0] == ("Kaixo", "(kaixo)", "interjection", "inanimate")
        assert friendly[1] == ("mundua", "(mundu)", "noun", "absolutive (sub/obj), definite (the), singular")

    def test_handles_quirks(self):
        raw_analysis = [("euskal", "euskal", "ADJ", "")]

        friendly = apply_friendly_mappings(raw_analysis, "en")

        assert friendly[0] == ("euskal", "(euskal)", "adjective", "combining prefix")

    def test_handles_empty_features(self):
        raw_analysis = [("test", "test", "NOUN", "")]

        friendly = apply_friendly_mappings(raw_analysis, "en")

        assert friendly[0] == ("test", "(test)", "noun", "")

    def test_localizes_to_basque(self):
        raw_analysis = [("Kaixo", "kaixo", "INTJ", "Animacy=Inan")]

        friendly = apply_friendly_mappings(raw_analysis, "eu")

        assert friendly[0] == ("Kaixo", "(kaixo)", "harridura", "bizigabea")
