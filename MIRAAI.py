import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM


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
                'motor, and appliance loads into a structured schedule.'
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
                'Calculate the estimated daily consumption and create a detailed load schedule.'
            ),
            agent=self.load_analyst,
            expected_output='A structured load schedule showing total wattage, ampacity, and daily consumption.'
        )

        design_system_task = Task(
            description=(
                f'Using the load schedule provided, draft the component specifications '
                f'for a {target_kw}kW Grid-Tie Solar System. Include a conceptual node list for the single line diagram '
                '(e.g., PV Array -> DC Disconnect -> Inverter -> AC Breaker -> Main Panel).'
            ),
            agent=self.system_designer,
            expected_output='A detailed system specification sheet and single line diagram layout.'
        )

        mira_crew = Crew(
            agents=[self.load_analyst, self.system_designer],
            tasks=[analyze_load_task, design_system_task],
            process=Process.sequential
        )

        return mira_crew.kickoff()


def main():
  
    st.set_page_config(page_title="MiraAi | Free Solar Load Schedule & SLD Generator", page_icon="⚡", layout="centered")

    st.title("⚡ MiraAi: Auto-Designer")
    st.markdown("Generate instant, NEC-compliant load schedules and single-line diagrams (SLD) for grid-tie solar systems. Input your residential electrical loads, and our AI engineering agent will automatically calculate breaker sizing, voltage drops, and system specifications in seconds.")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.success("App is running in production mode.")
        st.markdown("---")
        st.markdown("### System Constraints")
        target_kw = st.number_input("Target System Size (kW)", min_value=1.0, max_value=50.0, value=5.5, step=0.5)

  
    with st.form("project_form"):
        st.subheader("📋 Project Specifications")

        col1, col2 = st.columns(2)
        with col1:
            lighting = st.text_area("Lighting Load", value="12x 15W LED fixtures", height=100)
            appliances = st.text_area("Standard Appliances", value="1x Refrigerator (300W), 1x Microwave", height=100)

        with col2:
            outlets = st.text_area("Plug/Convenience Loads", value="8x 200W convenience outlets", height=100)
            hvac = st.text_area("HVAC / Motors", value="1x 1.5HP Air Conditioning Unit", height=100)

        additional_notes = st.text_input("Additional Goal/Notes", value="Offset daytime usage with grid-tie solar.")

      
        submitted = st.form_submit_button("Generate Engineering Docs", type="primary")

    if submitted:
      
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.error("⚠️ Server Error: API Key not found in Secrets. Please contact the administrator.")
            return

      
        project_scope = (
            f"Lighting: {lighting}. "
            f"Plugging: {outlets}. "
            f"Appliances: {appliances}. "
            f"HVAC/Motors: {hvac}. "
            f"Goal: {additional_notes}"
        )

        st.info("🤖 MiraAi is analyzing the loads and drafting the system...")

       
        with st.spinner('Agents are collaborating... This usually takes 15-30 seconds.'):
            try:
            
                mira = MiraAi(api_key=api_key)
                result = mira.run_workflow(target_kw, project_scope)

                st.success("✅ Design Complete!")

               
                st.markdown("---")
                st.markdown("### 📄 Final Engineering Deliverable")
                st.markdown(result)

            except Exception as e:
                st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
