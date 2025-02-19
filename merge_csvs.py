import pandas as pd
import os

def merge_csvs(directory: str):
    # List all CSV files in the data directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    merged_df = pd.DataFrame()
    # Read all CSV files into a list of DataFrames
    for i in csv_files:
        df = pd.read_csv(f'{directory}/{i}')
        df['Season'] = f"20{i[1:3]}-20{i[3:5]}"
        if 'Time' in df.columns:
            df.drop(columns=['Time'], axis=1, inplace=True)
        merged_df = pd.concat([merged_df, df], ignore_index=True)
    
    return merged_df

def main():
    epl_df = merge_csvs('data/EPL')
    epl_df.to_csv('data/csv_data/epl_matches.csv', index=False)
    laliga_df = merge_csvs('data/LaLiga')
    laliga_df.to_csv('data/csv_data/laliga_matches.csv', index=False)
    

if __name__ == "__main__":
    main()