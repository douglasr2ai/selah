"""
Tela de favoritos/marcadores.

Este módulo exibe os versículos salvos como favoritos
e permite navegar até eles ou removê-los.
"""
import customtkinter as ctk
from typing import Callable

from app.components.widgets import (
    COLORS, StyledButton, StyledLabel, Card, ScrollableFrame
)


class FavoritesScreen(ctk.CTkFrame):
    """
    Tela de visualização de favoritos.

    Exibe todos os versículos marcados como favoritos,
    permitindo navegar até eles ou removê-los.
    """

    def __init__(
        self,
        master,
        database,
        on_select: Callable[[int, int, int], None],
        on_back: Callable[[], None]
    ) -> None:
        """
        Inicializa a tela de favoritos.

        Args:
            master: Widget pai.
            database: Instância do banco de dados.
            on_select: Callback ao selecionar um favorito (book, chapter, verse).
            on_back: Callback para voltar ao menu.
        """
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.db = database
        self.on_select = on_select
        self.on_back = on_back

        self._create_widgets()
        self._load_favorites()
        self._bind_keys()

    def _create_widgets(self) -> None:
        """Cria os widgets da tela."""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        title = StyledLabel(
            header,
            text="Meus Favoritos",
            size=24,
            weight="bold"
        )
        title.pack(side="left", padx=20, pady=15)

        # Contador de favoritos
        self.count_label = StyledLabel(
            header,
            text="",
            size=14,
            color="secondary"
        )
        self.count_label.pack(side="left", padx=10, pady=15)

        back_btn = StyledButton(
            header,
            text="Voltar (Esc)",
            command=self.on_back,
            width=100,
            height=35,
            variant="secondary"
        )
        back_btn.pack(side="right", padx=20, pady=12)

        # Área de favoritos (scrollable)
        self.favorites_frame = ScrollableFrame(self)
        self.favorites_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _bind_keys(self) -> None:
        """Configura atalhos de teclado."""
        self.master.bind("<Escape>", lambda e: self.on_back())

    def _unbind_keys(self) -> None:
        """Remove atalhos de teclado."""
        try:
            self.master.unbind("<Escape>")
        except:
            pass

    def _load_favorites(self) -> None:
        """Carrega e exibe os favoritos."""
        self._clear_favorites()

        favorites = self.db.get_all_favorites()

        if not favorites:
            self.count_label.configure(text="")
            self._show_empty_message()
            return

        self.count_label.configure(
            text=f"({len(favorites)} versículo{'s' if len(favorites) > 1 else ''})"
        )

        for fav in favorites:
            self._add_favorite_card(fav)

    def _clear_favorites(self) -> None:
        """Limpa a lista de favoritos."""
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()

    def _show_empty_message(self) -> None:
        """Exibe mensagem quando não há favoritos."""
        empty_frame = ctk.CTkFrame(self.favorites_frame, fg_color="transparent")
        empty_frame.pack(fill="x", pady=50)

        icon = StyledLabel(
            empty_frame,
            text="",
            size=48
        )
        icon.pack(pady=(0, 20))

        message = StyledLabel(
            empty_frame,
            text="Nenhum versículo favorito ainda",
            size=18,
            weight="bold"
        )
        message.pack(pady=(0, 10))

        hint = StyledLabel(
            empty_frame,
            text="Durante a leitura, clique no botao para salvar versículos",
            size=14,
            color="secondary"
        )
        hint.pack()

    def _add_favorite_card(self, favorite: dict) -> None:
        """
        Adiciona um card de favorito.

        Args:
            favorite: Dicionário com dados do favorito.
        """
        card = Card(self.favorites_frame)
        card.pack(fill="x", pady=5)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=15)

        # Linha superior: referência e botão remover
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        ref_btn = ctk.CTkButton(
            top_row,
            text=favorite["reference"],
            command=lambda f=favorite: self._select_favorite(f),
            fg_color="transparent",
            hover_color=COLORS["bg_main"],
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        ref_btn.pack(side="left")

        remove_btn = StyledButton(
            top_row,
            text="Remover",
            command=lambda f=favorite: self._remove_favorite(f),
            width=80,
            height=28,
            variant="secondary"
        )
        remove_btn.pack(side="right")

        # Texto do versículo
        verse_text = favorite["verse_text"]
        if len(verse_text) > 250:
            verse_text = verse_text[:250] + "..."

        verse_label = StyledLabel(
            inner,
            text=f'"{verse_text}"',
            size=14,
            color="secondary"
        )
        verse_label.pack(fill="x", pady=(10, 0))

        # Nota (se houver)
        if favorite.get("note"):
            note_frame = ctk.CTkFrame(inner, fg_color=COLORS["bg_main"], corner_radius=8)
            note_frame.pack(fill="x", pady=(10, 0))

            note_label = StyledLabel(
                note_frame,
                text=f"Nota: {favorite['note']}",
                size=12,
                color="secondary"
            )
            note_label.pack(padx=10, pady=8)

        # Botão ir para versículo
        go_btn = StyledButton(
            inner,
            text="Ir para versículo",
            command=lambda f=favorite: self._select_favorite(f),
            width=130,
            height=30,
            variant="primary"
        )
        go_btn.pack(anchor="e", pady=(10, 0))

    def _select_favorite(self, favorite: dict) -> None:
        """
        Seleciona um favorito e navega até ele.

        Args:
            favorite: Dicionário com dados do favorito.
        """
        self._unbind_keys()
        self.on_select(
            favorite["book_index"],
            favorite["chapter_index"],
            favorite["verse_index"]
        )

    def _remove_favorite(self, favorite: dict) -> None:
        """
        Remove um favorito.

        Args:
            favorite: Dicionário com dados do favorito.
        """
        self.db.remove_favorite(
            favorite["book_index"],
            favorite["chapter_index"],
            favorite["verse_index"]
        )
        self._load_favorites()

    def cleanup(self) -> None:
        """Limpa recursos ao sair da tela."""
        self._unbind_keys()
