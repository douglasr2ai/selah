"""
Tela do menu principal.
"""
import customtkinter as ctk
from app.components.widgets import COLORS, StyledButton, StyledLabel, Card


class MenuScreen(ctk.CTkFrame):
    """Menu principal do aplicativo."""

    def __init__(self, master, callbacks: dict):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.callbacks = callbacks

        self._create_widgets()

    def _create_widgets(self):
        # Container central
        container = Card(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(padx=60, pady=50)

        # Título
        title = StyledLabel(
            inner,
            text="Leitor Bíblico",
            size=32,
            weight="bold"
        )
        title.pack(pady=(0, 40))

        # Continuar leitura
        continue_btn = StyledButton(
            inner,
            text="Continuar Leitura",
            command=self.callbacks.get("continue_reading"),
            width=280,
            height=50,
            variant="primary"
        )
        continue_btn.pack(pady=10)

        # Selecionar livro/capítulo
        select_btn = StyledButton(
            inner,
            text="Selecionar Livro/Capítulo",
            command=self.callbacks.get("select_chapter"),
            width=280,
            height=50,
            variant="secondary"
        )
        select_btn.pack(pady=10)

        # Buscar
        search_btn = StyledButton(
            inner,
            text="Buscar na Bíblia",
            command=self.callbacks.get("search"),
            width=280,
            height=50,
            variant="secondary"
        )
        search_btn.pack(pady=10)

        # Favoritos
        favorites_btn = StyledButton(
            inner,
            text="Meus Favoritos",
            command=self.callbacks.get("favorites"),
            width=280,
            height=50,
            variant="secondary"
        )
        favorites_btn.pack(pady=10)

        # Dashboard
        dashboard_btn = StyledButton(
            inner,
            text="Estatísticas",
            command=self.callbacks.get("show_dashboard"),
            width=280,
            height=50,
            variant="secondary"
        )
        dashboard_btn.pack(pady=10)

        # Trocar versão
        version_btn = StyledButton(
            inner,
            text="Trocar Versão da Bíblia",
            command=self.callbacks.get("change_version"),
            width=280,
            height=50,
            variant="secondary"
        )
        version_btn.pack(pady=10)

        # Sair
        quit_btn = StyledButton(
            inner,
            text="Sair",
            command=self.callbacks.get("quit"),
            width=280,
            height=50,
            variant="secondary"
        )
        quit_btn.pack(pady=(20, 0))
