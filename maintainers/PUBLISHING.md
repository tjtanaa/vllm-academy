# Publishing this course

## Before a public release

Use `ACCEPTANCE.md` and `BACKLOG.md`. Complete human review and validate each hardware lane before advertising its lab as tested. Retain the reference attribution, evidence labels and limitation statement. The destination is `tjtanaa/vllm-academy`. Retain the original MIT notice; define the reviewer process and release criteria before promoting the draft.

## GitHub reading experience

The Markdown tree works directly in a GitHub repository. `README.md` links to the syllabus and lessons. `READING_GUIDE.md`, authoring templates, issue/PR templates and the CPU workflow are included. Inspect the actual GitHub Actions run for the pushed commit; local checks do not establish its outcome.

## Offline reader and simple static website

`START_HERE.html` is a standalone reading copy with its CSS embedded and no JavaScript or external font/CDN dependency. It contains the course plan and all lessons, not the executable source files or instructor templates. Opening it locally does not install packages or contact a model service.

Rebuild after editing chapters:

```bash
python tools/build_handbook.py
# Optional HTML renderer in your separate documentation environment:
python -m pip install 'mistune>=3,<4'
python tools/build_handbook.py --html
```

For a simple static-site release, use the generated HTML as your site's index page under your chosen hosting workflow. Keep the downloadable repository archive alongside it and identify the release/source pin. Hosting configuration is a separate opt-in task; this bootstrap does not configure Pages or change repository permissions.

## Release evidence

Run CPU tests, documentation checks and shell syntax checks again. Save the environment and validation manifest. Re-run relevant GPU labs when their image/model/backend changes. Do not let a green CPU workflow overwrite the unverified CUDA/ROCm status. Rebuild the handbook only after source edits and source-reference checks are complete.
