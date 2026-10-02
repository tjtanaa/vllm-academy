# Original figures

The four diagrams were authored for this curriculum and rendered with Graphviz. They are conceptual teaching figures, not measured production traces or copied source-paper artwork. Committed `.dot` files provide editable diagram source and `.svg` files provide rendered vector output. Optional `.png` copies provide a broadly compatible view but are generated rather than committed. `render.py` regenerates them with an installed Graphviz `dot` executable.

01 separates a decoder model from surrounding service responsibilities. 02 opens the request and output boundaries. 03 follows image representations and distinct caches. 04 contrasts co-location and R/E/P/D placement without confusing them with model-parallelism axes.

A box is a responsibility, not necessarily one process/host. The multimodal diagram is a LLaVA-like teaching example, not a universal VLM architecture. Diagrams use words and position as well as color, and are described in the architecture atlas for readers who cannot use the images.

Underlying mechanisms are credited in the [source register](../REFERENCES.md). No fonts or third-party artwork are bundled.
