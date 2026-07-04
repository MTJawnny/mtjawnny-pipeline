# mtjawnny-pipeline

Weekly GitHub Actions pipeline: fetches Scryfall bulk data, merges custom
tags, builds the corpus artifacts for mtjawnny.com's tools.

Artifacts land in R2 at `cdn.mtjawnny.com`: `/cards/png/`, `/data/v/<date>/`,
`/data/latest.json`. No card data is ever committed to this repo.
