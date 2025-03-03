import os
import pandas as pd

df = pd.read_csv('movie.basics.tsv', sep='\t')
df['startYear'] = df['startYear'].astype(str)

for year in range(2025, 2050):
    year_str = str(year)
    filtered_df = df[df['startYear'] == year_str]
    if filtered_df.empty:
        print(f"No data found for the year {year_str}. Skipping...")
        continue

    sorted_df = filtered_df.sort_values(by='tconst', ascending=True)
    folder_name = f"{year_str}_data"
    os.makedirs(folder_name, exist_ok=True)
    year_tsv_path = os.path.join(folder_name, f"{year_str}.basics.tsv")
    sorted_df.to_csv(year_tsv_path, sep='\t', index=False)
    print(f"Saved {len(sorted_df)} rows for the year {year_str} to {year_tsv_path}")

    tconst_column = sorted_df[['tconst']]
    tconst_tsv_path = os.path.join(folder_name, f"{year_str}_ids.tsv")
    tconst_column.to_csv(tconst_tsv_path, sep='\t', index=False)
    tconst_column['imdb_url'] = tconst_column['tconst'].apply(lambda x: f'https://www.imdb.com/title/{x}/')
    urls_tsv_path = os.path.join(folder_name, f"{year_str}_urls.tsv")
    tconst_column.to_csv(urls_tsv_path, sep='\t', index=False)

    print(f"Processed data for the year {year_str}: {folder_name}")
