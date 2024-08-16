import pandas as pd
from sklearn.model_selection import train_test_split
import argparse
import os
import configparser

def parse_arguments():
    parser = argparse.ArgumentParser(description="Chia file CSV thành train và test với tỉ lệ tùy chỉnh.")
    parser.add_argument('-i', '--input_file', type=str, help='Đường dẫn đến file CSV đầu vào.')
    parser.add_argument('-o', '--output_dir', type=str, help='Thư mục để lưu file CSV đầu ra.')
    parser.add_argument('-r', '--ratio', type=float, help='Tỷ lệ chia dữ liệu cho train (mặc định là 0.8).')
    return parser.parse_args()

def read_config(config_file='split.ini'):
    config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
    config.read(config_file)
    return config

def main():
    args = parse_arguments()
    
    # Default values
    input_file = None
    output_dir = None
    ratio = 0.8
    
    # Read config file if present
    config = read_config()
    
    if 'SETTINGS' in config:
        print('SETTINGS')
        input_file = config['SETTINGS'].get('input_file', input_file, vars=os.environ)
        print(">>>" + input_file)
        output_dir = config['SETTINGS'].get('output', output_dir, vars=os.environ)
        print(">>>" +output_dir)
        ratio = config['SETTINGS'].getfloat('ratio', ratio)
    
    print(output_dir)
    # Override with command-line arguments if provided
    if args.input_file:
        print(args.input_file)
        input_file = args.input_file
    if args.output_dir:
        print(args.output_dir)
        output_dir = args.output_dir
    if args.ratio:
        ratio = args.ratio
    
    # Ensure required parameters are set
    if not input_file:
        raise ValueError("Cần cung cấp đường dẫn đến file CSV đầu vào qua dòng lệnh hoặc file cấu hình.")
    
    # Kiểm tra xem thư mục đầu ra có tồn tại hay không, nếu không thì tạo mới
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Đọc file CSV vào dataframe
    df = pd.read_csv(input_file)
    
    # Chia dữ liệu thành train và test với tỷ lệ tùy chỉnh
    train, test = train_test_split(df, test_size=(1 - ratio), random_state=42)
    
    # Tạo đường dẫn cho các file đầu ra
    train_file = os.path.join(output_dir, 'train.csv')
    test_file = os.path.join(output_dir, 'test.csv')
    
    # Lưu dữ liệu thành hai file CSV mới
    train.to_csv(train_file, index=False, encoding='utf-8-sig')
    test.to_csv(test_file, index=False, encoding='utf-8-sig')
    
    print(f"Dữ liệu đã được chia và lưu trữ trong thư mục {output_dir}:")
    print(f"Train: {len(train)} dòng - Đã lưu vào {train_file}")
    print(f"Test: {len(test)} dòng - Đã lưu vào {test_file}")

if __name__ == '__main__':
    main()
