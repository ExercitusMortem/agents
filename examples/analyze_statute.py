"""
Example: Analyze a legal document using LegalBot

This script demonstrates how to use the LegalBot orchestrator to analyze
a sample legal statute.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents import LegalBot


def main():
    # Sample legal text (simplified statute)
    sample_statute = """
    Article I: General Provisions
    
    Section 1: Definitions
    For the purposes of this statute, "contractor" shall mean any person or 
    entity engaged in the business of construction. "Owner" shall mean the 
    person or entity contracting for construction services.
    
    Section 2: Contractor Obligations
    Every contractor shall obtain proper licensing within 30 days of commencing 
    business operations. The contractor must maintain liability insurance in an 
    amount not less than $1,000,000. Contractors are required to provide written 
    estimates before beginning work.
    
    Section 3: Owner Rights
    The owner may inspect the work at any reasonable time. The owner shall make 
    payments within 15 days of receiving a proper invoice.
    
    Section 4: Penalties
    Violation of Section 2 shall result in a fine of not less than $5,000 and 
    not more than $25,000. The contractor may be subject to license suspension 
    for repeated violations. See also Section 10 of the State Licensing Code.
    
    Section 5: Dispute Resolution
    Any dispute arising under this statute shall be resolved through arbitration 
    as set forth in Smith v. Jones, 123 F.3d 456 (9th Cir. 2020).
    """
    
    print("=" * 80)
    print("LegalBot - Legal Document Analysis")
    print("=" * 80)
    print()
    
    # Initialize LegalBot
    print("Initializing LegalBot...")
    bot = LegalBot()
    print(f"Pipeline configured with {len(bot.pipeline)} agents:")
    for i, agent in enumerate(bot.pipeline, 1):
        print(f"  {i}. {agent.name}")
    print()
    
    # Analyze the document
    print("Analyzing legal document...")
    print("-" * 80)
    
    result = bot.analyze(
        text=sample_statute,
        jurisdiction="State",
        document_type="Statute"
    )
    
    print()
    
    # Check results
    if result["success"]:
        print("✓ Analysis completed successfully!")
        print()
        
        # Display summary
        print("Summary:")
        print("-" * 80)
        summary = result.get("summary", {})
        print(f"  Total Sections: {summary.get('total_sections', 0)}")
        print(f"  Obligations: {summary.get('total_obligations', 0)}")
        print(f"  Deadlines: {summary.get('total_deadlines', 0)}")
        print(f"  Penalties: {summary.get('total_penalties', 0)}")
        print(f"  Cross-References: {summary.get('total_cross_references', 0)}")
        print(f"  Case Citations: {summary.get('total_case_citations', 0)}")
        print()
        
        # Display pipeline status
        print("Pipeline Status:")
        print("-" * 80)
        for result_info in result.get("pipeline_results", []):
            status = "✓" if result_info["success"] else "✗"
            print(f"  {status} {result_info['agent']}")
        print()
        
        # Save report
        report = result.get("report", "")
        output_file = "legal_analysis_report.md"
        with open(output_file, "w") as f:
            f.write(report)
        
        print(f"Full report saved to: {output_file}")
        print()
        
        # Display sample of report
        print("Report Preview:")
        print("=" * 80)
        lines = report.split("\n")
        for line in lines[:30]:  # Show first 30 lines
            print(line)
        if len(lines) > 30:
            print(f"\n... ({len(lines) - 30} more lines)")
        print("=" * 80)
        
    else:
        print("✗ Analysis failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Stage: {result.get('stage', 'Unknown stage')}")
        print()
        
        # Display what completed
        print("Pipeline Status:")
        print("-" * 80)
        for result_info in result.get("pipeline_results", []):
            status = "✓" if result_info["success"] else "✗"
            error_msg = f" - {result_info.get('error', '')}" if result_info.get('error') else ""
            print(f"  {status} {result_info['agent']}{error_msg}")


if __name__ == "__main__":
    main()
