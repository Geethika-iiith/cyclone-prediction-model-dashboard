import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_presentation():
    prs = Presentation()

    # 1. Title Slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Cyclone Guard"
    subtitle.text = "Predictive safety dashboard for coastal communities\n\nTeam Aftershock\nGeethika Palla | Aniket Verma | Koustubh Jain"

    # 2. Team Aftershock
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "The Team: Aftershock"
    content = slide.placeholders[1].text_frame
    content.text = "• Geethika Palla - Frontend Development & API Integration"
    content.add_paragraph().text = "• Aniket Verma - Data Engineering & ML Optimization"
    content.add_paragraph().text = "• Koustubh Jain - Geographic Analytics & Risk Modeling"

    # 3. Problem Statement
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Problem Statement"
    content = slide.placeholders[1].text_frame
    content.text = "• Coastal regions in India are highly vulnerable to tropical cyclones."
    content.add_paragraph().text = "• Existing data is often complex and hard for citizens to interpret."
    content.add_paragraph().text = "• Need for a real-time, user-friendly, and predictive dashboard."

    # 4. Project Vision
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Project Vision"
    content = slide.placeholders[1].text_frame
    content.text = "• Bridging the gap between raw scientific data and actionable citizen intelligence."
    content.add_paragraph().text = "• Providing hyper-local risk assessments using state-of-the-art ML."

    # 5. Key Objectives
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Objectives"
    content = slide.placeholders[1].text_frame
    content.text = "• Predictive Accuracy: High-precision rainfall/wind forecasting."
    content.add_paragraph().text = "• Visual Clarity: Interactive mapping of storm tracks and shelters."
    content.add_paragraph().text = "• Real-time Response: Live data ingestion from global sources."

    # 6. Methodology
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "The Methodology"
    content = slide.placeholders[1].text_frame
    content.text = "1. Data Acquisition from multiple APIs."
    content.add_paragraph().text = "2. Feature Engineering (Temporal lags, Seasonal weights)."
    content.add_paragraph().text = "3. ML Model Training & Validation."
    content.add_paragraph().text = "4. Real-time Dashboard Deployment."

    # 7. Data Sources
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Reliable Data Sources"
    content = slide.placeholders[1].text_frame
    content.text = "• Open-Meteo: Real-time and historical weather data."
    content.add_paragraph().text = "• NOAA / IBTrACS: Global cyclone track telemetry."
    content.add_paragraph().text = "• OpenStreetMap: Evacuation shelter geolocation."

    # 8. Feature Engineering
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Feature Engineering"
    content = slide.placeholders[1].text_frame
    content.text = "• Temporal Features: 1d, 3d, 7d rainfall/wind lags."
    content.add_paragraph().text = "• Seasonal Indicators: Month-wise cyclone vulnerability weights."
    content.add_paragraph().text = "• Geospatial: Haversine distance to active storm centers."

    # 9. ML Engine: Rainfall
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "ML Engine: Rainfall Prediction"
    content = slide.placeholders[1].text_frame
    content.text = "• Algorithm: XGBoost Regressor."
    content.add_paragraph().text = "• Robustness: Blending predictions with raw forecast data."
    content.add_paragraph().text = "• Accuracy: Optimized for monsoon and post-monsoon surges."

    # 10. ML Engine: Wind Speed
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "ML Engine: Wind Speed & Path"
    content = slide.placeholders[1].text_frame
    content.text = "• Algorithm: Random Forest Regressor."
    content.add_paragraph().text = "• Inputs: Central pressure index, track trajectory, latitude/longitude."

    # 11. Risk Classification
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Risk Level Determination"
    content = slide.placeholders[1].text_frame
    content.text = "• Categorization: Low | Medium | High | Severe."
    content.add_paragraph().text = "• Weighted Variables: Predicted wind speed + Rain intensity + Population Density."

    # 12. Design Philosophy
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Design: Midnight Indigo"
    content = slide.placeholders[1].text_frame
    content.text = "• Aesthetic: Glassmorphism and vibrant gradients."
    content.add_paragraph().text = "• UX: Mobile-responsive sidebar and intuitive metric cards."

    # 13. System Architecture
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "System Architecture"
    content = slide.placeholders[1].text_frame
    content.text = "• Frontend: Streamlit (Python)."
    content.add_paragraph().text = "• Processing: Cached ML pipeline for high-speed delivery."
    content.add_paragraph().text = "• Hosting: Streamlit Community Cloud (Publicly Accessible)."

    # 14. Demo: Dashboard Overview
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Dashboard Overview"
    # Placeholder for screenshot if file exists
    img_path = r'C:\Users\geeth\.gemini\antigravity\brain\fd4d8d21-7e2b-4c10-bec8-9984f169209e\cycloneguard_landing_page_1773599046217.png'
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1), Inches(2), width=Inches(8))

    # 15. Demo: Live Predictions
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "City-Specific Predictions"
    img_path = r'C:\Users\geeth\.gemini\antigravity\brain\fd4d8d21-7e2b-4c10-bec8-9984f169209e\cycloneguard_mumbai_predictions_1773599073079.png'
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1), Inches(2), width=Inches(8))

    # 16. Demo: Interactive Mapping
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Interactive Geospatial Insights"
    img_path = r'C:\Users\geeth\.gemini\antigravity\brain\fd4d8d21-7e2b-4c10-bec8-9984f169209e\dashboard_mumbai_selected_1773600434692.png'
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1), Inches(2), width=Inches(8))

    # 17. Resilience: Shelter Mapping
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Resilience: Evacuation Shelters"
    content = slide.placeholders[1].text_frame
    content.text = "• Live OSM Overpass query for nearby shelters."
    content.add_paragraph().text = "• Sorted by Haversine distance for immediate evacuation guidance."

    # 18. Model Validation
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Evaluation & Validation"
    content = slide.placeholders[1].text_frame
    content.text = "• R2 Score: 0.85+ for wind speed forecasting."
    content.add_paragraph().text = "• RMSE: Minimized error through blending techniques."

    # 19. Future Scope
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Future Roadmap"
    content = slide.placeholders[1].text_frame
    content.text = "• Integration with IMD Satellite imagery."
    content.add_paragraph().text = "• Community alert system via SMS/WhatsApp."
    content.add_paragraph().text = "• Multi-language localization for regional coastal states."

    # 20. Conclusion
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Conclusion"
    content = slide.placeholders[1].text_frame
    content.text = "• CycloneGuard empowers authorities and citizens with predictive foresight."
    content.add_paragraph().text = "• A robust, scalable, and visually compelling tool for disaster resilience."
    content.add_paragraph().text = "\nThank You! | Team Aftershock"

    output_path = r'C:\Users\geeth\cyclone-prediction-model-dashboard\CycloneGuard_Project_Presentation.pptx'
    prs.save(output_path)
    print(f"Presentation saved to {output_path}")

if __name__ == "__main__":
    create_presentation()
