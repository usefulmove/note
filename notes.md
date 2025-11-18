# note interface options

## current implementation

 $ note 'order groceries' 'clean bathroom' -- current

## semantic

 $ note that order groceries -- single note

 $ note that order groceries & clean bathroom -- multiple notes

note: not a significant improvement. has trade-offs.

## other options

 $ note a 'order groceries' 'clean bathroom'
 $ note add 'order groceries' 'clean bathroom'

note: allows another level of robustness to malformed inputs
