# Study website generator

This branch (`gh-pages`) is the published website for the
[CCNA 200-301 v2.0 Study Guide](https://github.com/logiclinguist8989/200-301-CCNA-v2.0).
Everything outside this folder is generated — do not edit it by hand.

The site is built from the Markdown guides on `main`: a landing page, a "Start here" page, one page per
chapter, a chapter sidebar grouped by exam domain, full-text search, dark/light mode, per-chapter
progress tracking (saved in the reader's browser), and click-to-zoom figures.

Reading extras:

- **Self-check quizzes** — each chapter's practice questions and answer key become an interactive quiz.
  Multiple-choice questions are graded on click; open questions are "think, then reveal" with self-marking.
  Scores are saved in the reader's browser.
- **Callout boxes** — the guide's *Exam tip*, *Common trap*, *Security note*, *Best practice* and *PT note*
  paragraphs are styled as colour-coded boxes, plus a *Memory trick* per key topic and a *Lab it* pointer to
  each chapter's lab.
- **Terminal-style CLI blocks** — code blocks with IOS prompts render as a router console with a
  "Copy commands" button that strips prompts and output.
- **Subnetting practice** (`practice.html`) — unlimited random IPv4 questions in three difficulty levels,
  with streaks and step-by-step solutions.
- **Review schedule** — a finished chapter quiz comes back on the home page after 1 day, 1 week and 1 month
  (back to 1 day if the score is below 85 %).
- **Mistakes notebook** (`mistakes.html`) — every question missed in a quiz or exam is saved, with a retry
  card and a personal note per question.
- **Exam mode** (`exam.html`) — timed, mixed-chapter exams from the question bank, scored by exam domain,
  with resume and history.

All study data (progress, scores, review dates, mistakes, exam history) is kept in the reader's browser
(`localStorage`); nothing is sent anywhere.

## Rebuild after changing `main`

```bash
pip install markdown
git clone https://github.com/logiclinguist8989/200-301-CCNA-v2.0.git ccna
cd ccna && git worktree add ../site gh-pages
python3 ../site/_generator/build_site.py . ../site
cd ../site && git add -A && git commit -m "site: rebuild from main" && git push
```

`build_site.py` keeps `_generator/` and `.git` and replaces everything else.

| File | Purpose |
| --- | --- |
| `build_site.py` | Splits the guides into pages and renders them (Python + `markdown`) |
| `extras.py` | Quizzes, callouts, memory tricks and terminal-style CLI blocks |
| `static/style.css` | Layout, colours, dark mode, callouts, responsive design |
| `static/app.js` | Search, theme toggle, progress tracking, figure zoom, "on this page" highlighting, quizzes, copy buttons, subnetting practice |
| `static/study.js` | Review schedule, mistakes notebook and exam mode (reads `assets/site/questions.json`) |
| `static/favicon.svg` | Site icon |

Licensed like the rest of the repository: generated pages and figures under CC BY-NC-SA 4.0, the
generator code under MIT (see `LICENSE`, `LICENSE-CONTENT` and `LICENSE-CODE` on `main`).
