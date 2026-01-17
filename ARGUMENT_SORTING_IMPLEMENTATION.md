# Argument Sorting Implementation

## Overview

Arguments are now sorted to prioritize concise, quality contributions and prevent spam from users who post many arguments.

## Sorting Algorithm

Arguments are sorted using a two-level priority system:

1. **Primary sort**: Content length (shorter first)
2. **Secondary sort**: Author's total argument count for this decision (fewer first)

### Implementation

```python
# Sort by: 1) content length (shorter first), 2) author's argument count (fewer first)
def sort_key(arg):
    content_length = len(arg.content)
    author_arg_count = author_counts.get(arg.author_id, 0) if arg.author_id else 0
    return (content_length, author_arg_count)

sorted_arguments = sorted(all_arguments, key=sort_key)
```

## Rationale

### Why Prioritize Concise Arguments?

- **Quality over quantity**: Short, focused arguments are often more impactful
- **Readability**: Users can quickly scan the most important points
- **Encourages clarity**: Incentivizes authors to be concise and clear
- **Better UX**: Top arguments are easier to read on mobile devices

### Why Prioritize Authors with Fewer Arguments?

- **Prevent spam**: Users who post many arguments don't dominate the discussion
- **Diverse perspectives**: More voices are heard near the top
- **Fair representation**: New contributors aren't buried by prolific posters
- **Quality incentive**: Encourages users to post their best argument, not many mediocre ones

## Sorting Examples

### Example 1: Simple Case

**Arguments**:
- User A: "Short" (5 chars) - User A has 1 argument
- User B: "This is longer text" (19 chars) - User B has 1 argument
- User C: "Medium" (6 chars) - User C has 1 argument

**Sorted Order**:
1. User A: "Short" (5 chars, 1 arg)
2. User C: "Medium" (6 chars, 1 arg)
3. User B: "This is longer text" (19 chars, 1 arg)

### Example 2: Multiple Arguments Per Author

**Arguments**:
- User A: "Short" (5 chars) - User A has 3 arguments total
- User B: "Brief" (5 chars) - User B has 1 argument total
- User A: "Also short" (10 chars) - User A has 3 arguments total
- User C: "This is a longer argument" (25 chars) - User C has 1 argument total

**Sorted Order**:
1. User B: "Brief" (5 chars, 1 arg) ← Same length as A's first, but fewer total args
2. User A: "Short" (5 chars, 3 args)
3. User A: "Also short" (10 chars, 3 args)
4. User C: "This is a longer argument" (25 chars, 1 arg)

### Example 3: Mixed Scenario

**Arguments**:
- User A: "Very long argument with lots of text here" (42 chars) - 2 total
- User B: "Short" (5 chars) - 1 total
- User A: "Medium length" (13 chars) - 2 total
- User C: "Brief" (5 chars) - 3 total
- User D: "Also medium" (11 chars) - 1 total

**Sorted Order**:
1. User B: "Short" (5 chars, 1 arg) ← Shortest + fewest args
2. User C: "Brief" (5 chars, 3 args) ← Same length, but more args than B
3. User D: "Also medium" (11 chars, 1 arg) ← Longer, but fewer args than A
4. User A: "Medium length" (13 chars, 2 args)
5. User A: "Very long argument with lots of text here" (42 chars, 2 args)

## Implementation Details

### Location
- **File**: `glosowania/views.py`
- **Function**: `details(request, pk)`
- **Lines**: 215-236

### Process

1. **Query**: Fetch all arguments for the decision with author data
2. **Count**: Count total arguments per author using `Counter`
3. **Sort**: Apply custom sort key (content length, then author count)
4. **Separate**: Split sorted list into positive and negative arguments

### Performance Considerations

- Arguments are loaded into memory as a list for sorting
- For typical use cases (dozens of arguments), this is negligible
- If performance becomes an issue with hundreds of arguments, consider:
  - Caching author counts
  - Database-level sorting with annotations
  - Pagination

### Separate Sorting Per Type

Arguments are sorted within their type (FOR/AGAINST):
- Positive arguments are sorted among themselves
- Negative arguments are sorted among themselves
- This maintains the two-column layout while applying sorting

## Edge Cases

### Anonymous Arguments
- Arguments without an author (`author_id = None`) have `author_arg_count = 0`
- They are treated as having the fewest arguments per author
- Sorted by content length among other anonymous arguments

### Equal Length and Count
- When two arguments have the same length and same author count
- Python's `sorted()` maintains relative order (stable sort)
- Earlier arguments (by creation time) appear first

### Single Argument
- No special handling needed
- Sorting still works correctly with one argument

## Benefits

1. **Better UX**: Most impactful arguments appear first
2. **Anti-spam**: Prevents argument flooding by single users
3. **Fairness**: Gives all users equal visibility opportunity
4. **Quality incentive**: Encourages thoughtful, concise contributions
5. **Mobile-friendly**: Short arguments are easier to read on small screens

## Testing

### Manual Test Scenarios

1. **Create arguments of varying lengths**
   - Verify shorter arguments appear first

2. **Create multiple arguments from same user**
   - Verify they appear after single-argument users

3. **Mix of users and lengths**
   - Verify correct priority: length first, then author count

4. **Anonymous arguments**
   - Verify they sort correctly by length

5. **Edit argument to change length**
   - Verify sorting updates on page refresh

## Future Enhancements

Potential improvements to consider:

1. **Upvoting/Downvoting**: Allow users to vote on arguments
2. **Quality score**: Combine length, votes, and author reputation
3. **Time decay**: Slightly favor newer arguments
4. **Admin pinning**: Allow moderators to pin important arguments
5. **User preferences**: Let users choose sorting method

## Status

✅ **IMPLEMENTED** - Sorting is active in production
