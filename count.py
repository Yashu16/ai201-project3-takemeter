import pandas as pd

df = pd.read_csv("truefilm_posts_subset.csv", encoding="latin-1")
print(df['label'].value_counts())