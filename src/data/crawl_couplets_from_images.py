from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pyautogui
import pyperclip
import undetected_chromedriver as uc


# Đường dẫn tới thư mục chứa các ảnh và file output.txt
image_folder = "D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\OneDrive-2024-07-09\\CauDoiBinhDuong\\ilovepdf_pages-to-jpg"
output_file = "raw_cau_doi_binh_duong.txt"

options = uc.ChromeOptions()

# Tạo danh sách các ảnh trong thư mục
images = [os.path.join(image_folder, f"Phần 1_page-{i:04d}.jpg") for i in range(1, 171)]

# Khởi tạo trình duyệt
driver = uc.Chrome(options=options)

# URL của trang web
url = "https://www.jpgtotext.com/vi/image-to-text"

driver.get(url)

for i in range(0, len(images), 3):
    # Tải lên 3 ảnh
    uploaded_count = 0
    upload_img_paths = []
    for j in range(3):
        if i + j < len(images):
            image_path = images[i + j]
            upload_img_paths.append(image_path)
    file_upload = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "file"))
                )
    file_upload.send_keys('\n'.join(upload_img_paths))
    #         try:
    #             image_path = images[i + j]
    #             file_upload = WebDriverWait(driver, 10).until(
    #                 EC.presence_of_element_located((By.ID, "file"))
    #             )
    #             file_upload.clear()
    #             file_upload.send_keys(image_path)
    #             h3_element = WebDriverWait(driver, 10).until(
    #                 EC.presence_of_element_located((By.XPATH, f"//h3[contains(text(), 'Images ({uploaded_count + 1})')]"))
    #             )
    #         except Exception as ex:
    #             print(f"Failed to upload image: {image_path}. Exception: {ex}")
    #         else:
    #             uploaded_count += 1
    
    # if uploaded_count == 0:
    #     continue
    
    try:
        extract_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Extract Now')]"))
        )
        extract_button.click()
    except Exception as ex:
        print(f"Faile to execute extraction. Exception: {ex}")
        continue

    
    try:
        # Chờ cho đến khi tất cả các div chứa nút "Copy Content" xuất hiện
        divs = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'p-1 relative my-1 flex flex-wrap flex-col w-full border-2 border-gray-400 rounded-sm gap-y-3')]"))
        )
    except Exception as ex:
        print(f"Faile to get contents. Exception: {ex}")

    processed_img_count = 0
    for j in range(3):
        if i + j < len(images):
            try:
                WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.XPATH, f"(//button[contains(@class, 'bg-gray-200') and contains(., 'Copy Content')])[{j + 1}]"))
                )
            except Exception as ex:
                pass
            else:
                processed_img_count += 1
    
    failed_image_paths = []
    for index, div in enumerate(divs):
        try:
            copy_button = div.find_element(By.XPATH, ".//button[contains(@class, 'bg-gray-200') and contains(., 'Copy Content')]")
            if copy_button:
                copy_button.click()
                # print(f"Nút Copy Content ở vị trí div thứ {index + 1}")
                # Lấy văn bản đã sao chép từ clipboard và ghi vào file output.txt
                extracted_text = pyperclip.paste()

                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"Image: {images[i + index]}\n")
                    f.write(extracted_text + "\n\n")
                
                print(f"Extracted text from image: {images[i + index]}")
            else:
                failed_image_paths.append({images[i + index]})
        except:
            
            continue
    
    print(f"Failed to extract from: {failed_image_paths}")
    driver.refresh()
    
#     for j in range(processed_img_count):
#         copy_button = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.XPATH, f"(//button[contains(@class, 'bg-gray-200') and contains(., 'Copy Content')])[{j + 1}]"))
#         )
#         copy_button.click()

#         # Lấy văn bản đã sao chép từ clipboard và ghi vào file output.txt
#         extracted_text = pyperclip.paste()

#         with open(output_file, "a", encoding="utf-8") as f:
#             f.write(f"Image: {images[i + j]}\n")
#             f.write(extracted_text + "\n\n")

# # Lặp qua tất cả các file ảnh trong thư mục
# for i in range(1, 171):
#     image_path = os.path.join(image_folder, f"Phần 1_page-{i:04d}.jpg")
    
    

#     # # Nhấn nút Browse để mở File OpenDialog
#     # browse_button = WebDriverWait(driver, 10).until(
#     #     EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'browse-btn')]"))
#     # )

#     # driver.execute_script("arguments[0].scrollIntoView(true);", browse_button)

#     # browse_button.click()

#     # # Sử dụng pyautogui để nhập đường dẫn file và nhấn Enter
#     # time.sleep(2)  # Đợi File OpenDialog xuất hiện
#     # pyperclip.copy(image_path)
#     # pyautogui.hotkey('ctrl', 'v')  # Dán đường dẫn từ clipboard
#     # pyautogui.press('enter')
#     file_upload = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, "file"))
#     )
#     file_upload.send_keys(image_path)
#     # driver.execute_script(JS_ADD_TEXT_TO_INPUT, file_upload, image_path)
#     # driver.execute_script("arguments[0].value = arguments[1];", file_upload, image_path)
#     # file_upload.send_keys(image_path)

#     # Chờ cho đến khi upload hoàn tất
#     # WebDriverWait(driver, 30).until(
#     #     EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'center-preview-file-uploadIcon')]"))
#     # )
#     # Tìm và nhấn nút "Extract Now"
#     extract_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Extract Now')]"))
#     )
#     extract_button.click()

#     # Chờ cho đến khi nút "Copy Content" xuất hiện
#     copy_button = WebDriverWait(driver, 30).until(
#         EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'bg-gray-200') and contains(., 'Copy Content')]"))
#     )
#     copy_button.click()

#     # Nhấn nút 'Submit and Extract'
#     # Tìm phần tử có id="jsShadowRoot" và truy cập vào Shadow DOM của nó
#     # shadow_root = WebDriverWait(driver, 10).until(
#     #     EC.presence_of_element_located((By.ID, "jsShadowRoot"))
#     # )

#     # shadow_root.click()
#     # test = shadow_root.find_element(By.XPATH, "//div[contains(@class, 'below-tool-btn')]")
    
#     # driver.execute_script("arguments[0].scrollIntoView(true);", shadow_root)
#     #  # Sử dụng JavaScript để truy cập Shadow DOM và tìm `span` bên trong đó
#     # submit_button = shadow_root.find_element(By.CLASS_NAME, "below-tool-btn")
#     # submit_button.click()

#     # Tìm và nhấn nút 'Submit and Extract' bên trong Shadow DOM
#     # submit_button = WebDriverWait(shadow_root, 10).until(
#     #     EC.element_to_be_clickable((By.CSS_SELECTOR, "div.below-tool-btn.hoverEffect"))
#     # )
#     # driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)

#     # submit_button.click()

#     # Chờ cho đến khi nút Copy xuất hiện
#     # copy_button = WebDriverWait(driver, 20).until(
#     #     EC.element_to_be_clickable((By.XPATH, "//div[@class='d-flex align-items-center js-single-result-copy title-hover']"))
#     # )
#     # driver.execute_script("arguments[0].scrollIntoView(true);", copy_button)
#     # copy_button.click()

#     # Lấy văn bản đã sao chép từ clipboard và ghi vào file output.txt
#     extracted_text = pyperclip.paste()

#     with open(output_file, "a", encoding="utf-8") as f:
#         f.write(f"Image: {image_path}\n")
#         f.write(extracted_text + "\n\n")

#     # Refresh page để làm lại từ đầu với ảnh tiếp theo
#     driver.refresh()

# Đóng trình duyệt
driver.quit()
