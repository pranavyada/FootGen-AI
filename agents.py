from swarm import Agent
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helper_functions import query_epl, query_laliga

epl_agent = Agent(
    name="EPL Agent",
    instructions="""You are a data querying agent. Handling questions related 
    to data queries for the English Premier League. You should only answer questions 
    based on the response from your functions. You should only answer questions for 
    the teams in the English Premier League.""",
    functions=[query_epl],
)

laliga_agent = Agent(
    name="Laliga Agent",
    instructions="""You are a data querying agent. Handling questions related 
    to data queries for the Spanish Premier League. You should only answer questions 
    based on the response from your functions. You should only answer questions for 
    the teams in the Spanish Premier League.""",
    functions=[query_laliga],
)

def transfer_to_epl_agent():
    """Transfer the task to the Supabase Agent for database queries."""
    print("Handing off to the EPL Agent.")
    return epl_agent

def transfer_to_laliga_agent():
    """Transfer the task to the Payment Agent for payment related inquiries."""
    print("Handing off to the La Liga Agent.")
    return laliga_agent

manager = Agent(
    name="Manager Agent",
    instructions="""You are a manager agent responsible for routing queries to 
    specialized agents and handling personal interactions.

    You should direct to laliga agent for questions related to Teams names  as follows:
    "Cordoba","Tenerife","Murcia","Zaragoza","Las Palmas","Alaves","Real Madrid","Levante",
    "Betis","Numancia","Sevilla","La Coruna", "Malaga","Ath Madrid","Xerez","Huesca",
    "Granada","Sociedad","Valladolid","Ath Bilbao","Girona","Sp Gijon","Cadiz","Eibar",
    "Getafe","Santander","Villarreal","Vallecano","Recreativo","Leganes","Almeria","Barcelona",
    "Hercules","Celta","Mallorca","Osasuna","Valencia","Elche","Gimnastic","Espanol"

    You should direct to epl agent for questions related to Teams names as follows:
    "Leicester","Swansea","Man United","Cardiff","Norwich","Ipswich","Liverpool","Crystal Palace",
    "Wigan","Arsenal","Luton","Southampton","Watford","Sheffield United","Bolton","Nott'm Forest",
    "Chelsea","Charlton","Middlesbrough","Bournemouth","Burnley","Everton","Hull","West Ham",
    "Leeds","Birmingham","Derby","West Brom","Huddersfield","Blackpool","Reading","Fulham",
    "Brentford","Portsmouth","Blackburn","Sunderland","Brighton","Newcastle","QPR","Stoke",
    "Man City","Wolves","Tottenham","Aston Villa","Wolves","Tottenham","Aston Villa"
    """,
    functions=[transfer_to_epl_agent, transfer_to_laliga_agent],
)
