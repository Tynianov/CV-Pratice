import os
import cv2
import face_recognition

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .models import Person, PersonImage


class CompareFacesView(APIView):

    def post(self, request):
        if not request.FILES.get('image'):
            raise ValidationError({'file': 'No file detected'})

        image = request.FILES.get('image')
        uploaded_image_path = 'uploads/faces'
        uploads_directory = os.path.join(settings.MEDIA_ROOT, uploaded_image_path)
        if not os.path.exists(uploads_directory):
            os.makedirs(uploads_directory)
        fs = FileSystemStorage(location=uploads_directory)
        filename = fs.save(image.name, image)
        img_path = os.path.join(uploaded_image_path, filename)
        cv_image = cv2.imread(os.path.join(settings.MEDIA_ROOT, img_path))
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)

        known_faces = PersonImage.objects.all().values_list('encoding', flat=True)
        ids = PersonImage.objects.all().values_list('id', flat=True)
        names = []

        for encoding in encodings:
            matches = face_recognition.compare_faces(known_faces, encoding)
            name = "Unknown"

            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    person_image = PersonImage.objects.filter(id=ids[i]).first()
                    if person_image:
                        name = f'{person_image.person.first_name} {person_image.person.last_name}'
                        counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)
        print(names)

        return Response({'names': names})