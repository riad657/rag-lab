import sys
sys.path.insert(0, ".")
import importlib.util

spec = importlib.util.spec_from_file_location("hybride", "2.5_hybride.py")
hybride = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hybride)


def test_recherche_doliprane_trouve_le_bon_document():
    ids_trouves = hybride.recherche_hybride("Quelle est la posologie du Doliprane ?", k=3)
    assert any(cid.startswith("01_doliprane") for cid in ids_trouves)


def test_nombre_de_resultats_respecte():
    ids_trouves = hybride.recherche_hybride("Quelle est la posologie du Doliprane ?", k=3)
    assert len(ids_trouves) == 3


def test_question_vide_ne_plante_pas():
    ids_trouves = hybride.recherche_hybride("", k=3)
    assert ids_trouves is not None


def test_corpus_non_vide():
    assert len(hybride.tous_chunks) > 0
