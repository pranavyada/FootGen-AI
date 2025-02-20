# FootbGen AI

An AI-powered system that enables natural language queries for football match data from the English Premier League and Spanish La Liga.

## Overview
This system allows users to query football match data using natural language through a chat interface. It supports both English Premier League and La Liga data, providing match statistics, results, and historical information.

## Prerequisites

Before running the application, you need:

1. Python 3.8 or higher
2. PostgreSQL database
3. OpenAI API key
4. Git for cloning the repository

## Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/pranavyada/FootGen-AI.git
cd football-query-system
```

### 2. Set Up Python Environment

Create virtual environment
```bash
python -m venv venv
```

Activate virtual environment
For Windows:
```bash
venv\Scripts\activate
```
For macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Database Setup

1. Install PostgreSQL if not already installed
2. Create a new database in PostgreSQL
3. Create two tables:
   - `epl_data` for Premier League matches
   - `laliga_data` for La Liga matches

### 5. Environment Configuration

Create a `.env` file in the root directory with:
```python
OPENAI_API_KEY=your_openai_api_key
HOSTNAME=localhost
DATABASE=postgres
USER=postgres
PASSWORD=your_database_password
PORT=5432
```

## Running the Application

1. Ensure your virtual environment is activated
2. Start the application:
```bash
streamlit run app.py
```
3. Access the web interface at `http://localhost:8501`

## Example Queries

Try these sample queries:

For EPL:
- "Show all matches between Manchester United and Liverpool"
- "What was the score when Arsenal played Chelsea?"
- "How many goals did Tottenham score at home?"

For La Liga:
- "Show Barcelona vs Real Madrid matches"
- "What was Atletico Madrid's home record?"
- "Display matches where Sevilla won by more than 2 goals"

## Project Structure
├── app.py # Main Streamlit application\
├── agents.py # Query routing agents\
├── helper_functions.py # Utility functions\
├── merge_csvs.py # Data preprocessing\
├── requirements.txt # Dependencies\
└── data/ # Data directory\
      ├── EPL/ # EPL data files\
      ├── LaLiga/ # La Liga data files\
      └── csv_data/ # Processed files\

## Troubleshooting

Common issues and solutions:

1. Database Connection Issues:
   - Verify PostgreSQL is running
   - Check credentials in `.env` file
   - Ensure database and tables exist

2. OpenAI API Issues:
   - Verify API key is correct
   - Check internet connection
   - Confirm API quota

3. Data Import Problems:
   - Verify CSV files are in correct directories
   - Check file permissions
   - Ensure CSV format matches schema

## Support

For issues or questions:
1. Check the troubleshooting section
2. Contact Us: 
rokade.p@northeastern.edu
yada.p@northeastern.edu




