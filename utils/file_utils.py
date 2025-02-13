import os
import uuid
from werkzeug.utils import secure_filename

async def generate_unique_filename(filename):
    """Generate a unique filename while keeping the original extension."""
    unique_filename = str(uuid.uuid4())
    _, file_extension = os.path.splitext(filename)
    return f"{unique_filename}{file_extension}"