from openai import OpenAI
import os
import psycopg2
import logging
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Generate timestamp for unique filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'logs/run_{timestamp}.log'

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    filemode='w',  # 'w' mode creates a new file, 'a' would append
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv('HOSTNAME'),
        database=os.getenv('DATABASE'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        port=os.getenv('PORT')
    )


def execute_sql_query(sql_query: str) -> pd.DataFrame:
    """
    Executes the given SQL query using PostgreSQL and returns the results as a DataFrame.
    """
    if not sql_query.strip().lower().startswith("select"):
        logging.critical("Only SELECT queries are allowed for security reasons.")
        return pd.DataFrame()

    try:
        # Create connection
        conn = get_db_connection()
        
        # Execute query and fetch into DataFrame
        df = pd.read_sql_query(sql_query, conn)
        
        logging.info(f"Retrieved {len(df)} rows from database")
        return df
        
    except Exception as e:
        logging.error(f"Error executing SQL query: {str(e)}")
        return pd.DataFrame()
        
    finally:
        if conn:
            conn.close()


def clean_sql_query(markdown_query: str) -> str:
    """Clean the SQL query from markdown formatting"""
    lines = markdown_query.strip().split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith('```') or line.strip() == 'sql':
            continue
        cleaned_lines.append(line)

    cleaned_query = ' '.join(cleaned_lines).strip()
    cleaned_query = cleaned_query.replace('`', '')

    if not cleaned_query.strip().endswith(';'):
        cleaned_query += ';'

    return cleaned_query


def nl2sql_epl(natural_query: str, openai: OpenAI) -> str:
    """
    Converts a natural language query to an SQL query using OpenAI's GPT model.
    """
    schema_description = """
    Database Schema for football matches:
    Table: epl_data (
        "Div" TEXT,            -- Division 
        "Date" TEXT,           -- Date of the match
        "HomeTeam" TEXT,       -- Home Team
        "AwayTeam" TEXT,       -- Away Team
        "FTHG" TEXT,           -- Full Time Home Team Goals
        "FTAG" TEXT,           -- Full Time Away Team Goals
        "FTR" TEXT,            -- Full Time Result (H=Home Win, D=Draw, A=Away Win)
        "HTHG" TEXT,           -- Half Time Home Team Goals
        "HTAG" TEXT,           -- Half Time Away Team Goals
        "HTR" TEXT,            -- Half Time Result
        "Referee" TEXT,        -- Referee
        "HS" TEXT,             -- Home Team Shots
        "AS" TEXT,             -- Away Team Shots
        "HST" TEXT,            -- Home Team Shots on Target
        "AST" TEXT,            -- Away Team Shots on Target
        "HF" TEXT,             -- Home Team Fouls Committed
        "AF" TEXT,             -- Away Team Fouls Committed
        "HC" TEXT,             -- Home Team Corners
        "AC" TEXT,             -- Away Team Corners
        "HY" TEXT,             -- Home Team Yellow Cards
        "AY" TEXT,             -- Away Team Yellow Cards
        "HR" TEXT,             -- Home Team Red Cards
        "AR" TEXT,             -- Away Team Red Cards
        "B365H" TEXT,          -- Bet365 Home Team Win Odds
        "B365D" TEXT,          -- Bet365 Draw Odds
        "B365A" TEXT,          -- Bet365 Away Team Win Odds
        "Season" TEXT          -- Season (e.g., "2005-2006")
    )

    """

    messages = [
        {"role": "system", "content": """You are an expert SQL developer. Generate valid PostgreSQL SELECT queries based on the user's question about football matches. The generated response should only include the SQL query in markdown format and nothing else.Teams names are as follows:
    "Leicester","Swansea","Man United","Cardiff","Norwich","Ipswich","Liverpool","Crystal Palace","Wigan","Arsenal","Luton","Southampton"
"Watford","Sheffield United","Bolton","Nott'm Forest","Chelsea","Charlton","Middlesbrough","Bournemouth","Burnley","Everton","Hull","West Ham"
"Leeds","Birmingham","Derby","West Brom","Huddersfield","Blackpool","Reading","Fulham","Brentford","Portsmouth","Blackburn","Sunderland"
"Brighton","Newcastle","QPR","Stoke","Man City","Wolves","Tottenham","Aston Villa","Wolves","Tottenham","Aston Villa"

Make sure when you are selecting the teams, you select the exact team name as it is in the database as specified above.

This is incorrect syntax:
SELECT "HomeTeam", "AwayTeam", "FTHG", "FTAG" FROM epl_data WHERE ("HomeTeam" = 'Man United' AND "AwayTeam" = 'Man City' OR "HomeTeam" = 'Man City' AND "AwayTeam" = 'Man United') AND "Season" = '2023-24';

This is CORRECT syntax:
eTeam", "AwayTeam", "FTHG", "FTAG" FROM epl_data WHERE (("HomeTeam" = 'Man United' AND "AwayTeam" = 'Man City') OR ("HomeTeam" = 'Man City' AND "AwayTeam" = 'Man United')) AND "Season" = '2023-2024';
         
    Date column is a string of format DD/MM/YY
         
        ALWAYS USE THE CORRECT SYNTAX
         ADD EXPLICIT TYPE CASTING FROM TEXT DATATYPE FOR AGGREGATE FUNCTIONS
         Example:
         SELECT SUM(CAST("FTHG" AS INTEGER)) AS "TotalGoalsScoredAtHome" 
FROM epl_data 
WHERE "HomeTeam" = 'Tottenham';"""},
        {"role": "system", "content": f"Here is the database schema:\n{schema_description}"},
        {"role": "user", "content": f"Generate a PostgreSQL query for this question: {natural_query}"}
    ]

    try:
        response = openai.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=250
        )
        
        sql_query = response.choices[0].message.content.strip()
        return sql_query
    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        return None


def query_epl(natural_query: str) -> str:
    """
    Convert a natural language query into SQL using OpenAI, execute it via PostgreSQL,
    and generate a natural language response from the results.
    """
    openai = OpenAI(api_key=OPENAI_API_KEY)

    # Step 1: Convert Natural Language to SQL
    sql_query = nl2sql_epl(natural_query, openai)
    if not sql_query:
        logging.error("Failed to generate SQL query.")
        return "Sorry, I couldn't generate a SQL query for your question."
    print(sql_query)

    logging.info("Generated SQL Query")

    cleaned_query = clean_sql_query(sql_query)
    print(cleaned_query)
    logging.info(f"Cleaned SQL Query: {cleaned_query}")

    # Step 2: Execute the SQL Query
    results_df = execute_sql_query(cleaned_query)
    print("\n\nRESULTS DF\n",results_df)
    logging.info(f"Results DataFrame shape: {results_df.shape}")

    if results_df.empty:
        logging.warning("No results found for the given query.")
        return "I couldn't find any matches matching your criteria."

    # Step 3: Generate Natural Language Response
    try:
        results_summary = results_df.to_dict(orient="records")
        results_context = f"The results of the query are:\n{results_summary}"

        response = openai.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant who provides information about football matches. Your task is to summarize the database query results into natural language."},
                {"role": "user", "content": f"Summarize the following football match query results in natural language:\n{results_context}"}
            ],
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=200
        )

        answer = response.choices[0].message.content.strip()
        print("\n\ANSWER\n",answer)
        return answer
    except Exception as e:
        logging.error(f"Error generating natural language answer: {e}")
        return "Sorry, I couldn't generate a response from the query results."
    

def nl2sql_laliga(natural_query: str, openai: OpenAI) -> str:
    """
    Converts a natural language query to an SQL query for LaLiga data using OpenAI's GPT model.
    """
    schema_description = """
    Database Schema for football matches:
    Table: laliga_data (
        "Div" TEXT,            -- Division 
        "Date" TEXT,           -- Date of the match
        "HomeTeam" TEXT,       -- Home Team
        "AwayTeam" TEXT,       -- Away Team
        "FTHG" TEXT,           -- Full Time Home Team Goals
        "FTAG" TEXT,           -- Full Time Away Team Goals
        "FTR" TEXT,            -- Full Time Result (H=Home Win, D=Draw, A=Away Win)
        "HTHG" TEXT,           -- Half Time Home Team Goals
        "HTAG" TEXT,           -- Half Time Away Team Goals
        "HTR" TEXT,            -- Half Time Result
        "Referee" TEXT,        -- Referee
        "HS" TEXT,             -- Home Team Shots
        "AS" TEXT,             -- Away Team Shots
        "HST" TEXT,            -- Home Team Shots on Target
        "AST" TEXT,            -- Away Team Shots on Target
        "HF" TEXT,             -- Home Team Fouls Committed
        "AF" TEXT,             -- Away Team Fouls Committed
        "HC" TEXT,             -- Home Team Corners
        "AC" TEXT,             -- Away Team Corners
        "HY" TEXT,             -- Home Team Yellow Cards
        "AY" TEXT,             -- Away Team Yellow Cards
        "HR" TEXT,             -- Home Team Red Cards
        "AR" TEXT,             -- Away Team Red Cards
        "B365H" TEXT,          -- Bet365 Home Team Win Odds
        "B365D" TEXT,          -- Bet365 Draw Odds
        "B365A" TEXT,          -- Bet365 Away Team Win Odds
        "Season" TEXT          -- Season (e.g., "2005-2006")
    )

    
    """

    messages = [
        {"role": "system", "content": """You are an expert SQL developer. Generate valid PostgreSQL SELECT queries based on the user's question about LaLiga football matches. The generated response should only include the SQL query in markdown format and nothing else.Teams names are as follows:
    "Cordoba","Tenerife","Murcia","Zaragoza","Las Palmas","Alaves","Real Madrid","Levante","Betis","Numancia","Sevilla","La Coruna",
    "Malaga","Ath Madrid","Xerez","Huesca","Granada","Sociedad","Valladolid","Ath Bilbao","Girona","Sp Gijon","Cadiz","Eibar","Getafe",
    "Santander","Villarreal","Vallecano","Recreativo","Leganes","Almeria","Barcelona","Hercules","Celta","Mallorca","Osasuna","Valencia",
    "Elche","Gimnastic","Espanol"

    Make sure when you are selecting the teams, you select the exact team name as it is in the database as specified above.

    The correct syntax is:
    SELECT "HomeTeam", "AwayTeam", "FTHG", "FTAG" FROM laliga_data WHERE ("HomeTeam" = 'Real Madrid' AND "AwayTeam" = 'Barcelona') AND "Season" = '2023-2024';

    The incorrect syntax is:
    SELECT "HomeTeam", "AwayTeam", "FTHG", "FTAG" FROM laliga_data WHERE ("HomeTeam" = 'Real Madrid' AND "AwayTeam" = 'Barcelona') AND "Season" = '2023-2024';
         
    Date column is a string of format DD/MM/YY
         ALWAYS USE THE CORRECT SYNTAX
         ADD EXPLICIT TYPE CASTING FROM TEXT DATATYPE FOR AGGREGATE FUNCTIONS
         Example:
         SELECT SUM(CAST("FTHG" AS INTEGER)) AS "TotalGoalsScoredAtHome" 
FROM laliga_data 
WHERE "HomeTeam" = 'Real Madrid';
"""},
        {"role": "system", "content": f"Here is the database schema:\n{schema_description}"},
        {"role": "user", "content": f"Generate a PostgreSQL query for this question: {natural_query}"}
    ]

    try:
        response = openai.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=150
        )
        
        sql_query = response.choices[0].message.content.strip()
        return sql_query
    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        return None

def query_laliga(natural_query: str) -> str:
    """
    Convert a natural language query into SQL using OpenAI, execute it via PostgreSQL,
    and generate a natural language response from the results for LaLiga data.
    """
    openai = OpenAI(api_key=OPENAI_API_KEY)

    # Step 1: Convert Natural Language to SQL
    sql_query = nl2sql_laliga(natural_query, openai)
    if not sql_query:
        logging.error("Failed to generate SQL query.")
        return "Sorry, I couldn't generate a SQL query for your question."
    print(sql_query)

    logging.info("Generated SQL Query")

    cleaned_query = clean_sql_query(sql_query)
    print(cleaned_query)
    logging.info(f"Cleaned SQL Query: {cleaned_query}")

    # Step 2: Execute the SQL Query
    results_df = execute_sql_query(cleaned_query)
    print("\n\nRESULTS DF\n",results_df)
    logging.info(f"Results DataFrame shape: {results_df.shape}")

    if results_df.empty:
        logging.warning("No results found for the given query.")
        return "I couldn't find any LaLiga matches matching your criteria."

    # Step 3: Generate Natural Language Response
    try:
        results_summary = results_df.to_dict(orient="records")
        results_context = f"The results of the query are:\n{results_summary}"

        response = openai.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant who provides information about LaLiga football matches. Your task is to summarize the database query results into natural language."},
                {"role": "user", "content": f"Summarize the following LaLiga match query results in natural language:\n{results_context}"}
            ],
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=200
        )

        answer = response.choices[0].message.content.strip()
        print("\n\ANSWER\n",answer)
        return answer
    except Exception as e:
        logging.error(f"Error generating natural language answer: {e}")
        return "Sorry, I couldn't generate a response from the query results."

