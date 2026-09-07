"""Seed the Disease table with the 38 classes known by the model."""

from django.core.management.base import BaseCommand

from diseases.models import Disease

CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]


def prettify(raw_name):
    """Split "Tomato___Late_blight" into ("Tomato", "Late blight")."""

    plant, _, disease = raw_name.partition('___')

    plant = plant.replace('_', ' ').strip()
    disease = disease.replace('_', ' ').strip() or 'Unknown'

    return plant, disease


class Command(BaseCommand):
    help = 'Seed the Disease table with the model class names.'

    def handle(self, *args, **options):
        created_count = 0

        for raw_name in CLASS_NAMES:
            plant, disease = prettify(raw_name)

            is_healthy = disease.lower() == 'healthy'

            _, created = Disease.objects.update_or_create(
                name=raw_name,
                defaults={
                    'display_name': f'{plant} - {disease}',
                    'plant': plant,
                    'is_healthy': is_healthy,
                    'description': (
                        f'{plant} leaf classified as "{disease}" '
                        'by the Croply detection model.'
                    ),
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded diseases: {created_count} created, '
                f'{len(CLASS_NAMES) - created_count} already existed.'
            )
        )
