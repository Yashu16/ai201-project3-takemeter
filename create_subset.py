import pandas as pd

df = pd.read_csv("truefilm_posts.csv", encoding="latin-1")

reaction = df[df['label'] == 'reaction']        # all 62
analysis = df[df['label'] == 'analysis'].sample(70, random_state=42)
discussion = df[df['label'] == 'discussion'].sample(70, random_state=42)

subset = pd.concat([reaction, analysis, discussion]).reset_index(drop=True)
subset['text'] = subset['title'] + "\n\n" + subset['body'].fillna('')
subset = subset.drop(columns=['title', 'body'])

subset.to_csv("truefilm_posts_subset.csv", index=False, encoding="utf-8-sig")

print(subset['label'].value_counts())
print(f"Total rows: {len(subset)}")
