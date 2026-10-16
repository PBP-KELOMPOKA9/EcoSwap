from django import template

register = template.Library()


@register.filter
def rupiah(value):
    """75000 -> 'Rp75.000'."""
    try:
        angka = int(value)
    except (TypeError, ValueError):
        return value
    return 'Rp' + f'{angka:,}'.replace(',', '.')


@register.filter
def harga_label(barang):
    """'Gratis' untuk donasi, harga rupiah untuk jual."""
    if barang.is_donasi:
        return 'Gratis'
    return rupiah(barang.harga)


@register.filter
def inisial(user):
    nama = (user.get_full_name() or user.username or '?').split()
    return ''.join(n[0] for n in nama[:2]).upper()


@register.filter
def nama_tampil(user):
    full = user.get_full_name()
    if full:
        bagian = full.split()
        if len(bagian) > 1:
            return f'{bagian[0]} {bagian[1][0]}.'
        return bagian[0]
    return user.username
