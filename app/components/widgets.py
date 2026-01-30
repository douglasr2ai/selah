"""
Componentes de UI reutilizáveis.
"""
import customtkinter as ctk


# Paleta de cores - Modo normal
COLORS = {
    "bg_main": "#0D0D0D",      # Fundo principal (preto profundo)
    "bg_card": "#1A1A1A",      # Fundo de cards/menus
    "text_primary": "#FFFFFF",  # Texto principal
    "text_secondary": "#A0A0A0",  # Texto secundário
    "accent": "#4A90D9",       # Destaque/botões (azul suave)
    "success": "#4CAF50",      # Sucesso/lido (verde)
    "progress": "#4A90D9",     # Barra de progresso
}

# Paleta de cores - Modo noturno (quente/sépia)
COLORS_NIGHT = {
    "bg_main": "#1A1408",      # Fundo principal (marrom escuro)
    "bg_card": "#2A2010",      # Fundo de cards (marrom)
    "text_primary": "#FFE4B5",  # Texto principal (moccasin/âmbar)
    "text_secondary": "#C4A574",  # Texto secundário (tan)
    "accent": "#D4A055",       # Destaque/botões (dourado)
    "success": "#8B9A46",      # Sucesso/lido (verde oliva)
    "progress": "#D4A055",     # Barra de progresso
}


def get_colors(night_mode: bool = False) -> dict:
    """Retorna a paleta de cores apropriada."""
    return COLORS_NIGHT if night_mode else COLORS


class StyledButton(ctk.CTkButton):
    """Botão estilizado com tema escuro."""

    def __init__(self, master, text: str, command=None, width: int = 200,
                 height: int = 40, variant: str = "primary", **kwargs):
        if variant == "primary":
            fg_color = COLORS["accent"]
            hover_color = "#3A7BC8"
            text_color = COLORS["text_primary"]
        elif variant == "secondary":
            fg_color = COLORS["bg_card"]
            hover_color = "#2A2A2A"
            text_color = COLORS["text_primary"]
        elif variant == "success":
            fg_color = COLORS["success"]
            hover_color = "#3D9140"
            text_color = COLORS["text_primary"]
        else:
            fg_color = COLORS["accent"]
            hover_color = "#3A7BC8"
            text_color = COLORS["text_primary"]

        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            **kwargs
        )


class StyledLabel(ctk.CTkLabel):
    """Label estilizado."""

    def __init__(self, master, text: str, size: int = 14,
                 color: str = "primary", weight: str = "normal", **kwargs):
        text_color = COLORS["text_primary"] if color == "primary" else COLORS["text_secondary"]

        super().__init__(
            master,
            text=text,
            text_color=text_color,
            font=ctk.CTkFont(size=size, weight=weight),
            **kwargs
        )


class Card(ctk.CTkFrame):
    """Card/container com fundo escuro."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            **kwargs
        )


class ProgressBar(ctk.CTkProgressBar):
    """Barra de progresso estilizada."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            progress_color=COLORS["progress"],
            fg_color="#2A2A2A",
            height=8,
            corner_radius=4,
            **kwargs
        )


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Frame com scroll estilizado."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_main"],
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["accent"],
            **kwargs
        )


class VerseText(ctk.CTkTextbox):
    """Área de texto para exibir versículos."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_main"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Georgia", size=24),
            wrap="word",
            state="disabled",
            **kwargs
        )

    def set_text(self, text: str) -> None:
        """Define o texto do versículo."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", text)
        self.configure(state="disabled")
        # Centralizar o texto
        self.tag_add("center", "1.0", "end")
        self.tag_configure("center", justify="center")


class BookButton(ctk.CTkButton):
    """Botão para seleção de livro."""

    def __init__(self, master, text: str, command=None, is_read: bool = False, **kwargs):
        fg_color = COLORS["success"] if is_read else COLORS["bg_card"]
        hover_color = "#3D9140" if is_read else "#2A2A2A"

        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=COLORS["text_primary"],
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            height=35,
            **kwargs
        )


class ChapterButton(ctk.CTkButton):
    """Botão para seleção de capítulo."""

    def __init__(self, master, text: str, command=None, is_read: bool = False, **kwargs):
        fg_color = COLORS["success"] if is_read else COLORS["bg_card"]
        hover_color = "#3D9140" if is_read else "#2A2A2A"

        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=COLORS["text_primary"],
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            width=50,
            height=35,
            **kwargs
        )
