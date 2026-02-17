#!/usr/bin/env python3
"""
Example usage of the Legal Document Annotation System
"""

from src.agents import (
    AnnotationAgent,
    AnnotationSchema,
    MockLLMClient
)


def main():
    print("=" * 70)
    print("Legal Document Annotation System - Example")
    print("=" * 70)
    print()
    
    # 1. Display Schema Information
    print("1. ANNOTATION SCHEMA")
    print("-" * 70)
    schema = AnnotationSchema()
    
    print(f"Total Categories: {len(schema.get_all_categories())}")
    print()
    
    for category in schema.get_all_categories():
        cat_obj = schema.get_category(category)
        subtypes = schema.get_category_subtypes(category)
        print(f"  {category}: {cat_obj.description}")
        print(f"    Subtypes: {', '.join(subtypes)}")
    
    print()
    print("Annotation Guidelines:")
    print(schema.get_annotation_guidelines())
    
    # 2. Annotate Sample Legal Text
    print("\n2. SAMPLE ANNOTATION")
    print("-" * 70)
    
    sample_text = """
    EMPLOYMENT AGREEMENT
    
    Article 1: Payment Terms
    The Employee shall receive a monthly salary of $5,000, payable by the 
    first day of each month. Late payment will incur a penalty of 5% per day.
    
    Article 2: Obligations
    The Employee must complete all assigned tasks by the agreed deadlines.
    The Employee shall not disclose confidential information to third parties.
    The Employee may work from home up to two days per week.
    
    Article 3: Rights
    The Employee is entitled to 20 days of paid vacation annually.
    The Employee has the right to appeal any disciplinary action.
    The Employer may inspect the Employee's work with 24-hour notice.
    
    Article 4: Termination
    Either party may terminate this agreement with 30 days written notice.
    Violation of confidentiality will result in immediate termination and 
    possible legal action.
    
    Article 5: Governing Law
    This agreement is governed by Section 12 of the Employment Act 2020.
    For dispute resolution, see Clause 7.2 of this agreement.
    """
    
    print("Sample Legal Text:")
    print("-" * 70)
    print(sample_text)
    print("-" * 70)
    
    # Create annotation agent
    print("\nInitializing Annotation Agent...")
    client = MockLLMClient()
    agent = AnnotationAgent(llm_client=client)
    
    # Execute annotation
    print("Annotating document...")
    result = agent.execute({'text': sample_text})
    
    if result.success:
        print("\n✓ Annotation Successful!")
        print(f"\nMetadata:")
        print(f"  Total Annotations: {result.metadata['annotation_count']}")
        print(f"  Categories Used: {', '.join(result.metadata['categories_used'])}")
        
        # Group annotations by category
        print("\n3. ANNOTATIONS BY CATEGORY")
        print("-" * 70)
        
        annotations = result.data['annotations']
        categories_found = set(a['category'] for a in annotations)
        
        for category in sorted(categories_found):
            cat_annotations = agent.get_annotations_by_category(annotations, category)
            print(f"\n{category} ({len(cat_annotations)} found):")
            
            for i, ann in enumerate(cat_annotations[:5], 1):  # Show first 5
                text_preview = ann['text'][:60] + '...' if len(ann['text']) > 60 else ann['text']
                print(f"  {i}. [{ann['subtype']}] {text_preview}")
            
            if len(cat_annotations) > 5:
                print(f"  ... and {len(cat_annotations) - 5} more")
        
        # Show specific examples
        print("\n4. DETAILED EXAMPLES")
        print("-" * 70)
        
        # Show obligations
        obligations = agent.get_annotations_by_category(annotations, 'OBLIGATION')
        if obligations:
            print("\nOBLIGATIONS:")
            for i, ann in enumerate(obligations[:3], 1):
                print(f"\n  Example {i}:")
                print(f"    Type: {ann['subtype']}")
                print(f"    Text: {ann['text']}")
                print(f"    Context: {ann.get('context', 'N/A')}")
        
        # Show money references
        money = agent.get_annotations_by_category(annotations, 'MONEY')
        if money:
            print("\nMONETARY REFERENCES:")
            for i, ann in enumerate(money[:3], 1):
                print(f"\n  Example {i}:")
                print(f"    Type: {ann['subtype']}")
                print(f"    Text: {ann['text']}")
        
        # Show deadlines
        deadlines = agent.get_annotations_by_category(annotations, 'DEADLINE')
        if deadlines:
            print("\nDEADLINES:")
            for i, ann in enumerate(deadlines[:3], 1):
                print(f"\n  Example {i}:")
                print(f"    Type: {ann['subtype']}")
                print(f"    Text: {ann['text']}")
        
    else:
        print(f"\n✗ Annotation Failed: {result.error}")
    
    print("\n" + "=" * 70)
    print("Example Complete")
    print("=" * 70)


if __name__ == '__main__':
    main()
