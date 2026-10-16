# Shared contracts

`crosswalk-contracts` contains the small envelopes shared across future HTTP and job boundaries: health responses, error envelopes with trace IDs, and cursor pages. Keeping these models in one package prevents each adapter from inventing a different shape.
