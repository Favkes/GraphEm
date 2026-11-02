

## Structures
Both `Node` and `Edge` dataclasses contain the following fields:
- `id` - a unique, hashable identifier used to reference the object within the visualization
- `label` - a string that gets rendered on the object in viewport
- `colour` - the colour of the object in viewport
- `attributes` - a dict of any attributes the user would fancy having for their own use, invisible in viewport unless specified

`Node` objects also contain a `pos` field, specifying their position in the viewport.
`Edge` objects also contain a `source` and `target` field(s) specifying their respective source and target nodes by hashable id's.
