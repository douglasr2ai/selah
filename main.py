#!/usr/bin/env python3
"""
Leitor Bíblico - Aplicativo para leitura imersiva da Bíblia.

Funcionalidades:
- Dois modos de leitura: chunks (versículo inteiro) e palavra por palavra
- Controle de velocidade
- Persistência de posição e configurações
- Dashboard de estatísticas
- Tema escuro
"""
import customtkinter as ctk
from app.app import BibliaApp


def main():
    # Configurar tema escuro global
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Iniciar aplicativo
    app = BibliaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
