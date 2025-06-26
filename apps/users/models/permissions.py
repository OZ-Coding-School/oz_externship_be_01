from django.db import models


class PermissionsStudent(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="student_permissions")
    generation = models.ForeignKey("courses.Generation", on_delete=models.CASCADE, related_name="students")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permissions_student"


class PermissionsTrainingAssistant(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="ta_permissions")
    generation = models.ForeignKey("courses.Generation", on_delete=models.CASCADE, related_name="training_assistants")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permissions_ta"


class PermissionsStaff(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="staff_permissions")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="staffs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permissions_staff"
