import pandas as pd
import re
import json
import argparse
from utils import *

# def normalize_text(text):
#     """Normalize text by removing punctuation, spaces, and new lines."""
#     return re.sub(r'[^\u4e00-\u9fff]', '', str(text))

def normalize_text(text):
    """Normalize text by removing punctuation, spaces, and new lines except for specified Unicode ranges."""
    ranges = [
        (0x4e00, 0x9fff),   # CJK Unified Ideographs
        (0x3400, 0x4dbf),   # CJK Unified Ideographs Extension A
        (0x20000, 0x2a6df), # CJK Unified Ideographs Extension B
        (0x2a700, 0x2b73f), # CJK Unified Ideographs Extension C
        (0x2b740, 0x2b81f), # CJK Unified Ideographs Extension D
        (0x2b820, 0x2ceaf), # CJK Unified Ideographs Extension E
        (0x2ceb0, 0x2ebef), # CJK Unified Ideographs Extension F
        (0x30000, 0x3134f), # CJK Unified Ideographs Extension G
        (0x31350, 0x323af), # CJK Unified Ideographs Extension H
        (0x2ebf0, 0x2ee5f), # CJK Unified Ideographs Extension I
        (0xf900, 0xfaff)    # CJK Compatibility Ideographs
    ]
    
    # Tạo biểu thức chính quy cho các khoảng
    regex_parts = [f'{chr(start)}-{chr(end)}' for start, end in ranges]
    regex_pattern = f"[{''.join(regex_parts)}]"
    try:
        res = ''.join(re.findall(regex_pattern, text))
    except Exception as ex:
        print(text)
        raise ex
    # Lọc text chỉ giữ lại các ký tự trong các khoảng
    return res

def check_duplicate(row1, row2):
    """Check if two rows have duplicate Hán tự after normalization."""
    try:
        norm1 = normalize_text(row1['cn'])
        norm2 = normalize_text(row2['cn'])
    except Exception as ex:
        print(f"file1: {row1['cn']}")
        print(f"file2: {row2['cn']}")
        raise ex
    return compare_strings(norm1, norm2)

# # Đường dẫn tới hai file CSV
# file1_path = 'D:\\Document\\Master\\NLP\\Project\\output\\data\\dataset\\5000_couplets_filtered.csv'
# file2_path = 'D:\\Document\\Master\\NLP\\Project\\output\\data\\dataset\\caudoi_dataset.csv'

# # Đọc file CSV vào DataFrame
# df1 = pd.read_csv(file1_path)
# df2 = pd.read_csv(file2_path)

# # # Thêm cột 'source' để biết câu này từ file nào
# # df1['source'] = 'file1'
# # df2['source'] = 'file2'

# # Tạo DataFrame mới để lưu kết quả merge
# merged_df = pd.DataFrame(columns=df1.columns)

# # Tạo danh sách để lưu các chỉ số hàng trùng nhau
# duplicates = []

# # Kiểm tra các câu trùng nhau
# for i, row1 in df1.iterrows():
#     for j, row2 in df2.iterrows():
#         if check_duplicate(row1, row2):
#             duplicates.append((i, j))
#             break

# # Ghi các hàng không trùng vào DataFrame merged_df
# df1_non_duplicates = df1.loc[~df1.index.isin([d[0] for d in duplicates])]
# df2_non_duplicates = df2.loc[~df2.index.isin([d[1] for d in duplicates])]
# merged_df = pd.concat([merged_df, df1_non_duplicates, df2_non_duplicates], ignore_index=True)

# # Ghi các hàng trùng vào DataFrame merged_df (có thể tuỳ chọn cách xử lý)
# for i, j in duplicates:
#     row1 = df1.iloc[i]
#     row2 = df2.iloc[j]
#     # Chọn cách xử lý hàng trùng. Ví dụ: giữ lại hàng từ file1
#     merged_df = pd.concat([merged_df, pd.DataFrame([row1])], ignore_index=True)

# # Lưu DataFrame merged_df thành file CSV
# merged_csv_file_path = 'merged.csv'
# merged_df.to_csv(merged_csv_file_path, index=False, encoding='utf-8-sig')

# # Lưu DataFrame merged_df thành file JSON
# merged_json_file_path = 'merged.json'
# merged_df.to_json(merged_json_file_path, orient='records', force_ascii=False, indent=4)

# # Tạo báo cáo
# report = {
#     'total_rows_file1': len(df1),
#     'total_rows_file2': len(df2),
#     'total_merged_rows': len(merged_df),
#     'total_duplicates': len(duplicates)
# }

# # Lưu báo cáo thành file JSON
# report_json_file_path = 'report.json'
# with open(report_json_file_path, 'w', encoding='utf-8') as f:
#     json.dump(report, f, ensure_ascii=False, indent=4)

# print(f"Data has been successfully merged to {merged_csv_file_path} and {merged_json_file_path}")
# print(f"Report has been saved to {report_json_file_path}")
def main(file1_path, file2_path, output_csv, output_json, report_dir):
    # Đọc file CSV vào DataFrame
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)

    # Tạo DataFrame mới để lưu kết quả merge
    merged_df = pd.DataFrame(columns=df1.columns)

    # Tạo danh sách để lưu các chỉ số hàng trùng nhau
    duplicates = []

    # Kiểm tra các câu trùng nhau
    for i, row1 in df1.iterrows():
        for j, row2 in df2.iterrows():
            try:
                if check_duplicate(row1, row2):
                    duplicates.append((i, j))
                    break
            except Exception as ex:
                print(f"idx file1: {i}")
                print(f"idx file2: {j}")
                raise ex

    # Ghi các hàng không trùng vào DataFrame merged_df
    df1_non_duplicates = df1.loc[~df1.index.isin([d[0] for d in duplicates])]
    df2_non_duplicates = df2.loc[~df2.index.isin([d[1] for d in duplicates])]
    merged_df = pd.concat([merged_df, df1_non_duplicates, df2_non_duplicates], ignore_index=True)

    # Ghi các hàng trùng vào DataFrame merged_df (có thể tuỳ chọn cách xử lý)
    for i, j in duplicates:
        row1 = df1.iloc[i]
        row2 = df2.iloc[j]
        # Chọn cách xử lý hàng trùng. Ví dụ: giữ lại hàng từ file1
        merged_df = pd.concat([merged_df, pd.DataFrame([row1])], ignore_index=True)

    # Lưu DataFrame merged_df thành file CSV
    merged_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    # Lưu DataFrame merged_df thành file JSON
    merged_df.to_json(output_json, orient='records', force_ascii=False, indent=4)

    # Tạo báo cáo
    report = {
        'total_rows_file1': len(df1),
        'total_rows_file2': len(df2),
        'total_merged_rows': len(merged_df),
        'total_duplicates': len(duplicates)
    }

    # Lưu báo cáo thành file JSON
    report_json_file_path = f"{report_dir}/report.json"
    with open(report_json_file_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

    print(f"Data has been successfully merged to {output_csv} and {output_json}")
    print(f"Report has been saved to {report_json_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge two CSV files and generate a report.')
    parser.add_argument('-i', '--inputs', nargs=2, required=True, help='List of 2 CSV files to merge')
    parser.add_argument('-o', '--output', default='merged.csv', help='Output merged CSV file path')
    parser.add_argument('-j', '--json-output', default='merged.json', help='Output merged JSON file path')
    parser.add_argument('-r', '--report-dir', default='.', help='Directory to save the report')

    args = parser.parse_args()
    
    main(args.inputs[0], args.inputs[1], args.output, args.json_output, args.report_dir)