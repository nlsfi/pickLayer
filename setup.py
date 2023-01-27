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
    install_requires=[
        "qgis_plugin_tools>=0.2.0",
    ],
)
