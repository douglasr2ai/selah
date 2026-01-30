"""
Testes unitários para o módulo history.
"""
import tempfile
import time
import pytest

from app.utils.database import Database
from app.utils.history import History


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def database(temp_dir):
    """Cria uma instância de Database para testes."""
    return Database(temp_dir)


@pytest.fixture
def history(temp_dir, database):
    """Cria uma instância de History para testes."""
    return History(temp_dir, database)


class TestHistoryChapters:
    """Testes para capítulos lidos."""

    def test_mark_chapter_read(self, history):
        """Testa marcação de capítulo como lido."""
        history.mark_chapter_read("gn", 0)
        assert history.is_chapter_read("gn", 0) is True
        assert history.is_chapter_read("gn", 1) is False

    def test_get_chapters_read_for_book(self, history):
        """Testa obtenção de capítulos lidos de um livro."""
        history.mark_chapter_read("jo", 0)
        history.mark_chapter_read("jo", 2)
        history.mark_chapter_read("jo", 4)

        chapters = history.get_chapters_read_for_book("jo")
        assert 0 in chapters
        assert 2 in chapters
        assert 4 in chapters
        assert len(chapters) == 3


class TestHistorySession:
    """Testes para sessão de leitura."""

    def test_session_inactive_by_default(self, history):
        """Testa que sessão começa inativa."""
        assert history.is_session_active() is False

    def test_start_session(self, history):
        """Testa início de sessão."""
        history.start_session()
        assert history.is_session_active() is True

    def test_end_session(self, history):
        """Testa fim de sessão."""
        history.start_session()
        history.end_session()
        assert history.is_session_active() is False

    def test_session_records_time(self, history):
        """Testa que sessão registra tempo."""
        history.start_session()
        time.sleep(0.1)  # 100ms
        history.end_session()

        stats = history.get_stats()
        assert stats["total_time_seconds"] >= 0


class TestHistoryStats:
    """Testes para estatísticas."""

    def test_increment_verses(self, history):
        """Testa incremento de versículos."""
        history.increment_verses(5)
        history.increment_verses(3)

        stats = history.get_stats()
        assert stats["total_verses_read"] == 8

    def test_get_stats_format(self, history):
        """Testa formato das estatísticas."""
        stats = history.get_stats()

        assert "chapters_read" in stats
        assert "total_chapters" in stats
        assert "total_verses_read" in stats
        assert "total_time_hours" in stats
        assert "total_time_minutes" in stats
        assert "total_time_seconds" in stats
        assert "progress_percent" in stats

    def test_total_chapters_constant(self, history):
        """Testa que total de capítulos é 1189."""
        stats = history.get_stats()
        assert stats["total_chapters"] == 1189

    def test_progress_calculation(self, history):
        """Testa cálculo de progresso."""
        # Marcar alguns capítulos
        for i in range(10):
            history.mark_chapter_read("gn", i)

        stats = history.get_stats()
        assert stats["chapters_read"] == 10
        # 10/1189 * 100 ≈ 0.84%
        assert stats["progress_percent"] > 0
        assert stats["progress_percent"] < 1

    def test_time_formatting(self, history):
        """Testa formatação de tempo."""
        # Adicionar 2 horas e 30 minutos de tempo
        history.db.add_reading_time(2 * 3600 + 30 * 60)

        stats = history.get_stats()
        assert stats["total_time_hours"] == 2
        assert stats["total_time_minutes"] == 30


class TestHistoryClear:
    """Testes para limpeza de histórico."""

    def test_clear_history(self, history):
        """Testa limpeza completa do histórico."""
        history.mark_chapter_read("gn", 0)
        history.increment_verses(10)
        history.start_session()

        history.clear_history()

        assert history.is_chapter_read("gn", 0) is False
        assert history.is_session_active() is False
        stats = history.get_stats()
        assert stats["chapters_read"] == 0
        assert stats["total_verses_read"] == 0


class TestHistoryPersistence:
    """Testes de persistência."""

    def test_load_returns_false_when_empty(self, history):
        """Testa que load retorna False sem dados."""
        result = history.load()
        assert result is False

    def test_load_returns_true_with_data(self, history):
        """Testa que load retorna True com dados."""
        history.mark_chapter_read("gn", 0)

        # Nova instância
        history2 = History(history.config_dir, history.db)
        result = history2.load()
        assert result is True

    def test_save_always_returns_true(self, history):
        """Testa que save sempre retorna True (SQLite auto-salva)."""
        result = history.save()
        assert result is True
