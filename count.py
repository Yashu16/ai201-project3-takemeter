import pandas as pd

df = pd.read_csv("truefilm_posts.csv")
print(df['label'].value_counts())