from setuptools import setup, find_packages

setup(
    name="OpenGeo",
    version="0.1",
    packages=find_packages(),  
    install_requires=[  # Add dependencies here
        "numpy",  
        "rasterio",
        "numba",
        "gdal",
        
    ],
)
