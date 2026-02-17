"""
Legal Document Annotation Schema

Defines the comprehensive annotation schema for legal documents with 11 main categories.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class AnnotationSubtype:
    """Represents a subtype within an annotation category."""
    name: str
    description: str
    examples: List[str] = field(default_factory=list)


@dataclass
class AnnotationCategory:
    """Represents a main annotation category."""
    label: str
    description: str
    subtypes: Dict[str, AnnotationSubtype] = field(default_factory=dict)


class AnnotationSchema:
    """
    Legal Document Annotation Schema - Content Level
    
    Provides a comprehensive schema for annotating legal documents with
    11 main categories and their subtypes.
    """
    
    def __init__(self):
        self.categories: Dict[str, AnnotationCategory] = {}
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize all annotation categories and subtypes."""
        
        # 1. PARTIES / STAKEHOLDERS
        self.categories['PARTIES'] = AnnotationCategory(
            label='PARTIES',
            description='Entities involved in the legal text',
            subtypes={
                'PERSON': AnnotationSubtype(
                    name='PERSON',
                    description='Individual mentioned',
                    examples=['"John Doe"']
                ),
                'ORGANIZATION': AnnotationSubtype(
                    name='ORGANIZATION',
                    description='Company, government, NGO',
                    examples=['"Acme Corp."']
                ),
                'ROLE': AnnotationSubtype(
                    name='ROLE',
                    description='Legal role or designation',
                    examples=['"Tenant"', '"Plaintiff"', '"Arbitrator"']
                )
            }
        )
        
        # 2. OBLIGATION / DUTY
        self.categories['OBLIGATION'] = AnnotationCategory(
            label='OBLIGATION',
            description='What a party must do or refrain from doing',
            subtypes={
                'AFFIRMATIVE': AnnotationSubtype(
                    name='AFFIRMATIVE',
                    description='Must perform an action',
                    examples=['"The contractor shall deliver the goods by 15th March."']
                ),
                'PROHIBITIVE': AnnotationSubtype(
                    name='PROHIBITIVE',
                    description='Must refrain from an action',
                    examples=['"The tenant shall not sublease the property without consent."']
                ),
                'PERMISSIVE': AnnotationSubtype(
                    name='PERMISSIVE',
                    description='Allowed but not required',
                    examples=['"The employee may work from home once a week."']
                )
            }
        )
        
        # 3. RIGHTS / ENTITLEMENTS
        self.categories['RIGHTS'] = AnnotationCategory(
            label='RIGHTS',
            description='Permissions or claims a party possesses',
            subtypes={
                'FINANCIAL': AnnotationSubtype(
                    name='FINANCIAL',
                    description='Monetary entitlement',
                    examples=['"The employee is entitled to a bonus of $5,000."']
                ),
                'ACCESS': AnnotationSubtype(
                    name='ACCESS',
                    description='Right to use or enter',
                    examples=['"The landlord may inspect the premises with 24-hour notice."']
                ),
                'LEGAL': AnnotationSubtype(
                    name='LEGAL',
                    description='Claim under law',
                    examples=['"The citizen has the right to appeal."']
                )
            }
        )
        
        # 4. DEADLINES / TIMEFRAMES
        self.categories['DEADLINE'] = AnnotationCategory(
            label='DEADLINE',
            description='Specific times or durations for obligations or actions',
            subtypes={
                'ABSOLUTE': AnnotationSubtype(
                    name='ABSOLUTE',
                    description='Specific date',
                    examples=['"Submit the report by 31st March 2026."']
                ),
                'RELATIVE': AnnotationSubtype(
                    name='RELATIVE',
                    description='Duration from an event',
                    examples=['"Within 30 days of receiving notice."']
                ),
                'RECURRENT': AnnotationSubtype(
                    name='RECURRENT',
                    description='Repeating deadlines',
                    examples=['"Annual audit must be submitted every January."']
                )
            }
        )
        
        # 5. CONDITIONS / CONTINGENCIES
        self.categories['CONDITION'] = AnnotationCategory(
            label='CONDITION',
            description='Triggers for obligations, rights, or consequences',
            subtypes={
                'TRIGGER': AnnotationSubtype(
                    name='TRIGGER',
                    description='Event that activates obligation',
                    examples=['"If the buyer fails to pay, the seller may terminate."']
                ),
                'EXEMPTION': AnnotationSubtype(
                    name='EXEMPTION',
                    description='Circumstances exempting parties',
                    examples=['"This clause does not apply during emergencies."']
                ),
                'PRECEDENT': AnnotationSubtype(
                    name='PRECEDENT',
                    description='Must occur before action',
                    examples=['"Approval by the board is required before execution."']
                )
            }
        )
        
        # 6. DEFINITIONS / TERMS
        self.categories['DEFINITION'] = AnnotationCategory(
            label='DEFINITION',
            description='Explicitly defined terms within the document',
            subtypes={
                'TERM': AnnotationSubtype(
                    name='TERM',
                    description='Term being defined',
                    examples=['"\'Goods\' shall mean all items delivered under this contract."']
                ),
                'SCOPE': AnnotationSubtype(
                    name='SCOPE',
                    description='Scope or limitation of term',
                    examples=['"For the purposes of this Act, \'employee\' excludes interns."']
                )
            }
        )
        
        # 7. PENALTIES / SANCTIONS
        self.categories['PENALTY'] = AnnotationCategory(
            label='PENALTY',
            description='Consequences for non-compliance',
            subtypes={
                'FINANCIAL': AnnotationSubtype(
                    name='FINANCIAL',
                    description='Monetary fines or fees',
                    examples=['"Late payment will incur $500 per day."']
                ),
                'LEGAL': AnnotationSubtype(
                    name='LEGAL',
                    description='Legal actions',
                    examples=['"Violation may result in injunction or imprisonment."']
                ),
                'OPERATIONAL': AnnotationSubtype(
                    name='OPERATIONAL',
                    description='Suspension of rights/privileges',
                    examples=['"Access to services will be suspended until payment."']
                )
            }
        )
        
        # 8. PROCEDURES / PROCESSES
        self.categories['PROCEDURE'] = AnnotationCategory(
            label='PROCEDURE',
            description='Steps to fulfill legal obligations',
            subtypes={
                'FILING': AnnotationSubtype(
                    name='FILING',
                    description='Steps to submit documents',
                    examples=['"File the appeal at the district court registry."']
                ),
                'NOTIFICATION': AnnotationSubtype(
                    name='NOTIFICATION',
                    description='Communicating decisions or actions',
                    examples=['"Send written notice to all affected parties."']
                ),
                'COMPLIANCE': AnnotationSubtype(
                    name='COMPLIANCE',
                    description='Steps to comply with law or policy',
                    examples=['"Maintain records for five years."']
                )
            }
        )
        
        # 9. REFERENCES / CITATIONS
        self.categories['REFERENCE'] = AnnotationCategory(
            label='REFERENCE',
            description='Mentions of laws, cases, or other legal texts',
            subtypes={
                'STATUTE': AnnotationSubtype(
                    name='STATUTE',
                    description='Law, act, or regulation',
                    examples=['"As per Section 12 of the Companies Act 2013."']
                ),
                'CASE': AnnotationSubtype(
                    name='CASE',
                    description='Court decisions',
                    examples=['"R v Smith [2018] EWCA 123."']
                ),
                'INTERNAL': AnnotationSubtype(
                    name='INTERNAL',
                    description='Within same document',
                    examples=['"See Clause 4.2 for details."']
                )
            }
        )
        
        # 10. MONETARY / QUANTITATIVE DATA
        self.categories['MONEY'] = AnnotationCategory(
            label='MONEY',
            description='Amounts, percentages, or financial thresholds',
            subtypes={
                'AMOUNT': AnnotationSubtype(
                    name='AMOUNT',
                    description='Specific amount',
                    examples=['"$10,000"']
                ),
                'PERCENTAGE': AnnotationSubtype(
                    name='PERCENTAGE',
                    description='Percentage obligations',
                    examples=['"5% late fee"']
                ),
                'THRESHOLD': AnnotationSubtype(
                    name='THRESHOLD',
                    description='Minimum/maximum limit',
                    examples=['"Minimum capital contribution of $50,000"']
                )
            }
        )
        
        # 11. TEMPORAL / EVENT REFERENCES
        self.categories['TIME'] = AnnotationCategory(
            label='TIME',
            description='Events or dates that are not deadlines but relevant to context',
            subtypes={
                'EVENT': AnnotationSubtype(
                    name='EVENT',
                    description='Legal or contractual event',
                    examples=['"Upon execution of this contract…"']
                ),
                'DURATION': AnnotationSubtype(
                    name='DURATION',
                    description='Period covered',
                    examples=['"For a period of five years from signing."']
                )
            }
        )
    
    def get_category(self, label: str) -> AnnotationCategory:
        """Get a category by label."""
        return self.categories.get(label)
    
    def get_subtype(self, category_label: str, subtype_name: str) -> AnnotationSubtype:
        """Get a specific subtype from a category."""
        category = self.get_category(category_label)
        if category:
            return category.subtypes.get(subtype_name)
        return None
    
    def get_all_categories(self) -> List[str]:
        """Get list of all category labels."""
        return list(self.categories.keys())
    
    def get_category_subtypes(self, category_label: str) -> List[str]:
        """Get list of all subtype names for a category."""
        category = self.get_category(category_label)
        if category:
            return list(category.subtypes.keys())
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary format."""
        result = {}
        for label, category in self.categories.items():
            result[label] = {
                'description': category.description,
                'subtypes': {}
            }
            for subtype_name, subtype in category.subtypes.items():
                result[label]['subtypes'][subtype_name] = {
                    'description': subtype.description,
                    'examples': subtype.examples
                }
        return result
    
    def get_annotation_guidelines(self) -> str:
        """Return annotation guidelines as a formatted string."""
        guidelines = """
✅ Annotation Guidelines

1. Span-based tagging: Highlight exact words or phrases corresponding to labels.

2. Hierarchical tagging: Subtypes can be nested under main labels.

3. Cross-linking: Connect OBLIGATION → DEADLINE → PENALTY if they relate.

4. Granularity: If a clause contains multiple elements, annotate each separately.

5. Consistency: Use the same label names across the dataset to ensure uniformity.
"""
        return guidelines
