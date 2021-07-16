# How to train the model

## Introduction
This guide provides instructions how to train a tensorflow image classification model and to convert it to tflie so that it can be used on a Raspberry Pi.

You are supposed to do the training a your desktop.

## Contents
1. [Docker](#docker)
2. [VirtualEnv](#python-venv)

## Docker
You can use the prebuild tensorflow jupyter docker environment from https://hub.docker.com/r/jupyter/tensorflow-notebook.

To use the docker image execute this steps:
This has been tested on Ubuntu 20.04

1.  A computer with an NVIDIA GPU is required.
2.  Verify that the driver from NVIDIA is used 
3.  Install [Docker](https://get.docker.com/) version **1.10.0+**
 and [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**.
4.  Get access to your GPU via CUDA drivers within Docker containers.
    You can be sure that you can access your GPU within Docker, 
    if the command `docker run --gpus all nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04 nvidia-smi`
    returns a result similar to this one:
    ```bash
    Tue Jan  5 09:38:21 2021       
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 450.80.02    Driver Version: 450.80.02    CUDA Version: 10.1     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |                               |                      |               MIG M. |
    |===============================+======================+======================|
    |   0  GeForce RTX 207...  Off  | 00000000:01:00.0  On |                  N/A |
    |  0%   40C    P8     7W / 215W |    360MiB /  7974MiB |      1%      Default |
    |                               |                      |                  N/A |
    +-------------------------------+----------------------+----------------------+
                                                                                   
    +-----------------------------------------------------------------------------+
    | Processes:                                                                  |
    |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
    |        ID   ID                                                   Usage      |
    |=============================================================================|
    +-----------------------------------------------------------------------------+
    ``` 
    If you don't get an output similar than this one, follow the installation steps in this 
[medium article](https://medium.com/@christoph.schranz/set-up-your-own-gpu-based-jupyterlab-e0d45fcacf43).
    The CUDA toolkit is not required on the host system, as it will be 
    installed within the Docker containers using [NVIDIA-docker](https://github.com/NVIDIA/nvidia-docker).
    It is also important to keep your installed CUDA version in mind, when you pull images. 
    **You can't run images based on `nvidia/cuda:11.1` if you have only CUDA version 10.1 installed.**
    Check your host's CUDA-version with `nvcc --version` and update to at least 
    the same version you want to pull.
    
4. Pull and run the image. This can last some hours, as a whole data-science 
    environment will be downloaded:
   ```bash
   docker run --gpus all -d -it -p 8848:8888 -v $(pwd)/data:/home/jovyan/work -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes --user root cschranz/gpu-jupyter:v1.3_cuda-10.1_ubuntu-18.04_python-only
   ```
   This starts an instance with of *GPU-Jupyter* the tag `v1.3_cuda-10.1_ubuntu-18.04_python-only` at [http://localhost:8848](http://localhost:8848) (port `8484`).
   The default password is `gpu-jupyter` which should be changed as described [below](#set-password). 
   Furthermore, data within the host's `data` directory is shared with the container.
   Other versions of GPU-Jupyter are available and listed on Dockerhub under  [Tags](https://hub.docker.com/r/cschranz/gpu-jupyter/tags?page=1&ordering=last_updated).
   
5. Open the file TrainMowerModel.ipynb and run the content to train a new model

   
Within the Jupyterlab instance, you can check if you can access your GPU by opening a new terminal window and running
`nvidia-smi`. In terminal windows, you can also install new packages for your own projects. 
Some example code can be found in the repository under `extra/Getting_Started`.
If you want to learn more about Jupyterlab, check out this [tutorial](https://www.youtube.com/watch?v=7wfPqAyYADY).

Or use a [Google Tensorflow container](https://hub.docker.com/r/tensorflow/tensorflow/) 

## VirtualEnv

You can also use a Python virtual environment to run a script that trains a model

1. Python3 venv must be installed. If not run 'sudo apt install python3-venv'
2. Create a new virtual environment python3 -m venv ./training (See https://docs.python.org/3/library/venv.html)
3. Activate the venv source training/bin/activate
4. Install the requirements
	pip install --upgrade pip
	pip install tensorflow
	pip install opencv-python
	
	If you want local GPU Support see [GPU support](https://www.tensorflow.org/install/gpu?hl=de)
5. Run 'train.py' to create a tflite model
6. Test the model by running the 'detect_in_video.py' script



