import pytest

from hekb.category import KnowledgeCategory
from hekb.models import Concept


@pytest.fixture
def category() -> KnowledgeCategory:
    cat = KnowledgeCategory()
    cat.add_object(Concept(id="A", elements=frozenset({"a1", "a2"})))
    cat.add_object(Concept(id="B", elements=frozenset({"b1", "b2"})))
    cat.add_object(Concept(id="C", elements=frozenset({"c1"})))
    return cat
