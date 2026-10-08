"""Optional local Stable Diffusion demo; run after the separate uv setup."""

import argparse
import importlib.metadata
import json
import time
from pathlib import Path

import torch

MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
REVISION = "451f4fe16113bff5a5d2269ed5ad43b0592e9a14"
PROMPT = "An orange ceramic sphere on cream paper, studio photograph, soft shadow, centered composition"


def select_device(requested="auto"):
    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable. Check the driver and PyTorch build, or choose --device cpu.")
    if requested == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("Apple GPU acceleration is unavailable. Choose --device cpu.")
    return requested, torch.float16 if requested == "cuda" else torch.float32


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check the device without downloading a model")
    parser.add_argument("--device", choices=("auto", "cuda", "mps", "cpu"), default="auto")
    parser.add_argument("--prompt", default=PROMPT)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=20)
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("Use at least one inference step.")
    device, dtype = select_device(args.device)
    print(f"PyTorch {torch.__version__}; device={device}; dtype={dtype}", flush=True)
    if device == "cuda":
        print(torch.cuda.get_device_name(0), flush=True)
    if args.check:
        return
    if device == "cpu":
        print("CPU generation can take several minutes. Use the saved classroom result if needed.", flush=True)

    from diffusers import StableDiffusionPipeline

    started = time.perf_counter()
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL, revision=REVISION, dtype=dtype,
        variant="fp16" if device == "cuda" else None,
        use_safetensors=True,
    ).to(device)
    generator = torch.Generator(device="cpu").manual_seed(args.seed)
    image = pipe(
        args.prompt, num_inference_steps=args.steps,
        guidance_scale=7.5, width=512, height=512,
        generator=generator,
    ).images[0]

    output = Path(__file__).resolve().parents[1] / "out"
    output.mkdir(exist_ok=True)
    path = output / f"stable-diffusion-{args.seed}.png"
    image.save(path)
    metadata = {
        "model": MODEL, "revision": REVISION, "prompt": args.prompt,
        "seed": args.seed, "steps": args.steps, "guidance_scale": 7.5,
        "width": 512, "height": 512, "device": device, "dtype": str(dtype),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "versions": {name: importlib.metadata.version(name) for name in ("torch", "diffusers", "transformers", "accelerate")},
    }
    path.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {path} and its settings; {metadata['elapsed_seconds']} seconds including model loading.")


if __name__ == "__main__":
    main()
