import uuid
import os


def attachment_upload_to(instance, filename):
    """Rename uploaded attachment files to <uuid4>.<original_ext> for security."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"attachments/{uuid.uuid4().hex}.{ext}"
