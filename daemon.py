#!/usr/local/bin/python
#coding=UTF8 # Определяем кодировку, чтобы компилятор не падал в обморок
#version 2014.01.27

import sys, os, time, atexit
from signal import SIGTERM

class Daemon:
    """
    Общий класс демона

    Использование: Создать подкласс от Daemon и вызвать метод run()
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	self.stdin   = stdin
	self.stdout  = stdout
	self.stderr  = stderr
	self.pidfile = pidfile

    def daemonize(self):
	"""
	Здесь используется особая UNIX`овая магия double-fork
	"""
	# Пробуем отделиться в первый раз (first fork)
	try:
	    pid = os.fork()
	    if pid > 0:
		# Выходим из первого родительского процесса
		sys.exit(0)
	except OSError, e:
	    sys.stderr.write("Fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
	    sys.exit(1)

	# Отделяемся от родительского процесса
	os.chdir("/")
	os.setsid()
	os.umask(0)

	# Пробуем отделиться второй раз (second fork)
	try:
	    pid = os.fork()
	    if pid > 0:
		# Отделяемся от второго родительского процесса
		sys.exit(0)
	except OSError, e:
	    sys.stderr.write("Fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
	    sys.exit(1)

	# Перенаправляем стандартные файловые декрипторы
	sys.stdout.flush()
	sys.stderr.flush()
	si = file(self.stdin, 'r')
	so = file(self.stdout, 'a+')
	se = file(self.stderr, 'a+', 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

	# Записываем pidfile
	atexit.register(self.delpid)
	pid = str(os.getpid())
	file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
	os.remove(self.pidfile)

    def start(self):
	# Запуск демона
	sys.stderr.write("Starting daemon...\n")
	# Проверяем pidfile чтобы засечь повторный запуск демона
	try:
	    pf = file(self.pidfile,'r')
	    pid = int(pf.read().strip())
	    pf.close()
	except IOError:
	    pid = None

	if pid:
	    message = "Pidfile %s already exist. Daemon already running?\n"
	    sys.stderr.write(message % self.pidfile)
	    sys.exit(1)

	# Запускаем демона
	self.daemonize()
	self.run()

    def stop(self):
	# Остановка демона
	sys.stderr.write("Stopping daemon...\n")
	# Получаем pid из pidfile
	try:
	    pf = file(self.pidfile,'r')
	    pid = int(pf.read().strip())
	    pf.close()
	except IOError:
	    pid = None

	if not pid:
	    message = "Pidfile %s does not exist. Daemon not running?\n"
	    sys.stderr.write(message % self.pidfile)
	    return # "Не ошибка" при перезапуске

	# Пытаемся завершить процесс
	try:
	    while 1:
		os.kill(pid, SIGTERM)
		time.sleep(0.1)
	except OSError, err:
	    err = str(err)
	    if err.find("No such process") > 0:
		if os.path.exists(self.pidfile):
		    os.remove(self.pidfile)
	    else:
		print str(err)
		sys.exit(1)

    def restart(self):
	# Перезапуск демона
	self.stop()
	self.start()

    def run(self):
	pass