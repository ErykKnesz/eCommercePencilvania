import os
from werkzeug.utils import secure_filename


def save_img(dest, form):
    f = form.image.data
    filename = secure_filename(f.filename)
    f.save(os.path.join(dest, filename))
    return filename
