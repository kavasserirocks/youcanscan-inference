# youcanscan-inference/

# --- main.py ---
import io
import torch
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from torchvision import transforms
from PIL import Image
import timm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class FrozenViTClassifier(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.vit = timm.create_model("vit_small_patch16_224", pretrained=True, num_classes=0)
        for param in self.vit.parameters():
            param.requires_grad = False
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(self.vit.num_features + 2, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(128, 1)
        )

    def forward(self, x, meta):
        with torch.no_grad():
            features = self.vit(x)
        combined = torch.cat([features, meta], dim=1)
        return self.classifier(combined)

# Load model
model = FrozenViTClassifier()
model.load_state_dict(torch.load("best_model_pades_transfer.pt", map_location=torch.device("cpu")))
model.eval()

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model.to(device)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

@app.post("/predict")
async def predict(
    image: UploadFile = File(...),
    gender: int = Form(...),
    age: int = Form(...)
):
    image_bytes = await image.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = transform(img).unsqueeze(0).to(device)
    meta_tensor = torch.tensor([[gender, age / 100.0]], dtype=torch.float32).to(device)

    with torch.no_grad():
        output = model(image_tensor, meta_tensor)
        prob = torch.sigmoid(output).item()
        label = "malignant" if prob >= 0.5 else "benign"

    return {
        "label": label,
        "confidence": round(prob, 4)
    }