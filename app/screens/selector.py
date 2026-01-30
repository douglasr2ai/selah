"""
Tela de seleção de livro e capítulo.
"""
import customtkinter as ctk
from app.components.widgets import (
    COLORS, StyledButton, StyledLabel, Card,
    ScrollableFrame, BookButton, ChapterButton
)


class SelectorScreen(ctk.CTkFrame):
    """Tela para selecionar livro e capítulo."""

    def __init__(self, master, bible, history, on_select, on_back):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.bible = bible
        self.history = history
        self.on_select = on_select
        self.on_back = on_back
        self.selected_book_index = None

        self._create_widgets()
        self._show_books()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        back_btn = StyledButton(
            header,
            text="< Voltar",
            command=self._handle_back,
            width=100,
            height=40,
            variant="secondary"
        )
        back_btn.pack(side="left", padx=20, pady=10)

        self.title_label = StyledLabel(
            header,
            text="Selecione um Livro",
            size=20,
            weight="bold"
        )
        self.title_label.pack(side="left", padx=20, pady=10)

        # Área de conteúdo
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _handle_back(self):
        """Volta para a lista de livros ou menu."""
        if self.selected_book_index is not None:
            self.selected_book_index = None
            self._show_books()
        else:
            self.on_back()

    def _show_books(self):
        """Mostra a lista de livros."""
        self.title_label.configure(text="Selecione um Livro")

        # Limpar conteúdo
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Frame com scroll
        scroll_frame = ScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True)

        # Grid de livros
        books = self.bible.get_all_books()
        cols = 5
        for i, book in enumerate(books):
            row = i // cols
            col = i % cols

            # Verificar se todos os capítulos foram lidos
            chapters_read = self.history.get_chapters_read_for_book(book["abbrev"])
            is_complete = len(chapters_read) >= book["chapters"]

            btn = BookButton(
                scroll_frame,
                text=book["name"],
                command=lambda idx=book["index"]: self._select_book(idx),
                is_read=is_complete,
                width=140
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # Configurar colunas
        for col in range(cols):
            scroll_frame.columnconfigure(col, weight=1)

    def _select_book(self, book_index: int):
        """Seleciona um livro e mostra capítulos."""
        self.selected_book_index = book_index
        self._show_chapters(book_index)

    def _show_chapters(self, book_index: int):
        """Mostra os capítulos de um livro."""
        book_name = self.bible.get_book_name(book_index)
        self.title_label.configure(text=f"{book_name} - Selecione um Capítulo")

        # Limpar conteúdo
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Frame com scroll
        scroll_frame = ScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True)

        # Grid de capítulos
        chapter_count = self.bible.get_chapter_count(book_index)
        book_abbrev = self.bible.get_book_abbrev(book_index)
        chapters_read = self.history.get_chapters_read_for_book(book_abbrev)

        cols = 10
        for i in range(chapter_count):
            row = i // cols
            col = i % cols

            is_read = i in chapters_read

            btn = ChapterButton(
                scroll_frame,
                text=str(i + 1),
                command=lambda idx=i: self._select_chapter(idx),
                is_read=is_read
            )
            btn.grid(row=row, column=col, padx=3, pady=3)

        # Configurar colunas
        for col in range(cols):
            scroll_frame.columnconfigure(col, weight=1)

    def _select_chapter(self, chapter_index: int):
        """Seleciona um capítulo e inicia a leitura."""
        self.on_select(self.selected_book_index, chapter_index)
