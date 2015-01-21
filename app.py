from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import moment


def fetchInputs(entries):
   inputs = []
   for entry in entries:
      field = entry[0]
      text  = entry[1].get()
      inputs.append(text)
      # print('%s: "%s"' % (field, text)) 
   return {'staffNumber':inputs[0], 'password':inputs[1], 'startTime': inputs[2], 'finishTime': inputs[3], 'lunchMinutes': inputs[4]}

def makeform(root, fields):
   entries = []
   for field, setting in zip(fields, settings):
      row = Frame(root)
      lab = Label(row, width=15, text=field, anchor='w')
      if field == "Password":
      	ent = Entry(row, show="*")
      else:
      	ent = Entry(row)
      row.pack(side=TOP, fill=X, padx=5, pady=5)
      lab.pack(side=LEFT)
      ent.pack(side=RIGHT, expand=YES, fill=X)
      ent.insert(0, setting)
      entries.append((field, ent))
   return entries

def saveSetting(entries):
  inputs = fetchInputs(entries)
  if var.get():
    print "saving settings with password"
    encrypt_file(str(inputs), pwpass)
  else:
    print "saving settings without password"
    inputs["password"] = ""
    encrypt_file(str(inputs), pwpass)
  return inputs

def encrypt_file(inputs, key):
    # print "Text to encrypt: %s" % inputs
    enc = encrypt(key, inputs)
    with open(settingFile, 'wb') as fo:
        fo.write(enc)

def decrypt_file(file_name, key):
    with open(file_name, 'rb') as fo:
        ciphertext = fo.read()
    dec = decrypt(key, ciphertext)
    return eval(dec)


from Tkinter import *
fields = 'Staff Number', 'Password','Start Time', 'Finish Time', 'Lunch Minutes'

from simplecrypt import encrypt, decrypt
pwpass = "pwpass"
settingFile = "./uws_ts_setting.json.enc"
settingJson = decrypt_file(settingFile, pwpass)
settings = settingJson['staffNumber'], settingJson['password'], settingJson['startTime'], settingJson['finishTime'], settingJson['lunchMinutes']
# print settings

def go(entries):
  saveSetting(entries)
  inputs = fetchInputs(entries)

  driver = webdriver.Chrome()
  url = 'https://staffonline.uws.edu.au/alesco-wss-v13/faces/WJ0000?_afrWindowMode=0&_afrLoop=14955864744711028&_adf.ctrl-state=kljysmgc8_4'
  driver.get(url)
  driver.find_element_by_id('pt1:pt_s2:wssUsernameField::content').send_keys(inputs['staffNumber'])
  driver.find_element_by_id('pt1:pt_s2:wssPasswordField::content').send_keys(inputs['password'])
  element = driver.find_element_by_id('pt1:pt_s2:wssLoginButton')
  time.sleep(2)
  element.click()
  time.sleep(2)
  wait = WebDriverWait(driver, 10)
  wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="pt1:MWJ0000_NAVTIMEK"]/div/table/tbody/tr/td[2]/a'))).click()
  time.sleep(2)
  wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="pt1:MNAVTIMEK_NAVW01"]/td[2]'))).click()
  # time.sleep(3)
  # wait.until(EC.element_to_be_clickable((By.ID,'pt1:MNAVTIMEK_NAVW01'))).click()
  wait = WebDriverWait(driver, 15)
  time.sleep(4)
  srcUrl = wait.until(EC.element_to_be_clickable((By.ID,'pt1:r1:0:pt1:Main::f'))).get_attribute("src")
  driver.get(srcUrl)
  wait.until(EC.element_to_be_clickable((By.LINK_TEXT,'Edit'))).click()
  time.sleep(2)
  firstDayText = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/p[2]/table/tbody/tr[2]/td[1]'))).text
  firstDay = moment.date( firstDayText, "DD/MM/YYYY" )
  diffDays = moment.now().diff(firstDay, "days").days

  for day in range(diffDays+1):
    startId = 0
    endId = 0
    breakId = 0
    if day < 10 :
      startId = "START_TIME0" + str(day)
      endId = "END_TIME0" + str(day)
      breakId = "BREAK0" + str(day)
    else:
      startId = "START_TIME" + str(day)
      endId = "END_TIME" + str(day)
      breakId = "BREAK" + str(day)

    sval = driver.find_element_by_id(startId).get_attribute('value')
    if sval == "":
      driver.find_element_by_id(startId).send_keys(inputs['startTime'])

    fval = driver.find_element_by_id(endId).get_attribute('value')
    if fval == "":
      driver.find_element_by_id(endId).send_keys(inputs['finishTime'])

    lval = driver.find_element_by_id(breakId).get_attribute('value')
    if lval == "":
      driver.find_element_by_id(breakId).send_keys(inputs['lunchMinutes'])

if __name__ == '__main__':
   root = Tk()
   ents = makeform(root, fields)
   root.bind('<Return>', (lambda event, e=ents: go(e)))  
   var = IntVar()
   var.set(1)
   c = Checkbutton(root, text="Save Password", variable=var)
   c.pack(side=LEFT, padx=5, pady=5) 
   b1 = Button(root, text='Go', command=(lambda e=ents: go(e)))
   b1.pack(side=LEFT, padx=5, pady=5)
   b2 = Button(root, text='Quit', command=root.quit)
   b2.pack(side=LEFT, padx=5, pady=5)
   root.mainloop()

