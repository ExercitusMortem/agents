#!/usr/bin/env python3
"""
Comprehensive validation of the Legal Document Annotation System
"""

from src.agents import (
    AnnotationAgent,
    AnnotationSchema,
    MockLLMClient
)


def validate_schema():
    """Validate the annotation schema structure."""
    print("=" * 70)
    print("VALIDATION: Annotation Schema")
    print("=" * 70)
    
    schema = AnnotationSchema()
    
    # Expected structure
    expected = {
        'PARTIES': ['PERSON', 'ORGANIZATION', 'ROLE'],
        'OBLIGATION': ['AFFIRMATIVE', 'PROHIBITIVE', 'PERMISSIVE'],
        'RIGHTS': ['FINANCIAL', 'ACCESS', 'LEGAL'],
        'DEADLINE': ['ABSOLUTE', 'RELATIVE', 'RECURRENT'],
        'CONDITION': ['TRIGGER', 'EXEMPTION', 'PRECEDENT'],
        'DEFINITION': ['TERM', 'SCOPE'],
        'PENALTY': ['FINANCIAL', 'LEGAL', 'OPERATIONAL'],
        'PROCEDURE': ['FILING', 'NOTIFICATION', 'COMPLIANCE'],
        'REFERENCE': ['STATUTE', 'CASE', 'INTERNAL'],
        'MONEY': ['AMOUNT', 'PERCENTAGE', 'THRESHOLD'],
        'TIME': ['EVENT', 'DURATION']
    }
    
    all_pass = True
    
    # Validate categories
    categories = schema.get_all_categories()
    if len(categories) == 11:
        print("✓ All 11 categories present")
    else:
        print(f"✗ Expected 11 categories, found {len(categories)}")
        all_pass = False
    
    # Validate each category and its subtypes
    for category, expected_subtypes in expected.items():
        if category not in categories:
            print(f"✗ Missing category: {category}")
            all_pass = False
            continue
        
        cat_obj = schema.get_category(category)
        if not cat_obj:
            print(f"✗ Cannot retrieve category: {category}")
            all_pass = False
            continue
        
        actual_subtypes = schema.get_category_subtypes(category)
        if set(actual_subtypes) == set(expected_subtypes):
            print(f"✓ {category}: {len(actual_subtypes)} subtypes correct")
        else:
            print(f"✗ {category}: subtypes mismatch")
            print(f"  Expected: {expected_subtypes}")
            print(f"  Got: {actual_subtypes}")
            all_pass = False
    
    # Test schema methods
    schema_dict = schema.to_dict()
    if len(schema_dict) == 11:
        print("✓ to_dict() returns all categories")
    else:
        print("✗ to_dict() incomplete")
        all_pass = False
    
    guidelines = schema.get_annotation_guidelines()
    if guidelines and len(guidelines) > 0:
        print("✓ Annotation guidelines available")
    else:
        print("✗ Annotation guidelines missing")
        all_pass = False
    
    print()
    return all_pass


def validate_annotation_agent():
    """Validate the annotation agent functionality."""
    print("=" * 70)
    print("VALIDATION: Annotation Agent")
    print("=" * 70)
    
    client = MockLLMClient()
    agent = AnnotationAgent(llm_client=client)
    
    all_pass = True
    
    # Test 1: Valid input
    result = agent.execute({'text': 'The contractor shall deliver goods.'})
    if result.success:
        print("✓ Agent executes successfully with valid input")
    else:
        print(f"✗ Agent failed: {result.error}")
        all_pass = False
    
    # Test 2: Invalid input
    result = agent.execute("not a dict")
    if not result.success:
        print("✓ Agent correctly rejects invalid input")
    else:
        print("✗ Agent should reject invalid input")
        all_pass = False
    
    # Test 3: Empty text
    result = agent.execute({'text': ''})
    if not result.success:
        print("✓ Agent correctly rejects empty text")
    else:
        print("✗ Agent should reject empty text")
        all_pass = False
    
    # Test 4: Rule-based annotation
    text = """
    The Buyer shall pay $50,000 within 30 days.
    Late payment will incur a 5% penalty.
    Either party may terminate with notice.
    See Section 12 of the Agreement.
    """
    
    annotations = agent._rule_based_annotation(text)
    if len(annotations) > 0:
        print(f"✓ Rule-based annotation finds {len(annotations)} annotations")
        
        # Check for different categories
        categories_found = set(a['category'] for a in annotations)
        if len(categories_found) >= 3:
            print(f"✓ Multiple categories detected: {len(categories_found)}")
        else:
            print(f"✗ Expected multiple categories, found {len(categories_found)}")
            all_pass = False
    else:
        print("✗ Rule-based annotation found no annotations")
        all_pass = False
    
    # Test 5: Filtering methods
    test_annotations = [
        {'category': 'OBLIGATION', 'subtype': 'AFFIRMATIVE', 'text': 'shall'},
        {'category': 'MONEY', 'subtype': 'AMOUNT', 'text': '$100'},
        {'category': 'OBLIGATION', 'subtype': 'PROHIBITIVE', 'text': 'shall not'}
    ]
    
    obligations = agent.get_annotations_by_category(test_annotations, 'OBLIGATION')
    if len(obligations) == 2:
        print("✓ Filter by category works correctly")
    else:
        print(f"✗ Filter by category failed: expected 2, got {len(obligations)}")
        all_pass = False
    
    affirmative = agent.get_annotations_by_subtype(
        test_annotations, 'OBLIGATION', 'AFFIRMATIVE'
    )
    if len(affirmative) == 1:
        print("✓ Filter by subtype works correctly")
    else:
        print(f"✗ Filter by subtype failed: expected 1, got {len(affirmative)}")
        all_pass = False
    
    print()
    return all_pass


def validate_patterns():
    """Validate that patterns match expected legal text."""
    print("=" * 70)
    print("VALIDATION: Pattern Matching")
    print("=" * 70)
    
    client = MockLLMClient()
    agent = AnnotationAgent(llm_client=client)
    
    test_cases = [
        {
            'text': 'The contractor shall deliver the goods.',
            'expected_category': 'OBLIGATION',
            'expected_subtype': 'AFFIRMATIVE'
        },
        {
            'text': 'The tenant shall not sublease the property.',
            'expected_category': 'OBLIGATION',
            'expected_subtype': 'PROHIBITIVE'
        },
        {
            'text': 'The employee may work from home.',
            'expected_category': 'OBLIGATION',
            'expected_subtype': 'PERMISSIVE'
        },
        {
            'text': 'The fee is $10,000.',
            'expected_category': 'MONEY',
            'expected_subtype': 'AMOUNT'
        },
        {
            'text': 'Late payment will incur a 5% charge.',
            'expected_category': 'MONEY',
            'expected_subtype': 'PERCENTAGE'
        },
        {
            'text': 'Submit by December 31st, 2026.',
            'expected_category': 'DEADLINE',
            'expected_subtype': 'ABSOLUTE'
        },
        {
            'text': 'Within 30 days of receiving notice.',
            'expected_category': 'DEADLINE',
            'expected_subtype': 'RELATIVE'
        },
        {
            'text': 'As per Section 12 of the Act.',
            'expected_category': 'REFERENCE',
            'expected_subtype': 'STATUTE'
        }
    ]
    
    all_pass = True
    passed = 0
    
    for i, test in enumerate(test_cases, 1):
        annotations = agent._rule_based_annotation(test['text'])
        matching = [
            a for a in annotations 
            if a['category'] == test['expected_category'] 
            and a['subtype'] == test['expected_subtype']
        ]
        
        if matching:
            print(f"✓ Test {i}: Found {test['expected_category']}/{test['expected_subtype']}")
            passed += 1
        else:
            print(f"✗ Test {i}: Expected {test['expected_category']}/{test['expected_subtype']}")
            print(f"  Text: {test['text'][:50]}")
            all_pass = False
    
    print(f"\nPattern Matching: {passed}/{len(test_cases)} tests passed")
    print()
    return all_pass


def main():
    """Run all validations."""
    print("\n" + "=" * 70)
    print("LEGAL DOCUMENT ANNOTATION SYSTEM - COMPREHENSIVE VALIDATION")
    print("=" * 70)
    print()
    
    results = []
    
    # Run validations
    results.append(("Schema", validate_schema()))
    results.append(("Annotation Agent", validate_annotation_agent()))
    results.append(("Pattern Matching", validate_patterns()))
    
    # Summary
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    all_pass = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_pass = False
    
    print()
    if all_pass:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\nThe Legal Document Annotation System is fully functional with:")
        print("  - 11 main annotation categories")
        print("  - 31 subtypes across all categories")
        print("  - Rule-based pattern matching")
        print("  - LLM integration support")
        print("  - Comprehensive test coverage")
    else:
        print("⚠️  Some validations failed. Please review the output above.")
    
    print("=" * 70)
    print()
    
    return 0 if all_pass else 1


if __name__ == '__main__':
    exit(main())
