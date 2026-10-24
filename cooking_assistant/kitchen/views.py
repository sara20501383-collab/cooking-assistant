from django.shortcuts import render
from .models import Recipe
import requests

def find_recipe(request):
    results = []
    user_input = ""
    ai_recipe = None

    if request.method == 'POST':
        user_input = request.POST.get('ingredients', '')
        user_items = set(item.strip() for item in user_input.replace('،', ',').split(',') if item.strip())
        
        # ۱. جستجو در دیتابیس
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            needed = set(item.strip() for item in recipe.required_ingredients.replace('،', ',').split(',') if item.strip())
            if needed.issubset(user_items):
                results.append(recipe)

        # ۲. اگر پیدا نشد، به هوش مصنوعی وصل شو (با سرویس واسط جدید)
        if not results and user_input:
         
            try:
                api_key = "sk_9ZyKYFQP6HMCgh9pJCmnbP9EvTTMaSw8"
                prompt = f"من این مواد را دارم: {user_input}. یک دستور پخت ساده و خوشمزه با همین مواد به من بده."
                
                # استفاده از آدرس جدید با کلید
                url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}?key={api_key}"
                
                response = requests.get(url, timeout=20)
                
                if response.status_code == 200:
                    ai_recipe = {"text": response.text}
                else:
                    ai_recipe = {"error": f"خطا از سرور: {response.status_code}"}
                
            except Exception as e:
                ai_recipe = {"error": f"خطا در ارتباط: {str(e)}"} 
            except Exception as e:
                ai_recipe = {"error": f"خطا در ارتباط: {str(e)}"}

    return render(request, 'kitchen/result.html', {
        'results': results,
        'user_input': user_input,
        'ai_recipe': ai_recipe,
    })