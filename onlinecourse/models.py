
from django.db import models
from django.conf import settings


class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user} - {self.course}"


class Question(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    content = models.CharField(max_length=200)
    grade = models.IntegerField(default=50)

    def __str__(self):
        return "Question: " + self.content

    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(
            is_correct=True
        ).count()

        selected_correct = self.choice_set.filter(
            is_correct=True,
            id__in=selected_ids
        ).count()

        return all_answers == selected_correct


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE
    )
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f"Submission {self.id}"
