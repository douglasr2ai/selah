"""
Testes unitários para o módulo bible.
"""
import json
import tempfile
import os
import pytest

from app.utils.bible import Bible, BOOK_NAMES


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_bible_data():
    """Dados de exemplo para testes."""
    return [
        {
            "abbrev": "gn",
            "chapters": [
                ["No princípio, Deus criou os céus e a terra.", "A terra era sem forma e vazia."],
                ["Assim foram concluídos os céus e a terra.", "E Deus abençoou o sétimo dia."]
            ]
        },
        {
            "abbrev": "jo",
            "chapters": [
                ["No princípio era o Verbo.", "E o Verbo estava com Deus."],
                ["No terceiro dia, houve uma festa.", "E estava ali a mãe de Jesus."],
                ["Porque Deus amou o mundo.", "Para que todo o que nele crê não pereça."]
            ]
        }
    ]


@pytest.fixture
def bible(temp_dir, sample_bible_data):
    """Cria uma instância de Bible com dados de teste."""
    # Criar arquivo de teste
    filepath = os.path.join(temp_dir, "test.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sample_bible_data, f, ensure_ascii=False)

    bible = Bible(temp_dir)
    bible.load("test")
    return bible


class TestBibleLoad:
    """Testes de carregamento."""

    def test_load_existing_file(self, temp_dir, sample_bible_data):
        """Testa carregamento de arquivo existente."""
        filepath = os.path.join(temp_dir, "acf.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sample_bible_data, f)

        bible = Bible(temp_dir)
        result = bible.load("acf")

        assert result is True
        assert bible.version == "acf"

    def test_load_nonexistent_file(self, temp_dir):
        """Testa carregamento de arquivo inexistente."""
        bible = Bible(temp_dir)
        result = bible.load("nonexistent")

        assert result is False
        assert bible.version == ""


class TestBibleNavigation:
    """Testes de navegação."""

    def test_get_book_count(self, bible):
        """Testa contagem de livros."""
        assert bible.get_book_count() == 2

    def test_get_book_valid_index(self, bible):
        """Testa obtenção de livro com índice válido."""
        book = bible.get_book(0)
        assert book is not None
        assert book["abbrev"] == "gn"

    def test_get_book_invalid_index(self, bible):
        """Testa obtenção de livro com índice inválido."""
        assert bible.get_book(-1) is None
        assert bible.get_book(100) is None

    def test_get_book_name(self, bible):
        """Testa obtenção de nome do livro."""
        assert bible.get_book_name(0) == "Gênesis"
        assert bible.get_book_name(1) == "João"

    def test_get_book_abbrev(self, bible):
        """Testa obtenção de abreviação."""
        assert bible.get_book_abbrev(0) == "gn"
        assert bible.get_book_abbrev(1) == "jo"

    def test_get_chapter_count(self, bible):
        """Testa contagem de capítulos."""
        assert bible.get_chapter_count(0) == 2  # Gênesis
        assert bible.get_chapter_count(1) == 3  # João

    def test_get_chapter(self, bible):
        """Testa obtenção de capítulo."""
        chapter = bible.get_chapter(0, 0)
        assert len(chapter) == 2
        assert "No princípio" in chapter[0]

    def test_get_verse(self, bible):
        """Testa obtenção de versículo."""
        verse = bible.get_verse(0, 0, 0)
        assert "No princípio" in verse

    def test_get_verse_count(self, bible):
        """Testa contagem de versículos."""
        assert bible.get_verse_count(0, 0) == 2
        assert bible.get_verse_count(1, 2) == 2

    def test_get_reference(self, bible):
        """Testa formatação de referência."""
        ref = bible.get_reference(1, 2, 0)
        assert ref == "João 3:1"


class TestBiblePosition:
    """Testes de navegação de posição."""

    def test_get_next_position_same_chapter(self, bible):
        """Testa avanço dentro do mesmo capítulo."""
        result = bible.get_next_position(0, 0, 0)
        assert result == (0, 0, 1, False)

    def test_get_next_position_next_chapter(self, bible):
        """Testa avanço para próximo capítulo."""
        result = bible.get_next_position(0, 0, 1)  # Último versículo do capítulo
        assert result == (0, 1, 0, False)

    def test_get_next_position_next_book(self, bible):
        """Testa avanço para próximo livro."""
        result = bible.get_next_position(0, 1, 1)  # Último versículo do último capítulo
        assert result == (1, 0, 0, False)

    def test_get_next_position_end_of_bible(self, bible):
        """Testa fim da Bíblia."""
        result = bible.get_next_position(1, 2, 1)  # Último versículo
        assert result[3] is True  # is_end

    def test_get_previous_position_same_chapter(self, bible):
        """Testa retrocesso dentro do mesmo capítulo."""
        result = bible.get_previous_position(0, 0, 1)
        assert result == (0, 0, 0, False)

    def test_get_previous_position_previous_chapter(self, bible):
        """Testa retrocesso para capítulo anterior."""
        result = bible.get_previous_position(0, 1, 0)
        assert result == (0, 0, 1, False)  # Último versículo do cap anterior

    def test_get_previous_position_start_of_bible(self, bible):
        """Testa início da Bíblia."""
        result = bible.get_previous_position(0, 0, 0)
        assert result[3] is True  # is_start


class TestBibleSearch:
    """Testes de busca."""

    def test_search_finds_text(self, bible):
        """Testa busca por texto."""
        results = bible.search("Deus")
        assert len(results) > 0
        assert any("Deus" in r["verse_text"] for r in results)

    def test_search_case_insensitive(self, bible):
        """Testa busca case-insensitive."""
        results = bible.search("deus")
        assert len(results) > 0

    def test_search_no_results(self, bible):
        """Testa busca sem resultados."""
        results = bible.search("xyz123abc")
        assert len(results) == 0

    def test_search_empty_query(self, bible):
        """Testa busca com query vazia."""
        results = bible.search("")
        assert len(results) == 0

    def test_search_max_results(self, bible):
        """Testa limite de resultados."""
        results = bible.search("o", max_results=2)
        assert len(results) <= 2

    def test_search_returns_reference(self, bible):
        """Testa que busca retorna referência."""
        results = bible.search("princípio")
        assert len(results) > 0
        assert "reference" in results[0]

    def test_search_by_reference_full(self, bible):
        """Testa busca por referência completa."""
        result = bible.search_by_reference("João 3:1")
        assert result is not None
        assert result["book_index"] == 1
        assert result["chapter_index"] == 2
        assert result["verse_index"] == 0

    def test_search_by_reference_chapter_only(self, bible):
        """Testa busca por capítulo (sem versículo)."""
        result = bible.search_by_reference("João 1")
        assert result is not None
        assert result["book_index"] == 1
        assert result["chapter_index"] == 0
        assert result["verse_index"] == 0

    def test_search_by_reference_invalid(self, bible):
        """Testa busca por referência inválida."""
        result = bible.search_by_reference("Livro 999:999")
        assert result is None


class TestBibleAllBooks:
    """Testes para listagem de livros."""

    def test_get_all_books(self, bible):
        """Testa obtenção de todos os livros."""
        books = bible.get_all_books()

        assert len(books) == 2
        assert books[0]["abbrev"] == "gn"
        assert books[0]["name"] == "Gênesis"
        assert books[0]["chapters"] == 2
        assert books[1]["abbrev"] == "jo"


class TestBookNames:
    """Testes para mapeamento de nomes."""

    def test_all_books_have_names(self):
        """Testa que todas as abreviações têm nomes."""
        expected_abbrevs = [
            "gn", "ex", "lv", "nm", "dt", "js", "jz", "rt",
            "1sm", "2sm", "1rs", "2rs", "1cr", "2cr", "ed", "ne",
            "et", "jó", "sl", "pv", "ec", "ct", "is", "jr",
            "lm", "ez", "dn", "os", "jl", "am", "ob", "jn",
            "mq", "na", "hc", "sf", "ag", "zc", "ml",
            "mt", "mc", "lc", "jo", "at", "rm", "1co", "2co",
            "gl", "ef", "fp", "cl", "1ts", "2ts", "1tm", "2tm",
            "tt", "fm", "hb", "tg", "1pe", "2pe", "1jo", "2jo",
            "3jo", "jd", "ap"
        ]

        for abbrev in expected_abbrevs:
            assert abbrev in BOOK_NAMES, f"Falta nome para {abbrev}"

    def test_total_books_count(self):
        """Testa que há 66 livros mapeados."""
        assert len(BOOK_NAMES) == 66
