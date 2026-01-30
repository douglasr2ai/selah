"""
Tela de estatísticas/dashboard.
"""
import customtkinter as ctk
from app.components.widgets import COLORS, StyledButton, StyledLabel, Card, ProgressBar


class DashboardScreen(ctk.CTkFrame):
    """Tela de estatísticas de leitura."""

    def __init__(self, master, history, on_back):
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.history = history
        self.on_back = on_back

        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        back_btn = StyledButton(
            header,
            text="< Voltar",
            command=self.on_back,
            width=100,
            height=40,
            variant="secondary"
        )
        back_btn.pack(side="left", padx=20, pady=10)

        title = StyledLabel(
            header,
            text="Estatísticas de Leitura",
            size=20,
            weight="bold"
        )
        title.pack(side="left", padx=20, pady=10)

        # Container de estatísticas
        stats = self.history.get_stats()

        # Card principal
        main_card = Card(self)
        main_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        content = ctk.CTkFrame(main_card, fg_color="transparent")
        content.pack(expand=True, pady=40)

        # Progresso geral
        progress_label = StyledLabel(
            content,
            text="Progresso da Bíblia",
            size=24,
            weight="bold"
        )
        progress_label.pack(pady=(0, 20))

        progress_bar = ProgressBar(content, width=500)
        progress_bar.pack(pady=10)
        progress_bar.set(stats["progress_percent"] / 100)

        progress_text = StyledLabel(
            content,
            text=f"{stats['progress_percent']}% concluído",
            size=18,
            color="secondary"
        )
        progress_text.pack(pady=(5, 30))

        # Grid de estatísticas
        stats_grid = ctk.CTkFrame(content, fg_color="transparent")
        stats_grid.pack(pady=20)

        # Capítulos lidos
        self._create_stat_card(
            stats_grid,
            "Capítulos Lidos",
            f"{stats['chapters_read']} / {stats['total_chapters']}",
            0, 0
        )

        # Versículos lidos
        self._create_stat_card(
            stats_grid,
            "Versículos Lidos",
            str(stats['total_verses_read']),
            0, 1
        )

        # Tempo de leitura
        time_text = f"{stats['total_time_hours']}h {stats['total_time_minutes']}min"
        self._create_stat_card(
            stats_grid,
            "Tempo de Leitura",
            time_text,
            0, 2
        )

        # Botão limpar histórico
        clear_btn = StyledButton(
            content,
            text="Limpar Histórico",
            command=self._confirm_clear,
            width=200,
            height=40,
            variant="secondary"
        )
        clear_btn.pack(pady=(40, 0))

    def _create_stat_card(self, parent, title: str, value: str, row: int, col: int):
        """Cria um card de estatística."""
        card = Card(parent)
        card.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=20)

        title_label = StyledLabel(
            inner,
            text=title,
            size=14,
            color="secondary"
        )
        title_label.pack()

        value_label = StyledLabel(
            inner,
            text=value,
            size=28,
            weight="bold"
        )
        value_label.pack(pady=(5, 0))

    def _confirm_clear(self):
        """Confirma a limpeza do histórico."""
        # Criar janela de confirmação
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar")
        dialog.geometry("400x200")
        dialog.configure(fg_color=COLORS["bg_main"])
        dialog.transient(self.master)
        dialog.grab_set()

        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (200)
        y = (dialog.winfo_screenheight() // 2) - (100)
        dialog.geometry(f"+{x}+{y}")

        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(expand=True)

        label = StyledLabel(
            content,
            text="Tem certeza que deseja limpar\ntodo o histórico de leitura?",
            size=16
        )
        label.pack(pady=20)

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=10)

        cancel_btn = StyledButton(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            width=120,
            height=40,
            variant="secondary"
        )
        cancel_btn.pack(side="left", padx=10)

        confirm_btn = StyledButton(
            btn_frame,
            text="Limpar",
            command=lambda: self._clear_history(dialog),
            width=120,
            height=40,
            variant="primary"
        )
        confirm_btn.pack(side="left", padx=10)

    def _clear_history(self, dialog):
        """Limpa o histórico e atualiza a tela."""
        self.history.clear_history()
        dialog.destroy()
        # Recriar widgets para atualizar valores
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()
