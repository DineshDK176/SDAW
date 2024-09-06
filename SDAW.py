import os,webbrowser,pyttsx3,mediawiki,subprocess,urllib.error,time
import requests
import wolframalpha as wa
import threading as td
import datetime as dt
import speech_recognition as sr
from tkinter import *
from PIL import Image, ImageTk
from itertools import count

class GifLabel(Label):
    text = '' # A Text for Speech Function.
    f_back,con,length  = 0,0,0 # Feedback from Function call & Condition variable
    mic_ico,mic,key_ico,key,txt_fld,submit,label = None,None,None,None,None,None,None
    
    def __init__(self, master=None,**kwargs):
        
        super().__init__(master, **kwargs)
        self.frames = []
        self.loc = 0
        self.delay = 100
        
        
    def image_load(self, gif_pic): # To Load the Image
        if isinstance(gif_pic, str):
            gif_pic = Image.open(gif_pic)
            self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(gif_pic.copy()))
                gif_pic.seek(i)

        except EOFError:
             pass

        try:
            self.delay = gif_pic.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def next_frame(self): # To loop the Image frame
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(width=1300,bg='black',image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

    engine = pyttsx3.init()
    engine.setProperty('voice', 'en-in')
    engine.setProperty('rate', engine.getProperty('rate') - 40)
    
    def speak(self, query,con=None): # Text to Speech Function
        self.label = Label(root,bg='black')
        t = ''
        if con != 0:
            for i in query:
                try:
                    t += i + ' .\n'
                except TypeError:
                    pass
        elif con == 0:
            for i in list(query):
                try:
                    t += i
                except TypeError:
                    pass
        
        self.label.config(text=f"AI: {t}",fg="white")
        self.label.pack()
       

        try:
            self.engine.say(t)
            self.engine.runAndWait()
        
        except RuntimeError:
            time.sleep(15)
            self.engine.say(t)
            self.engine.runAndWait()
        self.label.destroy()

        
        if con == 1:
            root.destroy()
            exit()
        
    def Thread_speak(self,*txt,res=None,con=None):
        self.con = con
        txt = list(txt)
        if res != None:
            txt = str(txt)
            res.split(" ")
            c = 0
            for i in res:
                txt += i
                # txt += ' '
                c += 1
                if c == 100:
                    txt += '\n'
                    c=0
                    con = 0
        speech = td.Thread(target = self.speak,args = (txt,con))
        speech.start()


    def Run(self,*action): # To Run Multiple Tasks
            try:
                os.startfile(f'{action[1]}')
                self.Thread_speak(f'Openning {action[0]}...')
            except Exception as e:
                self.Thread_speak("I cannot find it...")
            self.txt_fld.delete('1.0','end')

    def pros(self, query): # To pass the Process to system
        query = query.replace(' ','')

        if ('goodbye' in query)  or ('bye' in query) or ("seeyou" in query):
            self.txt_fld.delete('1.0','end')
            self.Thread_speak("Ok GoodBye Thank you for Interacting with Me..",con=1)

        elif ('commandprompt' in query) or ('cmd' in query):
            self.Run('commandprompt','cmd')

        elif ('paint' in query):
            self.Run('paint','mspaint.exe')

        elif ('setting' in query) or ('controlpanel' in query):
            self.Run('setting','control.exe')

        elif ('calculator' in query) or ("calc" in query):
            self.Run('calculator','calc.exe')

        elif ("texteditor" in query) or ("notepad" in query):
            self.Run('notepad','Notepad.exe')

        elif ("wordpad" in query):
            self.Run('wordpad','wordpad.exe')

        elif ("folder" in query) or ("explorer" in query) or ("file" in query) or ("thispc" in query) or ("mycompute" in query):
            self.Run('','explorer.exe')

        elif ("vlc" in query) or ("videoplayer" in query):
            self.Run('videoplayer','vlc.exe')

        elif ("windowsmediaplayer" in query) or ('mediaplayer' in query):
            self.Run('media player','wmplayer.exe')

        elif ("chrome" in query) or ("browser" in query):
            self.Run(' ','chrome.exe')

        elif ("firefox" in query):
            self.Run('firefox','firefox.exe')

        elif ("search" in query) or ("google" in query):
            self.Thread_speak("Searching....")
            query = query.replace("search","")
            query = query.replace(" ","")
            webbrowser.open(f"google.com/search?q={query}")
            self.txt_fld.delete('1.0','end')

        elif ("youtube" in query):
            self.Thread_speak("Opening Youtube...")
            query = query.replace("youtube","")
            query = query.replace(" ","")
            webbrowser.open(f"youtube.com/results?search_query={query}")
            self.txt_fld.delete('1.0','end')

        elif ("wikipedia" in query):
            mk = mediawiki.MediaWiki()
            query = query.replace("wikipedia","")
            self.txt_fld.delete('1.0','end')
            try:
                self.Thread_speak("According to wikipedia",res=mk.summary(query,sentences=2),con = 2)
                
            except mediawiki.DisambiguationError as e:

                self.Thread_speak("Sorry the Information you looking is couldn't find...!")
                self.Thread_speak("Give Clear Content..")
            except requests.exceptions.ConnectionError as e:
                self.Thread_speak(str(e))

            except Exception as e:
                self.Thread_speak(str(e))

        elif ("play" in query):
            
            try:
                query = query.replace("play","")
                yt.playonyt(query)
                self.Thread_speak("Starting...")
                self.txt_fld.delete('1.0','end')

            except Exception:
                self.Thread_speak("Please Check Your Internet and Try again")

        elif ("shutdown" in query) or ("switchoff" in query) or ("poweroff" in query):
            subprocess.run(["shutdown","-s"])
            self.txt_fld.delete('1.0','end')
            self.Thread_speak("Ok GoodBye Thank you for Interacting with Me..",con=1)

        else:
            try:
                clt = wa.Client('GPGV2J-52JYUXUERG') #ID of the API
                res = clt.query(query)
                self.txt_fld.delete('1.0','end')
                ans=''

                for i in res.results:
                    ans+=i.text

                if ans == '':
                    self.Thread_speak('I cannot find the answer..')
                else :
                    self.Thread_speak(ans)

            except urllib.error.URLError :
                self.txt_fld.delete('1.0','end')
                self.Thread_speak("Please Check Your Internet and Try again")

    def get_txt(self): # Getting text from Text Field
        self.text = self.txt_fld.get('1.0','end').lower()
        self.pros(self.text)

    def welcome(self): # Welcome Wish
        time = int(dt.datetime.now().hour)
        if time >= 1 and time < 12:
            wish = "Good Morning"
        elif time >= 12 and time < 16:
            wish = "Good Afternoon"
        else:
            wish = "Good Evening"
        self.Thread_speak(wish,"I am Michael","How can I help you")



    def icon(self,val=None,txts=None):

        if val == 1: # For Keyboard intraction

            self.key.forget()

            self.mic.pack()

            self.txt_fld.pack()
            
            self.submit.pack()


            
        elif val == 0: # For Mic Interaction

            # self.label.config(text="Recognising...")
            # self.label.pack()
            #time.sleep(2)

            r = sr.Recognizer()
            while (1):
                err = 0
                try:
                    with sr.Microphone() as s:
                        mytxt = ''
                        r.adjust_for_ambient_noise(s,duration=0.2)
                        audio = r.listen(s)
                        mytxt = r.recognize_google(audio)
                        mytxt = mytxt.lower()
                except sr.RequestError as e:
                    self.Thread_speak(f"Please Check Your Internet Connection...")
                    self.icon(val = 1)
                    break
                except sr.UnknownValueError:
                    self.Thread_speak("Say again please..")
                    err = 1
                if err != 1:
                    print(mytxt)
                    self.pros(query=mytxt)
                    # time.sleep(len(mytxt))
        if txts == 0:

            self.label.destroy()

            self.txt_fld.forget()

            self.submit.forget()

            self.key.pack()

            self.mic.forget()

        
        
    def window(self,master=None): # Send the Address of the Required Files to PhotoImage function

        self.mic_ico = PhotoImage(file = "D:\\Codes\\Pyton\\SDAW\\Mic.png")

        self.mic = Button(master,width=23,height=25,image=self.mic_ico,command=lambda:self.icon(val=0,txts = 0))

        self.key_ico = PhotoImage(file = "D:\\Codes\\Pyton\\SDAW\\Keyboard.png")

        self.key = Button(master,image=self.key_ico,width=23,height=15,command= lambda:self.icon(val=1))

        self.txt_fld = Text(master,width=50,height=1,bg='white',fg='black')

        self.submit = Button(master,text='Submit',width=10,command=lambda :self.get_txt())

        self.key.pack()

        self.welcome()

        time.sleep(5)

        self.icon(val=0,txts=1)

        
if __name__ == '__main__': # Main Function
    try:
        import pywhatkit as yt
    except Exception as e:
        pass

    global root
    
    root = Tk()
    root.geometry('1355x850')
    root.title('Desktop  Assistant')
    root.config(bg='black')

    lb = GifLabel(root)
    lb.image_load('D:\\Codes\\Pyton\\SDAW\\AI Interface.gif')
    lb.pack()

    w_thread = td.Thread(target = lambda:lb.window(master=root))
    w_thread.start()
    root.mainloop()
