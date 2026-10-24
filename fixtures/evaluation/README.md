# Evaluation protocol

40 prompts (20 paired Chinese/English intentions). These are a labeling template, not a completed benchmark dataset. No human labels or representative photographs have been fabricated.

For each query, collect rights-permitted representative assets with source/license evidence, assign stable asset IDs, and have a human judge relevance: 0 irrelevant, 1 partly relevant, 2 relevant, 3 highly relevant. Record labels in judgments, IDs in representative_asset_ids, and set label_status to human_reviewed. Obtain enough candidates to assess the top 10.

Report Precision@10 (grade >=2), NDCG@10 (gain 2^grade−1), duplicate ratio, palette score, and observed human keep rate separately. Missing judgments are unjudged, not grade zero. Do not publish aggregate relevance metrics until labeling is complete. Compare identical candidate sets and model/preprocess revisions. Timing/peak RSS reports in docs are separate system checks using procedural fixtures.
