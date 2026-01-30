# Leitor Bíblico

Aplicativo desktop para leitura imersiva da Bíblia com tema escuro, dois modos de leitura e música de fundo.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Funcionalidades

- **Duas versões da Bíblia**: ACF (Almeida Corrigida Fiel) e NVI (Nova Versão Internacional)
- **Dois modos de leitura**:
  - **Chunks**: Exibe o versículo inteiro, tempo baseado no número de palavras
  - **Palavra por palavra**: Exibe uma palavra por vez para leitura focada
- **Controle de velocidade**: Ajuste de 0.1s a 5.0s por palavra
- **Tamanho de fonte ajustável**: De 16px a 72px
- **Modo noturno**: Cores quentes (âmbar/sépia) para leitura confortável à noite
- **Tela cheia**: Modo imersivo sem distrações
- **Música de fundo**: Toque músicas de uma pasta durante a leitura
- **Persistência total**: Salva posição, configurações e progresso
- **Dashboard de estatísticas**: Acompanhe capítulos lidos, versículos e tempo
- **Tema escuro**: Interface elegante com fundo preto e texto branco
- **Avanço automático**: Ao terminar um capítulo, avança para o próximo

## Instalação

### Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. Clone ou baixe o repositório

2. Instale as dependências:
```bash
cd biblia-app
pip install -r requirements.txt
```

3. Execute o aplicativo:
```bash
python main.py
```

## Como Usar

### Primeira Execução

Na primeira vez, você será solicitado a escolher sua versão preferida da Bíblia:
- **ACF**: Tradução tradicional e fiel aos textos originais
- **NVI**: Linguagem contemporânea e acessível

### Menu Principal

- **Continuar Leitura**: Retoma de onde você parou
- **Selecionar Livro/Capítulo**: Escolha um livro e capítulo específico
- **Estatísticas**: Veja seu progresso de leitura
- **Pasta de Música**: Selecione uma pasta com músicas para tocar durante a leitura
- **Trocar Versão da Bíblia**: Alterne entre ACF e NVI

### Tela de Leitura

A tela principal exibe:
- Referência do versículo atual (ex: João 3:16)
- Texto do versículo
- Barra de progresso do capítulo
- Controles de navegação e velocidade
- Player de música (se configurado)

## Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| `Espaço` | Play/Pause da leitura |
| `←` ou `A` | Versículo anterior |
| `→` ou `D` | Próximo versículo |
| `+` ou `=` | Aumentar velocidade |
| `-` | Diminuir velocidade |
| `Ctrl++` | Aumentar fonte |
| `Ctrl+-` | Diminuir fonte |
| `M` | Alternar modo (Chunks/Palavra) |
| `L` | Alternar modo noturno |
| `F11` | Tela cheia |
| `N` | Play/Pause da música |
| `Esc` | Voltar ao menu |

## Música de Fundo

1. No menu principal, clique em "Pasta de Música"
2. Selecione uma pasta contendo arquivos de áudio
3. Formatos suportados: MP3, WAV, OGG, FLAC
4. A música começa automaticamente ao iniciar a leitura
5. Use os controles na tela de leitura para:
   - Play/Pause
   - Próxima/Anterior música
   - Ajustar volume

## Estrutura do Projeto

```
biblia-app/
├── main.py                 # Ponto de entrada
├── requirements.txt        # Dependências
├── README.md              # Este arquivo
├── data/
│   ├── acf.json           # Bíblia ACF
│   └── nvi.json           # Bíblia NVI
├── app/
│   ├── app.py             # Classe principal
│   ├── screens/
│   │   ├── welcome.py     # Tela de boas-vindas
│   │   ├── menu.py        # Menu principal
│   │   ├── selector.py    # Seleção de livro/capítulo
│   │   ├── reader.py      # Tela de leitura
│   │   └── dashboard.py   # Estatísticas
│   ├── components/
│   │   └── widgets.py     # Componentes de UI
│   └── utils/
│       ├── bible.py       # Gerenciador da Bíblia
│       ├── config.py      # Configurações
│       ├── history.py     # Histórico de leitura
│       └── music.py       # Player de música
└── config/                # Criado em runtime
    ├── settings.json      # Configurações do usuário
    └── history.json       # Histórico de leitura
```

## Arquivos de Configuração

### settings.json
```json
{
  "bible_version": "acf",
  "reading_mode": "chunks",
  "word_speed": 1.0,
  "last_position": {
    "book_index": 0,
    "chapter_index": 0,
    "verse_index": 0
  },
  "music_folder": "C:/Musicas/Worship",
  "music_volume": 0.5,
  "music_enabled": true,
  "font_size": 32,
  "night_mode": false,
  "fullscreen": false
}
```

### history.json
```json
{
  "chapters_read": [
    {"book": "gn", "chapter": 0},
    {"book": "gn", "chapter": 1}
  ],
  "total_verses_read": 1234,
  "total_time_reading": 3600
}
```

## Paleta de Cores

### Modo Normal (Escuro)
| Elemento | Cor |
|----------|-----|
| Fundo principal | `#0D0D0D` |
| Fundo cards | `#1A1A1A` |
| Texto principal | `#FFFFFF` |
| Texto secundário | `#A0A0A0` |
| Destaque/Botões | `#4A90D9` |
| Sucesso/Lido | `#4CAF50` |

### Modo Noturno (Quente/Sépia)
| Elemento | Cor |
|----------|-----|
| Fundo principal | `#1A1408` |
| Fundo cards | `#2A2010` |
| Texto principal | `#FFE4B5` |
| Texto secundário | `#C4A574` |
| Destaque/Botões | `#D4A055` |
| Sucesso/Lido | `#8B9A46` |

## Tecnologias

- **Python 3**: Linguagem de programação
- **CustomTkinter**: Framework de UI moderno baseado em Tkinter
- **Pygame**: Reprodução de áudio para música de fundo

## Licença

Este projeto é de uso pessoal e educacional.

---

Desenvolvido com proposito de facilitar a leitura diária da Bíblia.
