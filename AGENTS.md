# Agent guidance for this repository

## Commits

- Use [Conventional Commits](https://www.conventionalcommits.org/) for every commit message: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`, etc. Optional scope in parentheses is fine. Use imperative mood in the subject (e.g. "add seed command" not "added").
- To align **existing** messages with Conventional Commits, use `git rebase -i` (pick `reword` or `exec` as needed). Do not rewrite history blindly.
- If those commits were **already pushed**, rewriting requires `git push --force-with-lease` and coordination with anyone else using the branch. Do not force-push unless the user explicitly approves.

## Remotes and pushes

- Do **not** run `git push` or otherwise update remotes (including pushes that deploy) unless the user **explicitly** asks to push.
