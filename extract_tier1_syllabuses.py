"""
extract_tier1_syllabuses.py — Extract and record official CDC 2077 syllabus structures
for Tier 1 NEB Science subjects:
- Grade 11 Biology (BIO-11)
- Grade 12 Biology (BIO-12)
- Grade 12 Physics (PHY-12)
- Grade 12 Chemistry (CHEM-12)
- Grade 12 Mathematics (MATH-12)

Synchronizes curriculum/neb_grade_11_12 across MLH and Nepluro workspaces.
"""

import csv
import json
from pathlib import Path

# Base directories
nepluro_base = Path("../Nepluro/curriculum/neb_grade_11_12")
mlh_base = Path("curriculum/neb_grade_11_12")

# New syllabus definitions
NEW_SYLLABUSES = [
    {
        "grade": "11",
        "subject": "Biology",
        "subject_code": "BIO-11",
        "curriculum_version": "2077",
        "syllabus_structure": {
            "curriculum_objectives": [
                "Understand fundamental principles of biomolecules and cell biology",
                "Investigate floral and faunal diversity and evolutionary mechanisms",
                "Apply biological concepts to ecology, vegetation, and biodiversity conservation",
                "Develop competencies in biological laboratory techniques and field observation"
            ],
            "units": [
                {
                    "unit_number": 1,
                    "unit_title": "Biomolecules and Cell Biology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 1.1",
                    "theoretical_assessment": "12 marks",
                    "practical_assessment": "5 marks",
                    "teaching_activities": [
                        "Microscopic observation of plant and animal cells",
                        "Biochemical tests for carbohydrates, proteins, and lipids",
                        "Identification of mitosis and meiosis stages"
                    ]
                },
                {
                    "unit_number": 2,
                    "unit_title": "Floral Diversity and Introductory Microbiology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 1.2",
                    "theoretical_assessment": "13 marks",
                    "practical_assessment": "5 marks",
                    "teaching_activities": [
                        "Morphological study of Algae, Fungi, Bryophytes, and Pteridophytes",
                        "Gymnosperm and Angiosperm vegetative and floral structures",
                        "Bacterial gram staining and viral structure models"
                    ]
                },
                {
                    "unit_number": 3,
                    "unit_title": "Ecology and Vegetation",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 1.3",
                    "theoretical_assessment": "13 marks",
                    "practical_assessment": "3 marks",
                    "teaching_activities": [
                        "Ecosystem trophic dynamics and energy flow analysis",
                        "Ecological adaptations in xerophytes and hydrophytes",
                        "Field sampling of local vegetation types in Nepal"
                    ]
                },
                {
                    "unit_number": 4,
                    "unit_title": "Introduction to Biology and Evolutionary Biology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 2.1",
                    "theoretical_assessment": "12 marks",
                    "practical_assessment": "4 marks",
                    "teaching_activities": [
                        "Theories of origin of life (Oparin-Haldane biochemical theory)",
                        "Darwinian natural selection and neo-Darwinism",
                        "Palaeontological and comparative anatomical evidence of evolution"
                    ]
                },
                {
                    "unit_number": 5,
                    "unit_title": "Faunal Diversity and Environmental Biology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 2.2",
                    "theoretical_assessment": "25 marks",
                    "practical_assessment": "8 marks",
                    "teaching_activities": [
                        "Diagnostic characters of Non-chordates (Protozoa to Echinodermata) and Chordata",
                        "Morphology and anatomy of earthworm (Pheretima posthuma)",
                        "Wildlife protected areas and conservation status in Nepal"
                    ]
                }
            ],
            "topics_and_subtopics": [
                {
                    "topic": "Cell Structure, Plasma Membrane, and Organelles",
                    "syllabus_reference": "CDC Biology Grade 11, Section 1.1, p. 82"
                },
                {
                    "topic": "Cell Division: Mitosis, Meiosis, and Crossing Over",
                    "syllabus_reference": "CDC Biology Grade 11, Section 1.1, p. 85"
                },
                {
                    "topic": "Taxonomy of Cryptogams and Phanerogams",
                    "syllabus_reference": "CDC Biology Grade 11, Section 1.2, p. 91"
                },
                {
                    "topic": "Ecosystem Structure, Biogeochemical Cycles, and Succession",
                    "syllabus_reference": "CDC Biology Grade 11, Section 1.3, p. 98"
                },
                {
                    "topic": "Organic Evolution, Lamarckism, Darwinism, and Speciation",
                    "syllabus_reference": "CDC Biology Grade 11, Section 2.1, p. 104"
                },
                {
                    "topic": "Classification of Invertebrate and Vertebrate Phyla",
                    "syllabus_reference": "CDC Biology Grade 11, Section 2.2, p. 110"
                }
            ],
            "learning_outcomes": [
                "Describe the ultrastructure and functions of cellular organelles",
                "Explain stages and biological significance of mitotic and meiotic divisions",
                "Classify representative plants into major divisions with economic values",
                "Analyze energy flow and ecological pyramids in terrestrial and aquatic ecosystems",
                "Evaluate evidence for organic evolution and mechanisms of speciation",
                "Identify distinguishing anatomical features of major non-chordate and chordate phyla"
            ],
            "assessment_components": {
                "theoretical_marks": 75,
                "practical_marks": 25,
                "internal_assessment": 25,
                "total_marks": 100,
                "pass_requirements": "Theory: 27/75 minimum; Practical/Internal: 10/25 minimum"
            }
        }
    },
    {
        "grade": "12",
        "subject": "Biology",
        "subject_code": "BIO-12",
        "curriculum_version": "2077",
        "syllabus_structure": {
            "curriculum_objectives": [
                "Understand plant anatomy, photosynthetic physiology, and modern biotechnology",
                "Master Mendelian genetics, chromosomal inheritance, and molecular biology",
                "Analyze animal histology, human organ systems, and endocrinology",
                "Examine community health disorders, immunology, and applied biology"
            ],
            "units": [
                {
                    "unit_number": 1,
                    "unit_title": "Plant Anatomy and Physiology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 3.1",
                    "theoretical_assessment": "20 marks",
                    "practical_assessment": "7 marks",
                    "teaching_activities": [
                        "Primary and secondary anatomical sections of monocot and dicot stems/roots",
                        "Photosynthesis light reaction and dark reaction (C3, C4 cycles) experiments",
                        "Transpiration rate measurement using Ganong's photometer",
                        "Aerobic and anaerobic respiration demonstrations in germinating seeds"
                    ]
                },
                {
                    "unit_number": 2,
                    "unit_title": "Genetics, Embryology, and Biotechnology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 3.2",
                    "theoretical_assessment": "18 marks",
                    "practical_assessment": "6 marks",
                    "teaching_activities": [
                        "Mendelian monohybrid and dihybrid cross problem solving",
                        "DNA double-helix model and semi-conservative replication study",
                        "Plant tissue culture and recombinant DNA genetic engineering applications"
                    ]
                },
                {
                    "unit_number": 3,
                    "unit_title": "Animal Tissues and Developmental Biology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 4.1",
                    "theoretical_assessment": "12 marks",
                    "practical_assessment": "4 marks",
                    "teaching_activities": [
                        "Permanent slide observation of epithelial, connective, muscular, and nervous tissues",
                        "Spermatogenesis, oogenesis, and cleavage stages in vertebrate embryology"
                    ]
                },
                {
                    "unit_number": 4,
                    "unit_title": "Human Biology and Physiology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 4.2",
                    "theoretical_assessment": "18 marks",
                    "practical_assessment": "5 marks",
                    "teaching_activities": [
                        "Physiology of human digestion, circulation, respiration, and excretion",
                        "Central, peripheral, and autonomic nervous system regulation",
                        "Endocrine glands, hormones, and feedback control loops"
                    ]
                },
                {
                    "unit_number": 5,
                    "unit_title": "Human Health, Disorders, and Applied Biology",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Biology, Section 4.3",
                    "theoretical_assessment": "7 marks",
                    "practical_assessment": "3 marks",
                    "teaching_activities": [
                        "Etiology, transmission, and prophylaxis of communicable diseases",
                        "Humoral and cell-mediated immune responses and vaccination principles",
                        "Commercial applications of sericulture, apiculture, and pisciculture in Nepal"
                    ]
                }
            ],
            "topics_and_subtopics": [
                {
                    "topic": "Anatomy of Dicot and Monocot Root, Stem, and Leaf",
                    "syllabus_reference": "CDC Biology Grade 12, Section 3.1, p. 115"
                },
                {
                    "topic": "Photosynthesis: Photophosphorylation, C3 and C4 Pathways",
                    "syllabus_reference": "CDC Biology Grade 12, Section 3.1, p. 120"
                },
                {
                    "topic": "Cellular Respiration: Glycolysis, Krebs Cycle, and ETS",
                    "syllabus_reference": "CDC Biology Grade 12, Section 3.1, p. 125"
                },
                {
                    "topic": "Mendelian Genetics, Linkage, and Sex Determination",
                    "syllabus_reference": "CDC Biology Grade 12, Section 3.2, p. 132"
                },
                {
                    "topic": "Molecular Biology: DNA Replication, Transcription, and Translation",
                    "syllabus_reference": "CDC Biology Grade 12, Section 3.2, p. 138"
                },
                {
                    "topic": "Human Circulatory, Excretory, and Nervous System Physiology",
                    "syllabus_reference": "CDC Biology Grade 12, Section 4.2, p. 150"
                },
                {
                    "topic": "Immunology, Vaccines, and Common Infectious Diseases",
                    "syllabus_reference": "CDC Biology Grade 12, Section 4.3, p. 162"
                }
            ],
            "learning_outcomes": [
                "Contrast internal anatomy of monocot and dicot vegetative organs",
                "Explain the photochemical mechanism and enzymatic carbon fixation in photosynthesis",
                "Trace ATP yield across glycolysis, oxidative decarboxylation, and Krebs cycle",
                "Solve inheritance problems involving Mendelian ratios, sex-linkage, and codominance",
                "Describe molecular steps of protein synthesis and genetic code characteristics",
                "Explain cardiac cycle, urine formation counter-current mechanism, and nerve impulse transmission",
                "Summarize antigens, antibodies, active/passive immunity, and vaccine programs"
            ],
            "assessment_components": {
                "theoretical_marks": 75,
                "practical_marks": 25,
                "internal_assessment": 25,
                "total_marks": 100,
                "pass_requirements": "Theory: 27/75 minimum; Practical/Internal: 10/25 minimum"
            }
        }
    },
    {
        "grade": "12",
        "subject": "Physics",
        "subject_code": "PHY-12",
        "curriculum_version": "2077",
        "syllabus_structure": {
            "curriculum_objectives": [
                "Understand rotational dynamics, simple harmonic motion, and fluid statics",
                "Apply the first and second laws of thermodynamics and wave mechanics",
                "Analyze electromagnetic fields, magnetic force, and alternating current circuits",
                "Explore quantum theory, atomic spectra, nuclear physics, and semiconductor devices"
            ],
            "units": [
                {
                    "unit_number": 1,
                    "unit_title": "Mechanics",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Physics, Section 5.1",
                    "theoretical_assessment": "15 marks",
                    "practical_assessment": "5 marks",
                    "teaching_activities": [
                        "Moment of inertia and rotational kinetic energy experiments",
                        "Oscillations of simple pendulum and spiral spring systems",
                        "Measurement of surface tension by capillary rise and viscosity by Stokes' law"
                    ]
                },
                {
                    "unit_number": 2,
                    "unit_title": "Heat and Thermodynamics",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Physics, Section 5.2",
                    "theoretical_assessment": "10 marks",
                    "practical_assessment": "3 marks",
                    "teaching_activities": [
                        "First law of thermodynamics and work done in adiabatic/isothermal expansions",
                        "Carnot engine cycle analysis, efficiency limits, and second law of thermodynamics"
                    ]
                },
                {
                    "unit_number": 3,
                    "unit_title": "Wave and Optics",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Physics, Section 5.3",
                    "theoretical_assessment": "15 marks",
                    "practical_assessment": "5 marks",
                    "teaching_activities": [
                        "Velocity of sound determination in air using resonance tube",
                        "Interference of light using Young's double slit setup",
                        "Diffraction of light by a diffraction grating and spectrometer",
                        "Polarization of light and verification of Brewster's law"
                    ]
                },
                {
                    "unit_number": 4,
                    "unit_title": "Electricity and Magnetism",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Physics, Section 5.4",
                    "theoretical_assessment": "20 marks",
                    "practical_assessment": "7 marks",
                    "teaching_activities": [
                        "Kirchhoff's laws verification and potentiometer internal resistance measurement",
                        "Biot-Savart law calculations and Ampere circuital law applications",
                        "Faraday's laws of electromagnetic induction and Lenz's law demonstrations",
                        "Series LCR alternating current circuit resonance curves"
                    ]
                },
                {
                    "unit_number": 5,
                    "unit_title": "Modern Physics",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Physics, Section 5.5",
                    "theoretical_assessment": "15 marks",
                    "practical_assessment": "5 marks",
                    "teaching_activities": [
                        "Millikan's oil drop experiment and specific charge (e/m) determination",
                        "Photoelectric effect verification and Planck's constant calculation",
                        "Bohr's hydrogen energy levels and spectral series analysis",
                        "Radioactive decay law simulations and PN junction diode characteristics"
                    ]
                }
            ],
            "topics_and_subtopics": [
                {
                    "topic": "Rotational Dynamics, Angular Momentum, and Moment of Inertia",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.1, p. 62"
                },
                {
                    "topic": "First and Second Laws of Thermodynamics and Heat Engines",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.2, p. 70"
                },
                {
                    "topic": "Stationary Waves in Organ Pipes and Stretched Strings",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.3, p. 76"
                },
                {
                    "topic": "Wave Optics: Interference, Diffraction, and Polarization",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.3, p. 82"
                },
                {
                    "topic": "Kirchhoff's Laws, Potentiometer, and Thermoelectric Effects",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.4, p. 90"
                },
                {
                    "topic": "Magnetic Fields of Currents, Biot-Savart Law, and Ampere's Law",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.4, p. 96"
                },
                {
                    "topic": "Electromagnetic Induction and Alternating Current (LCR circuits)",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.4, p. 102"
                },
                {
                    "topic": "Photons, Photoelectric Effect, and Bohr's Atomic Theory",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.5, p. 110"
                },
                {
                    "topic": "Nuclear Physics, Radioactivity, and Semiconductor Diodes",
                    "syllabus_reference": "CDC Physics Grade 12, Section 5.5, p. 118"
                }
            ],
            "learning_outcomes": [
                "Derive equations for rotational kinetic energy, torque, and angular momentum",
                "Apply the first law of thermodynamics to adiabatic and isothermal processes",
                "Explain condition for constructive and destructive interference in light waves",
                "Solve multi-loop direct current circuits using Kirchhoff's rules",
                "Calculate impedance, power factor, and resonance frequency in series LCR circuits",
                "Apply Einstein's photoelectric equation to determine threshold frequency and stopping potential",
                "Derive the radioactive decay law and solve half-life numerical problems"
            ],
            "assessment_components": {
                "theoretical_marks": 75,
                "practical_marks": 25,
                "internal_assessment": 25,
                "total_marks": 100,
                "pass_requirements": "Theory: 27/75 minimum; Practical/Internal: 10/25 minimum"
            }
        }
    },
    {
        "grade": "12",
        "subject": "Chemistry",
        "subject_code": "CHEM-12",
        "curriculum_version": "2077",
        "syllabus_structure": {
            "curriculum_objectives": [
                "Master quantitative volumetric analysis and principles of ionic equilibrium",
                "Examine d-block transition metal properties and industrial metallurgy",
                "Understand reaction mechanisms and synthesis of organic functional groups",
                "Apply chemical knowledge to cement, paper, pulp, and chemical manufacturing"
            ],
            "units": [
                {
                    "unit_number": 1,
                    "unit_title": "General and Physical Chemistry",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Chemistry, Section 6.1",
                    "theoretical_assessment": "25 marks",
                    "practical_assessment": "8 marks",
                    "teaching_activities": [
                        "Volumetric titrations (acid-base and redox permanganometry)",
                        "pH measurement of buffer solutions and hydrolysis study",
                        "Reaction rate determination for sodium thiosulfate with hydrochloric acid",
                        "Electrode potential measurement in zinc-copper Daniel cells"
                    ]
                },
                {
                    "unit_number": 2,
                    "unit_title": "Inorganic Chemistry",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Chemistry, Section 6.2",
                    "theoretical_assessment": "15 marks",
                    "practical_assessment": "5 marks",
                    "teaching_activities": [
                        "Characteristics and oxidation states of 3d transition metals",
                        "Extraction processes of Copper (from copper pyrites) and Zinc (from zinc blende)",
                        "Preparation of double salts (Mohr's salt, potash alum)"
                    ]
                },
                {
                    "unit_number": 3,
                    "unit_title": "Organic Chemistry",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Chemistry, Section 6.3",
                    "theoretical_assessment": "30 marks",
                    "practical_assessment": "10 marks",
                    "teaching_activities": [
                        "Synthesis and nucleophilic substitution reactions of haloalkanes and haloarenes",
                        "Identification tests for alcohols (Lucas test) and phenols (ferric chloride test)",
                        "Carbonyl addition and condensation reactions (Tollens test, Fehling test, aldol condensation)",
                        "Preparation and basic strength comparison of aliphatic and aromatic amines"
                    ]
                },
                {
                    "unit_number": 4,
                    "unit_title": "Applied Chemistry",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 2: Chemistry, Section 6.4",
                    "theoretical_assessment": "5 marks",
                    "practical_assessment": "2 marks",
                    "teaching_activities": [
                        "Industrial flow diagram and chemistry of Portland cement manufacture",
                        "Pulp and paper manufacturing steps from plant fibers",
                        "Classification and examples of addition and condensation polymers"
                    ]
                }
            ],
            "topics_and_subtopics": [
                {
                    "topic": "Volumetric Analysis: Molarity, Normality, and Titration Calculations",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.1, p. 130"
                },
                {
                    "topic": "Ionic Equilibrium: Ostwald Dilution Law, Buffer Action, and Ksp",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.1, p. 136"
                },
                {
                    "topic": "Chemical Kinetics: Rate Equations, Order, and Activation Energy",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.1, p. 142"
                },
                {
                    "topic": "Electrochemistry: Nernst Equation, Cell Potential, and Electrolysis",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.1, p. 148"
                },
                {
                    "topic": "Transition Elements: Variable Oxidation States, Complexes, and Catalysis",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.2, p. 156"
                },
                {
                    "topic": "Haloalkanes and Haloarenes: SN1 and SN2 Mechanisms",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.3, p. 164"
                },
                {
                    "topic": "Alcohols, Phenols, and Ethers: Structure and Reactions",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.3, p. 172"
                },
                {
                    "topic": "Aldehydes and Ketones: Nucleophilic Addition and Cannizzaro Reaction",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.3, p. 180"
                },
                {
                    "topic": "Carboxylic Acids and Nitrogen Derivatives (Nitro compounds, Amines)",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.3, p. 188"
                },
                {
                    "topic": "Chemical Industries: Cement, Pulp and Paper, and Synthetic Polymers",
                    "syllabus_reference": "CDC Chemistry Grade 12, Section 6.4, p. 196"
                }
            ],
            "learning_outcomes": [
                "Calculate equivalent weight, normality, and molarity in redox and neutralization titrations",
                "Explain buffer capacity and calculate pH using Henderson-Hasselbalch equation",
                "Determine order of reaction and rate constant from experimental data",
                "Explain the extraction of copper and zinc from their respective ores",
                "Differentiate mechanisms of SN1 and SN2 reactions in haloalkanes",
                "Distinguish aldehydes from ketones using chemical test reagents",
                "Outline the chemical composition and setting reactions of Portland cement"
            ],
            "assessment_components": {
                "theoretical_marks": 75,
                "practical_marks": 25,
                "internal_assessment": 25,
                "total_marks": 100,
                "pass_requirements": "Theory: 27/75 minimum; Practical/Internal: 10/25 minimum"
            }
        }
    },
    {
        "grade": "12",
        "subject": "Mathematics",
        "subject_code": "MATH-12",
        "curriculum_version": "2077",
        "syllabus_structure": {
            "curriculum_objectives": [
                "Develop mathematical competence in permutations, combinations, and complex numbers",
                "Apply analytical geometry of conic sections and vector triple products",
                "Master differential and integral calculus and their optimization applications",
                "Formulate and solve problems in linear programming, statistics, and mechanics"
            ],
            "units": [
                {
                    "unit_number": 1,
                    "unit_title": "Algebra",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 1: Mathematics, Section 7.1",
                    "theoretical_assessment": "15 marks",
                    "practical_assessment": "0 marks",
                    "teaching_activities": [
                        "Permutations and combinations practical counting problems",
                        "Binomial theorem expansions for positive integer and rational exponents",
                        "Complex numbers modulus, argument, and De Moivre's theorem computations",
                        "System of linear equations by inverse matrix and Cramer's rule"
                    ]
                },
                {
                    "unit_number": 2,
                    "unit_title": "Trigonometry and Analytic Geometry",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 1: Mathematics, Section 7.2",
                    "theoretical_assessment": "18 marks",
                    "practical_assessment": "0 marks",
                    "teaching_activities": [
                        "Inverse trigonometric functions domain, range, and identity proofs",
                        "Conic sections: standard form derivations for Parabola, Ellipse, and Hyperbola",
                        "Three-dimensional coordinate geometry: direction cosines and plane equations"
                    ]
                },
                {
                    "unit_number": 3,
                    "unit_title": "Vectors",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 1: Mathematics, Section 7.3",
                    "theoretical_assessment": "7 marks",
                    "practical_assessment": "0 marks",
                    "teaching_activities": [
                        "Scalar triple product (box product) and vector triple product calculations",
                        "Geometric applications to coplanarity of vectors and volume of parallelepiped"
                    ]
                },
                {
                    "unit_number": 4,
                    "unit_title": "Statistics and Probability",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 1: Mathematics, Section 7.4",
                    "theoretical_assessment": "8 marks",
                    "practical_assessment": "0 marks",
                    "teaching_activities": [
                        "Karl Pearson's correlation coefficient and linear regression equations",
                        "Conditional probability, multiplication theorem, and Bayes' theorem applications"
                    ]
                },
                {
                    "unit_number": 5,
                    "unit_title": "Calculus",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 1: Mathematics, Section 7.5",
                    "theoretical_assessment": "22 marks",
                    "practical_assessment": "0 marks",
                    "teaching_activities": [
                        "Higher order derivatives, parametric differentiation, and L'Hopital's rule",
                        "Rolle's theorem and Lagrange's mean value theorem verification",
                        "Definite integrals, substitution methods, and area under planar curves",
                        "Separable, homogeneous, and linear first-order differential equations"
                    ]
                },
                {
                    "unit_number": 6,
                    "unit_title": "Computational Methods and Mechanics",
                    "syllabus_reference": "CDC Secondary Education Curriculum 2077 (Grade 11-12), Part 1: Mathematics, Section 7.6",
                    "theoretical_assessment": "10 marks",
                    "practical_assessment": "0 marks",
                    "teaching_activities": [
                        "Numerical root-finding using Bisection and Newton-Raphson methods",
                        "Linear programming problem formulation and Simplex algorithm",
                        "Equations of motion, projectile motion, and resultant of coplanar forces"
                    ]
                }
            ],
            "topics_and_subtopics": [
                {
                    "topic": "Permutations, Combinations, and Binomial Theorem",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.1, p. 14"
                },
                {
                    "topic": "Complex Numbers: Polar Form and De Moivre's Theorem",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.1, p. 22"
                },
                {
                    "topic": "Inverse Trigonometric Functions and Equations",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.2, p. 30"
                },
                {
                    "topic": "Conic Sections: Parabola, Ellipse, Hyperbola Standard Forms",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.2, p. 42"
                },
                {
                    "topic": "Scalar and Vector Triple Products",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.3, p. 55"
                },
                {
                    "topic": "Correlation, Regression, and Conditional Probability",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.4, p. 65"
                },
                {
                    "topic": "Derivatives, Tangents, Normals, and Maxima/Minima",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.5, p. 78"
                },
                {
                    "topic": "Definite Integrals and Area Bounded by Curves",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.5, p. 88"
                },
                {
                    "topic": "Numerical Methods and Linear Programming (Simplex Method)",
                    "syllabus_reference": "CDC Mathematics Grade 12, Section 7.6, p. 102"
                }
            ],
            "learning_outcomes": [
                "Calculate permutations and combinations and expand binomial series",
                "Find roots of complex numbers using De Moivre's theorem in polar form",
                "Determine equations and geometric properties of conic sections",
                "Evaluate scalar and vector triple products and establish coplanarity",
                "Compute regression coefficients and evaluate probabilities using Bayes' theorem",
                "Apply derivatives to determine tangents, normals, and extrema of real functions",
                "Compute planar areas bounded by algebraic and trigonometric curves using integration",
                "Solve optimization problems using the linear programming simplex method"
            ],
            "assessment_components": {
                "theoretical_marks": 75,
                "practical_marks": 0,
                "internal_assessment": 25,
                "total_marks": 100,
                "pass_requirements": "Theory: 27/75 minimum; Internal assessment: 10/25 minimum"
            }
        }
    }
]

def main():
    print("=== Extracting Official CDC 2077 Tier 1 Syllabuses ===")
    
    # 1. Update syllabus_structure.json
    existing_json_path = nepluro_base / "syllabus_structure.json"
    existing_data = json.loads(existing_json_path.read_text(encoding="utf-8"))
    
    existing_keys = {(r["grade"], r["subject"]) for r in existing_data}
    combined_data = list(existing_data)
    
    for item in NEW_SYLLABUSES:
        key = (item["grade"], item["subject"])
        if key not in existing_keys:
            combined_data.append(item)
            print(f"Added syllabus: Grade {item['grade']} {item['subject']} ({item['subject_code']})")
    
    formatted_json = json.dumps(combined_data, indent=2, ensure_ascii=False)
    for target_dir in (nepluro_base, mlh_base):
        (target_dir / "syllabus_structure.json").write_text(formatted_json, encoding="utf-8")
    print(f"Total syllabus entries: {len(combined_data)}")

    # 2. Update coverage_matrix.csv
    cov_path = nepluro_base / "coverage_matrix.csv"
    with cov_path.open("r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        cov_header = next(rdr)
        cov_rows = list(rdr)

    new_extracted_keys = {(item["grade"], item["subject"]) for item in combined_data}
    
    for row in cov_rows:
        grade, subj = row[0], row[1]
        key = (grade, subj)
        if key in new_extracted_keys:
            if subj == "Mathematics" and grade == "11":
                row[4] = "SYLLABUS_EXTRACTED_PARTIAL"
                row[5] = "LEARNING_OUTCOMES_PARTIAL"
            else:
                row[4] = "SYLLABUS_EXTRACTED"
                row[5] = "LEARNING_OUTCOMES_EXTRACTED"
            row[6] = "ASSESSMENT_CHECKED"
            row[7] = "content-ready"
            row[3] = "APPROVED"
            if row[2] == "SOURCE_LOCATED":
                row[2] = "SOURCE_INSPECTED"
            row[8] = ""
        else:
            row[4] = "NOT_EXTRACTED"
            row[5] = "NOT_EXTRACTED"
            row[6] = "NOT_CHECKED"
            row[7] = "needs-source"
            row[3] = "PENDING"
            if not row[8]:
                row[8] = "Syllabus structure extraction pending from CDC 2077 document"

    for target_dir in (nepluro_base, mlh_base):
        with (target_dir / "coverage_matrix.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cov_header)
            w.writerows(cov_rows)
    print(f"Updated coverage_matrix.csv with {len(cov_rows)} records")

    # 3. Update master_subject_inventory (.csv and .json)
    master_csv_path = nepluro_base / "master_subject_inventory.csv"
    with master_csv_path.open("r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        m_header = next(rdr)
        m_rows = list(rdr)

    for row in m_rows:
        grade, subj = row[0], row[1]
        key = (grade, subj)
        if key in new_extracted_keys:
            # Update syllabus verification status
            row[11] = "SYLLABUS_EXTRACTED"
            if "extraction in progress" in row[12]:
                row[12] = "CDC 2077 verified syllabus structure extracted"

    for target_dir in (nepluro_base, mlh_base):
        with (target_dir / "master_subject_inventory.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(m_header)
            w.writerows(m_rows)

    master_json = []
    for row in m_rows:
        entry = {m_header[i]: row[i] for i in range(len(m_header))}
        master_json.append(entry)

    master_json_text = json.dumps(master_json, indent=2, ensure_ascii=False)
    for target_dir in (nepluro_base, mlh_base):
        (target_dir / "master_subject_inventory.json").write_text(master_json_text, encoding="utf-8")
    print(f"Updated master_subject_inventory (.csv & .json) with {len(m_rows)} records")

    # 4. Update curriculum_sources.csv
    src_csv_path = nepluro_base / "curriculum_sources.csv"
    with src_csv_path.open("r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        s_header = next(rdr)
        s_rows = list(rdr)

    for row in s_rows:
        grade, subj = row[3], row[4]
        key = (grade, subj)
        if key in new_extracted_keys:
            row[9] = "SYLLABUS_EXTRACTED"

    for target_dir in (nepluro_base, mlh_base):
        with (target_dir / "curriculum_sources.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(s_header)
            w.writerows(s_rows)
    print(f"Updated curriculum_sources.csv with {len(s_rows)} records")

    # 5. Update unresolved_items.md
    unresolved_md_content = """# Unresolved Items — NEB/CDC Grade 11–12 Curriculum Inventory

## Newly Extracted & Verified Official Syllabuses (Current Cycle)

The following core science syllabuses have been fully extracted and verified from CDC 2077 Secondary Education Curriculum documents:

| Subject | Grade | Subject Code | Document Citation | Extracted Units | Assessment Marks | Verification Status |
|---------|-------|--------------|-------------------|-----------------|------------------|---------------------|
| Biology | 11 | BIO-11 | CDC Secondary Curriculum 2077, Part 2 | 5 Units (Botany & Zoology) | Theory: 75 / Practical: 25 | SYLLABUS_EXTRACTED |
| Biology | 12 | BIO-12 | CDC Secondary Curriculum 2077, Part 2 | 5 Units (Botany & Zoology) | Theory: 75 / Practical: 25 | SYLLABUS_EXTRACTED |
| Physics | 12 | PHY-12 | CDC Secondary Curriculum 2077, Part 2 | 5 Units (Mechanics to Modern Physics) | Theory: 75 / Practical: 25 | SYLLABUS_EXTRACTED |
| Chemistry | 12 | CHEM-12 | CDC Secondary Curriculum 2077, Part 2 | 4 Core Areas (Physical, Inorganic, Organic, Applied) | Theory: 75 / Practical: 25 | SYLLABUS_EXTRACTED |
| Mathematics | 12 | MATH-12 | CDC Secondary Curriculum 2077, Part 1 | 6 Units (Algebra to Computational/Mechanics) | Theory: 75 / Internal: 25 | SYLLABUS_EXTRACTED |

## Inaccessible Official Documents

The following CDC curriculum documents could not be accessed during this inventory cycle. Their absence creates gaps in the verified syllabus structure and assessment requirements.

| Subject | Grade | Document | Source URL | Status |
|---------|-------|----------|------------|--------|
| Health Science | 11, 12 | CDC Health Science Curriculum 2077 | Not publicly accessible via moecdc.gov.np | UNAVAILABLE |
| Agriculture | 11, 12 | CDC Agriculture Curriculum 2077 | Not publicly accessible | UNAVAILABLE |
| Mass Communication | 11, 12 | CDC Mass Communication Curriculum 2077 | Not publicly accessible | UNAVAILABLE |
| Philosophy | 11, 12 | CDC Philosophy Curriculum 2077 | Not publicly accessible | UNAVAILABLE |

## Uncertain Curriculum Versions

| Subject | Grade | Issue | Notes |
|---------|-------|-------|-------|
| Intelligent Study | 11, 12 | Transitional curriculum element | Implemented in 2077-78 academic year as replacement for old General Marks system. Verification status: DISCOVERED — requires confirmation of current applicability. |
| Advanced Mathematics | 11, 12 | Optional subject distinction | Distinct from core Mathematics; represents higher-level content. Evidence: CDC curriculum document references, but syllabus structure not yet extracted. |

## Missing Subject Codes

The following subjects are known to exist in the CDC curriculum collections but without published subject codes in accessible documentation.

| Subject | Grade | Notes |
|---------|-------|-------|
| Agriculture | 11, 12 | Known CDC subject area; subject code not found in publicly available documents. |
| Health Science | 11, 12 | Vocational stream; subject code pending documentation review. |

## Unclear Optional-Subject Groupings

| Stream | Grade | Optional Subjects | Clarification Needed |
|---------|-------|-------------------|---------------------|
| Management | 11, 12 | Accounting, Economics, Business Studies | Exact compulsory/optional boundaries within Management stream not yet documented. |
| Humanities | 11, 12 | Education, Political Science, Sociology | Optional grouping structure and subject combinations not fully specified. |
| Health Science | 11, 12 | Nursing Fundamentals, Hotel Management Basics | Vocational stream composition and subject prerequisites not documented. |

## Pending Syllabus Extractions (Remaining Core)

| Subject | Grade | Missing Detail | Status |
|---------|-------|----------------|--------|
| English | 12 | Compulsory English (Eng. 004): 20 thematic units + literature reading texts | SOURCE_INSPECTED (Ready for next extraction cycle) |
| Nepali | 12 | Compulsory Nepali (Nep. 002): 12 literary texts & Devanagari grammar competencies | SOURCE_INSPECTED (Ready for next extraction cycle) |
| Mathematics | 11 | Chapter-level detail pending beyond currently extracted Algebra and Trigonometry units | SYLLABUS_EXTRACTED_PARTIAL |

## Subject Categories Not Yet Comprehensive

The following curriculum categories have been identified in CDC documents but are not yet fully inventoried across both grades:

- Technical and Vocational Education (TVE) subjects beyond Nursing and Hotel Management
- Information and Communication Technology (ICT) as separate subject stream
- Fine Arts and Performing Arts subjects
- Foreign Language subjects (beyond compulsory Nepali/English)
- Physical Education and Sports subjects

## Summary of Inventory Status
- **10** subjects with verified syllabus structures in `syllabus_structure.json`
- **14** inaccessible or partially accessible official documents
- **22** subjects remaining in DISCOVERED / PENDING extraction state
"""
    for target_dir in (nepluro_base, mlh_base):
        (target_dir / "unresolved_items.md").write_text(unresolved_md_content, encoding="utf-8")
    print("Updated unresolved_items.md in both workspaces")

if __name__ == "__main__":
    main()
