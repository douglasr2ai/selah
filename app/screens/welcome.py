"""
Tela de boas-vindas - Seleção inicial de versão da Bíblia.
"""
import customtkinter as ctk
from app.components.widgets import COLORS, StyledButton, StyledLabel, Card


class WelcomeScreen(ctk.CTkFrame):
    """Tela para primeira execução - escolher versão da Bíblia."""

    def __init__(self, master, on_select_version):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.on_select_version = on_select_version

        self._create_widgets()

    def _create_widgets(self):
        # Container central
        container = Card(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Padding interno
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(padx=60, pady=50)

        # Título
        title = StyledLabel(
            inner,
            text="Bem-vindo ao Leitor Bíblico",
            size=28,
            weight="bold"
        )
        title.pack(pady=(0, 10))

        # Subtítulo
        subtitle = StyledLabel(
            inner,
            text="Escolha sua versão preferida da Bíblia:",
            size=16,
            color="secondary"
        )
        subtitle.pack(pady=(0, 40))

        # Botão ACF
        acf_btn = StyledButton(
            inner,
            text="ACF - Almeida Corrigida Fiel",
            command=lambda: self.on_select_version("acf"),
            width=300,
            height=50,
            variant="primary"
        )
        acf_btn.pack(pady=10)

        # Descrição ACF
        acf_desc = StyledLabel(
            inner,
            text="Tradução tradicional e fiel aos textos originais",
            size=12,
            color="secondary"
        )
        acf_desc.pack(pady=(0, 20))

        # Botão NVI
        nvi_btn = StyledButton(
            inner,
            text="NVI - Nova Versão Internacional",
            command=lambda: self.on_select_version("nvi"),
            width=300,
            height=50,
            variant="secondary"
        )
        nvi_btn.pack(pady=10)

        # Descrição NVI
        nvi_desc = StyledLabel(
            inner,
            text="Linguagem contemporânea e acessível",
            size=12,
            color="secondary"
        )
        nvi_desc.pack(pady=(0, 20))
