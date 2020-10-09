#include <iostream>

#include "graph.cpp"

using namespace std;

void test_zyklus_einfach() {
    Graph g;
    auto zugA = g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));
    auto zugC = g.get_zug(string("C"));

    zugA->warte_auf(zugB);
    zugB->warte_auf(zugC);
    zugC->warte_auf(zugA);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 1);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 3);
    assert(abgleisen[0].count() == 1);
}

void test_zwei_zyklen_1_fstr() {
    Graph g;
    auto zugA = g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));
    auto zugC = g.get_zug(string("C"));

    zugA->warte_auf(zugB);
    zugA->warte_auf(zugC);
    zugB->warte_auf(zugA);
    zugC->warte_auf(zugA);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 2);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 1);
    assert(abgleisen[0].count() == 1);
}

void test_zwei_zyklen_2_fstr() {
    Graph g;
    auto zugA = g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));
    auto zugC = g.get_zug(string("C"));

    zugA->warte_auf(zugB, 0);
    zugA->warte_auf(zugC, 1);
    zugB->warte_auf(zugA);
    zugC->warte_auf(zugA);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 2);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 3);
    assert(abgleisen[0].count() == 1);
}

void test_grosser_kleiner_zyklus() {
    Graph g;
    auto zugA = g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));
    auto zugC = g.get_zug(string("C"));

    zugA->warte_auf(zugB);
    zugB->warte_auf(zugA);
    zugB->warte_auf(zugC);
    zugC->warte_auf(zugA);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 2);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 2);
    assert(abgleisen[0].count() == 1);
}

void test_gleicher_zyklus_unterschiedliche_fstr() {
    Graph g;
    auto zugA = g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));

    zugA->warte_auf(zugB, 0);
    zugA->warte_auf(zugB, 1);
    zugB->warte_auf(zugA, 0);
    zugB->warte_auf(zugA, 1);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 1);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 2);
    assert(abgleisen[0].count() == 1);
}

void test_mehrere_zyklen_anderer_startknoten() {
    Graph g;
    auto zugA = g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));
    auto zugC = g.get_zug(string("C"));
    auto zugD = g.get_zug(string("D"));

    zugA->warte_auf(zugB);
    zugB->warte_auf(zugA);
    zugC->warte_auf(zugA);
    zugC->warte_auf(zugD);
    zugD->warte_auf(zugC);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 2);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 4);
    assert(abgleisen[0].count() == 2);
}

void test_unbeteiligter_zug() {
    Graph g;
    g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));
    auto zugC = g.get_zug(string("C"));

    zugB->warte_auf(zugC);
    zugC->warte_auf(zugB);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 1);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 2);
    assert(abgleisen[0].count() == 1);
}

void test_zug_nicht_in_zyklus() {
    Graph g;
    auto zugA = g.get_zug(string("A"));
    auto zugB = g.get_zug(string("B"));
    auto zugC = g.get_zug(string("C"));
    auto zugD = g.get_zug(string("D"));
    g.get_zug(string("E"));

    zugA->warte_auf(zugB);
    zugB->warte_auf(zugA);
    zugC->warte_auf(zugD);

    auto zyklen = g.finde_zyklen();
    assert(zyklen.size() == 1);

    g.setze_bitmasken(zyklen);
    auto abgleisen = g.abgleisen(zyklen.size());

    assert(abgleisen.size() == 2);
    assert(abgleisen[0].count() == 1);
}

int main() {
    test_zyklus_einfach();
    test_zwei_zyklen_1_fstr();
    test_zwei_zyklen_2_fstr();
    test_grosser_kleiner_zyklus();
    test_gleicher_zyklus_unterschiedliche_fstr();
    test_mehrere_zyklen_anderer_startknoten();
    test_unbeteiligter_zug();
    test_zug_nicht_in_zyklus();
    cout << "Tests abgeschlossen" << endl;
}
