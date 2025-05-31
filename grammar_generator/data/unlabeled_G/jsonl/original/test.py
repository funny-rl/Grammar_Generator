import json
from collections import Counter

def get_specification(description: str) -> str:
    constraints_start_token = '\nconstraints\n'
    input_start_token = '\ninput\n'
    end_token = '\noutput\n'
    constraints_start = description.lower().find(constraints_start_token)
    input_start = description.lower().find(input_start_token)
    end = description.lower().find(end_token)
    constraints_start = len(description) if constraints_start < 0 else constraints_start
    input_start = len(description) if input_start < 0 else input_start
    start = min(constraints_start, input_start)
    start = 0 if start == len(description) else start
    end = len(description) if end < 0 else end
    return description[start:end].strip()

def categorize_by_description(description: str) -> int:
    desc = description.lower()
    if "the first line" in desc and "the second line" in desc and "the third line" in desc:
        return 3
    elif "the first line" in desc and "the second line" in desc:
        return 2
    elif "the only line" in desc or "the first line" in desc:
        return 1
    elif any(keyword in desc for keyword in ["lowercase english letters", "uppercase english letters", "characters"]):
        return 4
    else:
        return 5
    
# 파일 경로 설정
input_file = 'full.jsonl'
output_file = 'specification.jsonl'

# 1. 평균 길이 계산
descriptions = []
with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        data = json.loads(line)
        descriptions.append(len(data['description']))

avg_len = sum(descriptions) / len(descriptions)

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        data = json.loads(line)
        level = categorize_by_description(data['description'])
        if 4 >= level >= 2:
            data['description'] = get_specification(data['description'])
            if data['description'][:10].startswith("Input\n\n") and not "Examples" in data['description']:
                json.dump(data, outfile, ensure_ascii=False)
                outfile.write('\n')
                
import json

input_file = 'specification.jsonl'
output_file = 'train.jsonl'

# 모든 데이터 읽고 description 길이 기준으로 정렬
data_list = []
with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        data = json.loads(line)
        data_list.append((len(data['description']), data))
        data["grammar"] = {"productions": [""], "constraints": [""]}

# 길이 기준 내림차순 정렬 후 상위 2000개 선택
datas = sorted(data_list, key=lambda x: x[0], reverse=True)[40:1040]

# 결과 저장
with open(output_file, 'w', encoding='utf-8') as outfile:
    for _, data in datas:
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write('\n')
        
        