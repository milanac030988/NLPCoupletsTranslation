from fake_chatgpt_api import FakeChatGPTAPI

fake_api = FakeChatGPTAPI()
couplets = input("Nhập câu đối cần dịch:")
resp = fake_api.send_request(couplets)
print (f"Response from ChatGPT: {resp}")