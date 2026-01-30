"""
Gerenciador de histórico de leitura.

Este módulo gerencia o histórico e estatísticas de leitura,
utilizando SQLite como backend de armazenamento.
"""
import time
from typing import Optional, Dict, List

from app.utils.database import Database


class History:
    """
    Gerencia o histórico e estatísticas de leitura.

    Rastreia capítulos lidos, versículos e tempo de leitura,
    armazenando tudo em um banco SQLite.
    """

    TOTAL_CHAPTERS = 1189  # Total de capítulos na Bíblia

    def __init__(self, config_dir: str, database: Optional[Database] = None) -> None:
        """
        Inicializa o gerenciador de histórico.

        Args:
            config_dir: Diretório de configuração.
            database: Instância do banco de dados (opcional).
        """
        self.config_dir = config_dir
        self.db = database if database else Database(config_dir)
        self._session_start: Optional[float] = None

    def load(self) -> bool:
        """
        Carrega o histórico do banco de dados.

        Também realiza migração de arquivos JSON antigos se existirem.

        Returns:
            True se carregou dados existentes.
        """
        # Migração já é feita pelo Database ou Config
        return self.db.get_total_chapters_read() > 0

    def save(self) -> bool:
        """
        Salva o histórico (operação automática com SQLite).

        Returns:
            Sempre True pois SQLite salva automaticamente.
        """
        return True

    def start_session(self) -> None:
        """Inicia uma sessão de leitura."""
        self._session_start = time.time()

    def end_session(self) -> None:
        """Finaliza a sessão de leitura e registra o tempo."""
        if self._session_start is not None:
            elapsed = int(time.time() - self._session_start)
            self.db.add_reading_time(elapsed)
            self._session_start = None

    def is_session_active(self) -> bool:
        """
        Verifica se há uma sessão de leitura ativa.

        Returns:
            True se há uma sessão em andamento.
        """
        return self._session_start is not None

    def mark_chapter_read(self, book_abbrev: str, chapter_index: int) -> None:
        """
        Marca um capítulo como lido.

        Args:
            book_abbrev: Abreviação do livro (ex: "gn", "jo").
            chapter_index: Índice do capítulo (0-based).
        """
        self.db.mark_chapter_read(book_abbrev, chapter_index)

    def is_chapter_read(self, book_abbrev: str, chapter_index: int) -> bool:
        """
        Verifica se um capítulo foi lido.

        Args:
            book_abbrev: Abreviação do livro.
            chapter_index: Índice do capítulo.

        Returns:
            True se o capítulo foi lido.
        """
        return self.db.is_chapter_read(book_abbrev, chapter_index)

    def increment_verses(self, count: int = 1) -> None:
        """
        Incrementa o contador de versículos lidos.

        Args:
            count: Quantidade de versículos a incrementar.
        """
        self.db.increment_verses_read(count)

    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas de leitura.

        Returns:
            Dicionário com estatísticas:
            - chapters_read: Número de capítulos lidos
            - total_chapters: Total de capítulos na Bíblia (1189)
            - total_verses_read: Total de versículos lidos
            - total_time_hours: Horas de leitura
            - total_time_minutes: Minutos de leitura
            - total_time_seconds: Total em segundos
            - progress_percent: Percentual de progresso
        """
        stats = self.db.get_reading_stats()
        total_time = stats['total_time_reading']

        # Se há sessão ativa, adicionar tempo atual
        if self._session_start is not None:
            total_time += int(time.time() - self._session_start)

        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        chapters_read = self.db.get_total_chapters_read()

        return {
            "chapters_read": chapters_read,
            "total_chapters": self.TOTAL_CHAPTERS,
            "total_verses_read": stats['total_verses_read'],
            "total_time_hours": hours,
            "total_time_minutes": minutes,
            "total_time_seconds": total_time,
            "progress_percent": round(chapters_read / self.TOTAL_CHAPTERS * 100, 1)
        }

    def get_chapters_read_for_book(self, book_abbrev: str) -> List[int]:
        """
        Retorna lista de capítulos lidos de um livro.

        Args:
            book_abbrev: Abreviação do livro.

        Returns:
            Lista de índices de capítulos lidos.
        """
        return self.db.get_chapters_read_for_book(book_abbrev)

    def clear_history(self) -> None:
        """Limpa todo o histórico de leitura."""
        self.db.clear_history()
        self._session_start = None
