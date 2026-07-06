# zplus Quickstart

Launch a new password-protected Zensical site in a few commands.

## 1. Install (into a fresh venv)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install zensical
pip install git+https://github.com/peers8862/zplus.git
```

## 2. Create the site

```bash
zplus new my-site --profile projecthub
cd my-site
```

You now have the full nav skeleton (Project Hub, Work, Meetings, Challenges, …).
See the site kinds available with `zplus profiles`.

## 3. Set the password, then preview

```bash
$EDITOR .env          # set SITE_PASSWORD=your-password
zplus serve           # http://localhost:8000
```

## 4. Add a templated entry (dated, scaffolded)

```
$ zplus new-entry
Section?
  [1] Meetings  [2] Calls  [3] Timeline  [4] Challenges  …
  > 4
Title  > Supplier onboarding is slow
Date [2026-07-05]  >                 ← Enter accepts today
✔ wrote docs/business-challenges/2026-07-05-supplier-onboarding-is-slow.md
                                     …opens in your editor
```

Add `--fill` to answer each section at the terminal first.

## 5. Add a plain page to a section (fast build-out)

```
$ zplus add-page
Section?
  [1] Project Hub  [2] Spokes  [3] Phases  [4] Work  …
  > 4
Page name  > Q3 engagement
First text (optional) — end with a line containing only '.', or '.' to skip:
Kicks off Monday; scope agreed.
.
✔ wrote docs/work/q3-engagement.md
```

## 6. Publish (encrypted)

```bash
$EDITOR zplus.toml    # set [project].deploy_remote = "https://github.com/you/repo.git"
zplus deploy          # build → encrypt → push to gh-pages
```

Then set the repo's **Settings → Pages → Deploy from a branch → `gh-pages`**.

---

**Everyday loop:** `zplus new-entry` / `zplus add-page` → `zplus serve` to preview →
`zplus deploy` to publish. Full details in `GUIDE.md`.
