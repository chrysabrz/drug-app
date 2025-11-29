# Drug Compatibility & 3D Printing Assessment Tool

A comprehensive Streamlit application for analyzing drug interactions, dosing schedules, and properties for 3D printing compatibility assessment.

## Features

- **Drug Compatibility Check**: Analyze two drugs for interactions, dosing compatibility, and 3D printing feasibility
- **Single Drug Information**: View detailed information about individual drugs
- **Database Search**: Search and browse the comprehensive drug database
- **Category-Based Selection**: Select drugs by therapeutic category
- **AI Drug Agent**: Get AI-powered answers about drug compatibility for 3D printing applications

## Requirements

- Python 3.7+
- Streamlit
- BeautifulSoup4
- OpenAI API key (for AI features)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

```bash
streamlit run app.py
```

## Deployment on Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Environment**: Python 3

### Environment Variables

For AI features, set the OpenAI API key in Render's environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (optional, only needed for AI tab)

Note: The app will work without the OpenAI API key, but the AI Drug Agent tab will not function.

## File Structure

```
drug_compatibility_app_deploy/
├── app.py                              # Main Streamlit application
├── comprehensive_drug_database.json     # Drug database
├── OpenFDAfull.json                    # OpenFDA dosing data (optional)
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
└── render.yaml                         # Render deployment configuration
```

## Database Files

- `comprehensive_drug_database.json`: Main drug database with interactions, properties, and dosing information
- `OpenFDAfull.json`: Additional dosing information from OpenFDA (optional but recommended)

## Usage

1. **Check Compatibility**: Select two drugs to analyze their compatibility for 3D printing
2. **Single Drug Info**: Search for a drug to view detailed information
3. **Search Database**: Browse and search the entire drug database
4. **Category Selection**: Select drugs by therapeutic category
5. **AI Agent**: Ask questions about drug compatibility for 3D printing

## Important Notes

- This tool is for **3D printing compatibility assessment**, not medical advice
- All findings require expert evaluation before any clinical decisions
- The AI features require an OpenAI API key

## License

[Add your license here]

