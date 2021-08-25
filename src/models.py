from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from enum import Enum
import json

import psycopg2
import psycopg2.extras

from src.settings import DB_CREDS


class EntityClass(Enum):
    '''Represents the class of an entity, e.g. "Method"'''
    NONE = 0
    ORG = 1
    METHOD = 2
    PRODUCT = 3


@dataclass(frozen=True)
class Entity:
    '''An entity that has been identified as part of a document

    Attributes:
        parent_doc_id: an identifier for the document this entity exists within
        start: offset of the first character of this entity
          in the parent doc
        text: text from the parent document with this entity
        klass: class of this entity, e.g. "Method"
    '''

    parent_doc_id: int
    start: int
    text: str
    klass: EntityClass

    def __str__(self):
        return self.text

    @property
    def end(self):
        '''Offset of the last character of this entity in the parent doc'''
        return self.start + len(self.text)

    @property
    def location(self):
        return (self.start, self.end)


@dataclass
class Document:
    '''A document containing text

    Attributes:
        id: an identifier for the document
        text: the text of the document
    '''

    id: int
    text: str

    def __str__(self):
        return f'Document {self.id} "{self.text[:30]}..."'

    @classmethod
    def from_paper_id(cls, paper_id: int) -> Document:
        '''Constructs a document containing a paper abstract from a paper id

        Arguments:
            paper_id: the identifier for the paper

        Returns:
            A document containing a paper abstract
        '''

        conn = psycopg2.connect(**DB_CREDS)
        cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

        query = "SELECT * FROM paperabstractsinvertedindex WHERE paperid = %s"
        cur.execute(query, (paper_id,))
        result = cur.fetchone()
        text = cls._inverted_index_field_to_text(result.indexedabstract)

        cur.close()
        conn.close()
        return Document(result.paperid, text)

    @classmethod
    def from_paper_ids(cls, paper_ids: Collection[int]) -> list[Document]:
        '''Constructs many documents from paper ids

        Arguments:
            paper_ids: identifiers for the papers

        Returns:
            A list of document objects in the same order as the passed in
                paper IDs
        '''

        conn = psycopg2.connect(**DB_CREDS)
        cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

        query = "SELECT * FROM paperabstractsinvertedindex WHERE paperid IN %s"
        cur.execute(query, (tuple(paper_ids),))
        docs = {}
        for result in cur:
            text = cls._inverted_index_field_to_text(result.indexedabstract)
            docs[result.paperid] = Document(result.paperid, text)

        cur.close()
        conn.close()
        return [docs[paper_id] for paper_id in paper_ids]

    @staticmethod
    def _inverted_index_field_to_text(index: str) -> str:
        '''Uninverts the inverted index field'''
        index = json.loads(index)
        tokens = [''] * index['IndexLength']
        for token, positions in index['InvertedIndex'].items():
            for position in positions:
                tokens[position] = token
        return ' '.join(tokens)


class AnnotatedDocument(Document):
    '''Just like a :py:class:`Document`, but with entities

    Attributes:
        id: an identifier for the document
        text: the text of the document
        entities: a list of entities that exist within this document
    '''

    def __init__(self, entities: list[Entity], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entities = entities
