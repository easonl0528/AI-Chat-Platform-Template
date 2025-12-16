from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="geo-optimizer",
    version="0.1.0",
    description="GEO优化工具：合规、路由、Prompt库与发布看板示例",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GEO Toolkit",
    packages=find_packages(),
    py_modules=["app", "server"],
    include_package_data=True,
    package_data={"geo_optimizer": ["static/*.html", "static/*.js", "static/*.css"]},
    install_requires=["Flask>=3.0.3"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "geo-optimizer=app:main",
            "geo-optimizer-web=server:main",
        ]
    },
)
