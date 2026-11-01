from django.shortcuts import render, redirect
from .models import Recipe
import requests
import re

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
        
        # ۱. جستجو در دیتابیس
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            needed = set(item.strip() for item in recipe.required_ingredients.replace('،', ',').split(',') if item.strip())
            if needed.issubset(user_items):
                results.append(recipe)

        # ۲. اتصال به هوش مصنوعی
        if not results and user_input:
            try:
                prompt = f"""تو یک آشپز حرفه‌ای ایرانی هستی. من این مواد را در خانه دارم: {user_input}.
یک دستور پخت کامل، خوشمزه و با املای کاملاً صحیح فارسی بنویس که فقط با همین مواد (و نمک، روغن و آب) قابل تهیه باشد.
جواب را دقیقاً در این قالب بنویس:
نام غذا: [نام غذا]
مواد لازم: [مواد لازم]
دستور پخت: [مراحل کامل]
"""
                url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}"
                response = requests.get(url, timeout=60)
                
                if response.status_code == 200:
                    # ====== اصلاح خودکار غلط‌های املایی بدون کتابخانه اضافی ======
                    text = response.text
                    # تبدیل حروف عربی به فارسی
                    text = text.replace('ي', 'ی').replace('ك', 'ک')
                    # اصلاح نیم‌فاصله‌ها
                    text = re.sub(r'\bمی\s+(\w+)', r'می‌\1', text)
                    text = re.sub(r'\bنمی\s+(\w+)', r'نمی‌\1', text)
                    text = re.sub(r'(\w+)\s+ها\b', r'\1‌ها', text)
                    # حذف فاصله‌های اضافی
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    ai_recipe = {"text": text}
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
