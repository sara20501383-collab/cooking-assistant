from django.shortcuts import render, redirect
from .models import Recipe
import requests

def find_recipe(request):
    user_input = ""
    ai_recipe = None
    results = []

    if request.method == 'POST':
        user_input = request.POST.get('ingredients', '')
        request.session['user_ingredients'] = user_input
        return redirect('find_recipe')

    if 'user_ingredients' in request.session:
        user_input = request.session['user_ingredients']
        user_items = set(item.strip() for item in user_input.replace('،', ',').split(',') if item.strip())
        
        # ۱. جستجو در دیتابیس (حافظه)
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            needed = set(item.strip() for item in recipe.required_ingredients.replace('،', ',').split(',') if item.strip())
            if needed.issubset(user_items):
                results.append(recipe)

        # ۲. اگر در دیتابیس نبود، هوش مصنوعی پیشنهاد می‌دهد
        if not results and user_input:
            try:
                prompt = f"""تو یک آشپز حرفه‌ای ایرانی هستی. من این مواد را در خانه دارم: {user_input}.
یک دستور پخت کامل، خوشمزه و کاملاً روان به زبان فارسی بنویس که فقط با همین مواد (و نمک، روغن و آب) قابل تهیه باشد.
لطفاً دستور پخت را با جزئیات کامل بنویس و از هیچ کلمه انگلیسی یا علامت ستاره (*) استفاده نکن.
جواب را دقیقاً در این قالب بنویس:
نام غذا: [نام غذا]
مواد لازم: [مواد لازم]
دستور پخت: [مراحل کامل]
"""
                # ====== کلید API خود را اینجا بگذارید ======
                API_KEY = "sk_9ZyKYFQP6HMCgh9pJCmnbP9EvTTMaSw8"
                # ==========================================
                
                url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}?key={API_KEY}"
                
                response = requests.get(url, timeout=60)
                if response.status_code == 200:
                    ai_recipe = {"text": response.text}
                else:
                    ai_recipe = {"error": f"خطا از سرور: {response.status_code}"}
            except Exception as e:
                ai_recipe = {"error": f"خطا: {str(e)}"}

    return render(request, 'kitchen/result.html', {
        'results': results,
        'user_input': user_input,
        'ai_recipe': ai_recipe,
    })

def menu(request):
    all_recipes = Recipe.objects.all()
    return render(request, 'kitchen/menu.html', {'recipes': all_recipes})
