import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 更多详细信息，请参见
# https://packaging.python.org/guides/distributing-packages-using-setuptools/
setuptools.setup(
    name="sByterun",
    version="1.0",
    author="Atomicoo",
    author_email="atomicoo95@gmail.com",
    description="基于Python的简化版Python解释器，参考Byterun",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atomicoo/python_tutorials/FUNNY/sByterun",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)