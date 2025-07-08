from rest_framework import serializers


class FileListField(serializers.ListField):
    def to_internal_value(self, data):
        if data in ("", None, [""]) or data == "":
            return []
        return super().to_internal_value(data)
