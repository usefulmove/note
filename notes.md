# TODOs
[x] add is_valid() function (notedb.py)
[x] add nid integrity check (main.py)
  [x] append
  [x] update
  [x] delete
[x] pass integer nids to notedb module
  [x] get_notes
  [x] update_entry (rename update_note (?))
  [x] delete_entries (rename delete_notes (?))
[x] make (max + 1) robust to empty database
[x] update to let `notedb.send_error()` take an optional argument
[ ] question (?): how should i be selective about which functions and constants my module exposes?


# integrity check on note ids (nids)
- which side performs check (main or db)?
  - if error (not the same as the check) happens where received, main, error handling is cleaner
    - command termination is straightforward and doesn't need to propogate (!)
    - main needs either a list of valid nids or needs a check function (e.g., db.is_valid(nid))

> decision (!): error will be handled in main
> decision (!): error check will be done by db module. provided by db.is_valid() function.

```python
    if not db.is_valid(nid):
        # error handling
```


# make (max + 1) robust to empty database
- use `coalesce(max, 0) + 1`


# allow `notedb.send_error()` to take an optional argument
- remove second send error message function
