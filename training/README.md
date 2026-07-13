# VirtuaLook Training Pipeline

This folder contains the training script to fine-tune your own Try-On attention layers or custom LoRA weights on your fashion dataset offline.

## 📁 Dataset Preparation

Your dataset directory should follow this structure:
```text
tryon_dataset/
├── person/
│   ├── person_01.jpg
│   └── person_02.jpg
└── garment/
    ├── person_01.jpg   # must have matching filenames to link pairs
    └── person_02.jpg
```
For advanced training (CatVTON or IDM-VTON), you also need mask images (`mask/` folder) which specify the region of the person's body to inpaint.

## 🚀 Running the Training Loop

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start training**:
   ```bash
   python train_tryon.py --dataset_path data/tryon_dataset --output_dir checkpoints --steps 5000
   ```

3. **Export & Connect to Backend**:
   Copy the resulting trained attention weights or safetensors to `services/vton/weights/` to load them locally during inference!
