from django.db import models

# Create your models here.


class Page(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class SolverFeedback(models.Model):
    feedback = models.TextField()  # "Yes" or "No" or error message
    solution = models.TextField()

    def __str__(self):
        return f"Feedback: {self.feedback}, Solution: {self.solution[:20]}..."  # Display first 20 chars of the solution


class Message(models.Model):
    user_id = models.IntegerField()  # Assuming user ID is an integer
    message_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the message is created

    def __str__(self):
        return f"Message from User {self.user_id} at {self.timestamp}"


class EventSubmission(models.Model):
    event_id = models.CharField(max_length=100)
    event_name = models.CharField(max_length=100)
    scramble = models.TextField()
    user_solution = models.TextField()
    username = models.CharField(max_length=100)
    comment = models.TextField(blank=True, null=True)  # Optional comment field
    time_spent = models.IntegerField()  # time in seconds
    submitted_at = models.DateTimeField(auto_now_add=True)
    judge = models.TextField()
