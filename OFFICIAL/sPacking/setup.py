import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 更多详细信息，请参见
# https://packaging.python.org/guides/distributing-packages-using-setuptools/
setuptools.setup(
    name="example-pkg-atomicoo",
    version="0.0.1",
    author="Atomicoo",
    author_email="atomicoo95@gmail.com",
    description="最小版Python包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atomicoo/packing_tutorial",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)