import csv
import argparse

def txt_to_csv(txt_file1, txt_file2, csv_file):
    # Open the text files and read their contents
    with open(txt_file1, 'r', encoding='utf-8-sig') as f1, open(txt_file2, 'r', encoding='utf-8-sig') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    # Ensure both files have the same number of lines
    assert len(lines1) == len(lines2), "Text files do not have the same number of lines."

    # Write the contents to a CSV file
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header (optional)
        writer.writerow(['cn', 'vi'])
        
        # Write each line from the text files as a row in the CSV
        for line1, line2 in zip(lines1, lines2):
            writer.writerow([line1.strip(), line2.strip()])

    print(f"CSV file '{csv_file}' created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert two text files into a CSV file.")
    parser.add_argument('txt_file1', type=str, help="Path to the first text file.")
    parser.add_argument('txt_file2', type=str, help="Path to the second text file.")
    parser.add_argument('csv_file', type=str, help="Path to the output CSV file.")

    args = parser.parse_args()

    txt_to_csv(args.txt_file1, args.txt_file2, args.csv_file)
