from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "00_4216_scene_insert"
CROP_RECT = (1024, 32, 3072, 1568)
BOARD_LOCAL = (666, 310, 1230, 688)


def main():
    source_crop = Image.open(JOB / "source_crop.png").convert("RGBA")
    generated = Image.open(JOB / "generated_attempt_1.png").convert("RGBA")
    registered = generated.resize(source_crop.size, Image.Resampling.LANCZOS)
    registered.save(JOB / "generated_attempt_1_registered.png")
    registered.crop(BOARD_LOCAL).save(ROOT / "review" / "4216_registered_board_candidate.png")


if __name__ == "__main__":
    main()
