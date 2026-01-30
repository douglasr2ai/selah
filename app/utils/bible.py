"""
Utilitário para carregar e navegar na Bíblia.

Este módulo fornece acesso aos dados da Bíblia, permitindo
navegação entre livros, capítulos e versículos, além de busca textual.
"""
import json
import os
import re
from typing import Optional, List, Dict, Any

# Mapeamento de abreviações para nomes completos dos livros
BOOK_NAMES = {
    "gn": "Gênesis", "ex": "Êxodo", "lv": "Levítico", "nm": "Números",
    "dt": "Deuteronômio", "js": "Josué", "jz": "Juízes", "rt": "Rute",
    "1sm": "1 Samuel", "2sm": "2 Samuel", "1rs": "1 Reis", "2rs": "2 Reis",
    "1cr": "1 Crônicas", "2cr": "2 Crônicas", "ed": "Esdras", "ne": "Neemias",
    "et": "Ester", "jó": "Jó", "sl": "Salmos", "pv": "Provérbios",
    "ec": "Eclesiastes", "ct": "Cânticos", "is": "Isaías", "jr": "Jeremias",
    "lm": "Lamentações", "ez": "Ezequiel", "dn": "Daniel", "os": "Oséias",
    "jl": "Joel", "am": "Amós", "ob": "Obadias", "jn": "Jonas",
    "mq": "Miquéias", "na": "Naum", "hc": "Habacuque", "sf": "Sofonias",
    "ag": "Ageu", "zc": "Zacarias", "ml": "Malaquias",
    "mt": "Mateus", "mc": "Marcos", "lc": "Lucas", "jo": "João",
    "at": "Atos", "rm": "Romanos", "1co": "1 Coríntios", "2co": "2 Coríntios",
    "gl": "Gálatas", "ef": "Efésios", "fp": "Filipenses", "cl": "Colossenses",
    "1ts": "1 Tessalonicenses", "2ts": "2 Tessalonicenses",
    "1tm": "1 Timóteo", "2tm": "2 Timóteo", "tt": "Tito", "fm": "Filemom",
    "hb": "Hebreus", "tg": "Tiago", "1pe": "1 Pedro", "2pe": "2 Pedro",
    "1jo": "1 João", "2jo": "2 João", "3jo": "3 João", "jd": "Judas",
    "ap": "Apocalipse"
}


class Bible:
    """
    Gerencia a leitura e navegação na Bíblia.

    Carrega dados da Bíblia de arquivos JSON e fornece métodos para
    navegar entre livros, capítulos e versículos.

    Attributes:
        data_dir: Diretório contendo os arquivos de dados.
        books: Lista de livros carregados.
        version: Versão atual (acf ou nvi).
    """

    def __init__(self, data_dir: str) -> None:
        """
        Inicializa o gerenciador da Bíblia.

        Args:
            data_dir: Diretório contendo os arquivos JSON das versões.
        """
        self.data_dir = data_dir
        self.books: List[Dict[str, Any]] = []
        self.version: str = ""

    def load(self, version: str) -> bool:
        """
        Carrega uma versão da Bíblia.

        Args:
            version: Identificador da versão (acf ou nvi).

        Returns:
            True se carregou com sucesso.
        """
        filepath = os.path.join(self.data_dir, f"{version}.json")
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                self.books = json.load(f)
            self.version = version
            return True
        except Exception as e:
            print(f"Erro ao carregar bíblia: {e}")
            return False

    def get_book_count(self) -> int:
        """
        Retorna o número total de livros.

        Returns:
            Quantidade de livros (66 para Bíblia completa).
        """
        return len(self.books)

    def get_book(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Retorna um livro pelo índice.

        Args:
            index: Índice do livro (0-65).

        Returns:
            Dicionário com dados do livro ou None se índice inválido.
        """
        if 0 <= index < len(self.books):
            return self.books[index]
        return None

    def get_book_name(self, index: int) -> str:
        """
        Retorna o nome completo do livro.

        Args:
            index: Índice do livro.

        Returns:
            Nome do livro (ex: "Gênesis") ou string vazia.
        """
        book = self.get_book(index)
        if book:
            abbrev = book.get("abbrev", "")
            return BOOK_NAMES.get(abbrev, abbrev.upper())
        return ""

    def get_book_abbrev(self, index: int) -> str:
        """
        Retorna a abreviação do livro.

        Args:
            index: Índice do livro.

        Returns:
            Abreviação (ex: "gn" para Gênesis) ou string vazia.
        """
        book = self.get_book(index)
        if book:
            return book.get("abbrev", "")
        return ""

    def get_chapter_count(self, book_index: int) -> int:
        """
        Retorna o número de capítulos de um livro.

        Args:
            book_index: Índice do livro.

        Returns:
            Quantidade de capítulos ou 0 se livro inválido.
        """
        book = self.get_book(book_index)
        if book:
            return len(book.get("chapters", []))
        return 0

    def get_chapter(self, book_index: int, chapter_index: int) -> List[str]:
        """
        Retorna os versículos de um capítulo.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo (0-based).

        Returns:
            Lista de versículos ou lista vazia se inválido.
        """
        book = self.get_book(book_index)
        if book:
            chapters = book.get("chapters", [])
            if 0 <= chapter_index < len(chapters):
                return chapters[chapter_index]
        return []

    def get_verse(self, book_index: int, chapter_index: int, verse_index: int) -> str:
        """
        Retorna um versículo específico.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo.
            verse_index: Índice do versículo.

        Returns:
            Texto do versículo ou string vazia se inválido.
        """
        chapter = self.get_chapter(book_index, chapter_index)
        if 0 <= verse_index < len(chapter):
            return chapter[verse_index]
        return ""

    def get_verse_count(self, book_index: int, chapter_index: int) -> int:
        """
        Retorna o número de versículos em um capítulo.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo.

        Returns:
            Quantidade de versículos.
        """
        return len(self.get_chapter(book_index, chapter_index))

    def get_reference(self, book_index: int, chapter_index: int, verse_index: int) -> str:
        """
        Retorna a referência formatada.

        Args:
            book_index: Índice do livro.
            chapter_index: Índice do capítulo.
            verse_index: Índice do versículo.

        Returns:
            Referência no formato "Livro capítulo:versículo" (ex: "João 3:16").
        """
        book_name = self.get_book_name(book_index)
        return f"{book_name} {chapter_index + 1}:{verse_index + 1}"

    def get_next_position(
        self, book_index: int, chapter_index: int, verse_index: int
    ) -> tuple:
        """
        Retorna a próxima posição de leitura.

        Navega sequencialmente: versículo -> capítulo -> livro.

        Args:
            book_index: Índice do livro atual.
            chapter_index: Índice do capítulo atual.
            verse_index: Índice do versículo atual.

        Returns:
            Tupla (book_index, chapter_index, verse_index, is_end).
            is_end é True se chegou ao fim da Bíblia.
        """
        verse_count = self.get_verse_count(book_index, chapter_index)

        # Próximo versículo no mesmo capítulo
        if verse_index + 1 < verse_count:
            return (book_index, chapter_index, verse_index + 1, False)

        # Próximo capítulo no mesmo livro
        chapter_count = self.get_chapter_count(book_index)
        if chapter_index + 1 < chapter_count:
            return (book_index, chapter_index + 1, 0, False)

        # Próximo livro
        if book_index + 1 < len(self.books):
            return (book_index + 1, 0, 0, False)

        # Fim da Bíblia
        return (book_index, chapter_index, verse_index, True)

    def get_previous_position(self, book_index: int, chapter_index: int, verse_index: int) -> tuple:
        """
        Retorna a posição anterior de leitura.
        Retorna (book_index, chapter_index, verse_index, is_start)
        is_start = True se chegou ao início da Bíblia
        """
        # Versículo anterior no mesmo capítulo
        if verse_index > 0:
            return (book_index, chapter_index, verse_index - 1, False)

        # Capítulo anterior no mesmo livro
        if chapter_index > 0:
            new_chapter = chapter_index - 1
            last_verse = self.get_verse_count(book_index, new_chapter) - 1
            return (book_index, new_chapter, max(0, last_verse), False)

        # Livro anterior
        if book_index > 0:
            new_book = book_index - 1
            last_chapter = self.get_chapter_count(new_book) - 1
            last_verse = self.get_verse_count(new_book, last_chapter) - 1
            return (new_book, max(0, last_chapter), max(0, last_verse), False)

        # Início da Bíblia
        return (0, 0, 0, True)

    def get_all_books(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de todos os livros com nome e índice.

        Returns:
            Lista de dicionários com: index, abbrev, name, chapters.
        """
        result = []
        for i, book in enumerate(self.books):
            abbrev = book.get("abbrev", "")
            name = BOOK_NAMES.get(abbrev, abbrev.upper())
            chapters = len(book.get("chapters", []))
            result.append({
                "index": i,
                "abbrev": abbrev,
                "name": name,
                "chapters": chapters
            })
        return result

    def search(
        self,
        query: str,
        max_results: int = 100,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Busca por texto nos versículos da Bíblia.

        Args:
            query: Texto a ser buscado.
            max_results: Número máximo de resultados.
            case_sensitive: Se a busca diferencia maiúsculas/minúsculas.

        Returns:
            Lista de resultados com:
            - book_index: Índice do livro
            - chapter_index: Índice do capítulo
            - verse_index: Índice do versículo
            - verse_text: Texto do versículo
            - reference: Referência formatada
            - highlight: Texto com destaque da busca
        """
        if not query or not query.strip():
            return []

        results = []
        search_query = query if case_sensitive else query.lower()

        for book_idx, book in enumerate(self.books):
            if len(results) >= max_results:
                break

            chapters = book.get("chapters", [])
            for chapter_idx, verses in enumerate(chapters):
                if len(results) >= max_results:
                    break

                for verse_idx, verse_text in enumerate(verses):
                    if len(results) >= max_results:
                        break

                    text_to_search = verse_text if case_sensitive else verse_text.lower()

                    if search_query in text_to_search:
                        reference = self.get_reference(book_idx, chapter_idx, verse_idx)

                        # Criar highlight do texto
                        if case_sensitive:
                            highlight = verse_text.replace(
                                query, f"**{query}**"
                            )
                        else:
                            # Busca case-insensitive mantendo o case original
                            pattern = re.compile(re.escape(query), re.IGNORECASE)
                            highlight = pattern.sub(
                                lambda m: f"**{m.group()}**",
                                verse_text
                            )

                        results.append({
                            "book_index": book_idx,
                            "chapter_index": chapter_idx,
                            "verse_index": verse_idx,
                            "verse_text": verse_text,
                            "reference": reference,
                            "highlight": highlight
                        })

        return results

    def search_by_reference(self, reference: str) -> Optional[Dict[str, Any]]:
        """
        Busca um versículo por referência (ex: "João 3:16").

        Args:
            reference: Referência no formato "Livro capítulo:versículo".

        Returns:
            Dicionário com dados do versículo ou None se não encontrado.
        """
        # Padrões comuns de referência
        patterns = [
            r"^(\d?\s*\w+)\s+(\d+):(\d+)$",  # "João 3:16" ou "1 João 3:16"
            r"^(\d?\s*\w+)\s+(\d+)$",  # "João 3" (capítulo inteiro)
        ]

        reference = reference.strip()

        for pattern in patterns:
            match = re.match(pattern, reference, re.IGNORECASE)
            if match:
                groups = match.groups()
                book_name = groups[0].strip().lower()
                chapter_num = int(groups[1]) - 1  # Converter para 0-based

                verse_num = None
                if len(groups) > 2:
                    verse_num = int(groups[2]) - 1  # Converter para 0-based

                # Encontrar livro pelo nome ou abreviação
                book_idx = self._find_book_index(book_name)
                if book_idx is None:
                    return None

                # Validar capítulo
                if chapter_num < 0 or chapter_num >= self.get_chapter_count(book_idx):
                    return None

                # Se versículo especificado, validar
                if verse_num is not None:
                    if verse_num < 0 or verse_num >= self.get_verse_count(book_idx, chapter_num):
                        return None

                    return {
                        "book_index": book_idx,
                        "chapter_index": chapter_num,
                        "verse_index": verse_num,
                        "verse_text": self.get_verse(book_idx, chapter_num, verse_num),
                        "reference": self.get_reference(book_idx, chapter_num, verse_num)
                    }
                else:
                    # Retornar primeiro versículo do capítulo
                    return {
                        "book_index": book_idx,
                        "chapter_index": chapter_num,
                        "verse_index": 0,
                        "verse_text": self.get_verse(book_idx, chapter_num, 0),
                        "reference": self.get_reference(book_idx, chapter_num, 0)
                    }

        return None

    def _find_book_index(self, name: str) -> Optional[int]:
        """
        Encontra o índice de um livro pelo nome ou abreviação.

        Args:
            name: Nome ou abreviação do livro.

        Returns:
            Índice do livro ou None se não encontrado.
        """
        name_lower = name.lower().strip()

        # Buscar por abreviação exata
        for idx, book in enumerate(self.books):
            if book.get("abbrev", "").lower() == name_lower:
                return idx

        # Buscar por nome completo
        for abbrev, full_name in BOOK_NAMES.items():
            if full_name.lower() == name_lower:
                for idx, book in enumerate(self.books):
                    if book.get("abbrev", "").lower() == abbrev:
                        return idx

        # Buscar por início do nome
        for abbrev, full_name in BOOK_NAMES.items():
            if full_name.lower().startswith(name_lower):
                for idx, book in enumerate(self.books):
                    if book.get("abbrev", "").lower() == abbrev:
                        return idx

        return None
