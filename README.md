# FootGen AI

An AI-powered system that enables natural language queries for football match data from the English Premier League and Spanish La Liga.

## Overview
This system allows users to query football match data using natural language through a chat interface. It supports both English Premier League and La Liga data, providing match statistics, results, and historical information. Link to our data https://www.football-data.co.uk/data.php

## System Architecture
![System Architecture](Architecture-diagram.jpg)

## Methodology
FootGen AI integrates a modular architecture combining natural language understanding with structured football data. The pipeline includes:

- **Data Collection & ETL:** Historical match data for EPL and La Liga was scraped from football-data.co.uk and cleaned before being loaded into a PostgreSQL database using Python-based ETL scripts.

- **Conversational Frontend:** Users interact through a Streamlit app that uses OpenAI embeddings and ChromaDB to maintain contextual memory for seamless multi-turn dialogue.

- **Multi-Agent System:** An OpenAI Swarm-based architecture routes queries through a manager agent to league-specific agents, ensuring domain-aware responses.

- **NL2SQL Querying:** Natural language queries are converted into SQL using GPT-3.5-turbo with few-shot prompting, and results are translated into human-readable responses.

This architecture allows users to ask complex football questions without needing to know SQL.



## Project Structure
- `app.py`: Main Streamlit application
- `agents.py`: Query routing agents
- `helper_functions.py`: Utility functions
- `merge_csvs.py`: Data preprocessing
- `requirements.txt`: Dependencies
- `data/`: Data directory
  - `EPL/`: EPL data files
  - `LaLiga/`: La Liga data files
  - `csv_data/`: Processed files

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
3. Create two tables with the following columns:
   - `epl_data` for Premier League matches
      - columns (datatype=text): Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,Referee,HS,AS,HST,AST,HF,AF,HC,AC,HY,AY,HR,AR,B365H,B365D,B365A,Season 
   - `laliga_data` for La Liga matches
      - columns (datatype=text): Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,HS,AS,HST,AST,HF,AF,HC,AC,HY,AY,HR,AR,B365H,B365D,B365A,Season 

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
- "What was the score when Arsenal played Chelsea in the 2023-2024 season?"
- "Who was the referee for the match between Arsenal and Chelsea in the 2023-2024 season?"

For La Liga:
- "How many red cards did Barcelona get in 2009-2010 season?"
- "How many away goals did real madrid score in 2018-2019 season?"
- "How many fouls were committed in 2019-2020 season in LaLiga?"

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

## Demo
Click the thumbnail below to be redirected to the full demo video on YouTube.
[![Watch the demo](video_thumbnail.png)](https://youtu.be/aWG0FntlFfE)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Contact Us: 
rokade.p@northeastern.edu
yada.p@northeastern.edu




