import cv2
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

        if not image or not image.endswith(settings.IRIS_EXTENSION):
            return Response('Invalid image', status=400)

        try:
            image = cv2.imread(image)
            code, mask = encode_photo(image)

            for person in Person.objects.iris():
                person.compare_iris(image, code, mask)
            PersonIrisCompare.objects.filter(person=self).delete()

            persons = PersonIrisCompare.objects.filter(person=self)
            serializer = PersonIrisCompareSerializer(persons, many=True)

            return Response(serializer.data, status=200)
        except Exception as e:
            return Response('Smth went wrong', status=400)
