#GraphQL Harvester
GraphQL Harvester is a research-grade mitmproxy addon designed to extract, correlate, and operationalize GraphQL intelligence from large-scale JavaScript statics and live API traffic.
It focuses on building a deterministic understanding of GraphQL schemas as they appear in real-world production environments.
The tool was developed through hands-on offensive security research and practical GraphQL testing against complex, high-traffic platforms.
---
Overview:
Modern GraphQL implementations often distribute schema knowledge across:
Minified JavaScript bundles
Multiple statics files
Dynamic /api/graphql requests
GraphQL Harvester addresses this fragmentation by correlating observed runtime variables with static GraphQL references, producing actionable insights for security testing and analysis.
---
Key Capabilities:
#Static & Runtime Intelligence
Intercepts and parses JavaScript static files to extract GraphQL-related artifacts.
Actively monitors /api/graphql traffic to observe real execution variables.
#Deterministic doc_id Correlation
Implements a strict three-pass correlation pipeline to accurately bind each doc_id to its variables.
Designed to minimize false associations common in heuristic-based tools.
#Cross-File Global Memory
Maintains a session-wide global memory model.
Correlates data captured from multiple statics files into a unified GraphQL view.
Optimized for large bundles and fragmented deployments.
#Observed Parameters Live Hints
Displays live intersections between:
Variables observed in /api/graphql
Variables extracted from statics
Interactive controls: Add,Update,Preview,Reset
#Automated Injection Rule Promotion
Intersected parameters are automatically promoted into injectionRules.
Each auto-generated rule is clearly tagged to preserve analyst awareness and control.
Designed to assist—not replace—manual testing decisions.
#Robust GraphQL Request Parsing
Safely extracts variables from:
JSON bodies (dicts & arrays)
application/x-www-form-urlencoded
GET query parameters
Handles malformed or edge-case payloads defensively.
#Consistent Key Normalization
Normalizes variable keys across statics, runtime data, and UI output.
Resolves common inconsistencies such as Scale vs scale.
---
Output & Storage Model:
The system implements a dual-storage architecture optimized for security assessment workflows:
A) ~/graphql_harvester/session.html: 
Ephemeral (resets on proxy restart)
No duplicates, current analysis context
Active testing session analysis
B) ~/graphql_harvester/repository.html:
Persistent (survives restarts)
Complete historical data, all discovered artifacts
Long-term assessment tracking, pattern analysis.
Storage Integrity: All data is stored transparently in human-readable HTML/JSON formats with no hidden directories or background persistence mechanisms.
All outputs are stored explicitly and transparently under:
~/graphql_harvester/
No hidden directories.
No background persistence.
Full analyst visibility over collected data.
---
Interface:
Dark theme with red glow accents.
Blurred background branding (XVISOR03).
Designed for extended analysis sessions with minimal visual fatigue.
---
Intended Use:
GraphQL Harvester is intended for:
GraphQL security research
Offensive security testing
Bug bounty reconnaissance
API security assessments
Schema intelligence gathering
The tool reflects real-world GraphQL architectures commonly seen in large platforms and complex frontend ecosystems.
---
Scope & Design Philosophy:
While the correlation engine was initially developed through research on Meta-style GraphQL deployments, the underlying methodology is architecture-driven, not platform-locked.
The project emphasizes:
Determinism over heuristics
Analyst control over blind automation
Practical applicability over academic abstraction
---
Requirements:
Python 3.x
mitmproxy
------
Disclaimer:
This tool is provided for authorized security testing and research only.
The author assumes no responsibility for misuse or deployment outside legal and ethical boundaries.
---
License:
Licensed under the Apache License, Version 2.0.
See the LICENSE file for full details.
---
Usage
1-Install mitmproxy.
2-Place the GraphQL Harvester addon in a local directory.
3-Run mitmproxy with the addon enabled:
   mitmproxy --listen-host MITM-HOST --listen-port MITM-PORT -s harvester_addon.py
4-Browse the target application as usual.
5-Collected artifacts and analysis output will be available under:
   ~/graphql_harvester/
---
Hasan Habeeb
Offensive cybersecurity researcher with extensive hands-on experience in web and API security, GraphQL analysis, and offensive security research, including vulnerability discoveries in large-scale production environments.
---
