import cv2
import numpy as np

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from iris.iris_recognition.recognition import encode_photo
from iris.models import PersonIris
from log_entry.models import LogEntry


class IrisRecognizeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        image = request.FILES.get('image')

        if not image:
            return Response('Image required', status=400)

        if not image.name.endswith('.bmp'):
            return Response('Bmp image required', status=400)

        try:
            image_bytes = image.read()
            np_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)

            encoded_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(encoded_image, cv2.COLOR_BGR2RGB)
            code, mask = encode_photo(rgb)

            result = None
            percentage = 0
            for iris in PersonIris.objects.all():
                recognize = iris.compare_iris(code, mask)
                if recognize and recognize['percentage'] > percentage:
                    result = recognize
                    percentage = recognize['percentage']

            LogEntry.objects.create(authorization_type=LogEntry.IRIS, result=result is not None,
                                    person=result.get('person') if result is not None else None,
                                    percentage=percentage, image=image)

            if result:
                name = f"{result['person'].first_name} {result['person'].last_name}"
                return Response(
                        {"result": "We found matching iris", "name": name},
                        status=HTTP_200_OK,
                )
            return Response('Not Found', status=404)
        except Exception as e:
            print(e)
            return Response('Smth went wrong', status=400)
