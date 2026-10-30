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

        # ۲. اگر در دیتابیس پیدا نشد، هوش مصنوعی پیشنهاد می‌دهد
        if not results and user_input:
            try:
                prompt = f"من این مواد غذایی را در خانه دارم: {user_input}. لطفاً یک دستور پخت ساده و خوشمزه که فقط با همین مواد قابل تهیه است، به من بده."
                url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}"
                
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
    # نمایش تمام غذاهای ذخیره شده در دیتابیس
    all_recipes = Recipe.objects.all()
    return render(request, 'kitchen/menu.html', {'recipes': all_recipes})
