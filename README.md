# Dimensional XBRL-GL and Structured CSV Project

This project modernizes **XBRL Global Ledger (XBRL GL)** by enabling it to be expressed using **xBRL-CSV** format. Through the use of a **dimensional definition linkbase**, this approach allows any XBRL GL XML instance to be represented as a single structured CSV file.

## 🔧 Key Features

- Converts **PWD 2016 XBRL GL** definitions into a semantic model.
- Generates both **palette schema taxonomy** and **OIM dimensional taxonomy** (hypercube-based).
- Transforms **XML instance documents** into structured **xBRL-CSV**.
- Supports two authoring paths:
  - **Palette-based reverse modeling**
  - **Semantic model-driven generation** via FSM → BSM → LHM

## 📁 Repository Contents

```
xBRL-GL
├─docs/
│   └── user-guide.adoc  # Contains the full AsciiDoc user guide
├─scripts                # Directory for Python scripts used in various processes.
├─semantic-model         # Equivalent to UML Class Diagram in Single Sheet Format
│  ├─FSM                 # Foundational Semantic Model in CSV 
│  ├─BSM                 # Business Semantic Model in CSV
│  └─LHM                 # Logical Hierarchical Model
├─tests
│  └─Windows11           # Batch scripts related to testing.
├─xBRL-CSV_instance      # Instances of xBRL GL in xBRL-CSV format.
├─xBRL-CSV_taxonomy      # Palette taxonomy for xBRL GL, organized into subdirectories:
│  ├─bus                 # Business module
│  │  └─lang
│  ├─cor                 # Core module
│  │  └─lang
│  ├─ehm                 # Enhanced Measurable module
│  │  └─lang
│  ├─muc                 # MultiCurrency module
│  │  └─lang
│  ├─plt                 # Contains both tuple taxonomy and xBRL-CSV taxonomy
|  │  ├─gl-plt-all-2025-12-01 # Tuple based palette taxonomy
|  │  └─gl-plt-oim-2025-12-01 # Dimension based palette taxonomy
│  ├─srcd                # Summary Reporting Contextual Data module
│  │  └─lang
│  └─taf                 # Tax Audit File module
│      └─lang
└─XBRL-GL-2016-PWD       # Public Working Draft published in 2016
   This taxonomy provides a standardized format for representing data fields from accounting and operational systems. It consists of modular sets:
   - COR (Core): Foundational module including essential data fields for all types of information in XBRL GL.
   - BUS (Business): Augments COR with additional accounting and operational details, including inventory, business metrics, and organizational information.
   - MUC (Multicurrency): Adds detailed fields for handling multicurrency information and additional entity details.
   - TAF (Tax Audit File): Includes fields required for tax and audit purposes, developed with input from international tax agencies.
   - SRCD (Summary Reporting Contextual Data): Facilitates linking detailed XBRL GL data to final reporting using XBRL taxonomies or other XML schemas.
   - EHM (Enhanced Measurable): Provides fields specific to inventory and fixed assets representation.
   Each module extends the Core but can be used independently. The taxonomy structure compiles schemas into a cohesive set via a "palette" schema (e.g., gl-plt-2016-12-01.xsd).
```

## 📜 Licensing

- **Scripts:** MIT License  
- **Documentation & Artifacts:** Creative Commons Attribution 4.0 (CC BY 4.0)

## 📚 User Guide

See [docs/USER-GUIDE.md](docs/USER-GUIDE.md) for a full walkthrough, including Mermaid flowcharts, CLI examples, and script documentation.

## 🚀 Quick Start

Open the project in VS Code and run the included launch configurations via `launch.json`.  
Use sample instance files in the `ids/` directory and start generating structured xBRL-CSV output.
