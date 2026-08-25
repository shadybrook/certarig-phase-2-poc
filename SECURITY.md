# Security and safety reporting

CertaRig is an educational proof of concept. Do not use it as the only protection for personnel, pressure equipment, mains electricity, or industrial machinery.

## Report a software issue

Open a GitHub issue without including passwords, API keys, private network addresses, personal information, or unpublished hardware details.

## Secrets

Keep CERTARIG_OPERATOR_KEY, OPENAI_API_KEY, tokens, certificates, and private configuration outside the repository. The included environment file is an example only.

## Phase 2 safety boundary

The browser application uses synthetic data and has no physical control authority. The supplementary edge code defaults to localhost and forces its hardware adapter into a safe state at startup.

## Hardware boundary

Raspberry Pi GPIO must never directly drive a relay coil, solenoid, miniature circuit breaker, mains circuit, motor starter, or industrial load. Any later hardware work requires correctly rated isolation, independent protection, an emergency stop, a pressure relief path, and competent engineering review.
