# *******************************************************************************
#
# File: fake_chatgpt_api.py
#
# Initially created by Cuong Nguyen / July 2024
#
# Description:
#   Provides a fake ChatGPT API class for users to interact with as if it were a real API.
#   This implementation uses Selenium to run a browser in the background, handling interactions
#   with the ChatGPT web interface and maintaining context for conversations.

#   Users can utilize this class to simulate API calls to ChatGPT, while the underlying
#   mechanism uses Selenium to manage the browser and perform the necessary actions to
#   communicate with ChatGPT..
#
# History:
#
# 01.07.2024 / V 0.1 / Cuong Nguyen
# - Initialize
#
# *******************************************************************************
from signal import *
from selenium import webdriver as webdriver
from selenium.webdriver.chrome.service import Service as Service
from typing import Any
from dataclasses import dataclass
from selenium.webdriver.remote.webelement import WebElement
import undetected_chromedriver as uc

class FakeChatGPTAPI:
    """
A fake ChatGPT API class for simulating API interactions with ChatGPT.

This class uses Selenium to control a web browser, allowing users to interact with the ChatGPT
web interface programmatically. It maintains the context of conversations and performs actions
on behalf of the user, providing a seamless API-like experience.

Methods of this class enable users to send messages, receive responses, and manage conversation
context, mimicking the behavior of a real API while leveraging the ChatGPT web interface
through Selenium.
    """
    SCRIPT_DIR: str
    INI_FILE_PATH: str
    is_context_created: bool
    driver_path: str
    url: str
    wait_time: int
    driver: uc.Chrome
    prompt_text_area: WebElement
    send_button: WebElement

    """
Constructor for the FakeChatGPTAPI class.

**Arguments:**

* ``config_path``

  / *Condition*: optional / *Type*: str / *Default*: "" /

  The path to the configuration file.

**Returns:**

(*no returns*)
    """
    def __init__(self, config_path: str = ...) -> None: ...
    
    """
Destructor for the FakeChatGPTAPI class.

This method is called when an instance of the FakeChatGPTAPI class is about to be destroyed.
It ensures that any necessary cleanup is performed, such as closing the Selenium browser.

**Returns:**

(*no returns*)
    """
    def __del__(self) -> None: ...
    
    """
Check if the user is logged in to the ChatGPT web interface.

**Returns:**

  / *Type*: bool /

  True if the user is logged in, otherwise False.
    """
    def is_login(self) -> bool: ...

    """
Perform a manual login to the ChatGPT web interface.

This method initiates the manual login process, allowing the user to enter their credentials
and complete any required authentication steps.

**Returns:**

(*no returns*)
    """
    def manual_login(self) -> None: ...

    """
Delete the current conversation context.

This method clears the conversation history, allowing for a fresh start without any previous
context affecting the new interactions.

**Returns:**

(*no returns*)
    """
    def delete_context(self) -> None: ...

    """
Check if ChatGPT-4.0 is available.

This method verifies the availability of ChatGPT-4.0 for use.

**Returns:**

  / *Type*: bool /

  True if ChatGPT-4.0 is available, otherwise False.
    """
    def check_chatgpt4o(self) -> None: ...

    """
Send a request to the ChatGPT web interface and receive a response.

**Arguments:**

* ``request``

  / *Condition*: required / *Type*: str /

  The request string to be sent to ChatGPT.

**Returns:**

  / *Type*: str /

  The response from ChatGPT.
    """
    def send_request(self, request: str) -> str: ...

    """
Click the 'Regenerate Response' button on the ChatGPT web interface.

This method simulates a click on the 'Regenerate Response' button to request a new response
for the current context.

**Returns:**

(*no returns*)
    """
    def click_regen(self) -> None: ...

"""
Extract JSON data from a given text string.

**Arguments:**

* ``text``

  / *Condition*: required / *Type*: str /

  The text string containing JSON data.

**Returns:**

  / *Type*: dict /

  A dictionary representation of the extracted JSON data.
"""
def extract_json(text: str) -> dict: ...

"""
Handle signals from the operating system.

**Arguments:**

* ``sig``

  / *Condition*: required / *Type*: int /

  The signal number received from the OS.

* ``frame``

  / *Condition*: required / *Type*: frame object /

  The current stack frame.

* ``obj``

  / *Condition*: required / *Type*: object /

  The object that is handling the signal.

**Returns:**

(*no returns*)
"""
def signal_handler(sig, frame, obj) -> None: ...
