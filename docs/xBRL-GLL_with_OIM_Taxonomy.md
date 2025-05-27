## Requirements for a Revised XBRL GL Taxonomy Framework Leveraging XBRL-OIM, Hierarchical Tidy Data, and Dimensional Structure

Building on the XBRL Open Information Model (OIM) and best practices in dimensional taxonomy design, the following requirements define the foundation for a revised XBRL GL taxonomy. This taxonomy must integrate hierarchical tidy data principles with a robust dimensional architecture, supported by a hierarchical definition linkbase.

---

### **1. Syntax-Independent Semantic Model (OIM Foundation)**

* All business semantics must be defined in a syntax-agnostic manner, in accordance with the OIM standard. This ensures semantic consistency across multiple serializations, including xBRL-XML, xBRL-CSV, and xBRL-JSON.

---

### **2. Hierarchical Tidy Data Organization**

* Data must adhere to tidy data principles: each fact is uniquely defined by its dimensional context and primary item.
* Hierarchical relationships between business objects (e.g., `accountingEntries`, `entryHeader`, `entryDetail`) must be explicitly modeled through dimensions, enabling multi-level aggregation, drill-down, and semantic clarity.

---

### **3. Dimensional Structure and Definition Linkbase**

* The taxonomy must employ explicit dimensions, each associated with a domain of permissible members.
* Hierarchical levels (e.g., document, line item) should be modeled using typed dimensions.
* Dimensional hierarchies must be declared in a dedicated definition linkbase using `domain-member` arcs and `@targetRole` attributes to support structured and navigable hierarchies.
* Distinct link roles and arcroles must be used to organize separate relationship networks, enhancing modularity and interpretability.

---

### **4. Modularization and Extensibility**

* The taxonomy should be modular, with clear separation between primary items, dimensions, domains, and member hierarchies—each defined in its own schema or linkbase for maintainability and reuse.
* Extension mechanisms must support the addition of new concepts, dimensions, or hierarchies without modifying the base taxonomy.
* Extensions must remain discoverable, semantically interoperable, and consistent with the core model.

---

### **5. Link Roles and Relationship Networks**

* Every extended link role must have a unique URI and a human-readable label to provide context.
* Link roles must be used to logically group related relationships, supporting clarity in complex, multi-dimensional hierarchies for both human users and automated processors.

---

### **6. Validation and Business Rules**

* The taxonomy must support validation of instance documents against both dimensional and hierarchical structures.
* Business rules should be expressed in a syntax-independent manner, using OIM-compatible validation mechanisms (e.g., Formula 1.0) to ensure data quality and logical consistency.

---

### **7. Technical and Interoperability Requirements**

* The taxonomy must be compatible with OIM processors and support serialization into xBRL-CSV and xBRL-JSON, enabling scalable, efficient data exchange.
* It must include robust namespace and versioning strategies to facilitate taxonomy evolution and module identification.
* Where OIM limitations exist, clear migration paths must be provided to preserve continuity from traditional XML-based XBRL taxonomies.

---

### **Summary Table: Key Requirements**

| Requirement Area                | Description                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------------- |
| Syntax-Independent Semantics    | Define business meaning in a syntax-agnostic, OIM-compliant way                              |
| Hierarchical Tidy Data          | Organize facts using hierarchical and dimensional tidy data structures                       |
| Dimensional Definition Linkbase | Maintain hierarchies of dimension members using a structured definition linkbase             |
| Modularization & Extensibility  | Enable modular taxonomy design with support for flexible extensions                          |
| Link Roles                      | Use labeled, unique link roles to group and navigate relationship networks                   |
| Validation & Business Rules     | Ensure syntax-independent validation and enforce business logic through OIM-compatible rules |
| Technical Interoperability      | Support xBRL-CSV/JSON, processor compatibility, and version control                          |

---

### **Conclusion**

A modernized XBRL GL taxonomy must be grounded in a modular, syntax-neutral semantic model. It should incorporate hierarchical tidy data, explicit and typed dimensions, and a structured definition linkbase. This architecture ensures extensibility, validation, and interoperability—enabling scalable, standards-based reporting across diverse data exchange formats.
