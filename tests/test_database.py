"""
Testes unitários para o módulo database.
"""
import os
import tempfile
import pytest

from app.utils.database import Database


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def database(temp_dir):
    """Cria uma instância de Database para testes."""
    return Database(temp_dir)


class TestDatabaseSettings:
    """Testes para configurações."""

    def test_set_and_get_string(self, database):
        """Testa armazenamento de strings."""
        database.set_setting("test_key", "test_value")
        assert database.get_setting("test_key") == "test_value"

    def test_set_and_get_int(self, database):
        """Testa armazenamento de inteiros."""
        database.set_setting("count", 42)
        assert database.get_setting("count") == 42

    def test_set_and_get_float(self, database):
        """Testa armazenamento de floats."""
        database.set_setting("volume", 0.75)
        assert database.get_setting("volume") == 0.75

    def test_set_and_get_bool(self, database):
        """Testa armazenamento de booleanos."""
        database.set_setting("enabled", True)
        assert database.get_setting("enabled") is True

    def test_set_and_get_dict(self, database):
        """Testa armazenamento de dicionários."""
        data = {"book_index": 1, "chapter_index": 2, "verse_index": 3}
        database.set_setting("position", data)
        assert database.get_setting("position") == data

    def test_get_nonexistent_returns_default(self, database):
        """Testa retorno de valor default."""
        assert database.get_setting("nonexistent") is None
        assert database.get_setting("nonexistent", "default") == "default"

    def test_get_all_settings(self, database):
        """Testa obtenção de todas as configurações."""
        database.set_setting("key1", "value1")
        database.set_setting("key2", 123)

        settings = database.get_all_settings()
        assert "key1" in settings
        assert "key2" in settings
        assert settings["key1"] == "value1"
        assert settings["key2"] == 123

    def test_update_existing_setting(self, database):
        """Testa atualização de configuração existente."""
        database.set_setting("key", "old_value")
        database.set_setting("key", "new_value")
        assert database.get_setting("key") == "new_value"


class TestDatabaseHistory:
    """Testes para histórico de leitura."""

    def test_mark_chapter_read(self, database):
        """Testa marcação de capítulo como lido."""
        database.mark_chapter_read("gn", 0)
        assert database.is_chapter_read("gn", 0) is True
        assert database.is_chapter_read("gn", 1) is False

    def test_mark_same_chapter_twice(self, database):
        """Testa marcação duplicada (não deve gerar erro)."""
        database.mark_chapter_read("jo", 2)
        database.mark_chapter_read("jo", 2)  # Não deve gerar erro
        assert database.is_chapter_read("jo", 2) is True

    def test_get_chapters_read_for_book(self, database):
        """Testa obtenção de capítulos lidos de um livro."""
        database.mark_chapter_read("sl", 22)
        database.mark_chapter_read("sl", 23)
        database.mark_chapter_read("sl", 90)

        chapters = database.get_chapters_read_for_book("sl")
        assert 22 in chapters
        assert 23 in chapters
        assert 90 in chapters
        assert len(chapters) == 3

    def test_get_total_chapters_read(self, database):
        """Testa contagem total de capítulos lidos."""
        assert database.get_total_chapters_read() == 0

        database.mark_chapter_read("gn", 0)
        database.mark_chapter_read("gn", 1)
        database.mark_chapter_read("ex", 0)

        assert database.get_total_chapters_read() == 3

    def test_increment_verses_read(self, database):
        """Testa incremento de versículos lidos."""
        database.increment_verses_read(5)
        database.increment_verses_read(3)

        stats = database.get_reading_stats()
        assert stats["total_verses_read"] == 8

    def test_add_reading_time(self, database):
        """Testa adição de tempo de leitura."""
        database.add_reading_time(60)
        database.add_reading_time(120)

        stats = database.get_reading_stats()
        assert stats["total_time_reading"] == 180

    def test_clear_history(self, database):
        """Testa limpeza do histórico."""
        database.mark_chapter_read("gn", 0)
        database.increment_verses_read(10)
        database.add_reading_time(300)

        database.clear_history()

        assert database.get_total_chapters_read() == 0
        stats = database.get_reading_stats()
        assert stats["total_verses_read"] == 0
        assert stats["total_time_reading"] == 0


class TestDatabaseFavorites:
    """Testes para favoritos."""

    def test_add_favorite(self, database):
        """Testa adição de favorito."""
        result = database.add_favorite(
            book_index=42,
            chapter_index=2,
            verse_index=15,
            verse_text="Porque Deus amou o mundo...",
            reference="João 3:16"
        )
        assert result is True

    def test_add_duplicate_favorite(self, database):
        """Testa adição de favorito duplicado."""
        database.add_favorite(0, 0, 0, "Texto", "Ref")
        result = database.add_favorite(0, 0, 0, "Texto", "Ref")
        assert result is False

    def test_is_favorite(self, database):
        """Testa verificação de favorito."""
        assert database.is_favorite(0, 0, 0) is False

        database.add_favorite(0, 0, 0, "Texto", "Ref")
        assert database.is_favorite(0, 0, 0) is True

    def test_remove_favorite(self, database):
        """Testa remoção de favorito."""
        database.add_favorite(0, 0, 0, "Texto", "Ref")
        assert database.is_favorite(0, 0, 0) is True

        result = database.remove_favorite(0, 0, 0)
        assert result is True
        assert database.is_favorite(0, 0, 0) is False

    def test_remove_nonexistent_favorite(self, database):
        """Testa remoção de favorito inexistente."""
        result = database.remove_favorite(99, 99, 99)
        assert result is False

    def test_get_all_favorites(self, database):
        """Testa obtenção de todos os favoritos."""
        database.add_favorite(0, 0, 0, "Texto 1", "Ref 1")
        database.add_favorite(1, 1, 1, "Texto 2", "Ref 2")

        favorites = database.get_all_favorites()
        assert len(favorites) == 2

    def test_update_favorite_note(self, database):
        """Testa atualização de nota do favorito."""
        database.add_favorite(0, 0, 0, "Texto", "Ref")
        database.update_favorite_note(0, 0, 0, "Minha nota")

        favorites = database.get_all_favorites()
        assert favorites[0]["note"] == "Minha nota"

    def test_get_favorites_count(self, database):
        """Testa contagem de favoritos."""
        assert database.get_favorites_count() == 0

        database.add_favorite(0, 0, 0, "Texto", "Ref")
        database.add_favorite(1, 1, 1, "Texto", "Ref")

        assert database.get_favorites_count() == 2


class TestDatabasePersistence:
    """Testes de persistência."""

    def test_data_persists_across_instances(self, temp_dir):
        """Testa se dados persistem entre instâncias."""
        # Primeira instância - salvar dados
        db1 = Database(temp_dir)
        db1.set_setting("test", "value")
        db1.mark_chapter_read("gn", 0)
        db1.add_favorite(0, 0, 0, "Texto", "Ref")

        # Segunda instância - verificar dados
        db2 = Database(temp_dir)
        assert db2.get_setting("test") == "value"
        assert db2.is_chapter_read("gn", 0) is True
        assert db2.is_favorite(0, 0, 0) is True

    def test_database_file_created(self, temp_dir):
        """Testa se arquivo do banco é criado."""
        Database(temp_dir)
        db_path = os.path.join(temp_dir, "selah.db")
        assert os.path.exists(db_path)
