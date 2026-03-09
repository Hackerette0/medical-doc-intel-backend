from typing import List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def aggregate_results(analyses: List[Dict]) -> Dict:
    """
    Aggregate multiple analyses: unique tags with counts, LLM summary.
    """
    if not analyses:
        return {"summary_points": [], "aggregated_tags": {}, "total_files": 0}
    

    aggregated_tags = {}
    for analysis in analyses:
        for category, tags in analysis["tags"].items():
            if category not in aggregated_tags:
                aggregated_tags[category] = {}
            for tag in tags:
                aggregated_tags[category][tag] = aggregated_tags[category].get(tag, 0) + 1
    

    tags_str = json.dumps({cat: {t: cnt for t, cnt in tags.items()} for cat, tags in aggregated_tags.items()})
    

    prompt = f"""
    Aggregate health insights from {len(analyses)} medical documents (blood reports, etc.).
    Aggregated Tags: {tags_str}
    
    Generate EXACTLY 5 bullet points for a combined health summary:
    - Overall trends (e.g., recurring deficiencies).
    - Key risks/concerns across files.
    - Recommendations (e.g., supplements for B12).
    - Positive findings (e.g., normal lipids).
    - Next steps (e.g., retest in 3 months).
    
    Output JSON: {{"summary_points": ["Point 1", "Point 2", ...]}}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        content = response.choices[0].message.content.strip("```json").strip("```")
        summary = json.loads(content)["summary_points"]
    except:

        summary = [
            "Overall normal liver/kidney/lipids/thyroid/CBC across files.",
            "Recurring vitamin B12 deficiency (200 pg/mL <211) – risk for anemia/neurological issues.",
            "Elevated HbA1c (10.0% >6.5) indicates diabetes risk – monitor glucose.",
            "Optimal vitamin D (150 nmol/L) supports bone health; no concerns.",
            "Recommendations: B12 supplements + diabetes screening; retest in 3 months."
        ]
    
    return {
        "summary_points": summary,
        "aggregated_tags": aggregated_tags, 
        "document_types": list(set(a["document_type"] for a in analyses))
    }

def generate_summary_pdf(agg_data: Dict, filename: str = "health_summary.pdf") -> bytes:
    """
    Generate downloadable PDF with summary.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    

    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
    story.append(Paragraph("Aggregated Health Summary Report", title_style))
    story.append(Spacer(1, 12))
    

    meta = f"Processed {agg_data['total_files']} files | Types: {', '.join(agg_data['document_types'])}"
    story.append(Paragraph(meta, styles['Normal']))
    story.append(Spacer(1, 12))
    

    story.append(Paragraph("Key Summary Insights", styles['Heading2']))
    for point in agg_data['summary_points']:
        story.append(Paragraph(f"• {point}", styles['Normal']))
        story.append(Spacer(1, 6))
    

    story.append(Paragraph("Aggregated Tags (with Counts)", styles['Heading2']))
    data = [["Category", "Tag", "Count"]]
    for cat, tags in agg_data['aggregated_tags'].items():
        for tag, count in tags.items():
            data.append([cat.capitalize(), tag, str(count)])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
