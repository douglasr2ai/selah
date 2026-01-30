"""
Tela de leitura - O coração do aplicativo.
"""
import customtkinter as ctk
from app.components.widgets import COLORS, COLORS_NIGHT, get_colors, StyledButton, StyledLabel, Card, ProgressBar


class ReaderScreen(ctk.CTkFrame):
    """Tela de leitura com modos chunks e palavra por palavra."""

    def __init__(self, master, bible, config, history, music, database, on_back):
        # Obter cores baseado no modo noturno
        self.night_mode = config.night_mode
        self.colors = get_colors(self.night_mode)

        super().__init__(master, fg_color=self.colors["bg_main"])
        self.bible = bible
        self.config = config
        self.history = history
        self.music = music
        self.db = database
        self.on_back = on_back

        # Estado da leitura
        self.book_index = 0
        self.chapter_index = 0
        self.verse_index = 0
        self.word_index = 0
        self.is_playing = False
        self.timer_id = None
        self.music_check_id = None
        self.current_words = []

        # Configurações
        self.reading_mode = config.reading_mode  # "chunks" ou "word"
        self.word_speed = config.word_speed  # segundos por palavra
        self.font_size = config.font_size  # tamanho da fonte
        self.is_fullscreen = False

        self._create_widgets()
        self._bind_keys()

    def _create_widgets(self):
        # Header com referência e modo
        self.header = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], height=60)
        self.header.pack(fill="x", padx=20, pady=20)
        self.header.pack_propagate(False)

        self.reference_label = ctk.CTkLabel(
            self.header,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.reference_label.pack(side="left", padx=20, pady=15)

        # Controles do header (direita)
        header_controls = ctk.CTkFrame(self.header, fg_color="transparent")
        header_controls.pack(side="right", padx=10)

        # Botão modo noturno
        self.night_btn = StyledButton(
            header_controls,
            text="Noturno (L)" if not self.night_mode else "Normal (L)",
            command=self._toggle_night_mode,
            width=100,
            height=30,
            variant="secondary"
        )
        self.night_btn.pack(side="left", padx=5)

        # Botão tela cheia
        self.fullscreen_btn = StyledButton(
            header_controls,
            text="Tela Cheia (F11)",
            command=self._toggle_fullscreen,
            width=120,
            height=30,
            variant="secondary"
        )
        self.fullscreen_btn.pack(side="left", padx=5)

        # Modo de leitura
        mode_frame = ctk.CTkFrame(header_controls, fg_color="transparent")
        mode_frame.pack(side="left", padx=10)

        self.mode_label = ctk.CTkLabel(
            mode_frame,
            text=f"Modo: {'Chunks' if self.reading_mode == 'chunks' else 'Palavra'}",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        self.mode_label.pack(side="left", padx=10)

        mode_btn = StyledButton(
            mode_frame,
            text="Alternar (M)",
            command=self._toggle_mode,
            width=100,
            height=30,
            variant="secondary"
        )
        mode_btn.pack(side="left")

        # Área principal de texto
        self.text_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], corner_radius=12)
        self.text_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.text_display = ctk.CTkLabel(
            self.text_frame,
            text="",
            font=ctk.CTkFont(family="Georgia", size=self.font_size),
            text_color=self.colors["text_primary"],
            wraplength=800,
            justify="center"
        )
        self.text_display.place(relx=0.5, rely=0.5, anchor="center")

        # Controle de fonte (canto inferior direito do texto)
        font_frame = ctk.CTkFrame(self.text_frame, fg_color="transparent")
        font_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.font_label = ctk.CTkLabel(
            font_frame,
            text=f"Fonte: {self.font_size}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        self.font_label.pack(side="left", padx=5)

        font_down_btn = StyledButton(
            font_frame,
            text="A-",
            command=self._decrease_font,
            width=35,
            height=28,
            variant="secondary"
        )
        font_down_btn.pack(side="left", padx=2)

        font_up_btn = StyledButton(
            font_frame,
            text="A+",
            command=self._increase_font,
            width=35,
            height=28,
            variant="secondary"
        )
        font_up_btn.pack(side="left", padx=2)

        # Barra de progresso
        self.progress_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], height=50)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        self.progress_frame.pack_propagate(False)

        progress_inner = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        progress_inner.pack(fill="both", expand=True, padx=20, pady=10)

        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            width=600,
            height=8,
            corner_radius=4,
            progress_color=self.colors["progress"],
            fg_color="#2A2A2A"
        )
        self.progress_bar.pack(side="left", padx=(0, 20))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_inner,
            text="Capítulo: 0%",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        self.progress_label.pack(side="left")

        # Controles de leitura
        self.controls_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], height=80)
        self.controls_frame.pack(fill="x", padx=20, pady=(10, 10))
        self.controls_frame.pack_propagate(False)

        controls_inner = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        controls_inner.pack(expand=True)

        # Botão voltar versículo
        back_verse_btn = StyledButton(
            controls_inner,
            text="<< Voltar",
            command=self._previous_verse,
            width=100,
            height=45,
            variant="secondary"
        )
        back_verse_btn.pack(side="left", padx=10, pady=15)

        # Botão play/pause
        self.play_btn = StyledButton(
            controls_inner,
            text="Play",
            command=self._toggle_play,
            width=120,
            height=45,
            variant="primary"
        )
        self.play_btn.pack(side="left", padx=10, pady=15)

        # Botão pular versículo
        skip_btn = StyledButton(
            controls_inner,
            text="Pular >>",
            command=self._next_verse,
            width=100,
            height=45,
            variant="secondary"
        )
        skip_btn.pack(side="left", padx=10, pady=15)

        # Controle de velocidade
        speed_frame = ctk.CTkFrame(controls_inner, fg_color="transparent")
        speed_frame.pack(side="left", padx=30)

        self.speed_label = ctk.CTkLabel(
            speed_frame,
            text=f"Velocidade: {self.word_speed:.1f}s",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        self.speed_label.pack(side="top")

        speed_btns = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_btns.pack(side="top")

        slower_btn = StyledButton(
            speed_btns,
            text="-",
            command=self._decrease_speed,
            width=40,
            height=30,
            variant="secondary"
        )
        slower_btn.pack(side="left", padx=2)

        faster_btn = StyledButton(
            speed_btns,
            text="+",
            command=self._increase_speed,
            width=40,
            height=30,
            variant="secondary"
        )
        faster_btn.pack(side="left", padx=2)

        # Botão favoritar
        self.fav_btn = StyledButton(
            controls_inner,
            text="Favoritar (F)",
            command=self._toggle_favorite,
            width=110,
            height=45,
            variant="secondary"
        )
        self.fav_btn.pack(side="left", padx=10, pady=15)

        # Botão menu
        menu_btn = StyledButton(
            controls_inner,
            text="Menu (Esc)",
            command=self._go_to_menu,
            width=100,
            height=45,
            variant="secondary"
        )
        menu_btn.pack(side="left", padx=10, pady=15)

        # Controles de música (sempre visível)
        self._create_music_controls()

    def _create_music_controls(self):
        """Cria os controles de música (sempre visível)."""
        self.music_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], height=60)
        self.music_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.music_frame.pack_propagate(False)

        music_inner = ctk.CTkFrame(self.music_frame, fg_color="transparent")
        music_inner.pack(expand=True)

        # Ícone de música
        self.music_icon = ctk.CTkLabel(
            music_inner,
            text="♪",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.music_icon.pack(side="left", padx=10)

        # Botão música anterior
        self.prev_track_btn = StyledButton(
            music_inner,
            text="<<",
            command=self._prev_track,
            width=40,
            height=35,
            variant="secondary"
        )
        self.prev_track_btn.pack(side="left", padx=5)

        # Botão play/pause música
        self.music_play_btn = StyledButton(
            music_inner,
            text="Play",
            command=self._toggle_music,
            width=80,
            height=35,
            variant="secondary"
        )
        self.music_play_btn.pack(side="left", padx=5)

        # Botão próxima música
        self.next_track_btn = StyledButton(
            music_inner,
            text=">>",
            command=self._next_track,
            width=40,
            height=35,
            variant="secondary"
        )
        self.next_track_btn.pack(side="left", padx=5)

        # Nome da música
        self.track_label = ctk.CTkLabel(
            music_inner,
            text="Sem músicas na pasta music/",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        self.track_label.pack(side="left", padx=20)

        # Volume
        volume_frame = ctk.CTkFrame(music_inner, fg_color="transparent")
        volume_frame.pack(side="left", padx=20)

        self.vol_label = ctk.CTkLabel(
            volume_frame,
            text="Vol:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        self.vol_label.pack(side="left")

        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=1,
            width=100,
            height=16,
            command=self._on_volume_change,
            progress_color=self.colors["accent"],
            button_color=self.colors["accent"],
            fg_color="#2A2A2A"
        )
        self.volume_slider.set(self.config.music_volume)
        self.volume_slider.pack(side="left", padx=5)

        # Atualizar label se houver músicas
        self._update_track_label()

    def _bind_keys(self):
        """Configura os atalhos de teclado."""
        self.master.bind("<space>", lambda e: self._toggle_play())
        self.master.bind("<Left>", lambda e: self._previous_verse())
        self.master.bind("<Right>", lambda e: self._next_verse())
        self.master.bind("<a>", lambda e: self._previous_verse())
        self.master.bind("<d>", lambda e: self._next_verse())
        self.master.bind("<plus>", lambda e: self._increase_speed())
        self.master.bind("<equal>", lambda e: self._increase_speed())
        self.master.bind("<minus>", lambda e: self._decrease_speed())
        self.master.bind("<m>", lambda e: self._toggle_mode())
        self.master.bind("<Escape>", lambda e: self._go_to_menu())
        self.master.bind("<n>", lambda e: self._toggle_music())
        self.master.bind("<f>", lambda e: self._toggle_favorite())
        # Novos atalhos
        self.master.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.master.bind("<l>", lambda e: self._toggle_night_mode())
        self.master.bind("<Control-plus>", lambda e: self._increase_font())
        self.master.bind("<Control-equal>", lambda e: self._increase_font())
        self.master.bind("<Control-minus>", lambda e: self._decrease_font())
        self.master.bind("<Control-KP_Add>", lambda e: self._increase_font())
        self.master.bind("<Control-KP_Subtract>", lambda e: self._decrease_font())

    def _unbind_keys(self):
        """Remove os atalhos de teclado."""
        keys = [
            "<space>", "<Left>", "<Right>", "<a>", "<d>",
            "<plus>", "<equal>", "<minus>", "<m>", "<Escape>", "<n>", "<f>",
            "<F11>", "<l>", "<Control-plus>", "<Control-equal>",
            "<Control-minus>", "<Control-KP_Add>", "<Control-KP_Subtract>"
        ]
        for key in keys:
            try:
                self.master.unbind(key)
            except:
                pass

    def start_reading(self, book_index: int, chapter_index: int, verse_index: int = 0):
        """Inicia a leitura em uma posição específica."""
        self.book_index = book_index
        self.chapter_index = chapter_index
        self.verse_index = verse_index
        self.word_index = 0

        self._update_display()
        self._start_timer()

        # Iniciar música automaticamente se houver músicas
        if self.music.get_playlist_count() > 0:
            self.music.play()
            self._update_music_button()
            self._start_music_check()

    # === Controles de Fonte ===
    def _increase_font(self):
        """Aumenta o tamanho da fonte."""
        self.font_size = min(72, self.font_size + 2)
        self._apply_font_size()

    def _decrease_font(self):
        """Diminui o tamanho da fonte."""
        self.font_size = max(16, self.font_size - 2)
        self._apply_font_size()

    def _apply_font_size(self):
        """Aplica o novo tamanho de fonte."""
        self.text_display.configure(font=ctk.CTkFont(family="Georgia", size=self.font_size))
        self.font_label.configure(text=f"Fonte: {self.font_size}")
        self.config.font_size = self.font_size
        self.config.save()

    # === Modo Noturno ===
    def _toggle_night_mode(self):
        """Alterna entre modo normal e noturno."""
        self.night_mode = not self.night_mode
        self.colors = get_colors(self.night_mode)
        self.config.night_mode = self.night_mode
        self.config.save()
        self._apply_colors()

    def _apply_colors(self):
        """Aplica as cores do tema atual."""
        # Fundo principal
        self.configure(fg_color=self.colors["bg_main"])

        # Header
        self.header.configure(fg_color=self.colors["bg_card"])
        self.reference_label.configure(text_color=self.colors["text_primary"])
        self.mode_label.configure(text_color=self.colors["text_secondary"])

        # Botão noturno
        self.night_btn.configure(text="Normal (L)" if self.night_mode else "Noturno (L)")

        # Área de texto
        self.text_frame.configure(fg_color=self.colors["bg_card"])
        self.text_display.configure(text_color=self.colors["text_primary"])
        self.font_label.configure(text_color=self.colors["text_secondary"])

        # Progresso
        self.progress_frame.configure(fg_color=self.colors["bg_card"])
        self.progress_bar.configure(progress_color=self.colors["progress"])
        self.progress_label.configure(text_color=self.colors["text_secondary"])

        # Controles
        self.controls_frame.configure(fg_color=self.colors["bg_card"])
        self.speed_label.configure(text_color=self.colors["text_secondary"])

        # Música
        self.music_frame.configure(fg_color=self.colors["bg_card"])
        self.music_icon.configure(text_color=self.colors["text_primary"])
        self.track_label.configure(text_color=self.colors["text_secondary"])
        self.vol_label.configure(text_color=self.colors["text_secondary"])
        self.volume_slider.configure(
            progress_color=self.colors["accent"],
            button_color=self.colors["accent"]
        )

    # === Favoritos ===
    def _toggle_favorite(self):
        """Alterna o versículo atual como favorito."""
        is_fav = self.db.is_favorite(
            self.book_index, self.chapter_index, self.verse_index
        )

        if is_fav:
            # Remover dos favoritos
            self.db.remove_favorite(
                self.book_index, self.chapter_index, self.verse_index
            )
        else:
            # Adicionar aos favoritos
            verse_text = self.bible.get_verse(
                self.book_index, self.chapter_index, self.verse_index
            )
            reference = self.bible.get_reference(
                self.book_index, self.chapter_index, self.verse_index
            )
            self.db.add_favorite(
                self.book_index,
                self.chapter_index,
                self.verse_index,
                verse_text,
                reference
            )

        self._update_favorite_button()

    def _update_favorite_button(self):
        """Atualiza o visual do botão de favorito."""
        is_fav = self.db.is_favorite(
            self.book_index, self.chapter_index, self.verse_index
        )
        if is_fav:
            self.fav_btn.configure(text="Favoritado", variant="success")
        else:
            self.fav_btn.configure(text="Favoritar (F)")

    # === Tela Cheia ===
    def _toggle_fullscreen(self):
        """Alterna modo tela cheia."""
        self.is_fullscreen = not self.is_fullscreen
        self.master.attributes('-fullscreen', self.is_fullscreen)
        self.config.fullscreen = self.is_fullscreen
        self.config.save()

        if self.is_fullscreen:
            self.fullscreen_btn.configure(text="Janela (F11)")
        else:
            self.fullscreen_btn.configure(text="Tela Cheia (F11)")

    # === Controles de Música ===
    def _start_music_check(self):
        """Inicia verificação periódica para trocar de música."""
        if self.music_check_id:
            self.after_cancel(self.music_check_id)

        def check():
            if self.music.is_playing:
                self.music.check_track_ended()
                self._update_track_label()
            self.music_check_id = self.after(1000, check)

        self.music_check_id = self.after(1000, check)

    def _stop_music_check(self):
        """Para a verificação de música."""
        if self.music_check_id:
            self.after_cancel(self.music_check_id)
            self.music_check_id = None

    def _update_display(self):
        """Atualiza a exibição do versículo."""
        # Atualizar referência
        reference = self.bible.get_reference(
            self.book_index, self.chapter_index, self.verse_index
        )
        self.reference_label.configure(text=reference)

        # Obter versículo
        verse = self.bible.get_verse(
            self.book_index, self.chapter_index, self.verse_index
        )

        if self.reading_mode == "chunks":
            # Mostrar versículo inteiro
            self.text_display.configure(text=f'"{verse}"')
        else:
            # Modo palavra por palavra
            self.current_words = verse.split()
            if self.word_index < len(self.current_words):
                self.text_display.configure(text=self.current_words[self.word_index])
            else:
                self.text_display.configure(text="")

        # Atualizar progresso
        verse_count = self.bible.get_verse_count(self.book_index, self.chapter_index)
        if verse_count > 0:
            progress = (self.verse_index + 1) / verse_count
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"Capítulo: {int(progress * 100)}%")

        # Atualizar botão de favorito
        self._update_favorite_button()

    def _start_timer(self):
        """Inicia o timer automático."""
        self.is_playing = True
        self.play_btn.configure(text="Pause")
        self._schedule_next()

    def _stop_timer(self):
        """Para o timer."""
        self.is_playing = False
        self.play_btn.configure(text="Play")
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def _schedule_next(self):
        """Agenda a próxima atualização."""
        if not self.is_playing:
            return

        if self.reading_mode == "chunks":
            # Calcular tempo baseado no número de palavras
            verse = self.bible.get_verse(
                self.book_index, self.chapter_index, self.verse_index
            )
            word_count = len(verse.split())
            delay = int(word_count * self.word_speed * 1000)
            self.timer_id = self.after(delay, self._advance_verse)
        else:
            # Modo palavra - avançar uma palavra por vez
            delay = int(self.word_speed * 1000)
            self.timer_id = self.after(delay, self._advance_word)

    def _advance_word(self):
        """Avança para a próxima palavra (modo word)."""
        if not self.is_playing:
            return

        self.word_index += 1

        if self.word_index >= len(self.current_words):
            # Fim do versículo, avançar para próximo
            self._advance_verse()
        else:
            self.text_display.configure(text=self.current_words[self.word_index])
            self._schedule_next()

    def _advance_verse(self):
        """Avança para o próximo versículo."""
        if not self.is_playing:
            return

        # Registrar versículo lido
        self.history.increment_verses(1)

        # Obter próxima posição
        next_book, next_chapter, next_verse, is_end = self.bible.get_next_position(
            self.book_index, self.chapter_index, self.verse_index
        )

        if is_end:
            # Fim da Bíblia
            self._stop_timer()
            self.text_display.configure(text="Fim da Bíblia! Parabéns!")
            return

        # Verificar se mudou de capítulo
        if next_chapter != self.chapter_index or next_book != self.book_index:
            # Marcar capítulo atual como lido
            book_abbrev = self.bible.get_book_abbrev(self.book_index)
            self.history.mark_chapter_read(book_abbrev, self.chapter_index)

        # Atualizar posição
        self.book_index = next_book
        self.chapter_index = next_chapter
        self.verse_index = next_verse
        self.word_index = 0

        # Salvar posição
        self.config.last_position = {
            "book_index": self.book_index,
            "chapter_index": self.chapter_index,
            "verse_index": self.verse_index
        }
        self.config.save()

        self._update_display()
        self._schedule_next()

    def _toggle_play(self):
        """Alterna entre play e pause."""
        if self.is_playing:
            self._stop_timer()
        else:
            self._start_timer()

    def _next_verse(self):
        """Pula para o próximo versículo."""
        was_playing = self.is_playing
        self._stop_timer()

        # Obter próxima posição
        next_book, next_chapter, next_verse, is_end = self.bible.get_next_position(
            self.book_index, self.chapter_index, self.verse_index
        )

        if not is_end:
            # Verificar se mudou de capítulo
            if next_chapter != self.chapter_index or next_book != self.book_index:
                book_abbrev = self.bible.get_book_abbrev(self.book_index)
                self.history.mark_chapter_read(book_abbrev, self.chapter_index)

            self.book_index = next_book
            self.chapter_index = next_chapter
            self.verse_index = next_verse
            self.word_index = 0

            self.config.last_position = {
                "book_index": self.book_index,
                "chapter_index": self.chapter_index,
                "verse_index": self.verse_index
            }
            self.config.save()

            self._update_display()

        if was_playing:
            self._start_timer()

    def _previous_verse(self):
        """Volta para o versículo anterior."""
        was_playing = self.is_playing
        self._stop_timer()

        # Obter posição anterior
        prev_book, prev_chapter, prev_verse, is_start = self.bible.get_previous_position(
            self.book_index, self.chapter_index, self.verse_index
        )

        if not is_start or (prev_book != self.book_index or prev_chapter != self.chapter_index
                           or prev_verse != self.verse_index):
            self.book_index = prev_book
            self.chapter_index = prev_chapter
            self.verse_index = prev_verse
            self.word_index = 0

            self.config.last_position = {
                "book_index": self.book_index,
                "chapter_index": self.chapter_index,
                "verse_index": self.verse_index
            }
            self.config.save()

            self._update_display()

        if was_playing:
            self._start_timer()

    def _toggle_mode(self):
        """Alterna entre modo chunks e palavra."""
        was_playing = self.is_playing
        self._stop_timer()

        if self.reading_mode == "chunks":
            self.reading_mode = "word"
        else:
            self.reading_mode = "chunks"

        self.word_index = 0
        self.config.reading_mode = self.reading_mode
        self.config.save()

        self.mode_label.configure(
            text=f"Modo: {'Chunks' if self.reading_mode == 'chunks' else 'Palavra'}"
        )

        self._update_display()

        if was_playing:
            self._start_timer()

    def _increase_speed(self):
        """Aumenta a velocidade (diminui o tempo)."""
        self.word_speed = max(0.1, self.word_speed - 0.1)
        self.config.word_speed = self.word_speed
        self.config.save()
        self.speed_label.configure(text=f"Velocidade: {self.word_speed:.1f}s")

    def _decrease_speed(self):
        """Diminui a velocidade (aumenta o tempo)."""
        self.word_speed = min(5.0, self.word_speed + 0.1)
        self.config.word_speed = self.word_speed
        self.config.save()
        self.speed_label.configure(text=f"Velocidade: {self.word_speed:.1f}s")

    # Controles de música
    def _toggle_music(self):
        """Alterna play/pause da música."""
        if not self.music.is_available():
            return

        if self.music.get_playlist_count() == 0:
            return

        if self.music.is_playing:
            self.music.pause()
        else:
            self.music.play()
            self._start_music_check()

        self._update_music_button()

    def _update_music_button(self):
        """Atualiza o texto do botão de música."""
        if self.music.is_playing:
            self.music_play_btn.configure(text="Pause")
        else:
            self.music_play_btn.configure(text="Play")

    def _next_track(self):
        """Próxima música."""
        if self.music.get_playlist_count() > 0:
            self.music.next_track()
            self._update_track_label()

    def _prev_track(self):
        """Música anterior."""
        if self.music.get_playlist_count() > 0:
            self.music.previous_track()
            self._update_track_label()

    def _update_track_label(self):
        """Atualiza o nome da música atual."""
        if self.music.get_playlist_count() > 0:
            track_name = self.music.get_current_track_name()
            if len(track_name) > 40:
                track_name = track_name[:37] + "..."
            self.track_label.configure(text=track_name)
        else:
            self.track_label.configure(text="Sem músicas na pasta music/")

    def _on_volume_change(self, value):
        """Callback quando o volume muda."""
        self.music.set_volume(value)
        self.config.music_volume = value
        self.config.save()

    def _go_to_menu(self):
        """Volta para o menu principal."""
        self._stop_timer()
        self._stop_music_check()
        self._unbind_keys()
        # Sair da tela cheia se estiver
        if self.is_fullscreen:
            self.master.attributes('-fullscreen', False)
        # Parar música ao sair
        if self.music.is_playing:
            self.music.stop()
        self.on_back()

    def cleanup(self):
        """Limpa recursos ao sair da tela."""
        self._stop_timer()
        self._stop_music_check()
        self._unbind_keys()
        if self.is_fullscreen:
            self.master.attributes('-fullscreen', False)
        if self.music.is_playing:
            self.music.stop()
