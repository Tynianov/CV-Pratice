import cv2
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from iris.iris_recognition.recognition import encode_photo
from person.models import Person


class IrisRecognizeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        image = request.POST.get('image')

        if not image.endswith(settings.IRIS_EXTENSION):
            return Response()

        try:
            image = cv2.imread(image)
            code, mask = encode_photo(image)
            result = [person.compare_iris(image, code, mask) for person in Person.objects.iris()]

        except Exception as e:
            return Response('Smth went wrong', status=400)
