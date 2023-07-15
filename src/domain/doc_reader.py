import pdfplumber
import tiktoken
from typing import List, Union

class DocReader:
    def __init__(self, doc: str=None, uploaded: dict=None) -> None:
        self.doc = doc
        self.uploaded = uploaded
        self.text = None
        self.chunks = None

    def parse_doc(self, autogen: bool=True) -> None:
        """Parse a single document (.pdf, .doc, .txt) and generate chunks if you want.
        Call object.text or .chunks to access the results.

        Args:
            autogen (bool, optional): Auto-generate text chunks? Defaults to True.

        Returns:
            None
        """
        self.text = self.indentify_type()
        if autogen:
            self.gen_chunks(self.text)
        return None

    def indentify_type(self) -> str:
        actions = {
            "pdf": self.__parse_pdf,
            "doc": self.__parse_word,
            "txt": self.__parse_txt,
        }

        #_type = str(self.doc.split('.')[-1]).lower()
        try:
            _type = str(self.doc.split('.')[-1]).lower()
        except Exception as e:
            _type = str(self.uploaded['file'].filename.split('.')[-1]).lower()
            self.doc = self.uploaded['temp']
        print(f"Parsing for {_type} file")
        return actions.get(_type)()

    def __parse_pdf(self) -> str:
        fulltext = ""
        with pdfplumber.open(self.doc) as pdf:
            for page in pdf.pages:
                fulltext += page.extract_text()
        pdf.close()
        return fulltext

    def __parse_word(self) -> str:
        raise NotImplementedError("WORD parser needs to be implemented")

    def __parse_txt(self) -> str:
        fulltext = ""
        with open(self.doc, "r", encoding="utf8") as txt:
            fulltext = txt.read()
        txt.close()
        return fulltext

    def gen_chunks(self, text: str, chunk_size: int=500) -> list[str]:
        """Generate text chunks from a full document text

        Args:
            text (str): a text parsed from a document, unique huge string
            chunk_size (int, optional): Chunk size to fit an embedding model. Defaults to 500.

        Returns:
            list[str]: A list o chunks to be feeded at an embedding model
        """
        chunks = []
        while len(text) > chunk_size:
            last_period_index = text[:chunk_size].rfind('.')
            if last_period_index == -1:
                last_period_index = chunk_size
            chunks.append(text[:last_period_index])
            text = text[last_period_index+1:]
        chunks.append(text)
        self.chunks = chunks
        return chunks

    def num_tokens_from_string(self, string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(string))

    def num_tokens_from_chunks(self, chunks: list[str]) -> int:
        return sum(self.num_tokens_from_string(chunk, "cl100k_base") for chunk in chunks)

    def check_price(self) -> List[Union[int, float]]:
        num_tokens = self.num_tokens_from_chunks(self.chunks)
        embedding_cost = num_tokens*.0001/1000
        print(f"Number of tokens: {num_tokens}")
        print(f"Cost in USD to generate tokens embeddings: {embedding_cost}")
        return [num_tokens, embedding_cost]

