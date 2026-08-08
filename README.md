⚡MiraAi: Auto-Designer

MiraAi is an autonomous, multi-agent workflow designed to streamline electrical engineering
tasks. Powered by CrewAI and Google Gemini, it acts as a virtual engineering team, automatically
calculating residential electrical loads and drafting code-compliant Single-Line Diagrams (SLDs) for
grid-tie solar systems.

View the Live Web App Here: https://solar-engineering-ai.streamlit.app

🛠️How it Works

MiraAi utilizes an Agentic Workflow rather than a traditional linear script. The application
coordinates two distinct AI agents that pass data to one another sequentially:
1. The Load Analyst: Takes raw user input (lighting, HVAC, convenience loads, etc.), parses the
consumption data, and generates a structured, NEC-compliant load schedule.
2. The System Designer: Receives the schedule from the Analyst and uses it to draft precise
component specifications (breaker sizing, wire gauge) and a conceptual SLD layout for a
target kW solar system.

🚀Technology Stack

Frontend / UI: Streamlit
Orchestration Framework: CrewAI
LLM Provider: Google Gemini (via langchain-google-genai )
Language: Python 3.12

💻Local Installation & Setup

If you want to run this application locally on your own machine, follow these steps:
1. Clone the repository
git clone https://github.com/your-username/mira-ai-app.git
cd mira-ai-app

2. Set up a virtual environment (Recommended)
python3.12 -m venv .venv
source .venv/bin/activate # On Windows use: .venv\Scripts\activate

3. Install the dependencies
pip install -r requirements.txt

4. Set your API Key The application requires a free Google Gemini API key. You can get one from
Google AI Studio. Create a file named .streamlit/secrets.toml in your project root and add
your key:
GEMINI_API_KEY = "your-actual-api-key-here"

5. Run the application
streamlit run app.py

📈Future Roadmap

[ ] Implement CrewAI Custom Tools to offload exact mathematical calculations (e.g., voltage
drop percentages) from the LLM to hardcoded Python functions for guaranteed accuracy.

[ ] Add PDF export functionality for the final engineering deliverables.

[ ] Expand the workflow to include a third "Code Compliance Reviewer" agent.
Built as a showcase for integrating Multi-Agent Systems into practical B2B workflows.
