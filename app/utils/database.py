"""
Módulo de gerenciamento do banco de dados SQLite.

Este módulo centraliza todas as operações de persistência do aplicativo,
incluindo configurações, histórico de leitura e favoritos.
"""
import os
import sqlite3
import json
from typing import Any, Optional, List, Dict
from contextlib import contextmanager


class Database:
    """
    Gerenciador do banco de dados SQLite.

    Cria o banco automaticamente se não existir e gerencia
    todas as operações de CRUD para configurações, histórico e favoritos.
    """

    DB_NAME = "selah.db"

    def __init__(self, config_dir: str) -> None:
        """
        Inicializa o banco de dados.

        Args:
            config_dir: Diretório onde o banco será armazenado.
        """
        self.config_dir = config_dir
        self.db_path = os.path.join(config_dir, self.DB_NAME)

        # Criar diretório se não existir
        os.makedirs(config_dir, exist_ok=True)

        # Inicializar banco de dados
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """
        Context manager para conexão com o banco de dados.

        Yields:
            Conexão SQLite configurada.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Cria as tabelas se não existirem."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabela de configurações (chave-valor)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Tabela de histórico de capítulos lidos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters_read (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_abbrev TEXT NOT NULL,
                    chapter_index INTEGER NOT NULL,
                    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(book_abbrev, chapter_index)
                )
            """)

            # Tabela de estatísticas de leitura
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reading_stats (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total_verses_read INTEGER DEFAULT 0,
                    total_time_reading INTEGER DEFAULT 0
                )
            """)

            # Inicializar estatísticas se não existir
            cursor.execute("""
                INSERT OR IGNORE INTO reading_stats (id, total_verses_read, total_time_reading)
                VALUES (1, 0, 0)
            """)

            # Tabela de favoritos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_index INTEGER NOT NULL,
                    chapter_index INTEGER NOT NULL,
                    verse_index INTEGER NOT NULL,
                    verse_text TEXT NOT NULL,
                    reference TEXT NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(book_index, chapter_index, verse_index)
                )
            """)

            # Índices para melhor performance nas buscas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_favorites_reference
                ON favorites(book_index, chapter_index, verse_index)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chapters_book
                ON chapters_read(book_abbrev)
            """)

    # === Métodos de Configuração ===

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Obtém uma configuração do banco.

        Args:
            key: Chave da configuração.
            default: Valor padrão se não existir.

        Returns:
            Valor da configuração ou default.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row is None:
                return default

            # Tentar deserializar JSON
            try:
                return json.loads(row['value'])
            except (json.JSONDecodeError, TypeError):
                return row['value']

    def set_setting(self, key: str, value: Any) -> None:
        """
        Define uma configuração no banco.

        Args:
            key: Chave da configuração.
            value: Valor a ser armazenado (serializado como JSON).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Serializar como JSON para suportar tipos complexos
            json_value = json.dumps(value, ensure_ascii=False)
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
            """, (key, json_value))

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Obtém todas as configurações.

        Returns:
            Dicionário com todas as configurações.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")

            settings = {}
            for row in cursor.fetchall():
                try:
                    settings[row['key']] = json.loads(row['value'])
                except (json.JSONDecodeError, TypeError):
                    settings[row['key']] = row['value']

            return settings

    # === Métodos de Histórico ===

    def mark_chapter_read(self, book_abbrev: str, chapter_index: int) -> None:
        """
        Marca um capítulo como lido.

        Args:
            book_abbrev: Abreviação do livro.
            chapter_index: Índice do capítulo.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO chapters_read (book_abbrev, chapter_index)
                VALUES (?, ?)
            """, (book_abbrev, chapter_index))

    def is_chapter_read(self, book_abbrev: str, chapter_index: int) -> bool:
        """
        Verifica se um capítulo foi lido.

        Args:
            book_abbrev: Abreviação do livro.
            chapter_index: Índice do capítulo.

        Returns:
            True se o capítulo foi lido.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM chapters_read
                WHERE book_abbrev = ? AND chapter_index = ?
            """, (book_abbrev, chapter_index))
            return cursor.fetchone() is not None

    def get_chapters_read_for_book(self, book_abbrev: str) -> List[int]:
        """
        Obtém lista de capítulos lidos de um livro.

        Args:
            book_abbrev: Abreviação do livro.

        Returns:
            Lista de índices de capítulos lidos.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT chapter_index FROM chapters_read
                WHERE book_abbrev = ?
                ORDER BY chapter_index
            """, (book_abbrev,))
            return [row['chapter_index'] for row in cursor.fetchall()]

    def get_total_chapters_read(self) -> int:
        """
        Obtém o total de capítulos lidos.

        Returns:
            Número total de capítulos lidos.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM chapters_read")
            return cursor.fetchone()['count']

    def get_reading_stats(self) -> Dict[str, int]:
        """
        Obtém as estatísticas de leitura.

        Returns:
            Dicionário com total_verses_read e total_time_reading.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT total_verses_read, total_time_reading
                FROM reading_stats WHERE id = 1
            """)
            row = cursor.fetchone()
            return {
                'total_verses_read': row['total_verses_read'],
                'total_time_reading': row['total_time_reading']
            }

    def increment_verses_read(self, count: int = 1) -> None:
        """
        Incrementa o contador de versículos lidos.

        Args:
            count: Quantidade a incrementar.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reading_stats
                SET total_verses_read = total_verses_read + ?
                WHERE id = 1
            """, (count,))

    def add_reading_time(self, seconds: int) -> None:
        """
        Adiciona tempo de leitura às estatísticas.

        Args:
            seconds: Segundos a adicionar.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reading_stats
                SET total_time_reading = total_time_reading + ?
                WHERE id = 1
            """, (seconds,))

    def clear_history(self) -> None:
        """Limpa todo o histórico de leitura."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chapters_read")
            cursor.execute("""
                UPDATE reading_stats
                SET total_verses_read = 0, total_time_reading = 0
                WHERE id = 1
            """)

    # === Métodos de Favoritos ===

    def add_favorite(
        self,
        book_index: int,
        chapter_index: int,
        verse_index: int,
        verse_text: str,
        reference: str,
        note: Optional[str] = None
    ) -> bool:
        """
        Adiciona um versículo aos favoritos.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo.
            verse_index: Índice do versículo.
            verse_text: Texto do versículo.
            reference: Referência formatada (ex: "João 3:16").
            note: Nota opcional do usuário.

        Returns:
            True se adicionado com sucesso, False se já existe.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO favorites
                    (book_index, chapter_index, verse_index, verse_text, reference, note)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (book_index, chapter_index, verse_index, verse_text, reference, note))
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_favorite(self, book_index: int, chapter_index: int, verse_index: int) -> bool:
        """
        Remove um versículo dos favoritos.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo.
            verse_index: Índice do versículo.

        Returns:
            True se removido, False se não existia.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM favorites
                WHERE book_index = ? AND chapter_index = ? AND verse_index = ?
            """, (book_index, chapter_index, verse_index))
            return cursor.rowcount > 0

    def is_favorite(self, book_index: int, chapter_index: int, verse_index: int) -> bool:
        """
        Verifica se um versículo é favorito.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo.
            verse_index: Índice do versículo.

        Returns:
            True se é favorito.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM favorites
                WHERE book_index = ? AND chapter_index = ? AND verse_index = ?
            """, (book_index, chapter_index, verse_index))
            return cursor.fetchone() is not None

    def get_all_favorites(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os favoritos.

        Returns:
            Lista de dicionários com dados dos favoritos.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, book_index, chapter_index, verse_index,
                       verse_text, reference, note, created_at
                FROM favorites
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def update_favorite_note(
        self,
        book_index: int,
        chapter_index: int,
        verse_index: int,
        note: str
    ) -> bool:
        """
        Atualiza a nota de um favorito.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo.
            verse_index: Índice do versículo.
            note: Nova nota.

        Returns:
            True se atualizado.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE favorites SET note = ?
                WHERE book_index = ? AND chapter_index = ? AND verse_index = ?
            """, (note, book_index, chapter_index, verse_index))
            return cursor.rowcount > 0

    def get_favorites_count(self) -> int:
        """
        Obtém a quantidade de favoritos.

        Returns:
            Número de favoritos.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM favorites")
            return cursor.fetchone()['count']

    # === Migração de JSON para SQLite ===

    def migrate_from_json(self, config_dir: str) -> None:
        """
        Migra dados dos arquivos JSON antigos para o SQLite.

        Args:
            config_dir: Diretório com os arquivos JSON.
        """
        settings_file = os.path.join(config_dir, "settings.json")
        history_file = os.path.join(config_dir, "history.json")

        # Migrar settings
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    for key, value in settings.items():
                        self.set_setting(key, value)
                # Renomear arquivo antigo como backup
                os.rename(settings_file, settings_file + ".backup")
            except Exception as e:
                print(f"Erro ao migrar settings: {e}")

        # Migrar history
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

                    # Migrar capítulos lidos
                    for chapter in history.get('chapters_read', []):
                        self.mark_chapter_read(
                            chapter.get('book', ''),
                            chapter.get('chapter', 0)
                        )

                    # Migrar estatísticas
                    with self._get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE reading_stats
                            SET total_verses_read = ?,
                                total_time_reading = ?
                            WHERE id = 1
                        """, (
                            history.get('total_verses_read', 0),
                            history.get('total_time_reading', 0)
                        ))

                # Renomear arquivo antigo como backup
                os.rename(history_file, history_file + ".backup")
            except Exception as e:
                print(f"Erro ao migrar history: {e}")
