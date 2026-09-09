"""Package-owned static assets for the milestone-3 diagnostic bundle.

A package rather than a loose directory so `importlib.resources` can reach the
files from an INSTALLED command with no repository present — the same reason
milestone 1 made the repository root an explicit parameter instead of deriving
it from the working directory.

The three files here are inert: markup, style, and the rendering code the bundle
ships. No ordering rule, no candidate rule and no feature arithmetic lives in
them; `mtj_foundry.pilot` precomputes all of that by calling the accepted
milestone-2 retrieval, and the browser draws what it is given.
"""
