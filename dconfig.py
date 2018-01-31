#coding=UTF8
# IP-адрес интерфейса, на котором будет работать демон
interface_ip    = ""
# UDP-порт для TFTP-сервера
port            = 69
# Время в секундах, через которое надо обновлять список портов и устройств
cycle_int       = 300
# Пауза по умолчанию при опросе UDP-сокета
sleep_def       = 0.05
# Время простоя (данные не поступают) в секундах, через которое надо выставить паузу по умолчанию
sleep_int       = 3
# Имя файла журнала
log_file        = "/var/log/dracon.log"
# Размер файла журнала при достижении которого начинается ротация
log_size        = 1048576
# Количество архивных копий лога
log_backupcount = 4

# Настройки для MySQL-сервера, откуда будут забираться данные
mysql_addr = "mysql.localhost"
mysql_user = "user"
mysql_pass = "password"
mysql_base = "devices"

# Настройки для PostgreSQL-сервера, откуда будут забираться данные. Используется как альтернатива MySQL
postgresql_addr = "postgresql.localhost"
postgresql_user = "user"
postgresql_pass = "pass"
postgresql_base = "devices"
use_postgresql  = False

# Запрос к базе данных для получения списка устройств. Поля: ip(str), type(int), custom(str)
devices_query = """
SELECT '10.90.90.95' AS ip, 24 AS type, '192.168.0.0/24' AS custom;
"""

# Запрос к базе данных для получения сведений о портах коммутатора. Поля: ip(str), port(int), ptype(int), comment(str)
ports_query = """
SELECT '10.90.90.95' AS ip, 1 AS port, 1 AS ptype, 'user12345' AS comment;
"""

# Настройки для MySQL-сервера, где будет храниться конфигурация и информация о транзакциях
mysql_addr_w = "localhost"
mysql_user_w = "dracon"
mysql_pass_w = "draconpass"
mysql_base_w = "dracon"
mysql_ctbl_w = "configs"
mysql_ttbl_w = "transactions"

# Соответствие идентификаторов типов устройств их названиям
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
mags_list   = [2, 5, 8, 9]

# Путь к каталогу с файлами конфигураций. Имя файла конфигураций должно соответствовать названию устройства
# Пример: Для устройства с ID=210 по пути "/usr/local/etc/dracon/config/" будет производиться поиск файла 'DES-3200-28_C1'
cf_path  = "/usr/local/etc/dracon/config/"

# Путь к каталогу с программным обеспечением
fw_path  = "/usr/local/etc/dracon/fw/"

# Соответствие названий устройств именам файлов с программным обеспечением
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
helpinfo = """
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