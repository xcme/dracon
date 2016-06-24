#coding=UTF8

# Функция для транслитерации кириллицы из определяемой пользователем кодировки (cp1251 в данном примере)
def Translit(srcstr):
    try: new_str = unicode(srcstr,'cp1251')
    except: new_str = srcstr
    conversion = {
	u'\u0410' : 'A',    u'\u0430' : 'a',  u'\u0411' : 'B',    u'\u0431' : 'b',  u'\u0412' : 'V',    u'\u0432' : 'v',
	u'\u0413' : 'G',    u'\u0433' : 'g',  u'\u0414' : 'D',    u'\u0434' : 'd',  u'\u0415' : 'E',    u'\u0435' : 'e',
	u'\u0401' : 'Yo',   u'\u0451' : 'yo', u'\u0416' : 'Zh',   u'\u0436' : 'zh', u'\u0417' : 'Z',    u'\u0437' : 'z',
	u'\u0418' : 'I',    u'\u0438' : 'i',  u'\u0419' : 'Y',    u'\u0439' : 'y',  u'\u041a' : 'K',    u'\u043a' : 'k',
	u'\u041b' : 'L',    u'\u043b' : 'l',  u'\u041c' : 'M',    u'\u043c' : 'm',  u'\u041d' : 'N',    u'\u043d' : 'n',
	u'\u041e' : 'O',    u'\u043e' : 'o',  u'\u041f' : 'P',    u'\u043f' : 'p',  u'\u0420' : 'R',    u'\u0440' : 'r',
	u'\u0421' : 'S',    u'\u0441' : 's',  u'\u0422' : 'T',    u'\u0442' : 't',  u'\u0423' : 'U',    u'\u0443' : 'u',
	u'\u0424' : 'F',    u'\u0444' : 'f',  u'\u0425' : 'H',    u'\u0445' : 'h',  u'\u0426' : 'Ts',   u'\u0446' : 'ts',
	u'\u0427' : 'Ch',   u'\u0447' : 'ch', u'\u0428' : 'Sh',   u'\u0448' : 'sh', u'\u0429' : 'Sch',  u'\u0449' : 'sch',
	u'\u042a' : '"',    u'\u044a' : '"',  u'\u042b' : 'Y',    u'\u044b' : 'y',  u'\u042c' : '\'',   u'\u044c' : '\'',
	u'\u042d' : 'E',    u'\u044d' : 'e',  u'\u042e' : 'Yu',   u'\u044e' : 'yu', u'\u042f' : 'Ya',   u'\u044f' : 'ya',
    }
    translitstring = []
    for c in new_str:
	translitstring.append(conversion.setdefault(c, c))
    return ''.join(translitstring).encode("utf-8")

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

# Пользовательская функция: Получение транслитерированного значения поля custom до разделителя '|'
def fn_tr_cst1(src):
    return Translit(src.split('|')[0])

# Пользовательская функция: Получение транслитерированного значения поля custom после разделителя '|'
def fn_tr_cst2(src):
    return Translit(src.split('|')[1])

# Пользовательская функция: Транслитерация переданного значения
def fn_tr(src):
    return Translit(src)
