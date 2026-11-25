# Roadmap

The versions below describe priorities and acceptance criteria. Dates will depend on testing and feedback.

| Version | Scope | Ready when |
| --- | --- | --- |
| **0.1** | Drive-backed project files, linked GitHub repositories, local bootstrap, native Docs read and guarded append, a PR and CI report, English documentation, and a two-chat PR pilot | A fresh install can link and clone a repo, and live Docs, PR checks, and the two-chat pilot are verified with fresh accounts |
| **0.2** | Setup diagnostics for Drive paths and GitHub access, versioned project configuration, and a guide for assistants with different connector capabilities | Common setup errors have actionable messages, and two fresh environments pass the same checks |
| **0.3** | Drive discovery and native Docs support for more document structures, plus a read-only cross-repository GitHub queue | Permission failures are visible, rich content survives guarded updates, and queue evidence names each PR head |
| **0.4** | Cross-project task summary, review handoffs, and opt-in scheduled reports | A scheduled run reports what it could verify and survives re-runs without duplicate records |
| **0.5** | Voice workflows and an optional shared deployment pipeline for static sites | A voice session hands off to text with reproducible evidence, and a preview deploy is proven before a production switch |

Each release should have a clean-install check, a reproducible exercise, and an explicit access model. Integrations are added in stages so a failure in one does not prevent local work.
