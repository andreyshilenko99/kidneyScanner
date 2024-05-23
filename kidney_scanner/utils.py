import numpy as np
from PIL import Image
from io import BytesIO
from ultralytics import YOLO


def process_image_and_get_bytes(config, decoded):
    model = YOLO(config['WEIGHTS_PATH'])

    yolo_outputs = model.predict(decoded)
    output = yolo_outputs[0]
    boxes = output.boxes
    # names = output.names
    coords = []

    for box in range(len(boxes)):
        # labels = names[boxes.cls[box].item()]
        # coordinates = boxes.xyxy[box].tolist()
        # confidence = np.round(boxes.conf[box].item(), 2)
        data_string = "0 " + " ".join(map(str, list(boxes.xywhn[box].cpu().numpy())))
        coords.append(data_string)

    img = output.plot()[:, :, ::-1]
    pil_image = Image.fromarray(img)
    byte_io = BytesIO()
    pil_image.save(byte_io, 'PNG')
    byte_io.seek(0)

    img_bytes = byte_io.getvalue()

    return img_bytes, coords
