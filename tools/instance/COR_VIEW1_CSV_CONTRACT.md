# Adopted View Definition and Responsibilities of the Generator

A View is defined by selecting items from an HMD and arranging them according to its structure. The CSV specified by the user for this task is a single file containing all 11 structural columns of the existing View1, the occurrence specifications at the top, and the values in columns L–O. The fact that a class with an upper multiplicity bound of one does not increase the occurrence hierarchy depth or define a dimension is a property of the View definition itself; it is not a rule by which the generator infers or corrects the definition through new transparency processing at runtime.

The definition used here faithfully extracts the selected items, multiplicities and occurrence specifications already present in the existing Excel workbook into a CSV. The script checks these against the adopted HMD using `semantic_path` and rejects inconsistencies. It must not silently remove classes or recalculate the View's `level`, parent relationships or dimensions to make the input acceptable. It must not create new `view_occurrence_level` or `parent` columns or inferred values.

The currently selected classes `documentInformation` (`0..1`), `entityParty` (`0..1`) and `detailAccountIdentifier` (`1`) have no corresponding dimensions in the adopted DTS; no new dimensions are added to the existing OIM for them. The Tuple representation retains the containers required by the existing schema, and neither the HMD nor the taxonomy is revised. This does not authorise the generator to add structures that are absent from the View definition.

The user's decision to permit changes to `local_name` and `multiplicity` at both the Candidate and Reviewed stages is recorded. However, because no specific replacement values have been provided, the current model is not changed.

For the CSV-input CLI, inputs, output profiles and dependencies, see `README_COR_VIEW1.md`. Historical registration hashes remain in WORK evidence and are not runtime inputs. No new model-definition columns or inferred hierarchy are added.
