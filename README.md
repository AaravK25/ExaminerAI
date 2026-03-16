<div align="center">
```mermaid
flowchart TD
    A([📄 Upload answer sheet image]) --> B[Preprocess<br>crop & enhance]
    B --> C[PaddleOCR<br>extract handwritten text]
    C --> D[Clean extracted text]

    D --> E[(Vector DB<br>Maths · Science · English)]

    E --> F{Query Router<br>identify subject}
    F --> G[Retrieve top-K rubric chunks<br>Hybrid Search: vector + BM25]
    G --> H{CRAG Verifier<br>relevance check}

    H -->|YES| I[Verified Rubric + Student Answer<br>→ Gemma on GPU]
    H -->|PARTIAL| J[Re-retrieve / expand / flag]
    H -->|NO| J
    J --> H

    I --> K[Gemma evaluates answer<br>vs rubric points]
    K --> L[Assign marks +<br>confidence score]
    L --> M([Output<br>Marks · Missing Points · Review Flag])

    style A fill:#4B5563,color:#fff,stroke:none
    style M fill:#4B5563,color:#fff,stroke:none
    style F fill:#1D4ED8,color:#fff,stroke:none
    style H fill:#1D4ED8,color:#fff,stroke:none
    style E fill:#065F46,color:#fff,stroke:none
    style J fill:#7C3AED,color:#fff,stroke:none
```

</div>
