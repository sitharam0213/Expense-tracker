from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm

# Register
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('expense_list')
    else:
        form = UserCreationForm()
    return render(request, 'expenses/register.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('expense_list')
    else:
        form = AuthenticationForm()
    return render(request, 'expenses/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Expense List + Search
@login_required(login_url='login')
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    if query:
        expenses = expenses.filter(title__icontains=query)
    if category:
        expenses = expenses.filter(category=category)

    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    form = ExpenseForm()

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'form': form,
        'total': total,
        'query': query,
        'category': category,
        'categories': ['Food', 'Transport', 'Shopping', 'Bills', 'Health', 'Other'],
    })

# Add Expense
@login_required(login_url='login')
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
    return redirect('expense_list')

# Delete Expense
@login_required(login_url='login')
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('expense_list')

# Edit Expense
@login_required(login_url='login')
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})