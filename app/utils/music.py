"""
Player de música de fundo para leitura.

Este módulo gerencia a reprodução de músicas de fundo usando pygame,
com suporte a playlist, shuffle e controle de volume.
"""
import os
import random
from typing import Optional, List

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class MusicPlayer:
    """
    Gerencia a reprodução de músicas de fundo.

    Utiliza pygame para reproduzir arquivos de áudio em diversos formatos,
    com suporte a playlist, shuffle, controle de volume e navegação entre faixas.

    Attributes:
        SUPPORTED_FORMATS: Formatos de áudio suportados (.mp3, .wav, .ogg, .flac).
    """

    SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac')

    def __init__(self) -> None:
        """Inicializa o player de música."""
        self.music_folder: Optional[str] = None
        self.playlist: List[str] = []
        self.current_index: int = 0
        self.is_playing: bool = False
        self.volume: float = 0.5
        self.shuffle: bool = True
        self._initialized: bool = False

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self._initialized = True
            except Exception as e:
                print(f"Erro ao inicializar pygame mixer: {e}")
                self._initialized = False

    def is_available(self) -> bool:
        """
        Verifica se o player está disponível.

        Returns:
            True se pygame está instalado e o mixer foi inicializado.
        """
        return PYGAME_AVAILABLE and self._initialized

    def set_folder(self, folder_path: str) -> bool:
        """
        Define a pasta de músicas e carrega a playlist.

        Args:
            folder_path: Caminho para a pasta contendo os arquivos de áudio.

        Returns:
            True se encontrou músicas na pasta.
        """
        if not folder_path or not os.path.isdir(folder_path):
            return False

        self.music_folder = folder_path
        self._load_playlist()
        return len(self.playlist) > 0

    def _load_playlist(self) -> None:
        """Carrega todos os arquivos de música da pasta configurada."""
        self.playlist = []
        if not self.music_folder:
            return

        for filename in os.listdir(self.music_folder):
            if filename.lower().endswith(self.SUPPORTED_FORMATS):
                filepath = os.path.join(self.music_folder, filename)
                self.playlist.append(filepath)

        if self.shuffle and self.playlist:
            random.shuffle(self.playlist)

        self.current_index = 0

    def play(self) -> bool:
        """
        Inicia a reprodução.

        Returns:
            True se iniciou a reprodução com sucesso.
        """
        if not self.is_available() or not self.playlist:
            return False

        try:
            if not pygame.mixer.music.get_busy():
                self._play_current()
            self.is_playing = True
            return True
        except Exception as e:
            print(f"Erro ao reproduzir: {e}")
            return False

    def _play_current(self) -> None:
        """Reproduz a música atual da playlist."""
        if not self.playlist:
            return

        try:
            pygame.mixer.music.load(self.playlist[self.current_index])
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            # Configurar evento para quando a música terminar
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
        except Exception as e:
            print(f"Erro ao carregar música: {e}")

    def pause(self) -> None:
        """Pausa a reprodução."""
        if self.is_available():
            pygame.mixer.music.pause()
            self.is_playing = False

    def unpause(self) -> None:
        """Retoma a reprodução pausada."""
        if self.is_available():
            pygame.mixer.music.unpause()
            self.is_playing = True

    def stop(self) -> None:
        """Para a reprodução completamente."""
        if self.is_available():
            pygame.mixer.music.stop()
            self.is_playing = False

    def next_track(self) -> None:
        """Avança para a próxima música da playlist."""
        if not self.playlist:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        if self.is_playing:
            self._play_current()

    def previous_track(self) -> None:
        """Volta para a música anterior da playlist."""
        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        if self.is_playing:
            self._play_current()

    def set_volume(self, volume: float) -> None:
        """
        Define o volume de reprodução.

        Args:
            volume: Nível de volume entre 0.0 (mudo) e 1.0 (máximo).
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.is_available():
            pygame.mixer.music.set_volume(self.volume)

    def get_current_track_name(self) -> str:
        """
        Retorna o nome do arquivo da música atual.

        Returns:
            Nome do arquivo sem o caminho, ou string vazia se não houver playlist.
        """
        if not self.playlist:
            return ""
        filepath = self.playlist[self.current_index]
        return os.path.basename(filepath)

    def check_track_ended(self) -> bool:
        """
        Verifica se a música terminou e avança para a próxima.

        Deve ser chamado periodicamente para detectar fim de faixa.

        Returns:
            True se a música terminou e avançou para a próxima.
        """
        if not self.is_available() or not self.is_playing:
            return False

        if not pygame.mixer.music.get_busy():
            self.next_track()
            return True
        return False

    def get_playlist_count(self) -> int:
        """
        Retorna o número de músicas na playlist.

        Returns:
            Quantidade de músicas carregadas.
        """
        return len(self.playlist)

    def toggle_shuffle(self) -> bool:
        """
        Alterna o modo shuffle.

        Quando ativado, embaralha a playlist mantendo a música atual.

        Returns:
            Novo estado do shuffle (True = ativado).
        """
        self.shuffle = not self.shuffle
        if self.shuffle and self.playlist:
            current_track = self.playlist[self.current_index] if self.playlist else None
            random.shuffle(self.playlist)
            if current_track:
                # Manter a música atual na posição 0
                try:
                    self.playlist.remove(current_track)
                    self.playlist.insert(0, current_track)
                    self.current_index = 0
                except ValueError:
                    pass
        return self.shuffle

    def cleanup(self) -> None:
        """Limpa recursos do player e encerra o mixer."""
        if self.is_available():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        self.is_playing = False
