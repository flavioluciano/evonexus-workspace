Use the @flow-git agent for git operations: $ARGUMENTS

If no arguments were provided, ask the user what git operation is needed (atomic commits, rebase, history cleanup). Flow detects project commit style from git log, splits changes by concern into atomic commits, and uses --force-with-lease (never --force, never on main/master).
