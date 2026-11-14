# Publishing on GitHub

Create an empty repository named `chess-material-reachability` under the `polilog` account. Do not initialize it with a README if importing the directory into an empty repository. In the extracted project directory:

```sh
git init
git add .
git status
git commit -m "Publish chess material reachability proof and explorer"
git branch -M main
git remote add origin git@github.com:polilog/chess-material-reachability.git
git push -u origin main
```

For an existing repository, copy the files into a clean working tree, review `git diff` and commit normally instead of reinitializing or overwriting unrelated work. The nine compressed data files are each below 25 MB, and below GitHub's ordinary 100 MiB per-file cap. No Git LFS or release assets are required. The all-in-one ZIP and download parts are transport files, not repository contents. Commit the extracted directory, including hidden `.github/` and `.gitignore` files. Do not commit `replay/`, `.venv/` or other generated files.

Suggested first public tag: `v1.0.0` after review. Suggested repository description: “Reproducible computer-assisted proof of reachable chess material classes, with certificate verification and an interactive proof-game explorer.”

The local Explorer requires Python and C++ and cannot run purely on GitHub Pages. GitHub Actions checks the source and proof; it does not deploy a public website. If a hosted service is desired, separately design resource limits, caching and server security before exposing the backend.
