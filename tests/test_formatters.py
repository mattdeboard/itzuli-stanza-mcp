import json

from itzuli_stanza_mcp.workflow import AnalysisRow, TranslationResult
from itzuli_stanza_mcp.formatters import format_as_markdown_table, format_as_json, format_as_dict_list


class TestFormatAsMarkdownTable:
    def test_formats_basic_translation_result(self):
        rows = [
            AnalysisRow("Kaixo", "(kaixo)", "interjection", "Animacy=Inan"),
            AnalysisRow("mundua", "(mundu)", "noun", "Case=Abs|Definite=Def|Number=Sing"),
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
        assert "| Kaixo | (kaixo) | interjection | Animacy=Inan |" in output
        assert "| mundua | (mundu) | noun | Case=Abs|Definite=Def|Number=Sing |" in output

    def test_formats_with_localized_labels_euskera(self):
        rows = [AnalysisRow("Kaixo", "(kaixo)", "interjection", "Animacy=Inan")]
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
        rows = [AnalysisRow("Kaixo", "(kaixo)", "interjection", "Animacy=Inan")]
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
        rows = [AnalysisRow("test", "(test)", "noun", "")]
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
        rows = [AnalysisRow("test", "(test)", "noun", None)]
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
            AnalysisRow("Kaixo", "(kaixo)", "interjection", "Animacy=Inan"),
            AnalysisRow("mundua", "(mundu)", "noun", "Case=Abs|Definite=Def|Number=Sing"),
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
        assert first_analysis["lemma"] == "(kaixo)"
        assert first_analysis["part_of_speech"] == "interjection"
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
        rows = [AnalysisRow("ñ", "(ñ)", "noun", "special")]
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
            AnalysisRow("Kaixo", "(kaixo)", "interjection", "Animacy=Inan"),
            AnalysisRow("mundua", "(mundu)", "noun", "Case=Abs|Definite=Def|Number=Sing"),
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
            "lemma": "(kaixo)",
            "part_of_speech": "interjection",
            "features": "Animacy=Inan",
        }
        assert output[1] == {
            "word": "mundua",
            "lemma": "(mundu)",
            "part_of_speech": "noun",
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
