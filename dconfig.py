#coding=UTF8
# Интерфейс, на котором будет работать демон
interface = ""
# UDP-порт для tftp-сервера
port      = 69
# Количество секунд, через которое надо обновлять список портов и устройств
cycle_int = 300
# Пауза по умолчанию при опросе UDP-сокета
sleep_def = 0.1
# Количество секунд простоя (данные не поступают), через которые надо выставить паузу по умолчанию
sleep_int = 3
# Лог-файл демона
logfile   = "/var/log/dracon.log"

# Настройки для MySQL-сервера, откуда будут забираться данные
mysql_addr = "mysql.myhost"
mysql_user = "user"
mysql_pass = "password"
mysql_base = "base"

# MySQL-запрос для получения IP-адресов и данных о портах коммутатора
mysql_query_p = """
SELECT '10.90.90.95' ip, 1 AS port, 1 AS ptype, 'user12345' AS comment1, 'VIP' AS comment2;
"""

# MySQL-запрос для получения данных о коммутаторах: IP-адрес, тип, сеть, адрес
mysql_query_d = """
SELECT '10.90.90.95' AS ip, 24 AS `type`, '192.168.0.0/24' AS custom1, 'Отдел разработки' AS custom2;
"""

# Кодировка данных в результате запроса (используется для транслитерации кириллицы)
inc_cpage = "cp1251"

# Настройки для сервера MongoDB, где будут храниться результаты работы
use_mongo  = True
mongo_addr = "mongodb.myhost"
mongo_user = "dracon"
mongo_pass = "paswword"
mongo_base = "draconf"
mongo_ucol = "config_up"
mongo_dcol = "config_down"

# Соответствие идентификаторов типов устройств и их названий
dev_types = {
     25:'DES-3200-28',
    131:'DES-3028',
     86:'DES-3200-18',
    112:'DES-3200-28_C1'
}

# Пустой набор портов по умолчанию: 1-24 - абонентские порты, 25 - uplink, 26-28 - downlink'и
default_ports = {'0.0.0.0':
	{1: {'type':'1', 'desc':'', 'user':'subscriber'},  2: {'type':'1', 'desc':'', 'user':'subscriber'},  3: {'type':'1', 'desc':'', 'user':'subscriber'},  4: {'type':'1', 'desc':'', 'user':'subscriber'},
	 5: {'type':'1', 'desc':'', 'user':'subscriber'},  6: {'type':'1', 'desc':'', 'user':'subscriber'},  7: {'type':'1', 'desc':'', 'user':'subscriber'},  8: {'type':'1', 'desc':'', 'user':'subscriber'},
	 9: {'type':'1', 'desc':'', 'user':'subscriber'}, 10: {'type':'1', 'desc':'', 'user':'subscriber'}, 11: {'type':'1', 'desc':'', 'user':'subscriber'}, 12: {'type':'1', 'desc':'', 'user':'subscriber'},
	13: {'type':'1', 'desc':'', 'user':'subscriber'}, 14: {'type':'1', 'desc':'', 'user':'subscriber'}, 15: {'type':'1', 'desc':'', 'user':'subscriber'}, 16: {'type':'1', 'desc':'', 'user':'subscriber'},
	17: {'type':'1', 'desc':'', 'user':'subscriber'}, 18: {'type':'1', 'desc':'', 'user':'subscriber'}, 19: {'type':'1', 'desc':'', 'user':'subscriber'}, 20: {'type':'1', 'desc':'', 'user':'subscriber'},
	21: {'type':'1', 'desc':'', 'user':'subscriber'}, 22: {'type':'1', 'desc':'', 'user':'subscriber'}, 23: {'type':'1', 'desc':'', 'user':'subscriber'}, 24: {'type':'1', 'desc':'', 'user':'subscriber'},
	25: {'type':'5', 'desc':  'uplink', 'user':''  }, 26: {'type':'2', 'desc':'downlink','user':''   }, 27: {'type':'2', 'desc':'downlink','user':''   }, 28: {'type':'2', 'desc':'downlink','user':''   }
	}
}

# Словарь с кодами портов и их сокращенными обозначениями
ports_types = {1:'ss',2:'mg',3:'br',4:'vp',5:'up',6:'ns',7:'eq',8:'pu',9:'pd'}
# 1 - абонентский порт, 2 - магистральный, 3 - сломанный, 4 - VIP-клиент, 5 - вход
# 6 - нестандартный, 7 - оборудование, 8 - вход (патчкорд), 9 - магистраль (патчкорд)

# Список кодов магистральных портов
mags_list   = [2,5,8,9]

# Путь к каталогу с файлами конфигураций. Имя файла конфигураций должно соответствовать названию устройства
# Пример: Для устройства с ID=210 по пути "/usr/local/etc/dracon/config/" будет производиться поиск файла 'DES-3200-28_C1'
cf_path = "/usr/local/etc/dracon/config/"

# Путь к каталогу с ПО
fw_path  = "/usr/local/etc/dracon/fw/"
# Соответствие названий устройств и файлов с программным обеспечением
fw_names = {
    'DES-3200-28'   : 'DES-3200R_1.85.B008.had',
    'DES-3028'      : 'DES_3028_52_V2.94-B07.had',
    'DES-3200-18'   : 'DES-3200R_1.85.B008.had',
    'DES-3200-28_C1': 'DES3200R_4.39.B008.had'
    }

# Доступные команды (имена файлов) и соответствующие им шаблоны с набором команд
commands = {
    'acl':['*header*', '*acl*'],
    'cpu_acl':['*header*', '*cpu_acl*'],
    'accounts':['*header*', '*accounts*'],
    'stp_lbd':['*header*', '*stp_lbd*'],
    'snmp':['*header*', '*snmp*'],
    'sntp':['*header*', '*sntp*'],
    'lldp':['*header*', '*lldp*'],
    'filtering':['*header*', '*filtering*'],
    'trusted_hosts':['*header*', '*trusted_hosts*'],
    'ipm':['*header*', '*ipm*'],
    'dhcp_relay':['*header*', '*dhcp_relay*'],
    'igmp_snooping':['*header*', '*igmp_snooping*'],
    'igmp_auth':['*header*', '*igmp_auth*'],
    'aaa':['*header*', '*aaa*'],
    'multi_filter':['*header*', '*multi_filter*'],
    'cos':['*header*', '*cos*'],
    'mon_log':['*header*', '*mon_log*'],
    'pdesc':['*header*', '*p_desc*'],
    'config':['*header*', '*acl*', '*cpu_acl*', '*accounts*', '*stp_lbd*', '*snmp*', '*sntp*', '*lldp*', '*filtering*', '*trusted_hosts*',
    '*ipm*', '*dhcp_relay*', '*igmp_snooping*', '*igmp_auth*', '*aaa*', '*multi_filter*', '*cos*', '*mon_log*', '*p_desc*', '*bottom*']
    }

# Содержимое справки, получаемой по команде (имени файла) 'help'
helpinfo="""
Available commands:

acl - Standard ACL
cpu_acl - CPU ACL
accounts - Accounts
stp_lbd - STP & LBD
snmp - SNMP
sntp - SNTP
lldp - LLDP
filtering - Traffic Segmentation,  Strom Control, DOS Prevention and DHCP Filter
trusted_hosts - Trusted hosts
ipm - IP-MAC-Port Binding
dhcp_relay - DHCP Relay
igmp_snooping - IGMP Snooping
igmp_auth - IGMP Authentication
aaa - Authentication, Authorization, Accounting
multi_filter - Multicast Filtering
cos - Class of Service
mon_log - Monitoring & Logging
pdesc - Switch and Ports Description only
config - Full set of all commands
help - This help

firmware - FW image for specified device

If downloaded data are 'Firmware', then it does not placed into the Mongo DB.

Uploading file has a size limit - 100 KB.

"""