import setuptools

setuptools.setup(
    name="mnist_classifier",
    version="0.1.0",
    description="Package containing mnist classifier with Sagemaker.",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["apache-airflow==2.3.2"],
    python_requires=">=3.7.*",
)
