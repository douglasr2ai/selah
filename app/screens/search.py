"""
Tela de busca na Bíblia.

Este módulo fornece uma interface para buscar versículos por texto
ou referência bíblica.
"""
import customtkinter as ctk
from typing import Callable, Optional

from app.components.widgets import (
    COLORS, StyledButton, StyledLabel, Card, ScrollableFrame
)


class SearchScreen(ctk.CTkFrame):
    """
    Tela de busca de versículos.

    Permite buscar por texto livre ou por referência bíblica,
    exibindo resultados com destaque do termo buscado.
    """

    def __init__(
        self,
        master,
        bible,
        on_select: Callable[[int, int, int], None],
        on_back: Callable[[], None]
    ) -> None:
        """
        Inicializa a tela de busca.

        Args:
            master: Widget pai.
            bible: Instância da classe Bible.
            on_select: Callback ao selecionar um resultado (book, chapter, verse).
            on_back: Callback para voltar ao menu.
        """
        super().__init__(master, fg_color=COLORS["bg_main"])
        self.bible = bible
        self.on_select = on_select
        self.on_back = on_back

        self._create_widgets()
        self._bind_keys()

    def _create_widgets(self) -> None:
        """Cria os widgets da tela."""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        title = StyledLabel(
            header,
            text="Buscar na Bíblia",
            size=24,
            weight="bold"
        )
        title.pack(side="left", padx=20, pady=15)

        back_btn = StyledButton(
            header,
            text="Voltar (Esc)",
            command=self.on_back,
            width=100,
            height=35,
            variant="secondary"
        )
        back_btn.pack(side="right", padx=20, pady=12)

        # Área de busca
        search_frame = Card(self)
        search_frame.pack(fill="x", padx=20, pady=(0, 20))

        search_inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_inner.pack(fill="x", padx=20, pady=20)

        # Campo de busca
        self.search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Digite o texto ou referência (ex: João 3:16, amor)",
            width=500,
            height=45,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["bg_main"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
            border_color=COLORS["accent"]
        )
        self.search_entry.pack(side="left", padx=(0, 10))

        search_btn = StyledButton(
            search_inner,
            text="Buscar",
            command=self._do_search,
            width=120,
            height=45,
            variant="primary"
        )
        search_btn.pack(side="left", padx=(0, 10))

        # Contador de resultados
        self.results_label = StyledLabel(
            search_inner,
            text="",
            size=14,
            color="secondary"
        )
        self.results_label.pack(side="left", padx=10)

        # Área de resultados (scrollable)
        self.results_frame = ScrollableFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Instruções iniciais
        self._show_instructions()

    def _bind_keys(self) -> None:
        """Configura atalhos de teclado."""
        self.search_entry.bind("<Return>", lambda e: self._do_search())
        self.master.bind("<Escape>", lambda e: self.on_back())

    def _unbind_keys(self) -> None:
        """Remove atalhos de teclado."""
        try:
            self.master.unbind("<Escape>")
        except:
            pass

    def _show_instructions(self) -> None:
        """Exibe instruções de uso."""
        instructions = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        instructions.pack(fill="x", pady=50)

        title = StyledLabel(
            instructions,
            text="Como buscar:",
            size=18,
            weight="bold"
        )
        title.pack(pady=(0, 20))

        tips = [
            "• Digite uma palavra ou frase para buscar em todos os versículos",
            "• Use uma referência como 'João 3:16' para ir direto ao versículo",
            "• A busca não diferencia maiúsculas de minúsculas",
            "• Clique em um resultado para ir até o versículo"
        ]

        for tip in tips:
            tip_label = StyledLabel(
                instructions,
                text=tip,
                size=14,
                color="secondary"
            )
            tip_label.pack(pady=5)

    def _clear_results(self) -> None:
        """Limpa os resultados anteriores."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def _do_search(self) -> None:
        """Executa a busca."""
        query = self.search_entry.get().strip()
        if not query:
            return

        self._clear_results()

        # Primeiro, tentar buscar como referência
        ref_result = self.bible.search_by_reference(query)
        if ref_result:
            self.results_label.configure(text="Referência encontrada")
            self._add_result(ref_result, is_reference=True)
            return

        # Buscar por texto
        results = self.bible.search(query, max_results=100)

        if not results:
            self.results_label.configure(text="Nenhum resultado encontrado")
            no_results = StyledLabel(
                self.results_frame,
                text=f'Nenhum versículo contém "{query}"',
                size=16,
                color="secondary"
            )
            no_results.pack(pady=50)
            return

        self.results_label.configure(
            text=f"{len(results)} resultado{'s' if len(results) > 1 else ''}"
        )

        for result in results:
            self._add_result(result)

    def _add_result(self, result: dict, is_reference: bool = False) -> None:
        """
        Adiciona um resultado à lista.

        Args:
            result: Dicionário com dados do resultado.
            is_reference: Se é resultado de busca por referência.
        """
        card = Card(self.results_frame)
        card.pack(fill="x", pady=5)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=15)

        # Referência (clicável)
        ref_btn = ctk.CTkButton(
            inner,
            text=result["reference"],
            command=lambda r=result: self._select_result(r),
            fg_color="transparent",
            hover_color=COLORS["bg_main"],
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        ref_btn.pack(fill="x")

        # Texto do versículo
        verse_text = result.get("highlight", result["verse_text"])

        # Processar highlight (substituir **texto** por formatação visual)
        # Como CTkLabel não suporta formatação rica, vamos mostrar sem marcação
        display_text = verse_text.replace("**", "")

        if len(display_text) > 200:
            display_text = display_text[:200] + "..."

        verse_label = StyledLabel(
            inner,
            text=f'"{display_text}"',
            size=14,
            color="secondary"
        )
        verse_label.pack(fill="x", pady=(5, 0))

        # Botão ir para versículo
        go_btn = StyledButton(
            inner,
            text="Ir para versículo",
            command=lambda r=result: self._select_result(r),
            width=130,
            height=30,
            variant="primary"
        )
        go_btn.pack(anchor="e", pady=(10, 0))

    def _select_result(self, result: dict) -> None:
        """
        Seleciona um resultado e navega até ele.

        Args:
            result: Dicionário com dados do resultado.
        """
        self._unbind_keys()
        self.on_select(
            result["book_index"],
            result["chapter_index"],
            result["verse_index"]
        )

    def cleanup(self) -> None:
        """Limpa recursos ao sair da tela."""
        self._unbind_keys()
