# Independent LIS3DH implementation acceptance checklist

Task: `lis3dh-v35/code_review`, SCI-Skills M4; source: local ST LIS3DH DocID17530 Rev 2 (54 pages). This checklist was written before runtime review.

| Source locator | Independent acceptance obligation | Evidence boundary |
| --- | --- | --- |
| p37 Tables 37–39 | ST codes 0, 1 and 2 persist under legal CTRL_REG4 read/write, preserving adjacent bits; code 3 is rejected atomically as outside the profile | No mechanical self-test output simulation or pass claim |
| p39 Tables 46–47 | Seven documented STATUS bits begin at zero; readable known mask is FE, with missing XDA reset authority remaining unknown | Full cold STATUS read must not fabricate XDA = 0 |
| pp31–32 register map and p40 output description | Cold dynamic outputs remain unknown; explicitly qualified post-ADC samples create known values; words use source-described left justification | Stimuli are digital samples, not acceleration or timing observations |
| p39 Table47 | New sample sets DA; replacement of unread previous values sets overrun; STATUS observation is not itself a sourced consumption action | Aggregate/axis bit-clear trigger unspecified here |
| p37 BDU/BLE descriptions | Active BDU or big-endian capture must not silently reuse unsupported baseline semantics | No fabricated atomic latch or endian behavior |
| pp16–17 mode and self-test descriptions | Mode configurations outside the documented bounded sample profile are rejected without state or trace mutation | No elapsed-time or MEMS actuation claims |
| p39 missing read-clear prose | Read consumption is either explicitly rejected by common-source profile or marked candidate with precise chosen pair/axis/aggregate rules | Candidate checks cannot be promoted to manufacturer certification |
| Source audit and reviewed source contract | Exact eight REPAIR field identities and eight dimensions, primary PDF SHA-256, accepted source contract identity and actual scenario replay bind evidence | A forged summary or unrelated successful test is insufficient |

Tests will use deliberate nonzero states, illegal-code boundaries, partial byte reads, order permutations, repeated reads, interleaved samples, malformed events and fresh object snapshots. Rejections must be atomic, including trace. Mutants will probe reset-mask fabrication, RW corruption, NA acceptance, sample knownness/flag failures, and candidate clear errors. Formal field/source/global admission remains closed regardless of bounded test success.

Primary next action: execute the independently derived checks against the new runtime and inspect any mismatch before producing the acceptance report.
