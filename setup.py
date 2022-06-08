from setuptools import setup

setup(
    name="pickLayer",
    version="0.0.0.dev0",
    packages=["pickLayer"],
    package_data={
        "pickLayer": [
            "metadata.txt",
            "*.png",
            "*.svg",
            "*.ts",
            "*.ui",
        ],
    },
)
