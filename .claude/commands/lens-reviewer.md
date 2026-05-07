Use the @lens-reviewer agent to review the following code: $ARGUMENTS

If no arguments were provided, ask the user what they want reviewed (specific files, recent diff, a PR). Lens is READ-ONLY and runs a 2-stage review (spec compliance first, then code quality), rating issues by severity (CRITICAL/HIGH/MEDIUM/LOW) with concrete fix suggestions.
