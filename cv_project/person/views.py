import os
import cv2
from pickle import loads
import numpy as np
from io import BytesIO
import face_recognition

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .models import Person, PersonImage
from log_entry.models import LogEntry


class CompareFacesView(APIView):

    def post(self, request):
        if not request.FILES.get('image'):
            raise ValidationError({'file': 'No file detected'})
        log_entry_data = {
            'authorization_type': LogEntry.FACE
        }
        image = request.FILES.get('image')
        uploaded_image_path = 'uploads/faces'
        uploads_directory = os.path.join(settings.MEDIA_ROOT, uploaded_image_path)
        if not os.path.exists(uploads_directory):
            os.makedirs(uploads_directory)
        fs = FileSystemStorage(location=uploads_directory)
        filename = fs.save(image.name, image)
        img_path = os.path.join(uploaded_image_path, filename)
        log_entry_data['image'] = filename

        cv_image = cv2.imread(os.path.join(settings.MEDIA_ROOT, img_path))
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)
        known_faces = [self.convert_binary_to_array(face)
                       for face in PersonImage.objects.all().order_by('id').values_list('encoding', flat=True)]
        ids = PersonImage.objects.all().order_by('id').values_list('id', flat=True)
        names = []
        found = False
        for encoding in encodings:
            try:
                matches = face_recognition.compare_faces(known_faces, encoding)
                name = "Unknown"
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                if matchedIdxs:
                    found = True
                counts = {}
                for i in matchedIdxs:
                    person_image = PersonImage.objects.filter(id=ids[i]).first()
                    if person_image:
                        name = f'{person_image.person.first_name} {person_image.person.last_name}'
                        counts[name] = counts.get(name, 0) + 1
                        log_entry_data['person'] = person_image.person

                if counts:
                    name = max(counts, key=counts.get)

                # update the list of names
                names.append(name)
            except TypeError as e:
                print('Error during face comparison', e)

        log_entry_data['result'] = found
        LogEntry.objects.create(**log_entry_data)

        if found:
            return Response({'result': 'Found match', 'names': names})

        return Response({'result': 'No matches found'})

    def convert_binary_to_array(self, text):
        out = BytesIO(text)
        out.seek(0)
        return np.load(out, allow_pickle=True)[0]
