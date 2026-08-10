import os
import re
import datetime
import streamlit as st
from io import BytesIO
from crewai import Agent, Task, Crew, Process, LLM
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def clean_text_for_pdf(text):
    """
    Cleans AI output to ensure perfect rendering in the PDF.
    """
    # 1. Remove math block markers
    text = text.replace("$$", "")
    text = text.replace("$", "")
    
    # 2. Fix common LaTeX symbols
    text = text.replace("\\times", "x")
    text = text.replace("^{\\circ}\\text{C}", "°C")
    text = text.replace("^{\\circ} C", "°C")
    text = text.replace("\\circ", "°")
    text = text.replace("\\Delta", "Δ")
    text = text.replace("\\_", "_")
    
    # 3. Extract text from \text{...} blocks
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    
    # 4. Clean up fractions \frac{a}{b} to a/b
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'\1/\2', text)
    
    # 5. Clean up bolding asterisks for plain text PDF
    text = text.replace("**", "")
    text = text.replace("### ", "")
    text = text.replace("## ", "")
    text = text.replace("# ", "")
    
    # 6. Sanitize for ReportLab (replace problematic characters)
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    
    return text

def generate_pdf(text):
    """Converts the cleaned text into a bulletproof PDF using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Create a custom style for the report body
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14, # Line spacing
        spaceAfter=12
    )
    
    # Create a title style
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        spaceAfter=20
    )

    Story = []
    
    # Add a title
    Story.append(Paragraph("MiraAi Engineering Report", title_style))
    
    # Split the text by double newlines to create separate paragraphs
    paragraphs = text.split('\n\n')
    
    for p in paragraphs:
        # Handle single line breaks within paragraphs
        p = p.replace('\n', '<br/>')
        if p.strip():
            Story.append(Paragraph(p, body_style))
            
    doc.build(Story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

class MiraAi:
    """
    MiraAi: An autonomous multi-agent workflow for electrical system design.
    """
    def __init__(self, api_key):
        self.gemini_llm = LLM(
            model="gemini/gemini-3.5-flash",
            api_key=api_key,
            temperature=0.2 
        )
        
        self.load_analyst = self._create_load_analyst()
        self.system_designer = self._create_system_designer()

    def _create_load_analyst(self):
        return Agent(
            role='Senior Electrical Load Analyst',
            goal='Analyze raw consumption data and generate a comprehensive, code-compliant load schedule.',
            backstory=(
                'You are an expert in electrical illumination and power distribution. '
                'You specialize in calculating accurate load requirements, breaking down lighting, '
                'motor, and appliance loads into a structured schedule based on the NEC.'
            ),
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    def _create_system_designer(self):
        return Agent(
            role='Grid-Tie Solar System Designer',
            goal='Design system specifications and single line diagram parameters for a Grid-Tie Solar System.',
            backstory=(
                'You are a veteran electrical engineer. You design optimal grid-tie solar setups, '
                'ensuring proper inverter sizing, protective relays, transformer considerations, and '
                'safe grid synchronization.'
            ),
            llm=self.gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    def run_workflow(self, target_kw, project_details):
        analyze_load_task = Task(
            description=(
                f'Analyze the following project details: {project_details}. '
                'Calculate the estimated daily consumption and create a detailed load schedule. '
                'Apply the NEC 125% rule for continuous loads where appropriate. '
                'CRITICAL: DO NOT use LaTeX formatting, dollar signs ($), or backslashes (\\). Use standard text and standard symbols like "x" for multiplication.'
            ),
            agent=self.load_analyst,
            expected_output='A structured load schedule showing total wattage, ampacity, and daily consumption in plain markdown.'
        )

        design_system_task = Task(
            description=(
                f'Using the load schedule provided, draft the component specifications '
                f'for a {target_kw}kW Grid-Tie Solar System. Include a conceptual node list for the single line diagram '
                '(e.g., PV Array -> DC Disconnect -> Inverter -> AC Breaker -> Main Panel). '
                'Check Main Panelboard Busbar & Main Breaker sizing compliance under NEC 705.12(B) (120% rule). '
                'CRITICAL: DO NOT use LaTeX formatting, dollar signs ($), or backslashes (\\). Use standard text and standard symbols like "x" for multiplication.'
            ),
            agent=self.system_designer,
            expected_output='A detailed system specification sheet and single line diagram layout in plain markdown.'
        )

        mira_crew = Crew(
            agents=[self.load_analyst, self.system_designer],
            tasks=[analyze_load_task, design_system_task],
            process=Process.sequential 
        )

        return mira_crew.kickoff()

def main():
    st.set_page_config(page_title="MiraAi | Free Solar Load Schedule & SLD Generator", page_icon="⚡", layout="centered")

    if 'history' not in st.session_state:
        st.session_state.history = []

    st.title("⚡ MiraAi: Auto-Designer")
    st.markdown("Generate instant, NEC-compliant load schedules and single-line diagrams (SLD) for grid-tie solar systems. Input your residential electrical loads, and our AI engineering agent will automatically calculate breaker sizing, voltage drops, and system specifications in seconds.")

    with st.sidebar:
        st.header("⚙️ Configuration")
        st.success("App is running in production mode.")
        st.markdown("---")
        st.markdown("### System Constraints")
        target_kw = st.number_input("Target PV System Size (kW)", min_value=1.0, max_value=50.0, value=5.5, step=0.5)
        
        st.markdown("---")
        st.header("🕰️ Generation History")
        if not st.session_state.history:
            st.info("Your past generated reports will appear here.")
        else:
            for idx, record in enumerate(reversed(st.session_state.history)):
                with st.expander(f"Report: {record['timestamp']}"):
                    st.caption(f"Size: {record['kw']} kW")
                    st.text(record['text'][:150] + "...") 
                    st.download_button(
                        label="📥 Download PDF",
                        data=record['pdf_bytes'],
                        file_name=f"MiraAi_Report_{record['timestamp'].replace(':', '-')}.pdf",
                        mime="application/pdf",
                        key=f"history_dl_{idx}"
                    )

    with st.form("project_form"):
        st.subheader("📋 Electrical Load Inputs")
        
        col1, col2 = st.columns(2)
        with col1:
            lighting = st.text_area("Lighting & Outlets", placeholder="12x 15W LED fixtures, 8x 200W convenience outlets", height=100)
            appliances = st.text_area("Standard Appliances", placeholder="1x Refrigerator (300W), 1x Microwave, TV", height=100)
        
        with col2:
            electric_range = st.text_area("Electric Range / Cooking (kW)", placeholder="1x 3.5kW Electric Range", height=100)
            hvac_motors = st.text_area("HVAC / Heavy Motors", placeholder="1x 1.5HP Air Conditioning Unit, 1x Water Pump", height=100)

        additional_notes = st.text_input("Additional Goal/Notes", placeholder="Offset daytime usage with grid-tie solar.")

        submitted = st.form_submit_button("Generate Engineering Docs", type="primary")

    if submitted:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.error("⚠️ Server Error: API Key not found in Secrets. Please contact the administrator.")
            return

        lighting_input = lighting if lighting.strip() else "12x 15W LED fixtures, 8x 200W convenience outlets"
        appliances_input = appliances if appliances.strip() else "1x Refrigerator (300W), 1x Microwave, TV"
        range_input = electric_range if electric_range.strip() else "1x 3.5kW Electric Range"
        hvac_input = hvac_motors if hvac_motors.strip() else "1x 1.5HP Air Conditioning Unit, 1x Water Pump"
        notes_input = additional_notes if additional_notes.strip() else "Offset daytime usage with grid-tie solar."

        project_scope = (
            f"Lighting & Outlets: {lighting_input}. "
            f"Electric Range/Cooking: {range_input}. "
            f"Standard Appliances: {appliances_input}. "
            f"HVAC/Motors: {hvac_input}. "
            f"Goal: {notes_input}"
        )

        st.info("🤖 MiraAi is analyzing the loads and drafting the system...")
        
        # Display a loading spinner while the AI works
        with st.spinner('Agents are collaborating... This usually takes 15-30 seconds.'):
            try:
                # Initialize and run the AI
                mira = MiraAi(api_key=api_key)
                result = mira.run_workflow(target_kw, project_scope)
                
                # Extract raw text from CrewOutput
                final_text = result.raw

                # SAVE TO SESSION STATE SO IT SURVIVES BUTTON CLICKS!
                st.session_state['current_report'] = final_text
                
                # Clean text specifically for the PDF generator
                cleaned_text = clean_text_for_pdf(final_text)
                
                # Generate bulletproof PDF
                pdf_bytes = generate_pdf(cleaned_text)
                st.session_state['current_pdf'] = pdf_bytes
                
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.history.append({
                    "timestamp": timestamp,
                    "kw": target_kw,
                    "text": cleaned_text,
                    "pdf_bytes": pdf_bytes
                })
                
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")

    # Display the report OUTSIDE the 'if submitted' block
    # This ensures it stays on screen even after clicking Download
    if 'current_report' in st.session_state:
        st.success("✅ Design Complete!")
        st.markdown("---")
        st.markdown("### 📄 Final Engineering Deliverable")
        
        # Display beautiful markdown on the webpage
        st.markdown(st.session_state['current_report'], unsafe_allow_html=True)
        
        st.markdown("---")
        st.download_button(
            label="📥 Download Engineering Report (PDF)",
            data=st.session_state['current_pdf'],
            file_name=f"MiraAi_Solar_SLD_Schedule.pdf",
            mime="application/pdf",
            type="primary"
        )

if __name__ == "__main__":
    main()
