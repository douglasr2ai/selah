"""
Classe principal do aplicativo Leitor Bíblico.

Este módulo contém a classe principal que orquestra todas as telas
e componentes do aplicativo.
"""
import os
import customtkinter as ctk

from app.utils.database import Database
from app.utils.bible import Bible
from app.utils.config import Config
from app.utils.history import History
from app.utils.music import MusicPlayer
from app.components.widgets import COLORS
from app.screens.welcome import WelcomeScreen
from app.screens.menu import MenuScreen
from app.screens.selector import SelectorScreen
from app.screens.reader import ReaderScreen
from app.screens.dashboard import DashboardScreen
from app.screens.search import SearchScreen
from app.screens.favorites import FavoritesScreen


class BibliaApp(ctk.CTk):
    """
    Aplicativo principal de leitura bíblica.

    Gerencia a navegação entre telas, configurações, histórico,
    música de fundo e leitura da Bíblia.
    """

    def __init__(self) -> None:
        """Inicializa o aplicativo."""
        super().__init__()

        # Configuração da janela
        self.title("Leitor Bíblico")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.configure(fg_color=COLORS["bg_main"])

        # Determinar diretórios
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.app_dir, "data")
        self.config_dir = os.path.join(self.app_dir, "config")
        self.music_dir = os.path.join(self.app_dir, "music")

        # Criar pasta de música se não existir
        os.makedirs(self.music_dir, exist_ok=True)

        # Inicializar banco de dados compartilhado
        self.database = Database(self.config_dir)

        # Inicializar componentes com banco compartilhado
        self.bible = Bible(self.data_dir)
        self.config = Config(self.config_dir, self.database)
        self.history = History(self.config_dir, self.database)
        self.music = MusicPlayer()

        # Carregar dados
        self.config.load()
        self.history.load()

        # Configurar música (pasta fixa: music/)
        self.music.set_folder(self.music_dir)
        self.music.set_volume(self.config.music_volume)

        # Tela atual
        self.current_screen = None

        # Configurar fechamento
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Mostrar tela inicial
        self._show_initial_screen()

    def _show_initial_screen(self):
        """Mostra a tela inicial apropriada."""
        if self.config.is_first_time():
            self._show_welcome()
        else:
            # Carregar bíblia salva
            if self.bible.load(self.config.bible_version):
                self._show_menu()
            else:
                self._show_welcome()

    def _clear_screen(self):
        """Remove a tela atual."""
        if self.current_screen:
            if hasattr(self.current_screen, 'cleanup'):
                self.current_screen.cleanup()
            self.current_screen.destroy()
            self.current_screen = None

    def _show_welcome(self):
        """Mostra a tela de boas-vindas."""
        self._clear_screen()
        self.current_screen = WelcomeScreen(self, self._on_select_version)
        self.current_screen.pack(fill="both", expand=True)

    def _on_select_version(self, version: str):
        """Callback quando uma versão é selecionada."""
        if self.bible.load(version):
            self.config.bible_version = version
            self.config.save()
            self._show_menu()

    def _show_menu(self) -> None:
        """Mostra o menu principal."""
        self._clear_screen()
        self.current_screen = MenuScreen(self, {
            "continue_reading": self._continue_reading,
            "select_chapter": self._show_selector,
            "search": self._show_search,
            "favorites": self._show_favorites,
            "show_dashboard": self._show_dashboard,
            "change_version": self._show_welcome,
            "quit": self._on_close
        })
        self.current_screen.pack(fill="both", expand=True)

    def _continue_reading(self):
        """Continua a leitura de onde parou."""
        pos = self.config.last_position
        self._start_reading(
            pos.get("book_index", 0),
            pos.get("chapter_index", 0),
            pos.get("verse_index", 0)
        )

    def _show_selector(self):
        """Mostra a tela de seleção de livro/capítulo."""
        self._clear_screen()
        self.current_screen = SelectorScreen(
            self,
            self.bible,
            self.history,
            self._on_select_chapter,
            self._show_menu
        )
        self.current_screen.pack(fill="both", expand=True)

    def _on_select_chapter(self, book_index: int, chapter_index: int) -> None:
        """Callback quando um capítulo é selecionado."""
        self._start_reading(book_index, chapter_index, 0)

    def _show_search(self) -> None:
        """Mostra a tela de busca."""
        self._clear_screen()
        self.current_screen = SearchScreen(
            self,
            self.bible,
            self._on_search_select,
            self._show_menu
        )
        self.current_screen.pack(fill="both", expand=True)

    def _on_search_select(self, book_index: int, chapter_index: int, verse_index: int) -> None:
        """Callback quando um resultado de busca é selecionado."""
        self._start_reading(book_index, chapter_index, verse_index)

    def _show_favorites(self) -> None:
        """Mostra a tela de favoritos."""
        self._clear_screen()
        self.current_screen = FavoritesScreen(
            self,
            self.database,
            self._on_favorite_select,
            self._show_menu
        )
        self.current_screen.pack(fill="both", expand=True)

    def _on_favorite_select(self, book_index: int, chapter_index: int, verse_index: int) -> None:
        """Callback quando um favorito é selecionado."""
        self._start_reading(book_index, chapter_index, verse_index)

    def _start_reading(self, book_index: int, chapter_index: int, verse_index: int) -> None:
        """Inicia a leitura em uma posição específica."""
        self._clear_screen()
        # Iniciar contagem de tempo de leitura
        self.history.start_session()
        self.current_screen = ReaderScreen(
            self,
            self.bible,
            self.config,
            self.history,
            self.music,
            self.database,
            self._on_exit_reader
        )
        self.current_screen.pack(fill="both", expand=True)
        self.current_screen.start_reading(book_index, chapter_index, verse_index)

    def _on_exit_reader(self):
        """Callback ao sair da tela de leitura."""
        # Parar contagem de tempo de leitura
        self.history.end_session()
        self._show_menu()

    def _show_dashboard(self):
        """Mostra o dashboard de estatísticas."""
        self._clear_screen()
        self.current_screen = DashboardScreen(
            self,
            self.history,
            self._show_menu
        )
        self.current_screen.pack(fill="both", expand=True)

    def _on_close(self):
        """Callback ao fechar o aplicativo."""
        # Parar música
        self.music.cleanup()
        # Salvar estado
        self.config.save()
        # Encerrar sessão se estiver ativa (fechou durante leitura)
        if self.history.is_session_active():
            self.history.end_session()
        self.history.save()

        # Fechar
        self.destroy()
