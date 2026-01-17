# Implementation Plan: Arguments as Separate Model

## Current State Analysis

### Existing Implementation
- **Model**: `Decyzja` (Decision/Voting) in `glosowania/models.py`
- **Current Fields**:
  - `args_for` (TextField, max_length=1500) - "Positive Aspects of the Idea"
  - `args_against` (TextField, max_length=1500) - "Negative Aspects of the Idea"
- **Current Behavior**:
  - Both fields are part of the creation form (`DecyzjaForm`)
  - Filled during vote creation in `dodaj.html` template
  - Can be edited by author in `edit.html` template
  - Displayed as simple text in `szczegoly.html` (details view)
  - No link interpretation
  - No individual timestamps
  - Single-user ownership (only author can edit)

### Problems with Current Implementation
1. Only the proposal author can add/edit arguments
2. Arguments are stored as single text blocks (not individual records)
3. No creation/modification timestamps per argument
4. No link rendering/interpretation
5. Cannot track who added which argument
6. Limited to max_length constraints

---

## Proposed Solution

### New Data Model: `Argument`

Create a new model to store individual arguments as separate database records.

**Model Structure**:
```python
class Argument(models.Model):
    ARGUMENT_TYPE_CHOICES = [
        ('FOR', _('Positive')),
        ('AGAINST', _('Negative')),
    ]
    
    decyzja = models.ForeignKey(
        Decyzja, 
        on_delete=models.CASCADE, 
        related_name='arguments'
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    argument_type = models.CharField(
        max_length=10,
        choices=ARGUMENT_TYPE_CHOICES,
        verbose_name=_('Argument Type')
    )
    content = models.TextField(
        max_length=1000,
        verbose_name=_('Argument Content'),
        help_text=_('Enter your argument. You can include links.')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Modified')
    )
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Argument')
        verbose_name_plural = _('Arguments')
    
    def __str__(self):
        return f"{self.get_argument_type_display()}: {self.content[:50]}..."
```

**Key Features**:
- Foreign key to `Decyzja` (voting/decision)
- Author tracking (who added the argument)
- Type field (FOR/AGAINST)
- Content field with reasonable length
- Automatic timestamps (`created_at`, `modified_at`)
- Related name for easy reverse queries

---

## Implementation Steps

### Phase 1: Database Changes

#### Step 1.1: Create New Model
- Add `Argument` model to `glosowania/models.py`
- Keep existing `args_for` and `args_against` fields temporarily for migration

#### Step 1.2: Create Migration
- Generate migration: `python manage.py makemigrations glosowania`
- This creates the new `Argument` table

#### Step 1.3: Data Migration (Optional)
- Create a data migration to convert existing `args_for` and `args_against` text into `Argument` records
- Split by line breaks or keep as single argument per field
- Set author to the `Decyzja.author` or None
- Set `created_at` to `Decyzja.data_powstania`

#### Step 1.4: Remove Old Fields (Later)
- After confirming everything works, create migration to remove `args_for` and `args_against`
- Update model to remove deprecated fields

---

### Phase 2: Forms

#### Step 2.1: Create Argument Form
Create `ArgumentForm` in `glosowania/forms.py`:

```python
class ArgumentForm(forms.ModelForm):
    class Meta:
        model = Argument
        fields = ('argument_type', 'content')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
```

#### Step 2.2: Update DecyzjaForm
Remove `args_for` and `args_against` from `DecyzjaForm.Meta.fields`:

```python
class DecyzjaForm(forms.ModelForm):
    class Meta:
        model = Decyzja
        fields = ('title', 'tresc', 'uzasadnienie', 'kara', 'znosi')
        # Removed: 'args_for', 'args_against'
```

---

### Phase 3: Views

#### Step 3.1: Update `dodaj` View
- Remove `args_for` and `args_against` from form processing
- After creating `Decyzja`, redirect to details page where users can add arguments

#### Step 3.2: Update `edit` View
- Remove `args_for` and `args_against` from form processing
- Arguments will be managed separately in details view

#### Step 3.3: Update `details` View
Add argument management functionality:

**Display Arguments**:
- Query all arguments for the decision: `arguments = Argument.objects.filter(decyzja=pk).select_related('author')`
- Separate into positive and negative lists
- Pass to template

**Add New Argument**:
- Handle POST request with `ArgumentForm`
- Create new `Argument` record
- Set `author` to `request.user`
- Set `decyzja` to current decision

**Edit Argument**:
- Allow users to edit their own arguments
- Handle via AJAX or separate view/modal

**Delete Argument** (Optional):
- Allow users to delete their own arguments
- Or allow only within certain time period

#### Step 3.4: Create Argument Management Views
Create dedicated views for argument CRUD:

```python
@login_required
def add_argument(request, pk):
    """Add argument to decision pk"""
    
@login_required
def edit_argument(request, argument_id):
    """Edit argument by argument_id (only own arguments)"""
    
@login_required
def delete_argument(request, argument_id):
    """Delete argument by argument_id (only own arguments)"""
```

---

### Phase 4: Templates

#### Step 4.1: Update `dodaj.html`
- Remove `form.args_for` and `form.args_against` fields
- Simplify form layout

#### Step 4.2: Update `edit.html`
- Remove `form.args_for` and `form.args_against` fields
- Simplify form layout

#### Step 4.3: Update `szczegoly.html`
Replace current argument display with new structure:

**Display Section**:
```django
<h5><u><b>{% trans 'Positive Arguments' %}</b></u></h5>
{% if positive_arguments %}
    {% for arg in positive_arguments %}
        <div class="argument-card">
            <div class="argument-content">
                {{ arg.content|urlize|linebreaks }}
            </div>
            <div class="argument-meta">
                <small>
                    {% trans 'By' %} {{ arg.author.username|default:"Anonymous" }}
                    | {% trans 'Added' %} {{ arg.created_at|date:"Y-m-d H:i" }}
                    {% if arg.created_at != arg.modified_at %}
                        | {% trans 'Modified' %} {{ arg.modified_at|date:"Y-m-d H:i" }}
                    {% endif %}
                </small>
                {% if arg.author == current_user %}
                    <a href="{% url 'glosowania:edit_argument' arg.id %}">{% trans 'Edit' %}</a>
                    <a href="{% url 'glosowania:delete_argument' arg.id %}">{% trans 'Delete' %}</a>
                {% endif %}
            </div>
        </div>
    {% endfor %}
{% else %}
    <p>{% trans 'No positive arguments yet.' %}</p>
{% endif %}

<h5><u><b>{% trans 'Negative Arguments' %}</b></u></h5>
{% if negative_arguments %}
    {% for arg in negative_arguments %}
        <div class="argument-card">
            <div class="argument-content">
                {{ arg.content|urlize|linebreaks }}
            </div>
            <div class="argument-meta">
                <small>
                    {% trans 'By' %} {{ arg.author.username|default:"Anonymous" }}
                    | {% trans 'Added' %} {{ arg.created_at|date:"Y-m-d H:i" }}
                    {% if arg.created_at != arg.modified_at %}
                        | {% trans 'Modified' %} {{ arg.modified_at|date:"Y-m-d H:i" }}
                    {% endif %}
                </small>
                {% if arg.author == current_user %}
                    <a href="{% url 'glosowania:edit_argument' arg.id %}">{% trans 'Edit' %}</a>
                    <a href="{% url 'glosowania:delete_argument' arg.id %}">{% trans 'Delete' %}</a>
                {% endif %}
            </div>
        </div>
    {% endfor %}
{% else %}
    <p>{% trans 'No negative arguments yet.' %}</p>
{% endif %}
```

**Add Argument Form**:
```django
<h5>{% trans 'Add Your Argument' %}</h5>
<form method="POST" action="{% url 'glosowania:add_argument' id.pk %}">
    {% csrf_token %}
    {{ argument_form|crispy }}
    <button type="submit" class="btn btn-primary btn-sm">{% trans 'Add Argument' %}</button>
</form>
```

#### Step 4.4: Create Argument Edit Template
Create `glosowania/templates/glosowania/edit_argument.html`:
- Form to edit argument content
- Show creation and modification dates
- Cancel button back to decision details

---

### Phase 5: URL Configuration

Update `glosowania/urls.py`:

```python
urlpatterns = (
    # ... existing patterns ...
    path('details/<int:pk>/add-argument/', v.add_argument, name='add_argument'),
    path('argument/<int:argument_id>/edit/', v.edit_argument, name='edit_argument'),
    path('argument/<int:argument_id>/delete/', v.delete_argument, name='delete_argument'),
)
```

---

### Phase 6: Link Interpretation

Use Django's built-in `urlize` template filter to automatically convert URLs to clickable links:

```django
{{ arg.content|urlize|linebreaks }}
```

This will:
- Convert URLs to `<a>` tags
- Preserve line breaks
- Handle http://, https://, www. patterns

**Alternative**: Use a markdown library if more formatting is needed:
- Install: `pip install markdown`
- Use: `{{ arg.content|markdown }}`
- Allows bold, italic, lists, etc.

---

### Phase 7: Admin Interface

Update `glosowania/admin.py`:

```python
from glosowania.models import Decyzja, Argument

class ArgumentInline(admin.TabularInline):
    model = Argument
    extra = 0
    fields = ('argument_type', 'author', 'content', 'created_at', 'modified_at')
    readonly_fields = ('created_at', 'modified_at')

class DecyzjaAdmin(admin.ModelAdmin):
    inlines = [ArgumentInline]
    # ... other configurations ...

admin.site.register(Decyzja, DecyzjaAdmin)
admin.site.register(Argument)
```

---

### Phase 8: Permissions & Security

#### Considerations:
1. **Who can add arguments?**
   - All logged-in users (`@login_required`)
   
2. **Who can edit arguments?**
   - Only the author of the argument
   - Check: `if argument.author == request.user`
   
3. **Who can delete arguments?**
   - Only the author of the argument
   - Or: Admin/moderators
   
4. **Time limits?**
   - Optional: Allow edits only within X hours of creation
   - Optional: Disable argument addition after voting starts

5. **Spam prevention?**
   - Rate limiting (e.g., max 5 arguments per user per decision)
   - Character limits already in model

---

### Phase 9: Testing

#### Manual Testing Checklist:
- [ ] Create new decision without arguments
- [ ] Add positive argument to existing decision
- [ ] Add negative argument to existing decision
- [ ] Edit own argument
- [ ] Try to edit someone else's argument (should fail)
- [ ] Delete own argument
- [ ] Verify timestamps are correct
- [ ] Verify links are clickable
- [ ] Test with URLs, www links, plain text
- [ ] Test line breaks in arguments
- [ ] Verify arguments display correctly in details view
- [ ] Test migration from old data

#### Unit Tests:
Create `glosowania/tests.py`:
- Test `Argument` model creation
- Test argument type choices
- Test foreign key relationships
- Test permissions (edit/delete own vs others)
- Test form validation

---

### Phase 10: Translations

Update Polish translations in `locale/pl/LC_MESSAGES/django.po`:

```po
msgid "Argument"
msgstr "Argument"

msgid "Arguments"
msgstr "Argumenty"

msgid "Positive"
msgstr "Pozytywny"

msgid "Negative"
msgstr "Negatywny"

msgid "Argument Type"
msgstr "Typ argumentu"

msgid "Argument Content"
msgstr "Treść argumentu"

msgid "Enter your argument. You can include links."
msgstr "Wprowadź swój argument. Możesz dodać linki."

msgid "Created At"
msgstr "Utworzono"

msgid "Last Modified"
msgstr "Ostatnia modyfikacja"

msgid "Add Your Argument"
msgstr "Dodaj swój argument"

msgid "Add Argument"
msgstr "Dodaj argument"

msgid "Edit Argument"
msgstr "Edytuj argument"

msgid "Delete Argument"
msgstr "Usuń argument"

msgid "Positive Arguments"
msgstr "Argumenty pozytywne"

msgid "Negative Arguments"
msgstr "Argumenty negatywne"

msgid "No positive arguments yet."
msgstr "Brak argumentów pozytywnych."

msgid "No negative arguments yet."
msgstr "Brak argumentów negatywnych."

msgid "By"
msgstr "Przez"

msgid "Added"
msgstr "Dodano"

msgid "Modified"
msgstr "Zmodyfikowano"
```

Run: `python manage.py compilemessages`

---

## Migration Strategy

### Option A: Clean Break (Recommended for Development)
1. Create new `Argument` model
2. Remove old fields from forms immediately
3. Manually migrate important existing data if needed
4. Drop old fields after confirmation

### Option B: Gradual Migration (Recommended for Production)
1. Create new `Argument` model (keep old fields)
2. Display both old and new in templates
3. Disable editing of old fields
4. Data migration script to convert old → new
5. After all data migrated, remove old fields
6. Update templates to show only new format

---

## Estimated Effort

- **Phase 1 (Database)**: 1-2 hours
- **Phase 2 (Forms)**: 30 minutes
- **Phase 3 (Views)**: 2-3 hours
- **Phase 4 (Templates)**: 2-3 hours
- **Phase 5 (URLs)**: 15 minutes
- **Phase 6 (Links)**: 15 minutes
- **Phase 7 (Admin)**: 30 minutes
- **Phase 8 (Permissions)**: 1 hour
- **Phase 9 (Testing)**: 2-3 hours
- **Phase 10 (Translations)**: 1 hour

**Total**: ~12-15 hours

---

## Benefits of New Implementation

1. ✅ **Multiple contributors**: Anyone can add arguments
2. ✅ **Individual tracking**: Each argument has author, timestamps
3. ✅ **Editable**: Users can edit their own arguments
4. ✅ **Link support**: Automatic URL conversion with `urlize`
5. ✅ **Scalable**: No character limit issues (each argument separate)
6. ✅ **Audit trail**: Creation and modification dates tracked
7. ✅ **Better UX**: Clear separation of arguments, attribution
8. ✅ **Flexible**: Easy to add features (voting on arguments, replies, etc.)

---

## Future Enhancements (Optional)

1. **Voting on arguments**: Users can upvote/downvote individual arguments
2. **Replies/Threading**: Allow replies to arguments
3. **Argument categories**: Tag arguments (economic, social, legal, etc.)
4. **Rich text editor**: Use markdown or WYSIWYG editor
5. **Notifications**: Notify when someone adds argument to your proposal
6. **Moderation**: Flag inappropriate arguments
7. **Search**: Search within arguments
8. **Export**: Export arguments to PDF/CSV

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss during migration | High | Backup database before migration, test on staging |
| Performance with many arguments | Medium | Add pagination, use select_related/prefetch_related |
| Spam arguments | Medium | Rate limiting, moderation tools |
| Breaking existing workflows | High | Thorough testing, gradual rollout |
| Translation missing | Low | Complete translations before deployment |

---

## Rollback Plan

If issues occur:
1. Keep old fields in database (don't drop immediately)
2. Revert code to use old fields
3. Investigate and fix issues
4. Re-deploy with fixes

---

## Success Criteria

- [ ] Users can add multiple arguments after vote creation
- [ ] Arguments show author and timestamps
- [ ] Users can edit their own arguments
- [ ] Links in arguments are clickable
- [ ] Old vote creation form doesn't include argument fields
- [ ] All existing data preserved or migrated
- [ ] No performance degradation
- [ ] Polish translations complete
- [ ] Tests passing

---

## Notes

- The `urlize` filter is sufficient for basic link interpretation
- Consider adding CSS styling for argument cards
- The `modified_at` field uses `auto_now=True` which updates automatically
- Consider adding a "last edited by" field if multiple edits by different users is possible
- The implementation maintains the existing voting workflow



