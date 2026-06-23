import pandas as pd

df = pd.read_csv("truefilm_posts.csv", encoding="latin-1")

# handle both empty string and NaN
df['label'] = df['label'].fillna("")
if 'flag' not in df.columns:
    df['flag'] = ""
df['flag'] = df['flag'].fillna("")

# find where to start - last unlabeled row, iterate backwards
unlabeled = df[df['label'] == ""].index
if len(unlabeled) == 0:
    print("All posts labeled!")
    exit()

start = unlabeled[-1]
print(f"Resuming from post {start + 1} (going backwards)")

for i in df.index[start::-1]:
    if df.at[i, 'label'] != "":
        continue

    print(f"\n--- POST {i+1} of {len(df)} ---")
    print(f"TITLE: {df.at[i, 'title']}")
    print(f"\nBODY:\n{df.at[i, 'body']}")
    print("\nOptions: a=analysis, d=discussion, r=reaction, s=unsure, q=quit")
    
    label = input("Label: ").strip().lower()
    
    if label == "q":
        break
    elif label == "a":
        df.at[i, 'label'] = "analysis"
    elif label == "d":
        df.at[i, 'label'] = "discussion"
    elif label == "r":
        df.at[i, 'label'] = "reaction"
    elif label == "s":
        df.at[i, 'label'] = "unsure"
    else:
        print("Invalid input, skipping")
        continue

    flag = input("Flag this post? (p to flag, enter to skip): ").strip().lower()
    df.at[i, 'flag'] = "p" if flag == "p" else ""

    df.to_csv("truefilm_posts.csv", index=False)

print("Progress saved!")