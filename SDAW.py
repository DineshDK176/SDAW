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
        label = Label(root,bg='black')
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
        label.config(text=f"AI: {t}",fg="white")
        label.pack()
        
        try:
            self.engine.say(t)
            self.engine.runAndWait()
            
        except RuntimeError:
            time.sleep(5)
            self.engine.say(t)
            self.engine.runAndWait()
        label.destroy()
        
        if con == 1:
            root.destroy()
            exit()
        
    def Thread_speak(self,*txt,res=None,con=None):
        self.con = con
        txt = list(txt)
        if res != None:
            txt = str(txt)
            res.split()
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

    def Run(self,*action,txt_fld=None): # To Run Multiple Tasks
        
        self.Thread_speak(f'Openning {action[0]}...')
        os.startfile(f'{action[1]}')
        txt_fld.delete('1.0','end')

    def pros(self, query,txt_fld=None): # To pass the Process to system
        query = query.replace(' ','')

        if ('goodbye' in query)  or ('bye' in query):
            txt_fld.delete('1.0','end')
            self.Thread_speak("Ok GoodBye Thank you for Interacting with Me..",con=1)

        elif ('commandprompt' in query) or ('cmd' in query):
            self.Run('commandprompt','cmd',txt_fld=txt_fld)

        elif ('paint' in query):
            self.Run('paint','mspaint.exe',txt_fld=txt_fld)

        elif ('setting' in query) or ('controlpanel' in query):
            self.Run('setting','control.exe',txt_fld=txt_fld)

        elif ('calculator' in query):
            self.Run('calculator','calc.exe',txt_fld=txt_fld)

        elif ("texteditor" in query) or ("notepad" in query):
            self.Run('notepad','Notepad.exe',txt_fld=txt_fld)

        elif ("wordpad" in query):
            self.Run('wordpad','wordpad.exe',txt_fld=txt_fld)

        elif ("folder" in query) or ("explorer" in query) or ("file" in query):
            self.Run('folder','explorer.exe',txt_fld=txt_fld)

        elif ("vlc" in query) or ("videoplayer" in query):
            self.Run('videoplayer','vlc.exe',txt_fld=txt_fld)

        elif ("windowsmediaplayer" in query) or ('mediaplayer' in query):
            self.Run('media player','wmplayer.exe',txt_fld=txt_fld)

        elif ("chrome" in query) or ("browser" in query):
            self.Run(' ','chrome.exe',txt_fld=txt_fld)

        elif ("firefox" in query):
            self.Run('firefox','firefox.exe',txt_fld=txt_fld)

        elif ("search" in query):
            self.Thread_speak("Searching....")
            query = query.replace("search","")
            query = query.replace(" ","")
            webbrowser.open(f"google.com/search?q={query}")
            txt_fld.delete('1.0','end')

        elif ("youtube" in query):
            self.Thread_speak("Opening Youtube...")
            query = query.replace("youtube","")
            query = query.replace(" ","")
            webbrowser.open(f"youtube.com/results?search_query={query}")
            txt_fld.delete('1.0','end')

        elif ("wikipedia" in query):
            mk = mediawiki.MediaWiki()
            query = query.replace("wikipedia","")
            txt_fld.delete('1.0','end')
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
                txt_fld.delete('1.0','end')

            except Exception:
                self.Thread_speak("Please Check Your Internet and Try again")

        elif ("shutdown" in query) or ("switchoff" in query) or ("poweroff" in query):
            subprocess.run(["shutdown","-s"])
            txt_fld.delete('1.0','end')
            self.Thread_speak("Ok GoodBye Thank you for Interacting with Me..",con=1)

        else:
            try:
                clt = wa.Client('GPGV2J-HU83EK4K43')
                res = clt.query(self.text)
                txt_fld.delete('1.0','end')
                ans=''
                for i in res.results:
                    ans+=i.text
                if ans == '':
                    self.Thread_speak('I cannot find the answer..')
                else :
                    self.Thread_speak(ans)
            except urllib.error.URLError :
                txt_fld.delete('1.0','end')
                self.Thread_speak("Please Check Your Internet and Try again")

    def get_txt(self,txt_fld=None): # Getting text from Text Field
        self.text = txt_fld.get('1.0','end').lower()
        self.pros(self.text,txt_fld=txt_fld)

    def welcome(self): # Welcome Wish
        time = int(dt.datetime.now().hour)
        if time >= 1 and time < 12:
            wish = "Good Morning"
        elif time >= 12 and time < 16:
            wish = "Good Afternoon"
        else:
            wish = "Good Evening"
        self.Thread_speak(wish,"I am Michael","How can I help you")
        
        
    def window(self,master=None): # Send the Address of the Required Files to PhotoImage function

        mic_ico = PhotoImage(file = "D:\\Codes\\Pyton\\SDAW\\Mic.png")

        key_ico = PhotoImage(file = "D:\\Codes\\Pyton\\SDAW\\Keyboard.png")

        txt_fld = Text(master,width=50,height=1,bg='white',fg='black')

        submit = Button(master,text='Submit',width=10,command=lambda :self.get_txt(txt_fld=txt_fld))

        txt_fld.pack()
        
        submit.pack()
        
        self.welcome()
        
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
