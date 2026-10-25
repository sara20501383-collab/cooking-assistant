from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Recipe
import requests

def find_recipe(request):
    user_input = ""
    ai_recipe = None
    results = []

    # اگر درخواست از نوع POST بود (یعنی کاربر فرم را فرستاده)
    if request.method == 'POST':
        user_input = request.POST.get('ingredients', '')
        request.session['user_ingredients'] = user_input  # ذخیره در سشن
        return redirect('find_recipe')  # هدایت به همان صفحه (درخواست GET)

    # این بخش برای درخواست‌های GET اجرا می‌شود (چه بار اول، چه بعد از Redirect)
    if 'user_ingredients' in request.session:
        user_input = request.session['user_ingredients']
        
        user_items = set(item.strip() for item in user_input.replace('،', ',').split(',') if item.strip())
        
        # ۱. جستجو در دیتابیس
        all_recipes = Recipe.objects.all()
        for recipe in all_recipes:
            needed = set(item.strip() for item in recipe.required_ingredients.replace('،', ',').split(',') if item.strip())
            if needed.issubset(user_items):
                results.append(recipe)

        # ۲. اتصال به هوش مصنوعی (اگر در دیتابیس پیدا نشد)
        if not results and user_input:
            try:
                # سرویس Pollinations
                prompt = f"من این مواد را دارم: {user_input}. یک دستور پخت ساده و خوشمزه با همین مواد به من بده."
                url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}?key=کلید_API_خودت" # اگر کلید داری
                # یا بدون کلید:
                url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}"
                
                response = requests.get(url, timeout=60)
                if response.status_code == 200:
                    ai_recipe = {"text": response.text}
                else:
                    ai_recipe = {"error": f"خطا از سرور: {response.status_code}"}
            except Exception as e:
                ai_recipe = {"error": f"خطا: {str(e)}"}
        
        # بعد از نمایش نتیجه، سشن را پاک می‌کنیم تا با رفرش بعدی دوباره نمایش داده نشود
        # (این خط را می‌توانید حذف کنید اگر می‌خواهید نتیجه بعد از رفرش هم بماند)
        # del request.session['user_ingredients'] 

    return render(request, 'kitchen/result.html', {
        'results': results,
        'user_input': user_input,
        'ai_recipe': ai_recipe,
    })
