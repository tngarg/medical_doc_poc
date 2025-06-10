graph [
  directed 1
  multigraph 1
  node [
    id 0
    label "Arteriovenous Fistula"
    type "AccessType"
  ]
  node [
    id 1
    label "Inflow Artery"
    type "Vessel"
  ]
  node [
    id 2
    label "Outflow Vein"
    type "Vessel"
  ]
  node [
    id 3
    label "Arteriovenous Anastomosis"
    type "Procedure"
  ]
  node [
    id 4
    label "Hemodialysis Access"
    type "Procedure"
  ]
  node [
    id 5
    label "Duplex Ultrasound"
    type "Imaging"
  ]
  node [
    id 6
    label "Steal Phenomenon"
    type "Condition"
  ]
  node [
    id 7
    label "Hand Pain"
    type "Symptom"
  ]
  node [
    id 8
    label "Compression Maneuver"
    type "DiagnosticMethod"
  ]
  node [
    id 9
    label "Graft Stenosis"
    type "Condition"
  ]
  node [
    id 10
    label "PSV Doubling"
    type "DopplerFinding"
  ]
  node [
    id 11
    label "Vein Diameter"
    type "Measurement"
  ]
  node [
    id 12
    label "Access Suitability"
    type "ProcedureAssessment"
  ]
  node [
    id 13
    label "Color Doppler Imaging"
    type "Technique"
  ]
  node [
    id 14
    label "Vein Mapping"
    type "Procedure"
  ]
  node [
    id 15
    label "Cephalic Vein"
    type "Vein"
  ]
  node [
    id 16
    label "Fistula Creation"
    type "Procedure"
  ]
  node [
    id 17
    label "Subclavian Vein"
    type "Vein"
  ]
  node [
    id 18
    label "High Thrombosis Risk"
    type "RiskFactor"
  ]
  node [
    id 19
    label "Carotid Bifurcation"
    type "AnatomicalRegion"
  ]
  node [
    id 20
    label "Atherosclerotic Plaques"
    type "Pathology"
  ]
  node [
    id 21
    label "Spectral Doppler"
    type "Technique"
  ]
  node [
    id 22
    label "Peak Systolic Velocity"
    type "Measurement"
  ]
  node [
    id 23
    label "ICA/CCA Ratio"
    type "Measurement"
  ]
  node [
    id 24
    label "Stenosis Severity"
    type "Condition"
  ]
  node [
    id 25
    label "Plaque Echogenicity"
    type "Finding"
  ]
  node [
    id 26
    label "Plaque Composition"
    type "PathologyInsight"
  ]
  node [
    id 27
    label "POCUS"
    type "Technique"
  ]
  node [
    id 28
    label "Emergency Department"
    type "Facility"
  ]
  node [
    id 29
    label "Focused Bowel Ultrasound"
    type "Procedure"
  ]
  node [
    id 30
    label "Appendicitis"
    type "Condition"
  ]
  node [
    id 31
    label "Focused Pelvic Ultrasound"
    type "Procedure"
  ]
  node [
    id 32
    label "Ovarian Cyst"
    type "Condition"
  ]
  node [
    id 33
    label "QA Workflow"
    type "Process"
  ]
  node [
    id 34
    label "Exam Quality"
    type "Assessment"
  ]
  node [
    id 35
    label "MWL"
    type "WorkflowComponent"
  ]
  node [
    id 36
    label "ADT Message"
    type "SystemIntegration"
  ]
  edge [
    source 0
    target 1
    key "requires"
    relationship_type "requires"
  ]
  edge [
    source 0
    target 2
    key "requires"
    relationship_type "requires"
  ]
  edge [
    source 0
    target 3
    key "formed_by"
    relationship_type "formed_by"
  ]
  edge [
    source 4
    target 5
    key "monitored_by"
    relationship_type "monitored_by"
  ]
  edge [
    source 6
    target 7
    key "associated_with"
    relationship_type "associated_with"
  ]
  edge [
    source 6
    target 8
    key "evaluated_by"
    relationship_type "evaluated_by"
  ]
  edge [
    source 9
    target 10
    key "detected_by"
    relationship_type "detected_by"
  ]
  edge [
    source 11
    target 12
    key "impacts"
    relationship_type "impacts"
  ]
  edge [
    source 13
    target 14
    key "used_for"
    relationship_type "used_for"
  ]
  edge [
    source 15
    target 16
    key "preferred_for"
    relationship_type "preferred_for"
  ]
  edge [
    source 17
    target 18
    key "avoided_due_to"
    relationship_type "avoided_due_to"
  ]
  edge [
    source 19
    target 20
    key "site_of"
    relationship_type "site_of"
  ]
  edge [
    source 21
    target 22
    key "used_to_measure"
    relationship_type "used_to_measure"
  ]
  edge [
    source 23
    target 24
    key "used_to_classify"
    relationship_type "used_to_classify"
  ]
  edge [
    source 25
    target 26
    key "indicates"
    relationship_type "indicates"
  ]
  edge [
    source 27
    target 28
    key "used_in"
    relationship_type "used_in"
  ]
  edge [
    source 29
    target 30
    key "used_to_evaluate"
    relationship_type "used_to_evaluate"
  ]
  edge [
    source 31
    target 32
    key "used_to_evaluate"
    relationship_type "used_to_evaluate"
  ]
  edge [
    source 33
    target 34
    key "ensures"
    relationship_type "ensures"
  ]
  edge [
    source 35
    target 36
    key "enabled_by"
    relationship_type "enabled_by"
  ]
]
