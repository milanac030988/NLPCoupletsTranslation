import argparse
import os
import platform
import configparser
import subprocess

def parse_arguments():
    parser = argparse.ArgumentParser(description='Split text file into .hanzi and .vietnamese files.')
    parser.add_argument('-i', '--input', type=str, help='Input file path.')
    parser.add_argument('-o', '--output', type=str, help='Output folder path.')
    return parser.parse_args()

def read_config(config_file='split_mosses_corpus.ini'):
    config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
    config.read(config_file)
    return config
    
def replace_line_endings(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    
    content = content.replace(b'\r\n', b'\n')
    
    with open(file_path, 'wb') as file:
        file.write(content)


def split_file(input_file, output_folder):
    # Tách tên file và phần mở rộng
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Tạo tên file đầu ra dựa trên tên file đầu vào
    hanzi_file = os.path.join(output_folder, f'{base_name}.hanzi')
    vietnamese_file = os.path.join(output_folder, f'{base_name}.vietnamese')
    
    # Xóa file cũ nếu tồn tại
    if os.path.exists(hanzi_file):
        os.remove(hanzi_file)
    
    if os.path.exists(vietnamese_file):
        os.remove(vietnamese_file)
    
    if platform.system() == 'Windows':
        # PowerShell command to split the file
        powershell_script = f"""
        $inputFile = '{input_file}'
        $hanziFile = '{hanzi_file}'
        $vietnameseFile = '{vietnamese_file}'

        Get-Content $inputFile | ForEach-Object {{
            $columns = $_ -split "`t"
            if ($columns.Length -ge 2) {{
                $columns[0] | Add-Content $hanziFile
                $columns[1] | Add-Content $vietnameseFile
            }}
        }}
        """
        p = subprocess.Popen(["powershell.exe", "-Command", powershell_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            print(f"Error: {err.decode('utf-8')}")
        else:
            print("File split successfully on Windows using PowerShell.")
    else:  # Assume Linux/Unix
        os.system(f'cut -f 1 {input_file} > {hanzi_file}')
        os.system(f'cut -f 2 {input_file} > {vietnamese_file}')
    
    # Replace line endings in the output files
    replace_line_endings(hanzi_file)
    replace_line_endings(vietnamese_file)

def main():
    args = parse_arguments()
    
    # Default values
    input_file = 'corpus.txt_bk'
    output_folder = './output'
    
    # Read config file if present
    config = read_config()
    
    if 'split_corpus' in config:
        input_file = config['split_corpus'].get('input_file', input_file, vars=os.environ)
        output_folder = config['split_corpus'].get('output_folder', output_folder, vars=os.environ)
    
    # Override with command-line arguments if provided
    if args.input:
        input_file = args.input
    if args.output:
        output_folder = args.output
    
    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Perform the file splitting
    split_file(input_file, output_folder)

if __name__ == '__main__':
    main()
