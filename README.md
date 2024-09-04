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
- Python 3.7 trở lên
- Các thư viện Python cần thiết được liệt kê trong file `requirements.txt`

## Hướng dẫn cài đặt

### 1. Clone repository
Đầu tiên, bạn cần clone repository này về máy tính của mình:

```bash
git clone [repository-link]
cd [repository-directory]
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

## Cách sử dụng

### Chạy ứng dụng Streamlit
Sau khi hoàn thành các bước cài đặt, bạn có thể chạy ứng dụng Streamlit bằng lệnh:

```bash
streamlit run run.py
```

Ứng dụng sẽ mở ra trong trình duyệt của bạn, và bạn có thể bắt đầu sử dụng.

## Hỗ trợ
Nếu bạn gặp bất kỳ vấn đề gì hoặc có câu hỏi, vui lòng mở một issue trên trang GitHub của dự án hoặc liên hệ với chúng tôi qua email [nhtcuong@gmail.com].

## Giấy phép
Dự án này được cấp phép theo giấy phép MIT. Vui lòng tham khảo file `LICENSE` để biết thêm chi tiết.

Cảm ơn bạn đã quan tâm đến dự án của chúng tôi! Chúng tôi hy vọng bạn sẽ tìm thấy nó hữu ích và thú vị.
```
