# VirtuaLook: AI Virtual Try-On Engine

VirtuaLook is a state-of-the-art Virtual Try-On (VTON) platform driven entirely by local, offline Deep Learning models. 
Given a full-body photograph of a person and an image of a target garment, the system utilizes advanced Human Parsing and Diffusion Inpainting algorithms to generate a photorealistic composite image of the person wearing the garment.

This project focuses on the core Data Science and Computer Vision engineering required to orchestrate a Virtual Try-On pipeline, completely avoiding reliance on black-box third-party cloud APIs (such as Replicate).

## Core Architecture

The repository is structured as an end-to-end Machine Learning pipeline:

### 1. Human Parsing and Pose Estimation
Before garments can be synthesized, the system must understand the human body structure to avoid drawing clothes over faces or hands.
- We utilize MediaPipe to extract high-fidelity Pose Keypoints and Body Segmentation Masks.
- The system generates an "Agnostic Mask", isolating the torso while preserving the background and skin.

### 2. Diffusion Inpainting (Stable Diffusion / CatVTON)
The core generation is powered by a custom Stable Diffusion Inpainting pipeline.
- The system concatenates the target garment with the masked human image.
- By utilizing specialized Attention Modules (CatVTON), the model transfers the texture and structural geometry of the garment into the agnostic mask area, maintaining photorealistic lighting and folds.

## Directory Structure

```text
VirtuaLook/
├── src/
│   ├── data/             
│   ├── features/         
│   ├── models/           
│   └── pipeline/         
├── notebooks/            
├── backend/              
├── frontend/             
├── tests/                
├── pyproject.toml        
└── Makefile              
```

## Getting Started

### Data Science Environment (Model Prototyping)

The `notebooks/` directory contains step-by-step Jupyter Notebooks demonstrating the core Computer Vision tasks:
1. `01_VITON_HD_Data_Preparation.ipynb`: Preprocessing the VITON-HD paired dataset.
2. `02_Human_Parsing_and_Pose.ipynb`: Utilizing DensePose and MediaPipe for agnostic masking.
3. `03_Diffusion_Inpainting_and_TryOn.ipynb`: Fine-tuning and inference with the Diffusion model.

To setup the ML environment:
```bash
make install
make notebooks
```

### Application Deployment (FastAPI Backend)

The backend provides a REST API that directly interfaces with the local PyTorch pipeline. No internet connection is required for inference once the model weights are downloaded.

```bash
docker compose up --build
```

- Application Catalog: http://localhost:8000
- REST API Documentation: http://localhost:8000/docs

## Technical Highlights

- **Complete Offline Inference**: All processing, from Pose Extraction to Diffusion Generation, runs on local hardware. There are absolutely no calls to third-party endpoints.
- **Microservice Architecture**: The FastAPI backend decouples the heavy PyTorch inference loop from the User Interface, ensuring stability and scalability.
- **Extensible Pipeline**: The `TryOnPipeline` is designed modularly, allowing Data Scientists to easily swap out the Pose Extractor or the Diffusion Model with newer State-of-the-Art research implementations.
