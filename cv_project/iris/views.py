import cv2
import numpy as np

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from iris.iris_recognition.recognition import encode_photo
from iris.models import PersonIrisCompare
from iris.serializers import PersonIrisCompareSerializer
from person.models import Person


class IrisRecognizeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        image = request.FILES.get('image')

        if not image or not image.name.endswith(settings.IRIS_EXTENSION):
            return Response('Invalid image', status=400)

        # try:
        image_bytes = image.read()
        np_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)

        encoded_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        code, mask = encode_photo(encoded_image)

        for person in Person.objects.iris():
            person.compare_iris(image, code, mask)
            PersonIrisCompare.objects.filter(person=person).delete()

        persons = PersonIrisCompare.objects.filter()
        serializer = PersonIrisCompareSerializer(persons, many=True)

        return Response(serializer.data, status=200)
        # except Exception as e:
        #     print(e)
        #     return Response('Smth went wrong', status=400)
