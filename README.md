###Project Pipeline

```mermaid
flowchart TD
    A([📄 Upload answer sheet image]) --> B[Preprocess\ncrop & enhance]
    B --> C[PaddleOCR\nextract handwritten text]
    C --> D[Clean extracted text]

    D --> E[(Vector DB\nMaths · Science · English)]

    E --> F{Query Router\nidentify subject}
    F --> G[Retrieve top-K rubric chunks\nHybrid Search: vector + BM25]
    G --> H{CRAG Verifier\nrelevance check}

    H -->|YES| I
    H -->|PARTIAL| J[Re-retrieve / expand / flag]
    H -->|NO| J
    J --> H

    I[Verified Rubric + Student Answer\n→ Gemma on GPU]
    I --> K[Gemma evaluates answer\nvs rubric points]
    K --> L[Assign marks +\nconfidence score]
    L --> M([Output\nMarks · Missing Points · Review Flag])

    style A fill:#4B5563,color:#fff,stroke:none
    style M fill:#4B5563,color:#fff,stroke:none
    style F fill:#1D4ED8,color:#fff,stroke:none
    style H fill:#1D4ED8,color:#fff,stroke:none
    style E fill:#065F46,color:#fff,stroke:none
    style J fill:#7C3AED,color:#fff,stroke:none
```
