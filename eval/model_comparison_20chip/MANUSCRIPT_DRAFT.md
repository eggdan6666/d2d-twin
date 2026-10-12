# Provisional manuscript wording

This is a draft for review; it has not been inserted into paper/main.tex. The historical results and the present 20-chip expansion are separate cohorts.

## Methods

We evaluated three locally deployed code models on a fixed roster of 20 peripheral-device IRs. Each model produced four samples for each of three seeds (1, 2, and 3), yielding 12 samples per device and 240 per model. The documented generation settings were temperature 0.7, top-p 0.9, top-k 40, and a maximum of 2,048 new tokens. A sample was counted as fully passing when the black-box pytest process returned zero. Tests inapplicable to a given IR could be skipped; the number of passed test functions was therefore not treated as a universal assertion-accuracy denominator. Samples were nested within devices. Descriptive aggregate and device-level results were reported without an independent-trial significance claim.

## Results

In the 20-device expansion cohort, Qwen2.5-Coder-3B-Instruct, DeepSeek-Coder-6.7B-Instruct, and Qwen2.5-Coder-14B-Instruct achieved 22/240 (9.2%), 25/240 (10.4%), and 48/240 (20.0%) fully passing samples, respectively. Code-block extraction succeeded for 239/240, 240/240, and 240/240 samples. The Qwen-14B model exceeded Qwen-3B by 10.83 percentage points in this descriptive comparison. Device-level performance remained heterogeneous: Qwen-14B passed all 12 samples on AD5592R and ADS1220, but achieved no fully passing samples on 12 of the 20 devices. DeepSeek provides a cross-family comparison and is not interpreted as an intermediate point in a Qwen-only scaling law.

## Limitations and provenance

The archive verified at export time includes all 240 Qwen-14B results, 20 IRs, and source snapshots with matching SHA-256 hashes. This verifies the supplied artifact's integrity; it does not independently establish the exact files or model revisions used at every generation step in all arms. Seven archived IRs differ from current local IRs in annotations, and INA3221 additionally differs in access-permission semantics. Original scores are retained under the archived protocol, with revision re-scoring reported separately. The present results should remain exploratory until runtime provenance and the canonical IR revision are resolved.

CPU-only sensitivity re-scoring of the 36 existing INA3221 implementations under the archived and corrected IRs required 72 pytest runs. Return codes and passed-test counts matched the original records under both revisions, leaving the aggregate fully passing rates unchanged. This check does not replace generation-time provenance or regeneration under the corrected IR.

## Draft figure caption

Exploratory performance of three local code models on 20 peripheral-device IRs. (A) Proportion of fully passing samples, with 240 samples per model. (B) Fully passing sample counts for each device, with 12 samples per device and model. The twelve samples comprise three seeds and four generations per seed; repeated generations are nested within devices. Colors indicate descriptive pass proportions, and no significance markers are shown. Values are derived from the archived raw result JSONs.
