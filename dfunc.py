#coding=UTF8

# Пользовательская функция: Получение hex-значения 2-го октета IP-адреса
def fn_2oct(src):
    try:
	return hex(int(src.split('.')[1]))[2:].zfill(2)
    except:
	return ""

# Пользовательская функция: Получение hex-значения 3-го октета IP-адреса
def fn_3oct(src):
    try:
	return hex(int(src.split('.')[2]))[2:].zfill(2)
    except:
	return ""

# Пользовательская функция: Получение hex-значения 3-го октета IP-адреса, увеличенного на единичку
def fn_3op1(src):
    try:
	return hex(int(src.split('.')[2])+1)[2:].zfill(2)
    except:
	return ""

# Пользовательская функция: Получение hex-значения номера порта
def fn_xp(n):
    try:
	return hex(int(n))[2:].zfill(2)
    except:
	return ""

# Пользовательская функция: Получение значений полей custom#
def fn_cst(src):
    return src
