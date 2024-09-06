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

### 4. Tải các mô hình cần thiết:
Tải các mô hình cần thiết bằng lệnh:
```bash
python /workspaces/NLPCoupletsTranslation/src/data/download_data_models.py
```
Hoặc bạn có thể chạy ứng dụng lần đầu với argument `--download-data` bằng lệnh :

```bash
python run.py  `--download-data`
```
- `--download-data`: Tùy chọn này sẽ tải về các models cần thiết cho ứng dụng.

## Cách sử dụng

### Chạy ứng dụng Streamlit
Sau khi hoàn thành các bước cài đặt, bạn có thể chạy ứng dụng lần đầu bằng lệnh:

```bash
streamlit run run.py 
```

Ứng dụng sẽ mở ra trong trình duyệt của bạn, và bạn có thể bắt đầu sử dụng.


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
docker build -t han-nom-translation-app .
```

### 3. Chạy Container lần đầu tiên để tải dữ liệu

Trong lần chạy đầu tiên, bạn nên chạy container với argument `--download-data` để Docker có thể tải về các models cần thiết cho ứng dụng:

```bash
docker run -it -p 127.0.0.1:8501:8501 --name han-nom-app han-nom-translation-app --download-data
```

- `-it`: Chạy container ở chế độ tương tác.
- `-p 127.0.0.1:8501:8501`: Mở cổng 8501 trên localhost để truy cập ứng dụng từ bên ngoài.
- `han-nom-translation-app`: Tên của Docker image mà bạn đã xây dựng.
- `--download-data`: Tùy chọn này sẽ tải về các models cần thiết cho ứng dụng.
- `--name han-nom-app`: Đặt tên cho container là han-nom-app.

### 4. Chạy Container từ Docker Image (Những lần sau)

Sau khi đã tải dữ liệu, bạn có thể chạy lại container mà không cần tùy chọn `--download-data`:

```bash
docker run -d -p 127.0.0.1:8501:8501 --name han-nom-app han-nom-translation-app
```

### 5. Kiểm tra trạng thái của Container

Để kiểm tra xem container của bạn có chạy thành công hay không, sử dụng lệnh:

```bash
docker ps
```

Lệnh này sẽ liệt kê tất cả các container đang chạy. Bạn sẽ thấy tên `han-nom-app` trong danh sách nếu container đã khởi động thành công.

### 6. Truy cập ứng dụng

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

## Đóng góp

Nếu bạn muốn đóng góp vào dự án này, vui lòng tạo Pull Request hoặc mở Issues mới trên GitHub.

## Hỗ trợ
Nếu bạn gặp bất kỳ vấn đề gì hoặc có câu hỏi, vui lòng mở một issue trên trang GitHub của dự án hoặc liên hệ với chúng tôi qua email [nhtcuong@gmail.com].

## Giấy phép
Dự án này được cấp phép theo giấy phép MIT. Vui lòng tham khảo file `LICENSE` để biết thêm chi tiết.

Cảm ơn bạn đã quan tâm đến dự án của chúng tôi! Chúng tôi hy vọng bạn sẽ tìm thấy nó hữu ích và thú vị.
```
