# Ứng dụng dịch hoành phi câu đối Hán sang chữ Quốc ngữ hiện đại

## Giới thiệu

Chào mừng bạn đến với dự án "Ứng dụng dịch hoành phi câu đối Hán sang chữ Quốc ngữ hiện đại"! Đây là một công cụ hữu ích giúp chuyển đổi các hoành phi câu đối Hán sang chữ Quốc ngữ hiện đại. Ứng dụng này không chỉ giúp bảo tồn và phổ biến văn hóa truyền thống mà còn hỗ trợ việc nghiên cứu và giảng dạy văn học cổ điển Việt Nam. Với giao diện thân thiện và dễ sử dụng, ứng dụng này mang lại trải nghiệm dịch thuật nhanh chóng và chính xác, phù hợp với nhu cầu của cả người học lẫn các chuyên gia trong lĩnh vực.

## Tính năng

1. **Dịch âm:** Dịch chữ Hán sang âm Hán Việt.

2. **Dịch nghĩa:** Cung cấp bản dịch nghĩa của các câu đối, giúp người dùng nắm bắt nội dung và ý nghĩa sâu sắc ẩn chứa trong từng câu chữ.

3. **Giao diện đơn giản và dễ sử dụng:** Cho phép người dùng dễ dàng nhập liệu, lựa chọn phương pháp dịch và xem kết quả chỉ trong vài bước.

4. **Tùy chọn đa dạng:** Cho phép người dùng lựa chọn phương pháp dịch phù hợp với nhu cầu của mình, bao gồm cả dịch âm và dịch nghĩa.

5. **Xử lý dữ liệu tự động:** Ứng dụng tự động nhận diện và phân loại các cột dữ liệu trong file nhập, giúp tối ưu hóa quá trình dịch thuật.

6. **Hỗ trợ nhập liệu:** Hỗ trợ nhập liệu từ định dạng file CSV, Excel, giúp việc sử dụng ứng dụng trở nên linh hoạt và tiện lợi.

7. **Hiển thị kết quả trực quan:** Kết quả dịch thuật được hiển thị một cách trực quan và dễ hiểu, giúp người dùng dễ dàng theo dõi và đánh giá.

Ứng dụng này là công cụ không thể thiếu cho những ai quan tâm đến văn hóa Việt Nam, đặc biệt là trong việc bảo tồn và phát huy giá trị của các tác phẩm hoành phi câu đối.


## Yêu cầu hệ thống
Trước khi bắt đầu, hãy đảm bảo rằng hệ thống của bạn đã cài đặt:
- Python 3.9 trở lên
- Các thư viện Python cần thiết được liệt kê trong file `requirements.txt`

## Hướng dẫn cài đặt trên Ubuntu

### 1. Clone repository
Đầu tiên, bạn cần clone repository này về máy tính của mình:

```bash
git clone https://github.com/milanac030988/NLPCoupletsTranslation.git
cd NLPCoupletsTranslation
```

### 2. Cài đặt Env
Chạy setEnv.sh bằng dòng lệnh:
```bash
source setEnv.sh
```

### 3. Cài đặt các thư viện cần thiết
Sử dụng pip để cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```


## Cách sử dụng

### Chạy ứng dụng webapp
Sau khi hoàn thành các bước cài đặt, bạn có thể chạy ứng dụng webapp lần đầu bằng lệnh:

```bash
python run.py 
```

Ứng dụng sẽ mở ra trong trình duyệt của bạn tại địa chỉ [http://localhost:8501](http://localhost:8501), và bạn có thể bắt đầu sử dụng.

### Chạy translation service only
Nếu chỉ muốn chạy translation service, bạn có thể set RUNTYPE environment variable như sau:

```bash
export RUNTYPE=api
python run.py 
```
Một FastAPI service sẽ run ở port 8000. Bạn có thể tạo request đến API service bằng python code như sau:

- Send translation request:
```python
import requests
# URL của API FastAPI
url = "http://127.0.0.1:8000/translate/"

# Dữ liệu JSON theo format TranslateRequest
data = {
    "type": "text",
    "source": """細 柳 營 中 親 淑 女
夭 桃 華 裏 指 軍 符""",
    "method": ""
}

# Gửi request POST tới API FastAPI
response = requests.post(url, json=data)
```

- Send contribute request:
```python
import requests
# URL của API FastAPI
url = "http://127.0.0.1:8000/contribute/"

# Dữ liệu JSON theo format ContributeRequest
data_contribiute  = {
   "type": "text",
    "cn": """細 柳 營 中 親 淑 女
夭 桃 華 裏 指 軍 符""",
    "sv": """Tế liễu doanh trung thân thục nữ
Yêu đào hoa lý chỉ quân phù.""",
    "vi": """Chốn doanh liễu gần kề thục nữ
Vẻ đào tơ nay chỉ quân phù."""
}

# Gửi request POST tới API FastAPI
response = requests.post(url, json=data_contribiute)
```
# Hướng dẫn Train Data

## Train mô hình Transformer

Chạy lệnh sau để train mô hình Transformer:

```bash
python src/models/train_transformer.py
```

## Train mô hình Moses

### 1. Cài đặt Moses
Để cài đặt Moses, chạy các lệnh sau:

```bash
sudo apt-get install build-essential
sudo apt-get install cmake
sudo apt-get install git-core
sudo apt-get install zlib1g-dev libbz2-dev libboost-all-dev

git clone https://github.com/moses-smt/mosesdecoder.git
cd mosesdecoder
./bjam -j4
```
### 2. Tạo working directory
Tạo thư mục làm việc và chuyển vào thư mục này:
```bash
mkdir working-dir
cd working-dir
```
### 3. Cài đặt MGIZA alignment tools và kenlm
- Làm theo hướng dẫn cài đặt MGIZA alignment tools tại link: [Cài đặt MGIZA](https://hovinh.github.io/blog/2016-04-29-install-mgiza-ubuntu/)
- Làm theo hướng dẫn compile kenlm tại [kenlm](https://github.com/kpu/kenlm)

### 4. Chuẩn bị dữ liệu Corpus
Copy các file corpus dvsktt_corpus.hanzi và dvsktt_corpus.vietnamese trong \data\processed đến thư mục làm việc (working-dir).

### 5. Train mô hình Moses
Chạy lệnh sau để train mô hình Moses:
```bash
$MOSES/scripts/training/train-model.perl -root-dir train -corpus dvsktt_corpus -f hanzi -e vietnamese -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:3:/path/to/lm.arpa -external-bin-dir $GIZA/bin

```
Trong đó:

- `-corpus dvsktt_corpus`: chỉ định tên corpus.
- `-f hanzi -e vietnamese`: chỉ định ngôn ngữ nguồn (hanzi) và ngôn ngữ đích (vietnamese).
- `-alignment grow-diag-final-and`: chỉ định phương pháp căn chỉnh.
- `-reordering msd-bidirectional-fe`: chỉ định kiểu sắp xếp lại.
- `-lm 0:3:/path/to/lm.arpa`: chỉ định mô hình ngôn ngữ (thư mục kenlm).
- `-external-bin-dir $GIZA/bin: chỉ định thư mục của MGIZA.

# Hướng dẫn cài đặt ứng dụng với Docker

## Giới thiệu

Ứng dụng này được đóng gói dưới dạng container Docker để dễ dàng triển khai và chạy trên bất kỳ hệ thống nào hỗ trợ Docker.

## Yêu cầu

- Docker phải được cài đặt trên máy của bạn. Nếu chưa cài đặt, bạn có thể tham khảo hướng dẫn tại [Docker Official Website](https://docs.docker.com/get-docker/).

## Hướng dẫn cài đặt

### 1. Clone repository

Đầu tiên, bạn cần clone repo của ứng dụng về máy của mình:

```bash
git clone https://github.com/milanac030988/NLPCoupletsTranslation.git
cd NLPCoupletsTranslation
```

### 2. Xây dựng Docker Image

Sử dụng Dockerfile đã có sẵn để xây dựng Docker image cho ứng dụng của bạn:

```bash
docker build -t han-nom-translation-img .
```

### 3. Chạy Container

#### Chạy ứng dụng webapp

```bash
docker run --env-file app.env -it -p 8501:8501 -p 8000:8000 --name han-nom-app han-nom-translation-img
```

- `--env-file app.env`: Dùng file environment app.env cho webapp.
- `-it`: Chạy container ở chế độ tương tác.
- `-p 8501:8501`: Mở cổng 8501 trên localhost để truy cập ứng dụng webapp từ bên ngoài.
- `-p 8000:8000`: Mở cổng 8000 trên localhost để gọi api từ bên ngoài.
- `han-nom-translation-img`: Tên của Docker image mà bạn đã xây dựng.
- `--name han-nom-app`: Đặt tên cho container là han-nom-app.

#### Chạy translation service only

```bash
docker run --env-file api.env -it -p 8000:8000 --name han-nom-service han-nom-translation-img
```

- `--env-file api.env`: Dùng file environment api.env cho service.
- `-it`: Chạy container ở chế độ tương tác.
- `-p 8000:8000`: Mở cổng 8000 trên localhost để gọi api từ bên ngoài.
- `han-nom-translation-img`: Tên của Docker image mà bạn đã xây dựng.
- `--name han-nom-service`: Đặt tên cho container là han-nom-service.


### 5. Kiểm tra trạng thái của Container

Để kiểm tra xem container của bạn có chạy thành công hay không, sử dụng lệnh:

```bash
docker ps
```

Lệnh này sẽ liệt kê tất cả các container đang chạy. Bạn sẽ thấy tên `han-nom-app` trong danh sách nếu container đã khởi động thành công.

### 6. Truy cập ứng dụng web app

Mở trình duyệt và truy cập ứng dụng tại địa chỉ:

```
http://127.0.0.1:8501
```

Thay đổi địa chỉ và cổng tùy theo cấu hình của bạn.

## Các lệnh hữu ích khác

- **Xem logs của container:**

  ```bash
  docker logs han-nom-app
  ```

- **Dừng container:**

  ```bash
  docker stop han-nom-app
  ```
- **Start container:**

  ```bash
  docker start -a han-nom-app
  ```

- **Xóa container:**

  ```bash
  docker rm han-nom-app
  ```

- **Xóa Docker image:**

  ```bash
  docker rmi han-nom-translation-app
  ```

## Tham khảo thêm

- [Tài liệu Docker](https://docs.docker.com/)

## Các vấn đề đã biết trong quá trình chạy

### Vấn đề với GLIBCXX_3.4.29
#### Lỗi:
```
/usr/lib/x86_64-linux-gnu/libstdc++.so.6: version GLIBCXX_3.4.29 not found
```

#### Giải pháp:
Cập nhật libstdc bằng commands sau:

```bash
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get upgrade libstdc++6
```


## Đóng góp

Nếu bạn muốn đóng góp vào dự án này, vui lòng tạo Pull Request hoặc mở Issues mới trên GitHub.

## Hỗ trợ
Nếu bạn gặp bất kỳ vấn đề gì hoặc có câu hỏi, vui lòng mở một issue trên trang GitHub của dự án hoặc liên hệ với chúng tôi qua email [nhtcuong@gmail.com].

## Giấy phép
Dự án này được cấp phép theo giấy phép MIT. Vui lòng tham khảo file `LICENSE` để biết thêm chi tiết.

Cảm ơn bạn đã quan tâm đến dự án của chúng tôi! Chúng tôi hy vọng bạn sẽ tìm thấy nó hữu ích và thú vị.
```
