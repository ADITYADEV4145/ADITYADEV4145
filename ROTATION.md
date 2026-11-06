# Scheduled GIF rotation

The workflow runs at 00:17, 06:17, 12:17, and 18:17 UTC, plus manual runs from
Actions → Rotate profile GIF → Run workflow. GitHub can delay scheduled runs.

Four developer GIFs rotate in sequence, without immediate repeats. Only the
marked GIF block in README.md changes during GIF rotation. The next URL is checked for a valid GIF
response before writing. An unavailable image fails the run and leaves the
current README unchanged.

The same workflow also refreshes the ASCII Coding Activity graph in README.md.
It plots cumulative GitHub commit contributions for the last seven UTC dates,
including the current partial day, from a zero baseline at -7d. It uses GitHub's
GraphQL commit-contribution data rather than estimating coding hours. The graph
needs no external image host. API errors or incomplete results fail the run
and retain the previous graph. GitHub's contribution rules determine which
commits qualify; these totals are not every commit on every branch.

Each successful rotation creates a real README-change commit, authored and
committed as ADITYA PUNJANI using the account's GitHub noreply address. There
are no empty commits, backdated commits, bot authors, or co-author trailers.
These are automated maintenance commits. Their appearance on the contribution
graph depends on GitHub's contribution and account-email association rules.

No personal access token or extra service is needed: the workflow requests
contents: write for the repository's GITHUB_TOKEN. Repository policies and
branch protection must permit that token to push to the default branch.
Authentication may show GitHub Actions as the pusher, while the commit's author
and committer remain Aditya. No separate bot commit author is configured.

GitHub uses the workflow on the default branch. In public repositories,
scheduled workflows may be disabled after 60 days without repository activity.
Check the Actions tab if rotation stops. To pause rotation, disable the workflow
there. Edit GIFS in scripts/rotate_gif.py to change the selection.

The GIF changes on the schedule, rather than every browser refresh. GitHub's
image proxy or browser caching can delay visible updates.

Run local checks with:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Reference:
https://docs.github.com/en/actions/reference/authentication-in-a-workflow
