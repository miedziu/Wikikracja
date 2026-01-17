# Phase 1 Implementation - COMPLETED

## Summary

Phase 1 of the Arguments feature has been successfully implemented. The new `Argument` model has been created and migration files have been generated.

## Changes Made

### 1. Model Changes (`glosowania/models.py`)

Added new `Argument` model with the following fields:
- `decyzja` - ForeignKey to Decyzja (with related_name='arguments')
- `author` - ForeignKey to User (nullable)
- `argument_type` - CharField with choices: 'FOR' (Positive) or 'AGAINST' (Negative)
- `content` - TextField (max 1000 chars) for the argument text
- `created_at` - DateTimeField (auto_now_add=True)
- `modified_at` - DateTimeField (auto_now=True)

**Important**: The old `args_for` and `args_against` fields remain in the `Decyzja` model for backward compatibility.

### 2. Migration Files Created

#### `0009_argument.py` - Schema Migration
Creates the new `Argument` table with all necessary fields and relationships.

#### `0010_migrate_arguments_data.py` - Data Migration
Migrates existing data from old text fields to new Argument records:
- Converts `args_for` → Argument with type='FOR'
- Converts `args_against` → Argument with type='AGAINST'
- Preserves author information
- Only creates Arguments for non-empty fields
- Includes reverse migration (lossy - takes first argument of each type)

## Testing the Migrations

### Option 1: Using Docker (Recommended)

1. **Start the Docker containers:**
   ```bash
   cd /home/robert/code/gitops/wikikracja
   docker compose up -d
   ```

2. **Check migration plan (dry-run):**
   ```bash
   docker compose exec web python manage.py migrate glosowania --plan
   ```
   
   Expected output should show:
   - `[X] 0009_argument`
   - `[X] 0010_migrate_arguments_data`

3. **Apply migrations:**
   ```bash
   docker compose exec web python manage.py migrate glosowania
   ```

4. **Verify in Django shell:**
   ```bash
   docker compose exec web python manage.py shell
   ```
   
   Then in the shell:
   ```python
   from glosowania.models import Decyzja, Argument
   
   # Check if Argument model exists
   print(Argument.objects.count())
   
   # Check a specific decision's arguments
   d = Decyzja.objects.first()
   if d:
       print(f"Decision #{d.pk}: {d.title}")
       print(f"Old args_for: {d.args_for}")
       print(f"Old args_against: {d.args_against}")
       print(f"New arguments count: {d.arguments.count()}")
       for arg in d.arguments.all():
           print(f"  - {arg.get_argument_type_display()}: {arg.content[:50]}...")
   ```

### Option 2: Using Local Python Environment

If you have a local Python environment with Django installed:

1. **Apply migrations:**
   ```bash
   cd /home/robert/code/gitops/wikikracja
   python manage.py migrate glosowania
   ```

2. **Verify:**
   ```bash
   python manage.py shell
   # Then run the same verification code as above
   ```

## Rollback Instructions

If you need to rollback these migrations:

```bash
# Rollback to before the Argument model
docker compose exec web python manage.py migrate glosowania 0008_alter_decyzja_uzasadnienie

# This will:
# 1. Run the reverse data migration (copy first arguments back to text fields)
# 2. Drop the Argument table
```

## Next Steps (Phase 2+)

Once migrations are tested and applied:

1. **Phase 2**: Update forms to remove `args_for` and `args_against` from DecyzjaForm
2. **Phase 3**: Create views for adding/editing/deleting arguments
3. **Phase 4**: Update templates to display and manage arguments
4. **Phase 5**: Add URL patterns for argument management
5. **Phase 6**: Implement link interpretation with `urlize` filter
6. **Phase 7**: Update admin interface
7. **Phase 8**: Add permissions and security checks
8. **Phase 9**: Testing
9. **Phase 10**: Update translations

## Files Modified/Created

### Modified:
- `glosowania/models.py` - Added Argument model

### Created:
- `glosowania/migrations/0009_argument.py` - Schema migration
- `glosowania/migrations/0010_migrate_arguments_data.py` - Data migration
- `IMPLEMENTATION_PLAN_ARGUMENTS.md` - Full implementation plan
- `PHASE1_COMPLETED.md` - This file

## Database Schema

The new `glosowania_argument` table structure:

```sql
CREATE TABLE glosowania_argument (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    decyzja_id BIGINT NOT NULL,
    author_id INTEGER NULL,
    argument_type VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    modified_at DATETIME NOT NULL,
    FOREIGN KEY (decyzja_id) REFERENCES glosowania_decyzja(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES auth_user(id) ON DELETE SET NULL
);

CREATE INDEX idx_argument_decyzja ON glosowania_argument(decyzja_id);
CREATE INDEX idx_argument_author ON glosowania_argument(author_id);
CREATE INDEX idx_argument_type ON glosowania_argument(argument_type);
```

## Notes

- The old `args_for` and `args_against` fields are **NOT** removed yet
- This allows for a gradual migration and easy rollback if needed
- Once all phases are complete and tested, we can create a final migration to remove the old fields
- The data migration is idempotent - running it multiple times won't create duplicates (as long as you rollback first)
- The `urlize` template filter will handle link conversion automatically in templates
