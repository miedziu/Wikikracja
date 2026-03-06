# Podsumowanie naprawy problemu z duplikatami emaili

**Data:** 2026-03-06  
**Problem:** Użytkownicy otrzymywali 2 emaile z różnymi hasłami podczas aktywacji

---

## 🔍 Zdiagnozowany problem

### Objawy:
- Użytkownik dostawał 2 emaile aktywacyjne o tej samej godzinie
- Każdy email miał inne hasło
- W logach: podwójne wywołanie "Activating user"

### Prawdziwa przyczyna:
**Scheduler uruchamiał się dwa razy** - Django wywoływało `AppConfig.ready()` więcej niż raz, co powodowało utworzenie dwóch instancji schedulera.

---

## ✅ Zastosowane rozwiązania

### 1. **Guard w schedulerze** (`zzz/apps.py`)
```python
# Global flag to prevent multiple scheduler instances
_scheduler_started = False

def ready(self):
    global _scheduler_started
    
    if _scheduler_started:
        log.warning("Scheduler already started, skipping duplicate initialization")
        return
    
    # ... start scheduler
    _scheduler_started = True
```

### 2. **Walidacja uid_id** (`count_citizens.py`)
```python
if i.uid is None or i.uid_id is None or i.uid_id <= 0:
    log.warning(f'Skipping Uzytkownik id={i.id} with invalid uid_id={i.uid_id}')
    continue
```

### 3. **Tracking emaili** (`count_citizens.py`)
```python
activated_emails = set()

if i.uid.email.lower() in activated_emails:
    log.warning(f'Skipping user - email already activated')
    continue

activated_emails.add(i.uid.email.lower())
```

### 4. **Cleanup duplikatów** (`count_citizens.py`)
Usuwa legacy duplikaty użytkowników przed aktywacją.

### 5. **Usunięto niepotrzebny kod**
- Usunięto `zliczaj_obywateli` view - nie był używany

---

## 📝 Wszystkie zmodyfikowane pliki

1. `zzz/apps.py` - dodano guard zapobiegający wielokrotnemu uruchomieniu schedulera
2. `obywatele/management/commands/count_citizens.py` - dodano walidację, tracking, logging
3. `obywatele/views.py` - usunięto niepotrzebny view `zliczaj_obywateli`
4. `obywatele/models.py` - naprawiono signal `save_user_profile` (wcześniej)
5. `obywatele/auth_backends.py` - obsługa `MultipleObjectsReturned` (wcześniej)
6. `obywatele/forms.py` - obsługa race conditions (wcześniej)
7. `obywatele/migrations/0011_remove_duplicate_emails.py` - czyszczenie duplikatów (wcześniej)
8. `obywatele/migrations/0012_alter_user_email_unique.py` - unique constraint (wcześniej)
9. `glosowania/views.py` - try/except dla .get() (wcześniej)
10. `chat/utils.py` - try/except dla .get() (wcześniej)
11. `chat/consumers.py` - try/except dla WebSocket (wcześniej)

---

## 🎯 Rezultat

**Przed:**
- ❌ Scheduler uruchamiał się dwa razy
- ❌ Użytkownik dostawał 2 emaile z różnymi hasłami
- ❌ Duplikaty emaili powodowały 500 errors
- ❌ Brak obsługi wyjątków w wielu miejscach

**Po:**
- ✅ Scheduler uruchamia się tylko raz
- ✅ Użytkownik dostaje tylko 1 email z 1 hasłem
- ✅ Unique constraint na email zapobiega duplikatom
- ✅ Wszystkie krytyczne .get() mają try/except
- ✅ Race conditions są obsłużone
- ✅ WebSocket consumers są odporne na błędy

---

## 🚀 Wdrożenie

```bash
# Commit wszystkich zmian
git add .
git commit -m "Fix: Prevent duplicate scheduler instances and user activation emails"

# Push do repozytorium
git push

# Migracje wykonają się automatycznie podczas startu kontenera
```

---

## 📊 Weryfikacja po wdrożeniu

Sprawdź logi po deploy:
```bash
kubectl logs -f wikikracja-instance-1-xxx -n wikikracja
```

Powinno być:
- ✅ Tylko jedno "APScheduler initialized"
- ✅ Tylko jedno "Starting citizen count and reputation check..."
- ✅ Tylko jedno "Activating user X" dla każdego użytkownika
- ✅ Tylko jeden email wysłany do każdego użytkownika

Jeśli zobaczysz "Scheduler already started, skipping duplicate initialization" - to normalne, guard działa poprawnie.
