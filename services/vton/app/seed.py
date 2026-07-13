import uuid
from sqlalchemy.orm import Session
from .models import Garment

SAMPLE_GARMENTS = [
    {
        "name": "White Classic T-Shirt",
        "category": "tops",
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80",
        "description": "A clean white cotton t-shirt, versatile and timeless.",
    },
    {
        "name": "Blue Denim Jacket",
        "category": "tops",
        "image_url": "https://images.unsplash.com/photo-1611312449408-fcece27cdbb7?w=400&q=80",
        "description": "Classic denim jacket with a relaxed fit.",
    },
    {
        "name": "Black Hoodie",
        "category": "tops",
        "image_url": "/storage/garments/black-hoodie.jpg",
        "description": "Comfortable oversized black hoodie.",
    },
    {
        "name": "Floral Summer Dress",
        "category": "dresses",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&q=80",
        "description": "Light floral print dress, perfect for summer.",
    },
    {
        "name": "Slim Fit Chinos",
        "category": "pants",
        "image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400&q=80",
        "description": "Beige slim fit chino trousers.",
    },
    {
        "name": "Striped Polo Shirt",
        "category": "tops",
        "image_url": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=400&q=80",
        "description": "Navy and white striped polo shirt.",
    },
]


def seed_garments(db: Session) -> None:
    if db.query(Garment).count() > 0:
        return
    for data in SAMPLE_GARMENTS:
        garment = Garment(id=uuid.uuid4().hex, **data)
        db.add(garment)
    db.commit()
