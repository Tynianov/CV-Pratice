import cv2
import os
import sys
import numpy

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from person.models import Person
from person.views import convert_binary_to_array
from log_entry.models import LogEntry

from .models import PersonFingerprint
from .utils import get_descriptors, removedot


class FingerPrintRecognitionView(APIView):
    def post(self, request):
        if not request.FILES.get("image"):
            raise ValidationError({"file": "No file detected"})
        log_entry_data = {"authorization_type": LogEntry.FINGERPRINT}
        image = request.FILES.get("image")
        uploaded_image_path = "uploads/fingerprints"
        uploads_directory = os.path.join(settings.MEDIA_ROOT, uploaded_image_path)
        if not os.path.exists(uploads_directory):
            os.makedirs(uploads_directory)
        fs = FileSystemStorage(location=uploads_directory)
        filename = fs.save(image.name, image)
        img_path = os.path.join(uploaded_image_path, filename)
        log_entry_data["image"] = filename

        fingerprint_to_check = cv2.imread(
            os.path.join(settings.MEDIA_ROOT, img_path), cv2.IMREAD_GRAYSCALE
        )
        descriptors_to_check = get_descriptors(fingerprint_to_check)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        for fingerprint in PersonFingerprint.objects.all():
            know_fingerprint = cv2.imread(fingerprint.fingerprint.path, cv2.IMREAD_GRAYSCALE)
            know_descriptor = get_descriptors(know_fingerprint)

            matches = sorted(
                bf.match(descriptors_to_check, know_descriptor),
                key=lambda match: match.distance,
            )
            score = 0
            for match in matches:
                score += match.distance
            score_threshold = 33
            if score / len(matches) < score_threshold:
                name = f"{fingerprint.person.first_name} {fingerprint.person.last_name}"

                log_entry_data["person"] = fingerprint.person
                log_entry_data["result"] = True
                LogEntry.objects.create(**log_entry_data)

                return Response(
                    {"result": "We found matching fingerprint", "name": name},
                    status=HTTP_200_OK,
                )

        log_entry_data["result"] = False
        LogEntry.objects.create(**log_entry_data)
        return Response({"result": "No matches found"}, status=HTTP_404_NOT_FOUND)
