from __future__ import annotations

from collections.abc import Collection
import re
from typing import Optional

import networkx as nx
from SetSimilaritySearch import all_pairs

from src.models import Entity
from src.settings import SIM_THRESHOLD


def split_entity_parts(entity: Entity) -> Optional[tuple[Entity, Entity]]:
    """Extract an acronym from the entity, if it exists."""
    match = re.match(r'([^\(]*) \(([-0-9A-Za-z]{2,10})\)', str(entity))
    if match is None:
        return None
    full, acronym = match.groups()
    full = Entity(
            entity.parent_doc_id,
            entity.start + match.start(1),
            full,
            entity.klass)
    acronym = Entity(
            entity.parent_doc_id,
            entity.start + match.start(2),
            acronym,
            entity.klass)
    return (full, acronym)


def entity_to_set(entity: Entity,
                  set_len: int = 2, shift: int = 1) -> set[str]:
    """Turn an entity into a set of tokens."""
    label = entity.text.lower()
    this_set = []
    i = 0
    while i < len(label) - set_len + 1:
        this_set.append(label[i:i+set_len])
        i += shift
    return set(this_set)


def entities_to_pairs(
        entities: Collection[Entity],
        similarity_threshold: float) -> list[tuple[Entity, Entity]]:
    """Find all similar pairs of entities in a collection of entities."""

    pairs = []
    all_entities = []
    for item in entities:
        all_entities.append(item)
    # all_entities = entities.copy()
    for entity in entities:
        parts = split_entity_parts(entity)
        if parts is None:
            continue
        full, acronym = parts
        all_entities.extend([full, acronym])
        pairs.extend([
            (full, acronym),
            (entity, full),
            (entity, acronym)])

    entity_sets = [entity_to_set(e) for e in all_entities]
    similar_pairs = all_pairs(entity_sets, similarity_func_name="jaccard",
                              similarity_threshold=similarity_threshold)
    pairs.extend([
        (all_entities[p[0]], all_entities[p[1]]) for p in similar_pairs])
    return all_entities, pairs


def basic_cluster(
        entities: Collection[Entity],
        similarity_threshold: float = SIM_THRESHOLD
        ) -> dict[int, list[Entity]]:
    """Cluster entities into groups that all refer to the same thing."""

    all_entities, pairs = entities_to_pairs(entities, similarity_threshold)
    entity_to_idx = {e: i for i, e in enumerate(all_entities)}
    G = nx.Graph()
    for entity_1, entity_2 in pairs:
        G.add_edge(entity_to_idx[entity_1], entity_to_idx[entity_2])

    group_to_entities = {}
    for group, members in enumerate(sorted(nx.connected_components(G))):
        group_to_entities[group] = sorted([all_entities[m] for m in members],
                                          key=lambda e: e.text)

    return group_to_entities
