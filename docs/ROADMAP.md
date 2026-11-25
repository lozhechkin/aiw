# Roadmap

The versions below describe priorities and acceptance criteria. Dates will depend on testing and feedback.

| Version | Scope | Ready when |
| --- | --- | --- |
| **0.1** | Drive-backed project files, linked GitHub repositories, local bootstrap, English documentation, and a two-chat PR pilot | A fresh install can link and clone a repo, and another person can complete the documented pilot in their own accounts |
| **0.2** | Setup diagnostics for Drive paths and GitHub access, versioned project configuration, and a guide for assistants with different connector capabilities | Common setup errors have actionable messages, and two fresh environments pass the same checks |
| **0.3** | Supported Google Drive and Docs connector path, including native document readback and conflict-safe updates, plus a read-only GitHub PR/status report | Permission failures are visible, concurrent edits do not overwrite changes, and reported CI is tied to the exact commit |
| **0.4** | Cross-project task summary, review handoffs, and opt-in scheduled reports | A scheduled run reports what it could verify and survives re-runs without duplicate records |
| **0.5** | Voice workflows and an optional shared deployment pipeline for static sites | A voice session hands off to text with reproducible evidence, and a preview deploy is proven before a production switch |

Each release should have a clean-install check, a reproducible exercise, and an explicit access model. Integrations are added in stages so a failure in one does not prevent local work.
