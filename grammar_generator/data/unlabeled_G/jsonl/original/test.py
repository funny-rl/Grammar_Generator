import json

def get_specification(description: str) -> str:
    constraints_start_token = '\nconstraints\n'
    input_start_token = '\ninput\n'
    end_token = '\noutput\n'

    desc_lower = description.lower()
    constraints_start = desc_lower.find(constraints_start_token)
    input_start = desc_lower.find(input_start_token)
    end = desc_lower.find(end_token)

    constraints_start = len(description) if constraints_start < 0 else constraints_start
    input_start = len(description) if input_start < 0 else input_start
    start = min(constraints_start, input_start)
    start = 0 if start == len(description) else start
    end = len(description) if end < 0 else end

    specification = description[start:end].strip()
    return specification

def categorize_by_phrase(description: str) -> int:
    desc = description.lower()
    has_only_line = "the only line" in desc
    has_next_line = "the next line" in desc

    if has_only_line and not has_next_line:
        return 1
    elif has_next_line and not has_only_line:
        return 3
    elif has_only_line and has_next_line:
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

# 2. 조건을 만족하는 데이터만 저장
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        data = json.loads(line)
        desc_len = len(data['description'])

        # 평균 이상 길이만 유지
        if desc_len < avg_len:
            continue

        if categorize_by_phrase(data['description']) > 4:
            data['description'] = get_specification(data['description'])
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
datas = sorted(data_list, key=lambda x: x[0], reverse=True)[:1000]

# 결과 저장
with open(output_file, 'w', encoding='utf-8') as outfile:
    for _, data in datas:
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write('\n')
        
        