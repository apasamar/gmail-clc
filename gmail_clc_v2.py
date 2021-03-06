#!/usr/bin/env python

# Author: Abaraham Pasamar (apasamar [at] incide [dot] es
# Date: 2018-02-04
# version: 0.2 # some main menu udates
# This script is a GMAIL (IMAP) client. You can read mailboxes and show email header/body, etc


import imaplib, email, email.header, getpass, os, sys, datetime, time, os
import pprint

from texttable import Texttable
from colorama import *

###############################
# Simple header process is slow
# Logging all commands - sessions
# colored/not colored output
# export emails to file
# hashing
# Select Folder/mailbox

###### CREDENTIALS #############
#mailuser='your_email_account_here@domain.xx'
#mailpas='your_pass_here'

###############################

###### Texttable #######
t = Texttable()
header=["#","From","To","Date","Subject"]
t.set_cols_width([5,25,25,40,40])
t.set_cols_align(['l','l','l','l','l'])

#######################

def wait_key():
	try:
		input("Press enter to continue")
	except SyntaxError:
		pass

def read_single_keypress():
    """Waits for a single keypress on stdin.

    This is a silly function to call if you need to do it a lot because it has
    to store stdin's current setup, setup stdin for reading single keystrokes
    then read the single keystroke then revert stdin back after reading the
    keystroke.

    Returns the character of the key that was pressed (zero on
    KeyboardInterrupt which can happen when a signal gets handled)

    """
    import termios, fcntl
    fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(attrs_save) # copy the stored version to update
    # iflag
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                  | termios.ISTRIP | termios.INLCR | termios. IGNCR
                  | termios.ICRNL | termios.IXON )
    # oflag
    attrs[1] &= ~termios.OPOST
    # cflag
    attrs[2] &= ~(termios.CSIZE | termios. PARENB)
    attrs[2] |= termios.CS8
    # lflag
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                  | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    # read a single keystroke
    try:
        ret = sys.stdin.read(1) # returns a single character
    except KeyboardInterrupt:
        ret = 0
    finally:
        # restore old state
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return ret

def show_mailboxes(M):
	rv, mailboxes = M.list()
	if rv == 'OK':
		print(Fore.RED+"Mailboxes:")
		#'(\\HasNoChildren) "/" "INBOX"'
		for item in mailboxes:
			mailbox=item.split("\"")
			print(Fore.BLUE+"%s"%mailbox[3])

def select_mailbox(src_folder_name,mode):
	## Select MAILBOX ##
	rv, data = m.select(mailbox=src_folder_name, readonly=mode) # READONLY
	return rv

def chunks(l, n):
    if n < 1:
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]

def getmailid():
	num = input('Choose an email id (#): ')
	print(Fore.RESET + Back.RESET + Style.RESET_ALL)
	return int(num)

def getsearchstring():
	str = input('Enter a VALID Search String (ex. \'(FROM "John Doe")\' ): ')
	return str

def getfolder():
	str = input('Enter a VALID IMAP Folder: ')
	return str

def fetch_email(M,msgid):
	rv, data = M.fetch(msgid, '(RFC822)')
	if rv != 'OK':
		print("ERROR getting message", msgid)
		return
		### Get Message ##
	return email.message_from_string(data[0][1].decode('utf-8'))

def search_emails(M,searchstring):
	rv, data = M.search(None, searchstring)
	if rv != 'OK':
		print("No messages found!")
		return
	return data

####### PROCESS MAILBOX ######
def process_mailbox(M,searchstring):
	"""
	mailbox iteration
	return mailbox email_ids
	"""
	#######################
	###### READ MAILBOX #######
	#print ""
	#searchstring="ALL"
	data=search_emails(M,searchstring)
	msg_ids=data[0].split()
	#print msg_ids
	return msg_ids

def show_emails(emails_ids):
	"""
	print email_ids (main fields) using table output
	header parser
	"""
	row=[]
	###### Texttable #######
	t = Texttable()
	header=["#","Crypt","From","To","Date","Subject"]
	t.set_cols_width([6,5,25,25,25,40])
	t.set_cols_align(['l','l','l','l','l','l'])
	t.add_row(header)
	#######################
	#print emails
	for msgid in emails_ids:
		msg=fetch_email(m,msgid)
		subject_decode = email.header.decode_header(msg['Subject'])[0]
		if subject_decode[1]!=None:
			subject = subject_decode[0].decode(subject_decode[1]).encode('utf-8')
		else:
			subject = subject_decode[0]
		row.append(msgid) # Select msgig
		# encrypted email?
		if 'multipart/encrypted' in msg['Content-Type']:
			encrypted='yes'
		else:
			encrypted='no'
		row.append(encrypted)
		from_decode =email.header.decode_header(msg['From'])[0]
		if from_decode[1]!=None:
			From=from_decode[0].decode(from_decode[1]).encode('utf-8')
		else:
			From=from_decode[0]
		to_decode=email.header.decode_header(msg['To'])[0]
		if to_decode[1]!=None:
			To=to_decode[0].decode(to_decode[1]).encode('utf-8')
		else:
			To=to_decode[0]
		row.append(From) # Select From
		row.append(To)   # Select To
		date_tuple = email.utils.parsedate_tz(msg['Date'])
		if date_tuple:
			local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
	    	#row.append(local_date.strftime("%a, %d %b %Y %H:%M:%S"))
			row.append(local_date.strftime("%Y-%m-%d %H:%M:%S"))
		row.append(subject) # Select Subject
		###
		t.add_row(row) # Generate email table
		###
		row=[] # Clear ROW

	print(Fore.WHITE)
	print(t.draw()) # Print email table
	print(Fore.RESET + Back.RESET + Style.RESET_ALL)



def select_email():
	emailid=getmailid()
	msg=fetch_email(m,emailid)
	print(Fore.BLUE+"")
	print("print standard, only header, only text or full (s/h/t/b):")
	key=read_single_keypress()
	if key=='s':
		print_simple_header(msg)
		print_text(msg)
	if key=='h':
		print_header(msg)
	if key=='t':
		print_body(msg)
	if key=='b':
		print_header(msg)
		print_body(msg)
	export(msg)

def print_simple_header(msg):
	header_elements=['From','To','Date','Subject']
	parser=email.parser.HeaderParser()
	header=parser.parsestr(msg.as_string())
	for item in header.items():
		if item[0] in header_elements:
			print(Fore.GREEN+item[0]+": "+Fore.WHITE+item[1]+Fore.RESET)


def print_header(msg):
	print(Fore.RED+"==================================")
	print(Fore.RED+"=         EMAIL HEADER           =")
	print(Fore.RED+"==================================")
	print(Fore.RESET + Back.RESET + Style.RESET_ALL+" ")
	parser=email.parser.HeaderParser()
	header=parser.parsestr(msg.as_string())
	for item in header.items():
		print(Fore.GREEN+item[0]+": "+Fore.WHITE+item[1]+Fore.RESET)

def print_text(msg):
	for part in msg.walk():
		if part.get_content_type() == 'text/plain':
				print(part.get_payload(decode=True)) # prints the raw text

def print_body(msg):
	print(Fore.RED+"==================================")
	print(Fore.RED+"=       EMAIL TEXT BODY          =")
	print(Fore.RED+"==================================")
	print(Fore.RESET + Back.RESET + Style.RESET_ALL+" ")
	print_text(msg)

def export(msg):
	print (Fore.BLUE+"Do you want to export this email (y/n):")
	filename='temp.eml'
	key=read_single_keypress()
	if key=='y':
		export_email(msg,filename)
		open_email(filename)

def export_email(msg,filename):
	f=open(filename,'w') # Open file for each fetched email
	f.write(str(msg)) # Write email content to file
	f.close()

def open_email(filename):
	os.system("open "+filename)

######################


def main_menu(src_folder_name):
	page=1
	print(Fore.RESET+"\nSelect search: Inbox (i) | Encrypted Messages (e) | Change Folder (f) | Custom Search (c)")
	#wait_key()
	searchstring="ALL"
	key=read_single_keypress()
	if key=='e':
		searchstring='(TEXT \"BEGIN PGP MESSAGE\")'
	if key=='c':
    		searchstring=getsearchstring()
	if key=='f':
		src_folder_name="'"+getfolder()+"'"
		mode=True
		select_mailbox(src_folder_name,mode)	
	print (Fore.BLUE+"Processing mailbox... %s with search=%s, please wait.\n"%(src_folder_name,searchstring))
	## Do something with the mailbox ##
	start_time = time.time()
	msg_ids=process_mailbox(m,searchstring)  # SEARCH STRING
	### time calculation
	now=time.time()
	sec="process_mailbox: - %.2f seconds -" % (now - start_time)
	print(Fore.BLUE+sec)
	###
	start_time = time.time()
	reverse_ids=[]
	for i in reversed(msg_ids):
		reverse_ids.append(i) # read in reverse order
	block=10
	page_list=chunks(reverse_ids,block)
	show_emails(page_list[page-1])
	### time calculation
	now=time.time()
	sec="show_email: - %.2f seconds -" % (now - start_time)
	print(Fore.BLUE+sec)
	return page_list
	###

def inbox_menu(page_list,page):
	print(Fore.RESET+"\nMenu: n (next page) | b (previous page) | s (select email id) | g (goto page) | m (main menu) | q (quit)")
	#wait_key()
	key=read_single_keypress()
	if key=='n':
		start_time = time.time()
		page+=1
		print(Fore.BLUE+"'n' (next page), please wait...")
		#print(page)
		#print(page_list[page-1])
		show_emails(page_list[page-1])
		print(Fore.GREEN+"--page %d --"%page)
		### time calculation
		now=time.time()
		sec="next: - %.2f seconds -" % (now - start_time)
		print(Fore.BLUE+sec)
	if key=='b':
		start_time = time.time()
		page-=1
		print(Fore.BLUE+"'b' (previous page), please wait...")
		show_emails(page_list[page-1])
		print(Fore.GREEN+"--page %d --"%page)
		### time calculation
		now=time.time()
		sec="back: - %.2f seconds -" % (now - start_time)
		print(Fore.BLUE+sec)
	if key=='s':
		print(Fore.BLUE+"'s' (select email id)")
		start_time = time.time()
		select_email()
		### time calculation
		now=time.time()
		sec="select_email: - %.2f seconds -" % (now - start_time)
		print(Fore.BLUE+sec)
		while True:
			print(Fore.RESET+"\nMenu: b (back to inbox) | s (select email id)")
			key=read_single_keypress()
			if key=='b':
				show_emails(page_list[page-1])
				print(Fore.GREEN+"--page %d --"%page)
				break
			if key=='s':
				select_email()
	if key=='g':
		start_time = time.time()
		print(Fore.BLUE+"'g' (goto page)")
		num = input('Select page (#): ')
		page=int(num)
		print(Fore.BLUE+"please wait...")
		show_emails(page_list[page-1])
		print(Fore.GREEN+"--page %d --"%page)
		### time calculation
		now=time.time()
		sec="goto_pagel: - %.2f seconds -" % (now - start_time)
		print(Fore.BLUE+sec)
	
	if key=='m':
		start_time = time.time()
		print(Fore.BLUE+"'m' (main menu)")
		print(Fore.BLUE+"please wait...")
		main_menu(src_folder_name)
		### time calculation
		now=time.time()
		sec="main_menu: - %.2f seconds -" % (now - start_time)
		print(Fore.BLUE+sec)
	if key=='q':
		sys.exit()
	return page



######################

######  MAIN #######


###### LOGIN ########
m = imaplib.IMAP4_SSL('imap.gmail.com', 993)
try:
	m.login(mailuser, mailpass)
except m.error:
    print("LOGIN FAILED!!! ")
    sys.exit(1)
#####################

## show mailboxes list ##
#show_mailboxes(m)

## Select MAILBOX ##
mode=True # READONLY MODE
src_folder_name='Inbox' # DEFAULT FOLDER

rv=select_mailbox(src_folder_name,mode)

if rv == 'OK':
	page=1
	page_list=main_menu(src_folder_name)
	while True:
		page=inbox_menu(page_list,page)
else:
	print("ERROR: Unable to open mailbox: %s --> %s "%(src_folder_name,rv))


## Logout ##
print(Fore.BLUE+"Exiting...bye!")
print(Fore.RESET + Back.RESET + Style.RESET_ALL)
m.close()
m.logout()


#typ, data = obj.uid('STORE', msg_uid, '+X-GM-LABELS', desti_folder_name)
#typ, data = obj.uid('STORE', msg_uid, '-X-GM-LABELS', src_folder_name)
