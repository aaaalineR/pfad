# Optional: run Stable Diffusion locally

This is an instructor demo and an optional follow-up, not a tutorial requirement.
It runs a pretrained Stable Diffusion 1.5 pipeline in Python and saves a 512 x 512
PNG. Diffusers connects the text encoder, denoiser, scheduler and VAE; PyTorch
runs the tensor operations. The weights stay fixed: this is inference, not training.

## Set up a separate environment

From the `pfad` repository root, with a recent `uv`:

```bash
cd week05/diffusion
uv venv --no-project --python 3.12
uv pip install --torch-backend auto -r requirements.txt
uv run --no-project generate.py --check
uv run --no-project generate.py
```

These commands work in a terminal on Linux, Windows or macOS. The separate
`.venv` and `--no-project` keep the Week 4 Worker environment out of this demo.
The scripts deliberately use this environment rather than declaring isolated
script dependencies. `--torch-backend` belongs to `uv pip install`, not `uv run`.
The first installation downloads large libraries; the first generation downloads
model weights from Hugging Face. Run both before class. The public model is not
gated at the time this example was prepared; no image API key is required.

`uv` selects a PyTorch build for the detected accelerator. It does not install
or repair the system GPU driver. On NVIDIA, the check should report `cuda`; a
working NVIDIA driver is required. PyTorch wheels supply the runtime libraries,
so running this pretrained pipeline does not normally require a separately
installed system CUDA toolkit. If automatic wheel selection is unsuitable, use
the [official uv/PyTorch guide](https://docs.astral.sh/uv/guides/integration/pytorch/)
to choose a backend compatible with the driver and the pinned PyTorch version.

If you expect NVIDIA acceleration for a live demo, require it explicitly:

```bash
uv run --no-project generate.py --check --device cuda
uv run --no-project generate.py --device cuda
```

An unavailable CUDA device then fails before downloading weights, instead of
falling back to a slower CPU run. Check the laptop's graphics/power mode as well
as the driver if a previously available GPU disappears.

The example chooses CUDA first, Apple Silicon MPS second, and CPU otherwise.
CUDA uses `float16`; MPS and CPU use `float32`. CPU generation may take several
minutes. Use the saved classroom example if downloading or generation would
interrupt the lesson. Hardware and memory requirements vary; 512 x 512 and one
image keep this example modest. Lowering the step count reduces denoising work,
but does not substantially reduce the memory needed for the model weights.

For a deliberate CPU run, install the CPU build and select the device:

```bash
uv pip install --torch-backend cpu --reinstall-package torch -r requirements.txt
uv run --no-project generate.py --device cpu
```

The reinstall flag also replaces an existing CUDA Torch build, whose version
otherwise already satisfies the pin. You can run `--device cpu` with the CUDA
build too; replacing the wheel is optional.

## Predict, run, inspect

The output is `week05/out/stable-diffusion-7.png`, with a JSON file recording the
prompt, model revision, package versions, device and settings. The model revision
is pinned so a repository update does not silently replace the weights.

Keep the prompt and settings fixed, then change only the seed:

```bash
uv run --no-project generate.py --seed 8
```

Compare the two saved images. Does the sphere remain centered? What happened to
the shadow and material? Next, keep the seed fixed and change one prompt phrase:

```bash
uv run --no-project generate.py --prompt "An orange paper sphere on cream paper, studio photograph, soft shadow, centered composition"
```

This overwrites the seed-7 result; keep a copy first if you want to compare it.
The seed controls starting randomness. Matching it helps repeat an experiment,
but does not promise identical pixels across hardware or library versions. A
new CPU generator is created for each run, following the
[Diffusers reproducibility guide](https://huggingface.co/docs/diffusers/en/using-diffusers/reusing_seeds).

## Checks without generating an image

```bash
uv run --no-project generate.py --check
uv run --no-project test_generate.py
```

These checks neither download model weights nor contact an image service. The
tests cover device selection and precision, especially full-precision CPU
fallback. The main Week 5 image/GIF exercises do not depend on this environment.

Model: [Stable Diffusion 1.5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5),
licensed under CreativeML Open RAIL-M. Read the model card for its limitations and
license; the saved example is an observed output, not a promise about every prompt.
