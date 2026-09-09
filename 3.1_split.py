import json
import random

random.seed(42)

with open("dataset_posologie.jsonl", "r", encoding="utf-8") as f:
    exemples = [json.loads(line) for line in f]

indices = list(range(len(exemples)))
random.shuffle(indices)

train_idx = indices[:7]
val_idx = indices[7:8]
test_idx = indices[8:10]

def sauver(nom_fichier, idx_liste):
    with open(nom_fichier, "w", encoding="utf-8") as f:
        for i in idx_liste:
            f.write(json.dumps(exemples[i], ensure_ascii=False) + "\n")

sauver("dataset_train.jsonl", train_idx)
sauver("dataset_val.jsonl", val_idx)
sauver("dataset_test.jsonl", test_idx)

print(f"Train: {len(train_idx)} exemples")
print(f"Val: {len(val_idx)} exemples")
print(f"Test: {len(test_idx)} exemples (FIGE, ne pas regarder avant 3.5)")
