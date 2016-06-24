#coding=UTF8
# IP-адрес интерфейса, на котором будет работать демон
interface_ip = ""
# UDP-порт для tftp-сервера
port         = 69
# Количество секунд, через которое надо обновлять список портов и устройств
cycle_int    = 300
# Пауза по умолчанию при опросе UDP-сокета
sleep_def    = 0.05
# Количество секунд простоя (данные не поступают), через которые надо выставить паузу по умолчанию
sleep_int    = 3
# Лог-файл демона
logfile      = "/var/log/dracon.log"

# Настройки для MySQL-сервера, откуда будут забираться данные
mysql_addr = "mysql.myhost"
mysql_user = "user"
mysql_pass = "password"
mysql_base = "base"

# MySQL-запрос для получения IP-адресов и данных о портах коммутатора
mysql_query_p = """
SELECT '10.90.90.95' ip, 1 AS port, 1 AS ptype, 'user12345' AS comment;
"""

# MySQL-запрос для получения данных о коммутаторах: IP-адрес, тип, сеть, адрес
mysql_query_d = """
SELECT '10.90.90.95' AS ip, 24 AS `type`, '192.168.0.0/24' AS custom;
"""

# Настройки для сервера MongoDB, где будут храниться результаты работы
use_mongo  = True
mongo_addr = "mongodb.myhost"
mongo_user = "dracon"
mongo_pass = "password"
mongo_base = "draconf"
mongo_ucol = "config_up"
mongo_dcol = "config_down"

# Соответствие идентификаторов типов устройств и их названий
dev_types = {
     24 : 'DES-3200-28',	# DES-3200-28/A1
    218 : 'DES-3200-28',	# DES-3200-28/B1
    210 : 'DES-3200-28_C1',	# DES-3200-28/C1
    216 : 'DES-3200-18',	# DES-3200-18/A1
    217 : 'DES-3200-18',	# DES-3200-18/B1
    209 : 'DES-3200-18_C1',	# DES-3200-18/C1
    205 : 'DES-3028',		# DES-3028
    215 : 'DGS-3000-24TC',	# DES-3000-24TC
    252 : 'DGS-3000-26TC',	# DES-3000-24TC
}

# Словарь с кодами портов и их сокращенными обозначениями
ports_types = {1:'ss', 2:'mg', 3:'br', 4:'vp', 5:'up', 6:'ns', 7:'eq', 8:'pu', 9:'pd'}
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
    'DES-3200-28'    : 'DES-3200R_1.85.B008.had',
    'DES-3200-28_C1' : 'DES3200R_4.39.B008.had',
    'DES-3200-18'    : 'DES-3200R_1.85.B008.had',
    'DES-3200-18_C1' : 'DES3200R_4.39.B008.had',
    'DES-3028'       : 'DES_3028_52_V2.94-B07.had',
    'DGS-3000-24TC'  : 'DGS3000_Run_1_14_B008.had',
    'DGS-3000-26TC'  : 'DGS3000_Run_1_14_B008.had',
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