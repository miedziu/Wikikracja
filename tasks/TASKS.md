### Lista funkcjonalności modułu „Tablica Zadań”

#### Struktura tablicy
- Trzy sekcje widoku: **Aktywne** (wyłącznie zadania z przypisanym użytkownikiem), **Oczekujące** (pozostałe aktywne), **Zakończone** (status `zrealizowane` lub `anulowane`).
- W każdej sekcji zadania sortowane malejąco wg bilansu `głosy_za – głosy_przeciw`; przy remisie używamy najnowszej daty aktualizacji jako tie-breaker.

#### Model zadania
- Pola obowiązkowe: tytuł, treść,  przypisany użytkownik (opcjonalnie), data utworzenia/aktualizacji.
status (`aktywne`, `zrealizowane`, `anulowane`)
- Pola wyliczane: głosy_za - głosy_przeciw = Priorytet. Priorytety:
    - `krytyczny` - 20% najwyżej ocenianych aktywnych zadań,
    - `ważny` - 30% następnych,
    - `korzystny` - 50% pozostałych zadań,
    - `odrzucone` - ujemny priorytet.
  Procent jest liczony na podstawie wszystkich aktywnych zadań. W przypadku remisu priorytet jest przypisywany chronologicznie. Priorytet jest liczony przy każdym odświeżeniu strony.
- Brak logów przejęcia – historię właścicieli zastępuje aktualne pole „assigned_to”.

#### Głosowanie i priorytety
- Każdy zalogowany użytkownik może oddać **jeden** głos „za” lub „przeciw” na każde aktywne zadanie.
- Głos można zmienić w dowolnym momencie, dopóki zadanie nie zostanie zamknięte; po zamknięciu głosowanie jest zablokowane.
- Bilans `głosy_za – głosy_przeciw` decyduje jednocześnie o priorytecie i kolejności wyświetlania.

#### Tworzenie i przejmowanie zadań
- Formularz „Dodaj zadanie” dostępny dla wszystkich aktywnych użytkowników.
- Przycisk „Biorę na siebie” przypisuje zadanie do aktualnego użytkownika; każdy może przejąć zadanie od kogoś innego bez podawania powodu.
- Edycję treści/statusu może wykonywać wyłącznie aktualny właściciel zadania.
- Zamknięcie zadania (status `zrealizowane` lub `anulowane`) możliwe tylko przez właściciela.

#### Widoki i UI
- Lista tablicy prezentuje skrócone karty (tytuł, priorytet, bilans głosów, właściciel/status).
- Widok szczegółowy zawiera pełną treść zadania, historię głosów (liczniki), przyciski: „Biorę na siebie”, „Edytuj”, „Zamknij”, „Głosuj”.
- Formularz oceny sukces/porażka pojawia się po zamknięciu zadania.
- Walidacje UI: ukrywanie „Biorę na siebie” dla aktualnego właściciela, blokada głosowania/edycji w zadaniach zamkniętych.

#### Ocena sukcesu/porażki
- Po zamknięciu zadania każdy użytkownik może wystawić ocenę `sukces` lub `porażka`. To głosowanie nie kończy się nigdy, można zawsze zmienić głos na inny, aktualizację licznika powoduje odświeżenie strony.
- Końcowy wynik prezentowany jako licznik (np. 12/5).
- Widok „Zakończone” umożliwia filtrowanie po statusie i wyniku oceny, pokazuje procent sukcesów oraz liczbę oddanych ocen.

#### Ograniczenia techniczne
- Brak drag&drop oraz brak API – implementacja wyłącznie w istniejących widokach Django.
- Brak testów automatycznych.
- Brak systemu logów przejęć; Brak powiadomienia/monitoring są poza zakresem.
