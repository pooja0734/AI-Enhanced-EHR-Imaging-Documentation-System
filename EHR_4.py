"""
Milestone 4: Integration and Deployment
This script writes a markdown file and (optionally) a PDF for the milestone content.
"""

milestone_content = '# Milestone 4: Integration and Deployment\n\nObjective:\nDeploy and integrate the enhanced GenAI-powered EHR features into real-world clinical environments to support seamless healthcare operations.\n\nTasks:\n\n1. Model Deployment:\n   - Deploy trained GenAI models into real-time clinical workflows for automated note generation and image interpretation.\n   - Ensure model hosting and API integration support scalability and low-latency performance.\n   - Add monitoring & logging for model performance (latency, throughput, error rates) and data drift detection.\n\n2. System Integration:\n   - Integrate GenAI features with existing hospital EHR systems for unified access to image processing and clinical documentation tools.\n   - Establish secure data pipelines ensuring compliance with HIPAA and applicable healthcare data protection standards (e.g., encryption in transit & at rest, access controls, audit logs).\n   - Implement authentication & authorization (e.g., OAuth2, SSO) and follow hospital IT policies for network segmentation and data access.\n   - Define rollback and fail-safe procedures for clinical workflows to ensure patient safety if integration issues happen.\n\n3. Staff Onboarding and Training:\n   - Conduct onboarding sessions and practical workshops for medical staff to familiarize them with the new tools.\n   - Develop user guides, quick-start manuals, and short video demos for common tasks to improve adoption and reduce errors.\n   - Collect feedback and iterate on UI/UX and model outputs to align the tools with clinical workflows and clinician preferences.\n\nDeliverables & Acceptance Criteria:\n- Deployed model endpoints reachable from the clinical network with documented API specs.\n- Successful end-to-end integration test (image -> model -> EHR entry) with example cases.\n- Security & compliance checklist signed-off by hospital IT/security teams.\n- At least two onboarding sessions completed and supporting documentation delivered.\n- A short runbook for operations teams describing monitoring, incident response, and rollback steps.\n'

def write_md(path="Milestone4_Integration_Deployment.md"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(milestone_content)
    print(f"Wrote markdown to {path}")

def write_pdf(path="Milestone4_Integration_Deployment.pdf"):
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception as e:
        print("reportlab not available; skipping PDF generation:", e)
        return
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    story = [Paragraph(line, styles["Normal"]) for line in milestone_content.split("\n")]
    doc.build(story)
    print(f"Wrote PDF to {path}")

if __name__ == "__main__":
    write_md()
    write_pdf()
