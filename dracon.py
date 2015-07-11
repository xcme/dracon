#!/usr/local/bin/python2
#coding=UTF8
#version 0.9.9rc2 (2015.07.01)

import sys, socket, struct, logging, time, MySQLdb, hashlib, re, dfunc, bson, pymongo
from daemon import Daemon
from dconfig import interface, port, cycle_int, sleep_def, sleep_int
from dconfig import mysql_addr, mysql_user, mysql_pass, mysql_base
from dconfig import mysql_query_p, mysql_query_d, mongo_addr, mongo_user
from dconfig import mongo_pass, mongo_base, mongo_ucol, mongo_dcol, use_mongo
from dconfig import default_ports, fw_path, fw_names, cf_path, inc_cpage
from dconfig import dev_types, logfile, commands, helpinfo, ports_types
from dconfig import mags_list

logging.basicConfig(filename = logfile, level = logging.DEBUG, format = '%(asctime)s  %(message)s')

# --- Блок функций ---

# Функция для вычисления MD5 хеш-суммы
def md5(src):
    md5hash=hashlib.md5()
    md5hash.update(src)
    return md5hash.hexdigest()

# Функция для определния MD5 хеш-суммы и размера блока данных
def md5size(src):
    # Сортируем и склеиваем блоки данных
    data  =''.join([src[i] for i in sorted(src.keys())])
    # Возвращаем длину и значение MD5 блока данных
    return md5(data), len(data)

# Функция для получения даты и времени в двух форматах
def GetDTTM():
    # Получаем дату в формате unix timestamp
    dttm = int(time.time())
    # Возвращаем дату и в unix timestamp и в читабельном формате
    return dttm, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(dttm))

# Функция для преобразования IP адреса в Long IP
def ip2long(ip_addr):
    try: struct.unpack("!L", socket.inet_aton(ip_addr))
    except: return 0
    else: return struct.unpack("!L", socket.inet_aton(ip_addr))[0]

# Функция для определения имени файла ПО
def GetFWFileName(sw):
    # Если для данной модели есть запись возвращаем соответствующее имя файла
    if sw in fw_names.keys():
        return fw_names[sw]
    # А если нет, то возвращаем несуществующее имя
    else:
        return 'no_such_file'

# Функция получения информации об устройстве
def GetSWInfo(ip, devices):
    # Значения модели, адреса и пользовательского поля по умолчанию
    dtype='n/a'; custom1='n/a'; custom2='n/a'
    # Проверяем, есть ли IP устройства в словаре и есть ли соответствующий ID в словаре типов
    if (ip in devices): 
        if devices[ip]['dtype'] in dev_types:
	    # Получаем имя устройства по его типу
            dtype = dev_types[devices[ip]['dtype']]
	# Получаем адрес и пользовательское поле
        custom1 = devices[ip]['custom1']
        custom2 = devices[ip]['custom2']
    return dtype, custom1, custom2

# Функция для подготовки словаря портов
def PreparePorts(ports_tmp):
    # Создаем словарь для хранения результатов и его ключи
    ports = {}
    for line in ports_tmp:
        ports[line[0]]={}
    # Перебираем весь список с результатами MySQL-запроса. Результаты добавляем во временный словарь
    for line in ports_tmp:
        ports[line[0]].update({int(line[1]):{'ptype':line[2], 'comment1':Translit(line[3]), 'comment2':Translit(line[4])}})
    # Добавляем пустой набор портов в общий словарь
    ports.update(default_ports)
    # Словарь будет иметь вид {IP:{port:{'ptype':value, 'comment1':value, 'comment2':value},...}}.
    return ports

# Функция для получения списка устройств из базы MySQL
def GetDataFromMySQL(mysql_addr,mysql_user,mysql_pass,mysql_base,mysql_query,comment):
    try:
	# Пробуем подключиться к базе данных MySQL. Используем таймаут в 2 секунды
        mysql_db = MySQLdb.connect(host=mysql_addr, user=mysql_user, passwd=mysql_pass, db=mysql_base, connect_timeout=2)
    except MySQLdb.Error as err:
	# Если возникла ошибка при подключении, сообщаем об этом в лог и возвращаем пустой словарь
        logging.info("MySQL Error (%s): %s",mysql_addr,err.args[1]) 
        return {'0':0}
    else:
	# Если ошибок не было, сообщаем в лог об успешном подключении и создаем 'курсор' (особая, MySQLdb-шная магия)
        logging.info("Connection for MySQL Server '%s' (Read:'%s') established",mysql_addr,comment)
        mysql_cr = mysql_db.cursor()
        try:
	    # Пробуем выполнить запрос к базе
            mysql_cr.execute(mysql_query)
        except MySQLdb.Error as err:
	    # Если возникла ошибка при подключении, сообщаем об этом в лог и возвращаем пустой список
            logging.info("MySQL Read-Query (%s) failed: %s",comment,err.args[1]) # Пишем в лог об ошибке
            return [(0,0,0,'','')]
        else:
	    # Получаем все данные из 'курсора'
            mysql_data = mysql_cr.fetchall()
	    # Пишем в лог об успешном запросе
            logging.info("MySQL Read-Query (%s) OK. %s rows found",comment,len(mysql_data))
            return mysql_data

# Функция размещения полученной конфигурации в базе MongoDB
def PutConfigToMongoDB(mongo_addr, mongo_user, mongo_pass, mongo_base, mongo_coll, cfg, target, name, switch, ip, m5d):
    # Сортируем и склеиваем блоки данных
    cfg=''.join([cfg[i] for i in sorted(cfg.keys())])
    # Формируем данные для размещения их в MongoDB
    mongo_data={'date':GetDTTM()[0],'ip':ip2long(ip),'target':ip2long(target),'switch':switch,'name':name,'config':bson.binary.Binary(cfg),'hash':m5d}
    try:
	# Пробуем подключиться к серверу
	mongo_db = pymongo.MongoClient("mongodb://"+mongo_user+":"+mongo_pass+"@"+mongo_addr+"/"+mongo_base)
    except pymongo.errors.ConfigurationError, err:
	# Сообщаем в лог об ошибке подключения
	logging.info("MongDB Error (%s): %s",mongo_addr,err)
    else:
	# Если все хорошо, объявляем переменную-счетчик
        find_cnt=0
        try:
	    # Пробуем найти MD5-хеш в базе и подсчитываем сколько раз он там встречается
	    find_cnt=mongo_db[mongo_base][mongo_coll].find({'hash':m5d}).count()
        except:
	    # Обрабатываем исключение
	    find_cnt=-1
        if find_cnt==0:
	    # Если хеш в базе не найден и исключения не возникло:
            try:
		# Пробуем отправить данные
		insert_id=mongo_db[mongo_base][mongo_coll].insert(mongo_data)
            except pymongo.errors.OperationFailure, err:
		# Сообщаем лог об ошибке отправки
		logging.info("MongoDB Write Error: %s",err)
            else:
		# Или сообщаем об успешной операции
		logging.info("Succesfully sent %s bytes to MongoDB for '%s' ('%s'). Request from %s",len(cfg),target,switch,ip)
    finally:
	mongo_db.close()

# Функция получения последней конфигурации из базы MongoDB
def GetLastConfigFromMongoDB(mongo_addr, mongo_user, mongo_pass, mongo_base, mongo_coll, target):
    # По умолчанию конфиг пустой
    last_conf = ''
    try:
        # Пробуем подключиться к серверу
        mongo_db = pymongo.MongoClient("mongodb://"+mongo_user+":"+mongo_pass+"@"+mongo_addr+"/"+mongo_base)
    except pymongo.errors.ConfigurationError, err:
        # Сообщаем в лог об ошибке подключения
        logging.info("MongDB Error (%s): %s",mongo_addr,err)
    else:
        try:
            # Пробуем получить из базы последнюю запись для данного IP-адреса и затем получить значение поля 'config'
            last_conf = mongo_db[mongo_base][mongo_coll].find({'target':ip2long(target)}).sort('_id',-1).limit(1)
            last_conf = last_conf[0]['config']
        except:
	    last_conf = ''
    finally:
	mongo_db.close()
    return last_conf

# Функция для определения типа передачи, режима передачи, имени файла, номера блока, IP-адреса цели, типа данных и самих данных
def TFTP_Prepdata(tftpdata,ip):
    # Структура пакета при запросе: тип_пакета(2 байта)+имя_файла(ASCII-строка)+конец_строки(#00)+режим_передачи(ASCII-строка)+конец_строки(#00)
    # Пример: 0x0001+hexstr('config.cfg')+0x00+hexstr('octet')+0x00
    # Структура пакета при подтверждении блока: тип_пакета(2 байта)+номер_блока(2 байта)
    # Пример: 0x0004+0x0001
    # Перечисляем в словаре возможные значения типов пакета
    actions={1:'RRQ',2:'WRQ',3:'DATA',4:'ACK',5:'ERR',6:'ERR2'}
    # При этом обрабатывать будем только RRQ (чтение) и ACK (подтверждение приема)
    # Определяем значения переменных
    tftp_type='UNK'; transfer='unknown'; tftp_filename='unknown'; tftp_block=-1; target_ip=ip; data_type='config'; data_upl='';
    # Работаем только с блоками размером более 4 байт
    if len(tftpdata)>=4:
	# Если полученный тип пакета присутствует в списке, получаем из списка соответствующее значение
	if ord(tftpdata[1]) in actions:
	    tftp_type=actions[ord(tftpdata[1])]
	# Если тип запроса RRQ (чтение) или запись (WRQ) и указатель на конец строки присутствует и находится не в начале данных:
	if ((tftp_type=='RRQ') | (tftp_type=='WRQ')) & (tftpdata[2:].find(chr(0))!=-1):
	    # Пропускаем 2 знака, остаток разбиваем по chr(0) и получаем имя файла ('левая' часть деления)
	    name_tmp=tftpdata[2:].split(chr(0))[0]
	    # Пропускаем 2 знака, остаток разбиваем по chr(0) и получаем режим передачи ('правая' часть деления)
	    transfer=tftpdata[2:].split(chr(0))[1]
	    # Если в запрошенном файле присутствует символ '@', разбиваем имя на две части
	    if '@' in name_tmp:
		name_tmp=name_tmp.split('@')
		# IP-адресом считаем левую часть, а именем файла - правую часть
		if len(name_tmp[0])>0: target_ip=name_tmp[0]
		if len(name_tmp[1])>0: tftp_filename=name_tmp[1]
	    else:
		# Если '@' не присутствует, то имя файла не преобразовываем
		tftp_filename=name_tmp

	# Если тип запроса ACK или DATA и в данных есть еще хотя бы два байта, получаем номер блока из 3 и 4 символа (2 и 3 позиции)
	if ((tftp_type=='ACK') | (tftp_type=='DATA')) & (len(tftpdata)>=3):
	    tftp_block=ord(tftpdata[2])*256+ord(tftpdata[3])

	# Если тип запроса RRQ или WRQ, номер блока будет нулевым, что означает начало данных
	if ((tftp_type=='RRQ') | (tftp_type== 'WRQ')):
	    tftp_block=0

	# Если в типе передачи есть указатель на конец строки, получаем из данных тип передачи, убирая символы с кодом '0'
	if (transfer.find(chr(0))!=-1):
	    transfer=transfer.replace(chr(0),'')

	# Если запрошенное имя равно 'firmware', считаем, что у нас запросили ПО и указываем это в типе данных
	if (tftp_filename=='firmware'):
	    data_type='firmware'

	# Если запрошенное имя равно 'backup', считаем, что у нас запросили последнюю конфигурацию из базы MongoDB для конкретного IP, и указываем это в типе данных
	if (tftp_filename=='backup'):
	    data_type='backup'

	# Если тип запроса DATA и в данных есть еще хотя бы два байта, получаем данные (обрезать ethernet-трейлер не надо, этим занимаются другие уровни)
	if (tftp_type=='DATA') & (len(tftpdata)>=3):
	    data_upl=tftpdata[4:]

    return tftp_type, transfer, tftp_filename, tftp_block, target_ip, data_type, data_upl

# Функция для проверки корректности сетевого адреса ### Проверить нужна ли она вообще!!!
def GetOctets(custom1):
    # Отрезаем маску и получаем список октетов
    octets = custom1.split('/')[0].split('.')
    # Проверяем длину списка
    if len(octets) != 4:
        return False
    # Проверяем является ли октет допустимым числом
    for x in octets:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    # Возвращаем первые 3 октета, если все хорошо
    return octets[0], octets[1], octets[2]

# Функция, возвращающая список с типами портов и их диапазоном
def PStat(ports):
    # Функция получения диапазона портов
    def GetRange(ports_gr):
	# Получаем список ключей из словаря. При этом удаляем дубликаты (list(set())) и сортируем список
	_range = sorted(list(set(ports_gr.keys())))
	# Получаем два временных списка с ключами. Ключи - это номера портов. Первй спислк будет преобразован в диапазон, а второв возвращен без преобразования
	p_range = list(_range)
	full_p_range = list(_range)
	# Перебираем основной список, получая индекс элемента (i) и сам элемент (a)
	for i, a in enumerate(_range):
	    # Обрабатываем все элементы кроме минимального и максимального
	    # Если слева и справа от текущего номера идут последовательно, заменяем текущий элемент (который означает номер порта) на '*'
	    if ( a > min(_range) ) & ( a < max(_range) ):
		if ( a == _range[i-1] + 1 ) & ( a==_range[i+1] - 1 ):
		    p_range[i] = '*'
	# Из списка получаем строку, где элементы разделены запятыми, а '*' и ',-' заменены на '-'
	p_range=','.join(str(n) for n in p_range).replace('*,','-').replace(',-','-')
	# Удаляем двойные символы '-', заменяя их на одинарные
	while (p_range.find('--') != -1): p_range=p_range.replace('--','-')
	return {'range':p_range,'list':full_p_range}

    # 1 - абонентский порт, 2 - магистральный, 3 - сломанный, 4 - VIP-клиент, 5 - вход
    # 6 - нестандартный, 7 - оборудование, 8 - вход (патчкорд), 9 - магистраль (патчкорд)
    # Создаем результирующий словарь
    res_dict = {}
    # Проходим по всему списку типов (перебираем ключи)
    for pt in ports_types.keys():
	# Получаем временный словарь из переданного функции
	ports_tmp = dict(ports)
	# Перебираем основной словарь. 'p' - номер порта. Задача: оставить порты только нужного типа
	for p in ports:
	    # Если тип порта для основного словаря не равен определенному типу, удаляем соответствующий элемент во временном словаре
	    if ( ports[p]['ptype'] != pt ): del ports_tmp[p]
	res_dict[ports_types[pt]] = GetRange(ports_tmp)
    ports_tmp = dict(ports)
    # Получаем диапазон и список вообще всех портов
    res_dict['all'] = GetRange(ports_tmp)
    # Во временном списке оставляем порты с типом 2, 5, 8 и 9
    for p in ports:
	if ( int(ports[p]['ptype'] ) not in mags_list): del ports_tmp[p]
    # Получаем диапазон и список магистральных портов
    res_dict['mags'] = GetRange(ports_tmp)
    return res_dict

# Функция для транслитерации кириллицы в из определяемой пользователем кодировки
def Translit(srcstr):
    try: new_str = unicode(srcstr,inc_cpage)
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

# Функция подготовки данных
def GetData(ip,target,fname,sw,custom1,ports,custom2,transfer,data_type):
    # Определяем размер блока данных и объявляем переменную для хранения данных
    block_size = 512
    data = ''

    # Работаем, если запрошено ПО и имя файла указано
    if ( data_type == 'firmware' ) & ( GetFWFileName(sw) != 'no_such_file' ):
	# Если тип передачи 'octet' (без изменений)...
	if ( transfer == 'octet' ):
	    try:
		# ... пытаемся открыть файл
		fw_file = open(fw_path+GetFWFileName(sw),'r')
	    except:
		# Если не удалось - помещаем сообщение об ошибке в данные и пишем об этом в лог
		data = "# ERROR: Cannot open file %s%s" % (fw_path,GetFWFileName(sw))
		logging.info("ERROR: Cannot open file '%s%s'!",fw_path,GetFWFileName(sw))
	    else:
		# Если все хорошо - читаем файл
		data = fw_file.read()
		fw_file.close()
	else:
	    # Если тип передачи отличен от 'octet', помещаем в данные сообщение об необходимости изменить тип
	    data = "# Please, set transfer type to 'octet' (-i)!"

    # Получаем данные, если запрошен backup последней конфигурации
    if data_type == 'backup':
	data = GetLastConfigFromMongoDB(mongo_addr, mongo_user, mongo_pass, mongo_base, mongo_ucol, target)

    # Работаем, если запрошена конфигурация и устройство определено
    if ( (data_type == 'config') & (target != '0.0.0.0' )):
	# Если имя файла (которое является и командой) присутствует в наборе списков команд:
	if fname in commands.keys():
	    try:
		cf_file = file(cf_path+sw,'rt')
		cf_data = cf_file.read().split(':::')
		cf_file.close()
		cf_data = dict(cf_data[i:i+2] for i in range(1, len(cf_data), 2))
	    except:
		cf_data = ''
		logging.info("ERROR: Cannot open file '%s%s' or this file is incorrect!",cf_path,sw)

	    # Получаем диапазоны и списки портов в зависимости от их статуса
	    p_stats = PStat(ports)
	    # Шаблон для поиска конструкций вида [ss#1]
	    reg_x  = re.compile(r"(\[(?P<k>[a-zA-Z]+)\#(?P<v>\d+)\])")
	    # Шаблон для поиска конструкций вида [ss]
	    reg_nx = re.compile(r"(\[(?P<val>\S+)\])",re.IGNORECASE|re.DOTALL)
	    # Шаблон для поиска конструкций вида (fn#1)
	    reg_fn = re.compile(r"(\((?P<k>[a-zA-Z_0-9]+)\#(?P<v>[a-zA-Z_0-9]+)\))")

	    # Перебираем все команды внутри списка для данной команды
	    for cmd in commands[fname]:
		if cmd in cf_data:
		    # Находим для команды (имени файла) соответствующий блок, разбираем его на строки и перебираем их все
		    for cf_line in cf_data[cmd].split("\n"):
			# Получаем копию текущей строки, которую модернизируем при наличии в ней шаблонов
			new_cf_line = cf_line

			# Пробуем заменить подставить IP-адрес цели в шаблон {$target}
			if '{$target}' in new_cf_line:
			    try:
				new_cf_line = new_cf_line.replace('{$target}', target)
			    except:
				pass

			# Здесь выражение вида "config ports [ss#1] state enable" разбирается на список кортежей вида [('[ss#1]', 'ss', '1')]
			# Индекс [0] указывает на исходное значение в строке, [1] - на имя списка и [2] - на _значение_ (не индекс!) внутри списка
			# Если замена или вызов функции были неудачными, то строка "комментируется" - добавляется символ '#'
			for p_list in reg_x.findall(new_cf_line):
			    p_check = p_list[0]
			    try:
				# Если искомое значение присутствует внутри найденного списка, запоминаем это значение
				if int(p_list[2]) in p_stats[p_list[1]]['list']:
				    p_check = p_list[2]
			    except:
				new_cf_line = "#"+new_cf_line
			    # Заменяем шаблон на диапазон портов (если он был распознан) или на сам шаблон (то есть ничего не поменяется)
			    new_cf_line = new_cf_line.replace(p_list[0],p_check)

			# Разбираем выражение вида "config ports [ss] state enable" на список кортежей [('[ss]','ss'),..]. В большинстве случаев в списке будет один элемент.
			for p_range in reg_nx.findall(new_cf_line):
			    p_check = p_range[0]
			    try:
				# Если у диапазона ненулевая длина, запоминаем его значение, иначе "комментируем строку"
				if len(p_stats[p_range[1]]['range']) > 0:
				    p_check = p_stats[p_range[1]]['range']
				else:
				    new_cf_line = "#"+new_cf_line
			    except:
				new_cf_line = "#"+new_cf_line
			    # Заменяем шаблон на диапазон портов (если он был распознан) или на сам шаблон (то есть ничего не поменяется)
			    new_cf_line = new_cf_line.replace(p_range[0],p_check)

			# Аналогично первому случаю разбираем строку для поиска пользовательских функций по шаблону (fn#1)
			for fn_list in reg_fn.findall(new_cf_line):
			    # Проверяем, начинается ли пользовательская функция на 'fn_'
			    if fn_list[1][0:3] == 'fn_':
				# Определяем параметр пользовательской функции. Если используются зарезервированные слова, работаем с ними, иначе получаем параметр из запроса.
				fn_param = fn_list[2]
				if fn_list[2] == 'custom1':
				    fn_param = custom1
				if fn_list[2] == 'custom2':
				    fn_param = custom2
				try:
				    # Пробуем применить пользовательскую функцию. Имя функции получаем из шаблона. Сами функции хранятся в модуле dfunc.
				    new_cf_line = new_cf_line.replace(fn_list[0],getattr(dfunc,fn_list[1])(fn_param))
				except:
				    new_cf_line = "#"+new_cf_line

			    # Выполняем проверки на случай использования функций для получения 'comment1' и 'comment2'
			    elif fn_list[1][0:8] == 'comment1':
				try:
				    new_cf_line = new_cf_line.replace(fn_list[0],ports[int(fn_list[2])]['comment1'])
				except:
				    new_cf_line = "#"+new_cf_line

			    elif fn_list[1][0:8] == 'comment2':
				try:
				    new_cf_line = new_cf_line.replace(fn_list[0],ports[int(fn_list[2])]['comment2'])
				except:
				    new_cf_line = "#"+new_cf_line

			    else:
				# При использовании функций с нестандартными именами (начинается не с 'fn_' или 'cmt') также комментируем строку
				new_cf_line = "#"+new_cf_line

			data += new_cf_line+"\n"

    # Получаем контрольную сумму для данных
    m5d = md5(data)

    # Если цель не определена и запрошена "Справка", возвращаем краткую справку
    if ( (target == '0.0.0.0') & (fname=='help') ):
	data = helpinfo

    data_items=(lambda c, l: int(float(c)/l>=c//l)+c/l)(len(data),block_size) # Получаем количество блоков по 512 байт
    # Если длина данных кратна 512, добавляем 1 значение к общему количеству. Пример: для 1024 получаем 3
    # Разбиваем данные на блоки по 512 байт, нумеруя их
    data_list={i+1:data[x:x+block_size] for i,x in enumerate(xrange(0, len(data), block_size))}
    # Если ожидаем больше, чем получили, добавляем пустой элемент
    if data_items>len(data_list): data_list[len(data_list)+1]=''
    # Вставляем первый элемент, где указываем общее количество блоков
    data_list[0]=data_items

    # Примечание №1: Последним блоком данных при передаче считается блок меньше 512 символов.
    # Если же общая длина блоков кратна 512 символам, то последний блок никак не отличается от других
    # Для этого и добавляется блок, имеющий нулевую длину
    # Примечание №2: Минимальный ethernet-фрейма равен 60 байтам. Но здесь беспокоиться об этом не нужно.
    # При длине блока меньше 14 python при передаче UDP-датаграмы заполнит недостающие байты нулями
    return data_list, m5d


# --- Конец блока функций ---

# ------- Основной блок -------
def main():
    logging.info("Daemon 'Dracon' started...")
    # Получаем начальные значение таймера перезапуска и таймера опроса сокета, равные текущему времени в unix timestamp
    timer   = int(time.time())
    sltimer = int(time.time())
    # Устанавливаем паузу при опросе UDP-сокета по умолчанию
    sleeptime = sleep_def
    # Объявляем начальные значение для счетчиков запросов 'read' и 'write'
    tftp_rcnt = 0; tftp_wcnt = 0

    # Получаем информацию о портах устройств из базы данных
    ports_tmp = GetDataFromMySQL(mysql_addr,mysql_user,mysql_pass,mysql_base,mysql_query_p,'*Select ports*')
    # Получаем список портов
    ports = PreparePorts(ports_tmp)
    # Получаем информацию о коммутаторах из базы данных
    devices_tmp = GetDataFromMySQL(mysql_addr,mysql_user,mysql_pass,mysql_base,mysql_query_d,'*Select devices*')
    # Формируем словарь вида {ip:{type:val,custom1:val,custom2:val}}
    devices = {item[0]:{'dtype':item[1],'custom1':Translit(item[2]),'custom2':Translit(item[3])} for item in list(devices_tmp)}

    # Объявляем словарь для хранения данных и других параметров
    cfg_fw = {}
    # Объявляем словарь для хранения полученных данных с устройства. Сюда попадет конфигурация, которую отправит коммутатор
    cfg_up = {}

    # Создаем сокет для tftp
    tftp  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Пробуем открыть сокет и обрабатываем возможную ошибку
    try:
	tftp.bind((interface,port))
    # При возникновении ошибки делаем запись в логе и завершаем работу
    except socket.error as err:
	logging.info("Socket Error: %s Exiting...", err.args[1])
	sys.exit(2)
    # При отсутствии ошибки переводим сокет в режим non blocking
    else:
	tftp.setblocking(0) 

    # Дальше работаем в бесконечном цикле
    while True:
	# Проверяем, прошло ли достаточно времени с момента предыдущего запроса
	if (int(time.time())-timer >= cycle_int):
	    # Пишем в лог о количестве запросов за прошедшее время
	    logging.info('Requests for %s seconds: RRQ (download) - %s, WRQ (upload) - %s', cycle_int, tftp_rcnt, tftp_wcnt)
	    # Обнуляем счетчики и получаем новое значение таймера
	    tftp_rcnt=0; tftp_wcnt = 0
	    timer = int(time.time())

	    # Делаем новый запрос в базу для получения информации о портах
	    ports_tmp = GetDataFromMySQL(mysql_addr,mysql_user,mysql_pass,mysql_base,mysql_query_p,'*Select ports*')
	    # Если длина запроса составляет не менее 90% от длины предыдущего, то помещаем новый список портов в основной список
	    # Хоть мы и сравниваем словари разной структуры, но такое сравнение корректно, т.к. количество ключей в 'ports' и строк в 'ports_tmp' одинаково
	    if (len(ports_tmp) > len(ports)*0.9):
		ports = PreparePorts(ports_tmp)

	    # Получаем информацию о коммутаторах из базы данных
	    devices_tmp = GetDataFromMySQL(mysql_addr,mysql_user,mysql_pass,mysql_base,mysql_query_d,'*Select devices*')
	    # Если длина запроса составляет не менее 90% от длины предыдущего, то помещаем новый список устройств в основной список
	    if (len(devices_tmp) > len(devices)*0.9):
		devices={item[0]:{'dtype':item[1],'custom1':item[2],'custom2':Translit(item[3])} for item in list(devices_tmp)}

	# Пробуем получить данные с сокета (2 байта для типа передачи, 2 байта для номера блока и еще 512 для данных)
	try: tftpdata, tftpaddr = tftp.recvfrom(516)
	# Если данных нет возникнет ошибка
	except:
	    # Проверяем, достаточно ли долго не обновлялась переменная (не поступали данные) и устанавливаем паузу при опросе UDP-сокета по умолчанию
	    if (int(time.time())-sltimer >= sleep_int):
		sleeptime=sleep_def
	# Если ошибки не возникло, значит данные получены. Приступаем к их обработке
	else:
	    # IP-адрес удаленного хоста
	    rem_ip  =tftpaddr[0]
	    # Порт удаленного хоста
	    rem_port=tftpaddr[1]
	    # Определяем тип передачи, режим передачи, имя файла, номер блока, IP коммутатора, для которого запрошены данные, тип данных и сами данные (они есть при DATA-пакетах)
	    tftp_type, transfer, tftp_filename, tftp_block, target_ip, data_type, data_upl = TFTP_Prepdata(tftpdata,tftpaddr[0])
	    # Для общего случая определяем назначение - 'IP_отправителя:Port' - и цель - 'IP_устройства (модель_устройства)'
	    dip="%s:%s" % (rem_ip, rem_port)
	    dev="'%s' (%s)" % (target_ip, GetSWInfo(target_ip,devices)[0])
	    # В остальных случаях цель и модель попадают в словарь, с которым и ведется работа в дальнейшем. То есть dev может переопределяться ниже

	    if (tftp_type in ['RRQ','WRQ','ACK','DATA']):
		# Если получен известный тип данных, уменьшаем паузу при опросе UDP-совера и получаем новое значение таймера
		sleeptime=sleep_def/1000
		sltimer = int(time.time())

	    # Если пришел запрос на чтение, увеличиваем значение счетчика полученных запросов (R) и пишем в лог о полученной запросе
	    if (tftp_type=='RRQ'):
		tftp_rcnt += 1
		logging.info("-->Request (RRQ) from %s for device %s. Requested   file: '%s'", dip, dev, tftp_filename)
		# Пример: -->Request (RRQ) from '10.137.130.56:52843' for device '10.99.0.2' (DES-3200-28). Requested   file: 'cfg'

		# Можно запросить данные для произвольного устройства, но отдать - только для имеющегося. Потому на выходе может быть только реальный IP
		# Если коммутатора с IP назначения нет в списке и запрошена конфигурация, используем IP для коммутатора по умолчанию (0.0.0.0)
		if (target_ip not in ports) & (data_type=='config'): target_ip='0.0.0.0'
		# Если запрошено ПО, то данные о портах не нужны, но нужна модель устройства, поэтому не обнуляем IP

		# Получаем имя (модель), сеть и адрес удаленного устройства
		rem_dev, rem_cust1, rem_cust2 = GetSWInfo(target_ip,devices)
		# Если запрошена конфигурация, получаем данные в виде блоков и их MD5-сумму (от целой части без блоков)
		if (data_type == 'config'):
		    cfg_tmp, md5_tmp = GetData(rem_ip,target_ip,tftp_filename,rem_dev,rem_cust1,ports[target_ip],rem_cust2,transfer,data_type)

		# Если запрошено ПО или backup конфигурации, то проделываем то же самое, но вместо портов передаем пустой список
		if ( (data_type == 'firmware') or (data_type == 'backup') ):
		    cfg_tmp, md5_tmp = GetData(rem_ip,target_ip,tftp_filename,rem_dev,rem_cust1,[],              rem_cust2,transfer,data_type)

		# Если для удаленного хоста данные уже определены, обновляем их. В противном случае - добавляем
		if rem_ip in cfg_fw.keys():
		    cfg_fw[rem_ip].update({rem_port:{'data':cfg_tmp,'type':data_type,'md5':md5_tmp,'file':tftp_filename,'target':target_ip,'switch':rem_dev}})
		else:
		    cfg_fw[rem_ip]    =   {rem_port:{'data':cfg_tmp,'type':data_type,'md5':md5_tmp,'file':tftp_filename,'target':target_ip,'switch':rem_dev}}
		# На выходе получается словарь словарей вида {IP:{Remote_Port:{'data','md5','file','target','switch'}}}
		# Это нужно как для удобства получения информации, так и для одновременной передачи. Для каждой сессии передачи в словаре хранится своя информация

	    # Если пришло подтверждение передачи, проверяем, существуют ли данные для текущего соединения
	    if (tftp_type=='ACK') & (tftp_block in xrange(0,65536)):
		try:
		    cfg_fw[rem_ip][rem_port]['data'][tftp_block]
		# Обрабатываем ситуацию, когда данных нет. Такая ситуация может быть, если пакет с RRQ не попал на сервер:
		except:
		    logging.info('ERROR: Retrieving data (ACK) without request (RRQ) for %s for device %s for block %s!', dip, dev, tftp_block)

	    # Проверяем, существует ли данные для данного соединения. Если да - получаем количество блоков
	    try:
		cfg_fw[rem_ip][rem_port]['data'][0]
	    except:
		total_blocks=-1
	    else:
		total_blocks=cfg_fw[rem_ip][rem_port]['data'][0]

	    # Если блок меньше общего количество блоков и ожидается передача, тогда начинаем передачу. Если данных еще не существует, то условие не выполнится (-1<-1)
	    if (tftp_block<total_blocks) & ((tftp_type=='RRQ') | (tftp_type=='ACK')):
		# Пробуем отправить данные
		try:
		    tftp.sendto(chr(0)+chr(3)+(lambda x: chr(x//256)+chr(x%256))(tftp_block+1)+str(cfg_fw[rem_ip][rem_port]['data'][tftp_block+1]),(rem_ip,rem_port))
		# Обрабатываем возможную ошибку сокета, делаем запись в логе и завершаем работу
		except socket.error as err:
		    logging.info("Socket Error (DATA): %s. Exiting...", err.args[1])
		    sys.exit(2)
		else:
		    # Если тип 'RRQ', т.е. передача только начинается
		    if (tftp_type=='RRQ'):
			# IP-адрес и модель устройства
			dev="'%s' (%s)" % (cfg_fw[rem_ip][rem_port]['target'],cfg_fw[rem_ip][rem_port]['switch'])
			# Имя передаваемого файла
			fil="'%s'" % (cfg_fw[rem_ip][rem_port]['file'])
			# Если запрошено ПО определяем новое название файла
			if (cfg_fw[rem_ip][rem_port]['type']=='firmware'): fil="'%s'" % (GetFWFileName(cfg_fw[rem_ip][rem_port]['switch']))
			# Контрольная хеш-сумма
			m5d=cfg_fw[rem_ip][rem_port]['md5']
			# Пишем в лог о старте передачи
			logging.info('<--Sending data  to   %s for device %s. Prerared    file: %s, md5: %s', dip, dev, fil, m5d)
			# Пример:     <--Sending data  to   '10.137.130.56:52843' for device '10.99.0.2' (DES-3200-28). Prerared    file: 'cfg', md5: c6c253ff4110f77b917901bb89d762df

		    # Обрабатываем ситуацию, когда мы получили подтверждение от предпоследнего блока и только что отправили последний
		    if (tftp_block==total_blocks-1):
			# IP-адрес и модель устройства
			dev="'%s' (%s)" % (cfg_fw[rem_ip][rem_port]['target'],cfg_fw[rem_ip][rem_port]['switch'])
			# Имя передаваемого файла
			fil="'%s'" % (cfg_fw[rem_ip][rem_port]['file'])
			# Если запрошено ПО определяем новое название файла
			if (cfg_fw[rem_ip][rem_port]['type']=='firmware'): fil="'%s'" % (GetFWFileName(cfg_fw[rem_ip][rem_port]['switch']))
			# Общее количество блоков
			blk=str(tftp_block+1)
			# Получаем копию данных
			tmp_dct=cfg_fw[rem_ip][rem_port]['data'].copy()
			# Удаляем первый (нулевой) элемент с длиной словаря
			tmp_dct.pop(0)
			# Получаем MD5-сумму и размер полученных данных
			m5d, fln = md5size(tmp_dct)
			# Очищаем временный словарь
			tmp_dct.clear()
			# Пишем в лог об окончании передачи
			logging.info('Successfully sent to  %s for device %s. Transferred file: %s. Size: %s, blocks: %s', dip, dev, fil, fln, blk)
			# Пример:         Successfully sent to  '10.137.130.56:52843' for device '10.99.0.2' (DES-3200-28). Transferred file: 'cfg', blocks: 1

	    # Если получено подтверждение передачи последнего блока:
	    if (tftp_block==total_blocks) & (tftp_type=='ACK'):
		# Если была выгружена конфигурация, помещаем еще в базу данных:
		if (cfg_fw[rem_ip][rem_port]['type']=='config'):
		    # Получаем копию данных
		    tmp_dct=cfg_fw[rem_ip][rem_port]['data'].copy()
		    # Удаляем первый (нулевой) элемент с длиной словаря
		    tmp_dct.pop(0)
		    # Цель
		    tmp_tgt=cfg_fw[rem_ip][rem_port]['target']
		    # Запрошенный файл
		    tmp_fil=cfg_fw[rem_ip][rem_port]['file']
		    # Модель коммутатора
		    tmp_sw =cfg_fw[rem_ip][rem_port]['switch']
		    # Контрольная сумма
		    tmp_m5d=cfg_fw[rem_ip][rem_port]['md5']
		    # Помещаем полученные данные в базе MongoDB: PutConfigToMongoDB(адрес, пользователь, пароль, база, коллекция, данные, цель, коммутатор, IP, хеш)
		    if use_mongo:
			PutConfigToMongoDB(mongo_addr, mongo_user, mongo_pass, mongo_base, mongo_dcol, tmp_dct, tmp_tgt, tmp_fil, tmp_sw, rem_ip, tmp_m5d) 
		    # Очищаем временный словарь
		    tmp_dct.clear()
		# Удаляем данные из словаря, т.к. передача закончена и они больше не нужны
		del cfg_fw[rem_ip][rem_port]

	    if (tftp_type=='WRQ'):
		# Увеличиваем значение счетчика полученных запросов (W)
		tftp_wcnt += 1
		# Пишем в лог о полученной запросе
		logging.info('-->Offer (WRQ) from %s for device %s. Offered file: %s', dip,dev, tftp_filename)
		# Пример:     -->Offer (WRQ) from '10.137.130.56:57904' for device '10.99.0.2' (DES-3200-28). Offered     file: 'cfg'

		# Получаем имя (модель) удаленного устройства
		rem_dev=GetSWInfo(target_ip,devices)[0]
		# Если для удаленного хоста данные уже определены, затираем их
		if rem_ip in cfg_up.keys():
		    cfg_up[rem_ip].update({rem_port:{'cfg':{},'file':tftp_filename,'target':target_ip,'switch':rem_dev}})
		# Если же нет - добавляем
		else:
		    cfg_up[rem_ip]    =   {rem_port:{'cfg':{},'file':tftp_filename,'target':target_ip,'switch':rem_dev}}
		# На выходе получается словарь вида [IP][Port]['cfg'|'file'|'target'|'switch']
		# Это нужно для удобства получения информации, но главное - для одновременной передачи
		# Для каждой сессии передачи в словаре хранится своя информация

	    # Если ожидаем передачу и tftp_block в допустимом диапазоне
	    if ((tftp_type=='WRQ') | (tftp_type=='DATA')) & (tftp_block in xrange(0,65536)):
		# Проверяем, существуют ли данные для текущего соединения
		try: cfg_up[rem_ip][rem_port]['cfg']
		# Обрабатываем ситуацию, когда данных нет. Такая ситуация может быть, если пакет с WRQ не попал на сервер:
		except:
		    # Если тип передачи DATA, а данных нет, пишем в лог об ошибке
		    if (tftp_type=='DATA'):
			logging.info("ERROR: Transaction (DATA) without declaration (WRQ) for '%s'!", dip)
		# Данные получены, приступаем к обработке
		else:
		    # Если номер блока больше 200, значит размер файла превысил 100 КБ (512*200=102400). Такие данные в базу не попадут и будут удалены
		    if (tftp_block>200):
			# Имя передаваемого файла
			fil="'%s'" % (cfg_up[rem_ip][rem_port]['file'])
			# Определяем текст сообщения об ошибке
			error_msg='Transferred file '+fil+' from '+dip+' is too large (greater than 100 KB)'
			# Пробуем отправить сообщение об ошибке (диск заполнен)
			try:
			    tftp.sendto(chr(0)+chr(5)+chr(0)+chr(3)+error_msg+chr(0),(rem_ip,rem_port))
			# Если не получилось - не расстраиваемся :)
			except:
			    pass
			# Сообщаем об ошибке в лог
			logging.info("ERROR: %s", error_msg)
			# Удаляем весь блок данных из словаря
			del cfg_up[rem_ip][rem_port]
		    else:
			# Пробуем отправить подтверждение блока или начала передачи (ответ на WRQ, tftp_block равен 0)
			try:
			    tftp.sendto(chr(0)+chr(4)+(lambda x: chr(x//256)+chr(x%256))(int(tftp_block)),(rem_ip,rem_port))
			# Обрабатываем возможную ошибку сокета
			except socket.error as err:
			    # При возникновении ошибки делаем запись в логе
			    logging.info("Socket Error (ACK): %s. Exiting...", err.args[1])
			    # И завершаем работу
			    sys.exit(2)
			else:
			    # Если получены сами данные, а не запрос:
			    if (tftp_type=='DATA'):
				# Обновляем конфигурацию для полученного блока в словаре
				cfg_up[rem_ip][rem_port]['cfg'].update({tftp_block:data_upl})
				# Если блок короче 512 байт, считаем его последним
				if (len(data_upl)<512):
				    # Данные
				    tmp_dct=cfg_up[rem_ip][rem_port]['cfg']
				    # Цель
				    tmp_tgt=cfg_up[rem_ip][rem_port]['target']
				    # Запрошенный файл
				    tmp_fil=cfg_up[rem_ip][rem_port]['file']
				    # Модель коммутатора
				    tmp_sw =cfg_up[rem_ip][rem_port]['switch']
				    # Количество блоков
				    blk=len(cfg_up[rem_ip][rem_port]['cfg'])
				    # Получаем MD5-сумму и размер полученных данных
				    m5d, fln = md5size(cfg_up[rem_ip][rem_port]['cfg'])
				    # Пишем в лог об окончании приема
				    logging.info("Recieved file  from %s for device '%s' (%s). Transferred file: '%s'. Size: %s, blocks: %s, md5: %s", dip, tmp_tgt, tmp_sw, tmp_fil, fln, blk, m5d)
				    # Пример: Recieved file  from '10.137.130.56:57904' for device '10.99.0.2' (DES-3200-28). Transferred file: 'cfg'. Size: 318, blocks: 1, md5: c6c253ff4110f77b917901bb89d762df
				    # Помещаем полученные данные в базе MongoDB: PutConfigToMongoDB(адрес, пользователь, пароль, база, коллекция, данные, цель, коммутатор, IP, хеш)
				    if use_mongo:
					PutConfigToMongoDB(mongo_addr, mongo_user, mongo_pass, mongo_base, mongo_ucol, tmp_dct, tmp_tgt, tmp_fil, tmp_sw, rem_ip, m5d)
				    # Удаляем данные из словаря, т.к. передача закончена и они больше не нужны
				    del cfg_up[rem_ip][rem_port]
	time.sleep(sleeptime)

# ------- Конец основного блока -------

# ------- Служебный блок: создание и управление демоном -------

class MyDaemon(Daemon):
    def run(self):
	main()

if __name__ == "__main__":
    daemon = MyDaemon('/var/run/dracon.pid','/dev/null',logfile,logfile)
    if len(sys.argv) == 2:
	if   'start'     == sys.argv[1]:
	    daemon.start()
	elif 'faststart' == sys.argv[1]:
	    daemon.start()
	elif 'stop'      == sys.argv[1]:
	    daemon.stop()
	elif 'restart'   == sys.argv[1]:
	    daemon.restart()
	else:
	    print "Dracon: "+sys.argv[1]+" - unknown command"
	    sys.exit(2)
	sys.exit(0)
    else:
	print "usage: %s start|stop|restart" % sys.argv[0]
	sys.exit(2)

# ------- Конец служебного блока -------
