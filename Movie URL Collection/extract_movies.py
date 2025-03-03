import pandas as pd

df = pd.read_csv('title.basics.tsv', sep='\t')
df['titleType'] = df['titleType'].astype(str)
filtered_df = df[df['titleType'] == 'movie']
sorted_df = filtered_df.sort_values(by='startYear', ascending=True)
sorted_df.to_csv('movie.basics.tsv', sep='\t', index=False)
print("Number of rows in the file:", len(sorted_df))