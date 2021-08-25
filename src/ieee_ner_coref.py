from __future__ import annotations

from collections.abc import Collection

from src.coref import basic_cluster
from src.ner import BertForTokenClassificationML
from src.models import Document, AnnotatedDocument, Entity
from src.settings import MODELS_PATH


class EntityRecognizer:
    '''A simple wrapper around any number of entity recognition models.'''

    def __init__(self, method: str = 'best'):
        '''Initialize a new entity recognizer

        Arguments:
            method: the method to use for recognizing entities. Currently the
                only supported methods are `best` and `bert`.
        '''

        assert method in ['best', 'bert']
        if method in ['bert', 'best']:
            self.model = BertForTokenClassificationML.from_pretrained(
                    MODELS_PATH / 'hf_best')

    def recognize_entities(
            self, docs: list[Document]) -> list[AnnotatedDocument]:
        '''Locate the entities in a document.

        Arguments:
            docs: the documents within which we want to recognize entities

        Returns:
            The same documents that were passed in, but annotated with
            entities.
        '''

        return self.model.recognize_entities(docs)


class EntityClusterer:
    '''A simple wrapper around any number of entity clustering methods.'''
    def __init__(self, method: str = 'best'):
        '''Initialize a new entity clusterer

        Arguments:
            method: the method to use for recognizing entities. Currently the
                only supported methods are `best` and `basic`.
        '''

        assert method in ['best', 'basic']
        if method in ['best', 'basic']:
            self.cluster = basic_cluster

    def cluster(self, entities: Collection[Entity]) -> dict[int, list[Entity]]:
        '''Clusters like entities into groups.

        Arguments:
            entities: the entities to be clustered

        Returns:
            A dict mapping cluster id numbers (arbitrarily assigned) to lists
            of entities within that cluster
        '''
        raise NotImplementedError
