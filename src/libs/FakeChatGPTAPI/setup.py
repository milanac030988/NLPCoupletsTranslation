from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [Extension("fake_chatgpt_api", ["fake_chatgpt_api.py"])]

setup(
    ext_modules = cythonize(extensions)
)