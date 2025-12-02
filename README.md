# **OpenGeo**

OpenGeo is an open-source geospatial software suite designed to facilitate the processing, analysis, and visualization of geospatial data. It offers a comprehensive set of tools and libraries that cater to various geospatial needs, making it an invaluable resource for researchers, developers, and geospatial analysts.

## Conda environment

```
conda env create -f environment.yml
conda activate geo-env
```
or

```
conda create -n geo-env
conda activate geo-env
conda install -c conda-forge geopandas shapely rasterio fiona pyproj gdal pandas numpy matplotlib jupyterlab psutil tqdm

```
## Features
- Geospatial Data Processing: Efficient handling and processing of geospatial datasets.

- Analysis Tools: A suite of analytical tools for spatial data analysis.

- Extensibility: Easily extendable to integrate with other geospatial tools and libraries.

## **Download & Installation**
### Clone the Repository
To get started with OpenGeo on your local machine, use the following command:

```git clone https://github.com/lakshmikantakumar/OpenGeo.git```

```cd OpenGeo```
### Install Dependencies
Make sure you have Python installed (version 3.8 or higher is recommended). Then install the required Python packages:

```pip install -r requirements.txt```


## **Running the Scripts**
Each script in the OpenGeo repository is designed to be executed directly from the command line. You can get help and usage instructions for any script using the --help flag.

``` python <script_name>.py --help```


## **Disclaimer**

This code is provided "as is" without any warranties or guarantees regarding its correctness. Use at your own risk.
