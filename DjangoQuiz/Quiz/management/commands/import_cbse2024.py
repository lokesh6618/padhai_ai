import csv, pathlib, random
from django.core.management.base import BaseCommand, CommandError
from Quiz.models import Question

class Command(BaseCommand):
    help = "Import the first 20 one‑mark questions of CBSE Maths 2024 (code 30‑1‑1)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="CSV file with uid, options, correct(1‑4)")

    def handle(self, *args, csv_path, **kwargs):
        base_img = pathlib.Path("media/math_2024_430_1_1_BASIC")

        try:
            with open(csv_path, newline="", encoding="utf8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    uid = row["uid"]

                    # ── locate the image ────────────────────────────────
                    img_path = base_img / f"{uid}.png"
                    if not img_path.exists():
                        raise CommandError(f"Image {img_path} not found")

                    # ── choose correct index ────────────────────────────
                    correct = row["correct"].strip()
                    if not correct:
                        correct = random.randint(1, 4)
                    correct = int(correct)

                    Question.objects.update_or_create(
                        uid=uid,
                        defaults={
                            "image"  : f"math_2024_430_1_1_BASIC/{uid}.png",
                            "op1"    : row["op1"],
                            "op2"    : row["op2"],
                            "op3"    : row["op3"],
                            "op4"    : row["op4"],
                            "correct": correct,
                        },
                    )
                    self.stdout.write(self.style.SUCCESS(f"✔ Imported {uid}"))
        except FileNotFoundError:
            raise CommandError("CSV file not found")

        self.stdout.write(self.style.SUCCESS("🎉  All questions imported"))
