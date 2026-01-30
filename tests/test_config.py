"""
Testes unitários para o módulo config.
"""
import tempfile
import pytest

from app.utils.database import Database
from app.utils.config import Config


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
def config(temp_dir, database):
    """Cria uma instância de Config para testes."""
    return Config(temp_dir, database)


class TestConfigBasic:
    """Testes básicos de configuração."""

    def test_default_settings(self, config):
        """Testa se defaults são carregados."""
        config.load()

        assert config.bible_version is None
        assert config.reading_mode == "chunks"
        assert config.word_speed == 1.0
        assert config.music_volume == 0.5
        assert config.font_size == 32
        assert config.night_mode is False
        assert config.fullscreen is False

    def test_is_first_time(self, config):
        """Testa detecção de primeira execução."""
        config.load()
        assert config.is_first_time() is True

        config.bible_version = "nvi"
        config.save()
        assert config.is_first_time() is False


class TestConfigProperties:
    """Testes de propriedades."""

    def test_bible_version(self, config):
        """Testa configuração de versão da Bíblia."""
        config.load()
        config.bible_version = "acf"
        config.save()

        assert config.bible_version == "acf"

    def test_reading_mode(self, config):
        """Testa configuração de modo de leitura."""
        config.load()
        config.reading_mode = "word"
        config.save()

        assert config.reading_mode == "word"

    def test_word_speed_bounds(self, config):
        """Testa limites de velocidade."""
        config.load()

        config.word_speed = 0.05  # Menor que mínimo
        assert config.word_speed == 0.1

        config.word_speed = 10.0  # Maior que máximo
        assert config.word_speed == 5.0

        config.word_speed = 2.5  # Valor válido
        assert config.word_speed == 2.5

    def test_music_volume_bounds(self, config):
        """Testa limites de volume."""
        config.load()

        config.music_volume = -0.5  # Menor que mínimo
        assert config.music_volume == 0.0

        config.music_volume = 1.5  # Maior que máximo
        assert config.music_volume == 1.0

        config.music_volume = 0.7  # Valor válido
        assert config.music_volume == 0.7

    def test_font_size_bounds(self, config):
        """Testa limites de tamanho de fonte."""
        config.load()

        config.font_size = 10  # Menor que mínimo
        assert config.font_size == 16

        config.font_size = 100  # Maior que máximo
        assert config.font_size == 72

        config.font_size = 40  # Valor válido
        assert config.font_size == 40

    def test_last_position(self, config):
        """Testa configuração de última posição."""
        config.load()
        position = {"book_index": 5, "chapter_index": 3, "verse_index": 10}
        config.last_position = position
        config.save()

        assert config.last_position == position

    def test_night_mode(self, config):
        """Testa configuração de modo noturno."""
        config.load()
        config.night_mode = True
        config.save()

        assert config.night_mode is True

    def test_fullscreen(self, config):
        """Testa configuração de tela cheia."""
        config.load()
        config.fullscreen = True
        config.save()

        assert config.fullscreen is True

    def test_music_enabled(self, config):
        """Testa configuração de música habilitada."""
        config.load()
        config.music_enabled = False
        config.save()

        assert config.music_enabled is False


class TestConfigPersistence:
    """Testes de persistência."""

    def test_save_and_load(self, temp_dir, database):
        """Testa salvamento e carregamento."""
        # Primeira instância - salvar
        config1 = Config(temp_dir, database)
        config1.load()
        config1.bible_version = "nvi"
        config1.reading_mode = "word"
        config1.word_speed = 2.0
        config1.save()

        # Segunda instância - carregar
        config2 = Config(temp_dir, database)
        config2.load()

        assert config2.bible_version == "nvi"
        assert config2.reading_mode == "word"
        assert config2.word_speed == 2.0

    def test_get_and_set_generic(self, config):
        """Testa métodos get/set genéricos."""
        config.load()
        config.set("custom_key", "custom_value")
        config.save()

        assert config.get("custom_key") == "custom_value"
        assert config.get("nonexistent", "default") == "default"
