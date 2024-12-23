from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
import threading
from .decode import *
from .models import *
from .decode import *  # Import the Celery task
import time
from datetime import datetime

def unix(date, time):
    combined_input = f"{date} {time}:00"  # Add seconds as ":00"
        
    # Parse the combined string to a datetime object
    dt = datetime.strptime(combined_input, "%Y-%m-%d %H:%M:%S")
    
    # Convert the datetime object to a Unix timestamp
    unix_time = int(dt.timestamp())
    print(f"Unix time: {unix_time}")
    return unix_time

def file_input(request):
    return render(request, 'input_file.html')

def input(request):
    if request.method == 'POST' and request.FILES.get('binary_input_file'):
        file = request.FILES['binary_input_file']
        start_time = request.POST['start_time']
        start_date = request.POST['start_date']
        time = unix(start_time.str(), start_date.str())

        # Create a unique task ID for tracking progress
        task_id = str(time.time()).replace('.', '')

        # Reset progress
        cache.set(f"progress_{task_id}", 0)

        # Run the decoder in a background thread
        threading.Thread(target=ccsds_decoder, args=(file, task_id, time)).start()

        # Return the task ID to the client for tracking
        return HttpResponse(f"""
                            Your file has been captured successfully. It is under processing and will be updated in database soon under task:
                            task_id: {task_id} <br>
                            For interactive graphs <a href="http://localhost:3000/goto/TMXKr9IHR?orgId=1"> visit here </a>
                            """)#JsonResponse({"task_id": task_id})

    return JsonResponse({"error": "No file provided"}, status=400)

def get_progress(request, task_id):
    # Retrieve progress from the cache
    progress = cache.get(f"progress_{task_id}", None)
    
    if progress is None:
        return JsonResponse({"error": "Task ID not found"}, status=404)
    
    return JsonResponse({"progress": progress})


