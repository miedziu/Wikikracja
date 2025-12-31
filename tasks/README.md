### Tablica zadań – stan na dziś

#### Do zrobienia

- Ukrywanie i/lub usuwanie bardzo starych zadań

---

Poniżej spis aktualnie działających funkcji modułu **tasks** wraz z kluczowymi ograniczeniami.

#### Struktura widoku
1. **Actively handled** – aktywne zadania posiadające właściciela.
2. **Awaiting pickup** – aktywne zadania bez przypisanego użytkownika (z przyciskiem „Biorę na siebie”).
3. **Finished** – trzy podsekcje:
   - *Completed* (`completed`)
   - *Cancelled* (`cancelled`)
   - *Rejected* – każde zadanie, któremu algorytm przydzieli kategorię `rejected` (również te z sekcji aktywnych, aby było jasne, że mają ujemny bilans głosów).

Wszystkie listy bazują na jednym zapytaniu `Task.objects.with_metrics()` i sortowaniu `-votes_score`, następnie `-updated_at`.

---

#### Model i lifecycle
- Pola: `title`, `description`, `status` (Active/Completed/Cancelled), `created_by`, `assigned_to`, znaczniki czasu.
- `assigned_to` jest jedynym źródłem prawdy o właścicielu – nie prowadzimy historii przejęć.
- Formularz **Add task**: dostępny dla zalogowanych; zapis ustawia `created_by`.
- Przycisk **Biorę na siebie** w widoku listy/szczegółów przypisuje bieżącego użytkownika (dowolna osoba może przejąć zadanie).
- Edycja treści lub zamknięcie zadania (`completed` lub `cancelled`) są zablokowane dla osób innych niż aktualny właściciel (walidacja w `TaskEditView` i `TaskCloseView`).

---

#### Głosowanie i priorytety
- Każdy zalogowany użytkownik ma dokładnie jeden głos **za** (`+1`) lub **przeciw** (`-1`) na zadanie; ponowne głosowanie nadpisuje wcześniejszy wybór (`TaskVote` z `unique_together`).
- Bilans `votes_score` (suma głosów) decyduje o:
  1. Kolejności wyświetlania.
  2. Kategorii priorytetu:
     - `critical` – górne 20% zadań o nieujemnym wyniku.
     - `important` – kolejne 30%.
     - `beneficial` – pozostałe zadania o wyniku ≥ 0.
     - `rejected` – każde zadanie z ujemnym wynikiem.
- Priorytety obliczane są przy każdym renderowaniu listy – brak cache’u ani ręcznych override’ów.

---

#### Interakcje w UI
- Widok listy pokazuje kafelki z nazwą, skrótem opisu, właścicielem i bilansem głosów. Dla sekcji „Awaiting pickup” dostępny jest formularz POST przypinający zadanie.
- Widok szczegółowy:
  - Pełny opis, właściciel, status, znaczniki czasu, liczniki głosów oraz badgie z kategorią priorytetu.
  - Formularze głosowania `Vote up / Vote down` dostępne tylko dla zadań aktywnych.
  - Przycisk „Take task” widoczny tylko, gdy zadanie nie ma właściciela.
  - Przyciski „Edit” oraz „Close task” wyłącznie dla właściciela i tylko w statusie aktywnym.

---

#### Ocena sukcesu/porażki
- Po zamknięciu zadania udostępniany jest panel „Evaluate outcome”.
- Każdy użytkownik może oddać głos `success` lub `failure`; decyzję można zmieniać bez ograniczeń czasowych (`TaskEvaluation` z `unique_together`).
- Wynik prezentowany jest jako liczniki w widoku szczegółowym (badge „Success votes” / „Failure votes”).

---

#### Ograniczenia i brakujące elementy
1. Brak drag&drop oraz jakiegokolwiek API – obsługa wyłącznie przez widoki Django.
2. Brak automatycznego logowania zmian właściciela i brak powiadomień/monitoringu.
3. Brak testów automatycznych dla całego modułu.
