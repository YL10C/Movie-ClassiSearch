import os
import json
from nltk.stem import PorterStemmer
import re
import glob

with open("./stop_words.txt", 'r') as file:
    stop = file.read().lower().split()


def preprocess_text(text):
    text = text.lower()
    tokens = re.findall(r"\b\w+\b", text)
    tokens = [item for item in tokens if item not in stop]
    ps = PorterStemmer()
    tokens = [ps.stem(item) for item in tokens]
    return tokens


base_dir = "ttds_final_data"
fields = [
          "title",
          "genres",
          "plot",
          "score",
          "num_votes",
          "director",
          "release_date",
          "countries",
          "languages",
          "aka",
          "keywords",
          "cast_character",
          "quotes"
         ]

for i in range(2030, 2032):
    folder_path = os.path.join(base_dir, str(i))
    file_pattern = os.path.join(folder_path, "output*.jsonl")
    matching_files = glob.glob(file_pattern)
    if matching_files:
        file_path = matching_files[0]
        processed_data = {}
        with open(file_path, "r", encoding="utf-8") as file:
            print(f"Data from folder {i}:")
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    id = data["id"]
                    result_string = " ".join(str(data.get(field, "N/A")) for field in fields)
                    processed_text = preprocess_text(result_string)
                    processed_data[id] = processed_text
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in {file_path}: {e}")

            txt_file_path = os.path.join(folder_path, f"processed_{i}.txt")
            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                for key, value in processed_data.items():
                    txt_file.write(f"{key}: {' '.join(value)}\n")


    else:
        print(f"No data.jsonal file in folder {i}")

