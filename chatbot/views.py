from django.shortcuts import render
from django.http import JsonResponse
from .models import PDFDocument, ChatMessage
from .utils.pdf_processor import ChatBot
from django.views.decorators.csrf import csrf_exempt
import json

chatbot = ChatBot()

def chat_view(request):
    return render(request, 'chatbot/chat.html')

@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf'):
        pdf_file = request.FILES['pdf']
        document = PDFDocument.objects.create(file=pdf_file)
        response = chatbot.process_pdf(pdf_file)
        return JsonResponse({'message': response})
    return JsonResponse({'error': 'No PDF file received'}, status=400)

@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('message')
        context_type = data.get('context_type', 'general')  # 'general' or 'pdf'
        
        if question:
            response = chatbot.get_response(question, context_type)
            ChatMessage.objects.create(
                user_message=question,
                bot_response=response
            )
            return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)