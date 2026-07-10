# Security — inference-lab

This repo is public-facing evidence. The threat model is leakage, not intrusion: nothing
secret may enter pins, compose files, scripts, or archived evidence, because everything here
is meant to be readable by a stranger.

## Rules

1. **No secrets in pins or evidence.** No API keys, tokens, passwords, or cloud credentials in
   `pins/`, `scenarios/`, `quickstart/`, `evidence/`, `reports/`, or anywhere else in the
   repo. Compose files reference secrets via environment variables or local `.env` files that
   are git-ignored and documented as such.
2. **Demo keys are throwaway.** Any API key used in demos or quickstart flows is generated for
   the demo, treated as compromised the moment it appears on screen or in a log, and rotated
   (revoked) after the session. This is recorded in the demo script.
3. **Redaction before archiving.** Bearer tokens, `Authorization` headers, cookies, and any
   credential-shaped strings are redacted from archived logs and trace exports before commit
   (replace with `REDACTED`, keep surrounding context). Redaction is part of the
   evidence-capture step of every scenario script, not an afterthought.
4. **Upstream OSS communications contain no private data.** Issue reports, reproducers, and
   environment manifests posted upstream are reviewed (by the user, per the OSS gate) for
   private paths, hostnames, credentials, or unpublished program details before posting.
5. **Everything in evidence is publishable.** The landing-page claims must be traceable to
   archived evidence, so nothing unpublishable may enter `evidence/` in the first place. If a
   run captured something unpublishable, the sanitized version is a new dated entry and the
   incident is noted in `docs/implementation-notes.md`.
6. **GPU session hygiene.** GPU session manifests may name the provider and instance type but
   never account identifiers, billing tokens, or SSH material.

## Review checklist (applied to every evidence commit)

- [ ] No credential-shaped strings (`grep` for `Bearer `, `api[_-]?key`, `token=`, `sk-`,
      `AKIA`, `-----BEGIN`).
- [ ] No git-ignored `.env` content committed.
- [ ] Logs redacted; redaction noted in the evidence `notes.md`.
- [ ] Demo keys named as throwaway + rotation recorded where applicable.
