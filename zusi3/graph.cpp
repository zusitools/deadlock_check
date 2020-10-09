#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <stdint.h>

#include <boost/dynamic_bitset.hpp>

using namespace std;

// #define DEBUG
#define INDENT { for (size_t k = 0; k < indent; k++) cout << "  "; }

struct Zug {
    /* Alle Instanzen von dynamic_bitset<> haben dieselbe Groesse, naemlich die Anzahl Zyklen.
     * Ausnahme sind die Parameter zuege_ok und abgleisen in abgleisen_rec; diese haben die
     * Anzahl Zuege als Groesse.
     * Der Konstruktor muss immer mit der passenden Anzahl Bits aufgerufen werden. */

    // Zuggattung+Zugnummer, fuer UI
    std::string zuggattung;
    std::string zugnr;

    // Auf welche Zuege dieser Zug wartet, und jeweils in welchen Fahrstrassen-Alternativen
    std::unordered_map<Zug*, std::unordered_set<size_t>> wartet_auf;

    // Pro Fahrstrassenalternative: Durch welche Zyklen wird dieser Zug blockiert
    std::vector<boost::dynamic_bitset<>> wartet_auf_bitmaske;

    // An welchen Zyklen dieser Zug beteiligt ist.
    boost::dynamic_bitset<> zyklen_bitmaske;

    // Gesamtanzahl Fahrstrassen-Alternativen fuer diesen Zug.
    size_t anzahl_fahrstr;

    // Ob dieser Zug weitergeboten wurde
    bool ist_weitergeboten;

    // Ob dieser Zug als naechstes abgegleist wird
    bool wird_abgegleist;

    // Visited-Flag fuer die Zyklenerkennung
    bool visited;

    // Fuegt eine neue Relation "Dieser Zug wartet auf 'zug' in Fahrstrassenalternative 'fstr_idx'" hinzu.
    void warte_auf(Zug* zug, size_t fstr_idx = 0) {
        if (this->wartet_auf.find(zug) == std::end(this->wartet_auf)) {
            this->wartet_auf.insert(std::make_pair(zug, std::unordered_set<size_t>()));
        }
        this->wartet_auf[zug].insert(fstr_idx);
    }

    // Fuegt eine neue Relation "Dieser Zug ist in Fahrstrassenalternative 'fstr_idx' durch Zyklus 'zyklus_idx' blockiert" hinzu.
    void in_zyklus(size_t zyklus_idx, size_t fstr_idx, size_t anzahl_zyklen) {
        assert(zyklus_idx < anzahl_zyklen);
        while (fstr_idx >= this->wartet_auf_bitmaske.size()) {
            this->wartet_auf_bitmaske.push_back(std::move(boost::dynamic_bitset<>(anzahl_zyklen)));
        }
        assert(fstr_idx < this->wartet_auf_bitmaske.size());
        assert(zyklus_idx < this->wartet_auf_bitmaske[fstr_idx].size());
        this->wartet_auf_bitmaske[fstr_idx][zyklus_idx] = 1;
    }

    Zug() : anzahl_fahrstr(0), ist_weitergeboten(false), wird_abgegleist(false), visited(false) {}
};

typedef vector<Zug*> Zyklus;

class Graph {
    // Zuege nach Zugnummer
    std::unordered_map<std::string, Zug*> zuege_by_zugnr;

public:
    // Alle Zuege (= Knoten des Graphen)
    std::vector<unique_ptr<Zug>> zuege;

    Zug* get_zug(const std::string zugnr) {
        if (zuege_by_zugnr.find(zugnr) == zuege_by_zugnr.end()) {
            unique_ptr<Zug> zug = unique_ptr<Zug>(new Zug());
            zug->zugnr = zugnr;
            zuege_by_zugnr.emplace(zugnr, zug.get());
            zuege.push_back(std::move(zug));
        }
        return zuege_by_zugnr[zugnr];
    };

    vector<Zyklus> finde_zyklen() {
        vector<Zyklus> result;
        vector<Zug*> stack;
        for (auto& zug : this->zuege) {
            this->finde_zyklen(zug.get(), stack, result);
        }
        return result;
    };

    // Sucht ausgehend von 'start' rekursiv alle Zyklen und fuegt sie zum Vektor 'zyklen' hinzu.
    void finde_zyklen(Zug* start, vector<Zug*> &stack, vector<vector<Zug*>> &zyklen) {
#if 0
        cout << "finde_zyklen: " << start->zugnr << "; ";
        for (auto zug : stack) { cout << zug->zugnr << ", "; }
        cout << endl;
#endif

        for (auto it = stack.begin(); it != stack.end(); ++it) {
            auto zug = *it;
            if (zug == start) {
                vector<Zug*> zyklus(it, stack.end());
#if 0
                cout << "Zyklus gefunden: ";
                for (auto zug2 : zyklus) {
                    cout << zug2->zugnr << ", ";
                }
                cout << endl;
#endif
                zyklen.push_back(std::move(zyklus));
                break;
            }
        }

        if (start->visited) return;
        start->visited = true;

        stack.push_back(start);
        for (auto& pair : start->wartet_auf) {
            finde_zyklen(pair.first, stack, zyklen);
        }
        stack.pop_back();
    };

    // Setzt die Bitmasken 'wartet_auf_bitmaske' und 'zyklen_bitmaske' fuer alle Zuege anhand der uebergebenen Liste von Zyklen.
    void setze_bitmasken(vector<Zyklus> &zyklen) {
        for (auto& zug : this->zuege) {
            zug->zyklen_bitmaske.resize(zyklen.size());
        }

        for (size_t zyklus_idx = 0; zyklus_idx < zyklen.size(); ++zyklus_idx) {
            auto& zyklus = zyklen[zyklus_idx];
            for (size_t i = 0; i < zyklus.size(); ++i) {
                auto& zug = zyklus[i];
                auto& nachfolger = zyklus[(i+1) % zyklus.size()];

                for (auto fstr_idx : zug->wartet_auf[nachfolger]) {
                    zug->in_zyklus(zyklus_idx, fstr_idx, zyklen.size());
                }

                zug->zyklen_bitmaske[zyklus_idx] = 1;
            }
        }
    };

    vector<boost::dynamic_bitset<>> abgleisen(size_t anzahl_zyklen) {
        vector<boost::dynamic_bitset<>> result;

        if (anzahl_zyklen == 0) return result;

        boost::dynamic_bitset<> abgleisen(this->zuege.size());
        boost::dynamic_bitset<> todo_zuege(this->zuege.size());
        todo_zuege.set();
        boost::dynamic_bitset<> zyklen_ok(anzahl_zyklen);

        for (size_t i = 1; i < this->zuege.size(); ++i) {
            if (this->abgleisen_rec(i, 0, abgleisen, todo_zuege, zyklen_ok, result)) break;
        }
        return result;
    };

    bool abgleisen_rec(
            size_t anzahl_zuege,
            boost::dynamic_bitset<>::size_type min_abgleis_idx,
            boost::dynamic_bitset<> &abgleisen,
            boost::dynamic_bitset<> &todo_zuege,
            boost::dynamic_bitset<> &zyklen_ok,
            vector<boost::dynamic_bitset<>> &result,
            size_t indent = 0) {

#ifdef DEBUG
        INDENT cout << "abgleisen_rec anzahl_zuege = " << anzahl_zuege << ", min_abgleis_idx = " << min_abgleis_idx
            << ", abgleisen = " << abgleisen << ", todo_zuege = " << todo_zuege
            << ", zyklen_ok " << zyklen_ok << endl;
#endif

        // Finde alle Zuege, die noch nicht auf OK gesetzt sind, fuer die aber alle Bedingungen
        // erfuellt sind. Falls solch ein Zug gefunden wird, wird alles Weitere eine Rekursionsebene
        // tiefer erledigt.
        for (auto i = todo_zuege.find_first(); i != todo_zuege.npos; i = todo_zuege.find_next(i)) {
#ifdef DEBUG
            INDENT cout << "Zug " << i << " ist noch TODO. Pruefe, ob er OK ist" << endl;
#endif
            bool ok = this->zuege[i]->wartet_auf_bitmaske.size() == 0;
            for (auto& maske : this->zuege[i]->wartet_auf_bitmaske) {
#ifdef DEBUG
                INDENT cout << "Pruefe Maske " << maske << endl;
#endif
                if (maske.is_subset_of(zyklen_ok)) {
                    ok = true;
                    break;
                }
            }

            if (ok) {
                todo_zuege.set(i, false);
                auto neu_gebrochen = this->zuege[i]->zyklen_bitmaske - zyklen_ok;
                zyklen_ok |= neu_gebrochen;

#ifdef DEBUG
                INDENT cout << "Zug " << i << " ist jetzt OK; neu gebrochene Zyklen: " << neu_gebrochen << endl;
#endif
                auto success = abgleisen_rec(anzahl_zuege, min_abgleis_idx, abgleisen, todo_zuege, zyklen_ok, result, indent + 1);

                zyklen_ok -= neu_gebrochen;
                todo_zuege.set(i, true);
                return success;
            }
        }

        if (anzahl_zuege == 0) {
            if (!todo_zuege.any()) {
#ifdef DEBUG
                INDENT cout << "Gefunden! " << abgleisen << endl;
#endif
                result.push_back(abgleisen);
                return true;
            } else {
#ifdef DEBUG
                INDENT cout << "Nicht gefunden!" << endl;
#endif
                return false;
            }
        }

        auto success = false;

        // Probiere den naechsten Zug abzugleisen.
        for (auto i = min_abgleis_idx == 0 ? todo_zuege.find_first() : todo_zuege.find_next(min_abgleis_idx);
                i != todo_zuege.npos; i = todo_zuege.find_next(i)) {
            abgleisen.set(i, true);
            todo_zuege.set(i, false);
            auto neu_gebrochen = this->zuege[i]->zyklen_bitmaske - zyklen_ok;
            zyklen_ok |= neu_gebrochen;

#ifdef DEBUG
            INDENT cout << "Zug " << i << " wird abgegleist; neu gebrochene Zyklen: " << neu_gebrochen << endl;
#endif
            // Reihenfolge hier wichtig wg. Kurzauswertung!
            success = abgleisen_rec(anzahl_zuege - 1, i, abgleisen, todo_zuege, zyklen_ok, result, indent + 1) || success;

            zyklen_ok -= neu_gebrochen;
            todo_zuege.set(i, true);
            abgleisen.set(i, false);
        }

        return success;
    }

};
