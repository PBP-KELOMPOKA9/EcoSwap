from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Ulasan, FotoUlasan
from barang.models import Barang
from .forms import UlasanForm, FotoUlasanForm

@login_required(login_url='/admin/login/')
def daftar_ulasan(request, barang_id):
    barang = get_object_or_404(Barang, id=barang_id)
    
    if request.method == 'POST':
        ulasan_form = UlasanForm(request.POST)
        
        if ulasan_form.is_valid():
            ulasan_baru = ulasan_form.save(commit=False)
            ulasan_baru.barang = barang
            ulasan_baru.user = request.user
            ulasan_baru.save()

            files = request.FILES.getlist('gambar')
            for f in files:
                FotoUlasan.objects.create(ulasan=ulasan_baru, gambar=f)

            return redirect('ulasan:daftar_ulasan', barang_id=barang.id)
            
    else:
        ulasan_form = UlasanForm()
        foto_form = FotoUlasanForm()

    ulasan_list = Ulasan.objects.filter(barang=barang).annotate(
        like_count=Count('likes')
    ).order_by('-like_count', '-tanggal_dibuat')

    total_ulasan = ulasan_list.count()
    rata_rata = sum([u.rating for u in ulasan_list]) / total_ulasan if total_ulasan > 0 else 0
    
    bintang_stats = {
        '5': ulasan_list.filter(rating=5).count(),
        '4': ulasan_list.filter(rating=4).count(),
        '3': ulasan_list.filter(rating=3).count(),
        '2': ulasan_list.filter(rating=2).count(),
        '1': ulasan_list.filter(rating=1).count(),
    }

    context = {
        'barang': barang,
        'ulasan_list': ulasan_list,
        'total_ulasan': total_ulasan,
        'rata_rata': round(rata_rata, 1),
        'bintang_stats': bintang_stats,
        'ulasan_form': ulasan_form,
        'foto_form': foto_form,
    }
    
    return render(request, 'ulasan/daftar_ulasan.html', context)

@login_required(login_url='/admin/login/')
def edit_ulasan(request, ulasan_id):
    ulasan = get_object_or_404(Ulasan, id=ulasan_id)
    barang_id = ulasan.barang.id

    if request.user != ulasan.user:
        return redirect('ulasan:daftar_ulasan', barang_id=barang_id)

    if request.method == 'POST':
        form = UlasanForm(request.POST, instance=ulasan)
        if form.is_valid():
            form.save()
            
            deleted_ids = request.POST.get('deleted_images', '')
            if deleted_ids:
                id_list = [int(i) for i in deleted_ids.split(',') if i.isdigit()]
                FotoUlasan.objects.filter(id__in=id_list, ulasan=ulasan).delete()

            files = request.FILES.getlist('gambar')
            for f in files:
                FotoUlasan.objects.create(ulasan=ulasan, gambar=f)
                    
            return redirect('ulasan:daftar_ulasan', barang_id=barang_id)
    else:
        form = UlasanForm(instance=ulasan)

    context = {
        'form': form, 
        'barang_id': barang_id, 
        'ulasan': ulasan
    }
    return render(request, 'ulasan/edit_ulasan.html', context)

@login_required(login_url='/admin/login/')
def hapus_ulasan(request, ulasan_id):
    ulasan = get_object_or_404(Ulasan, id=ulasan_id)
    barang_id = ulasan.barang.id

    if request.user == ulasan.user:
        ulasan.delete()

    return redirect('ulasan:daftar_ulasan', barang_id=barang_id)

@login_required(login_url='/admin/login/')
def toggle_like(request, ulasan_id):
    if request.method == 'POST':
        ulasan = get_object_or_404(Ulasan, id=ulasan_id)
        
        if request.user in ulasan.likes.all():
            ulasan.likes.remove(request.user)
            liked = False
        else:
            ulasan.likes.add(request.user)
            liked = True
            
        return JsonResponse({
            'liked': liked,
            'total_likes': ulasan.total_likes
        })
        
    return JsonResponse({'error': 'Invalid request'}, status=400)