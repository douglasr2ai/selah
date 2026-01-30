"""
Gerenciador de configurações do usuário.

Este módulo gerencia todas as configurações persistentes do aplicativo,
utilizando SQLite como backend de armazenamento.
"""
from typing import Any, Optional, Dict

from app.utils.database import Database


class Config:
    """
    Gerencia as configurações do aplicativo.

    As configurações são armazenadas em um banco SQLite e incluem
    preferências de leitura, posição, música e interface.
    """

    DEFAULT_SETTINGS: Dict[str, Any] = {
        "bible_version": None,  # None = primeira vez, precisa escolher
        "reading_mode": "chunks",  # chunks ou word
        "word_speed": 1.0,  # segundos por palavra
        "last_position": {
            "book_index": 0,
            "chapter_index": 0,
            "verse_index": 0
        },
        "music_folder": None,  # Pasta com músicas de fundo
        "music_volume": 0.5,  # Volume da música (0.0 a 1.0)
        "music_enabled": True,  # Se a música está habilitada
        "font_size": 32,  # Tamanho da fonte do versículo
        "night_mode": False,  # Modo noturno (cores quentes)
        "fullscreen": False  # Tela cheia
    }

    def __init__(self, config_dir: str, database: Optional[Database] = None) -> None:
        """
        Inicializa o gerenciador de configurações.

        Args:
            config_dir: Diretório de configuração.
            database: Instância do banco de dados (opcional, será criada se não fornecida).
        """
        self.config_dir = config_dir
        self.db = database if database else Database(config_dir)
        self._cache: Dict[str, Any] = {}

    def load(self) -> bool:
        """
        Carrega as configurações do banco de dados.

        Também realiza migração de arquivos JSON antigos se existirem.

        Returns:
            True se carregou configurações existentes, False se usou defaults.
        """
        # Tentar migrar dados antigos do JSON
        self.db.migrate_from_json(self.config_dir)

        # Carregar configurações do banco
        stored = self.db.get_all_settings()

        if not stored:
            # Primeira execução - salvar defaults
            for key, value in self.DEFAULT_SETTINGS.items():
                self.db.set_setting(key, value)
            self._cache = self.DEFAULT_SETTINGS.copy()
            return False

        # Mesclar com defaults para garantir todas as chaves
        self._cache = {**self.DEFAULT_SETTINGS, **stored}
        return True

    def save(self) -> bool:
        """
        Salva as configurações no banco de dados.

        Returns:
            True se salvou com sucesso.
        """
        try:
            for key, value in self._cache.items():
                self.db.set_setting(key, value)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retorna uma configuração.

        Args:
            key: Chave da configuração.
            default: Valor padrão se não existir.

        Returns:
            Valor da configuração.
        """
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Define uma configuração.

        Args:
            key: Chave da configuração.
            value: Valor a ser armazenado.
        """
        self._cache[key] = value
        self.db.set_setting(key, value)

    @property
    def bible_version(self) -> Optional[str]:
        """Versão da Bíblia selecionada (acf ou nvi)."""
        return self._cache.get("bible_version")

    @bible_version.setter
    def bible_version(self, value: str) -> None:
        self._cache["bible_version"] = value

    @property
    def reading_mode(self) -> str:
        """Modo de leitura (chunks ou word)."""
        return self._cache.get("reading_mode", "chunks")

    @reading_mode.setter
    def reading_mode(self, value: str) -> None:
        self._cache["reading_mode"] = value

    @property
    def word_speed(self) -> float:
        """Velocidade de leitura em segundos por palavra (0.1 a 5.0)."""
        return self._cache.get("word_speed", 1.0)

    @word_speed.setter
    def word_speed(self, value: float) -> None:
        self._cache["word_speed"] = max(0.1, min(5.0, value))

    @property
    def last_position(self) -> Dict[str, int]:
        """Última posição de leitura (book_index, chapter_index, verse_index)."""
        return self._cache.get("last_position", {
            "book_index": 0,
            "chapter_index": 0,
            "verse_index": 0
        })

    @last_position.setter
    def last_position(self, value: Dict[str, int]) -> None:
        self._cache["last_position"] = value

    def is_first_time(self) -> bool:
        """
        Verifica se é a primeira vez que o usuário abre o app.

        Returns:
            True se nenhuma versão da Bíblia foi selecionada.
        """
        return self.bible_version is None

    @property
    def music_folder(self) -> Optional[str]:
        """Pasta com músicas de fundo."""
        return self._cache.get("music_folder")

    @music_folder.setter
    def music_folder(self, value: Optional[str]) -> None:
        self._cache["music_folder"] = value

    @property
    def music_volume(self) -> float:
        """Volume da música (0.0 a 1.0)."""
        return self._cache.get("music_volume", 0.5)

    @music_volume.setter
    def music_volume(self, value: float) -> None:
        self._cache["music_volume"] = max(0.0, min(1.0, value))

    @property
    def music_enabled(self) -> bool:
        """Se a música de fundo está habilitada."""
        return self._cache.get("music_enabled", True)

    @music_enabled.setter
    def music_enabled(self, value: bool) -> None:
        self._cache["music_enabled"] = value

    @property
    def font_size(self) -> int:
        """Tamanho da fonte dos versículos (16 a 72)."""
        return self._cache.get("font_size", 32)

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._cache["font_size"] = max(16, min(72, value))

    @property
    def night_mode(self) -> bool:
        """Se o modo noturno (cores quentes) está ativo."""
        return self._cache.get("night_mode", False)

    @night_mode.setter
    def night_mode(self, value: bool) -> None:
        self._cache["night_mode"] = value

    @property
    def fullscreen(self) -> bool:
        """Se o modo tela cheia está ativo."""
        return self._cache.get("fullscreen", False)

    @fullscreen.setter
    def fullscreen(self, value: bool) -> None:
        self._cache["fullscreen"] = value
