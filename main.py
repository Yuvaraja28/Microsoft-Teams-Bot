import threading, time, re, traceback, os, discord, base64
from io import BytesIO
from bs4 import BeautifulSoup
from selenium import webdriver
from colorama import Fore, Style
from discord.ext import commands
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains

"""
os.environ['BOT'] = None
os.environ['EMAIL'] = None
os.environ['PASSWORD'] = None
os.environ['GOOGLE_CHROME_BIN'] = None
os.environ['CHROMEDRIVER_PATH'] = None
os.environ['PORT'] = 80
"""

prefix = '>'
client = commands.Bot(prefix)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(status=discord.Status.online, type=discord.ActivityType.watching, name=f"all my Owner's Classes"))
    print(f'{Fore.CYAN}{Style.BRIGHT}Bot Started{Style.RESET_ALL}')
@client.command('login')
async def login_bot(ctx, mode=None):
    if mode == 'start':
        await ctx.send(auto_login.initate())
    elif mode == 'stop':
        await ctx.send(auto_login.discard())
    else:
        await ctx.send(f"**__Available Modes__**\n> `{prefix}login start` **-** to Start Auto-Login Process\n> `{prefix}login stop` **-** to Stop Auto-Login Process")
@client.command('calendar')
@commands.is_owner()
async def calendar_bot(ctx):
    await ctx.send(Tools.click_calendar())
@client.command('browser')
@commands.is_owner()
async def browser_bot(ctx, mode):
    if mode == 'restart':
        try:        
            await ctx.send(f"**{scrape.initate()}**")        
        except:
            await ctx.send("**ERROR :** Cant Restart the Broswer")
    elif mode == 'refresh':
        await ctx.send(scrape.refresh())
    else:
        await ctx.send(f"**__Available Modes__**\n> `{prefix}browser restart` **-** to Restart the current Browser\n> `{prefix}browser refresh` **-** to Refresh the current Tab")    
@client.command('class')
@commands.is_owner()
async def class_bot(ctx, mode):
    if mode == 'join':
        list = Tools.get_class_list()
        desc = "**__Below are the Classess Scheduled for Today__**\n"
        ids = []
        for x, y in enumerate(list):
            ids.append(y)
            desc += f"**{x+1})** {list[y]}\n"
        desc += "**Waiting for Input**\n"
        msg = await ctx.send(desc)
        while True:
            try:
                def check(message):
                    return message.author == ctx.author and message.channel == ctx.channel
                reply = await client.wait_for('message', check=check, timeout=60)
                id = int(reply.content)
                desc += 'Processing your command...\n'
                await msg.edit(content=desc)
                desc += auto_login.join_class([ids[id-1], list[ids[id-1]]])
                await msg.edit(content=desc)
                break
            except ValueError:
                desc += "**ERROR :** Enter a Valid Number not a String" + '\n'
                await msg.edit(content=desc)
            except:
                desc += f"Error Occured\n```py\n{traceback.format_exc()}```\n"
                await msg.edit(content=desc)
                break
    elif mode in ['leave', 'quit']:
        await ctx.send(auto_quit.initate())
    elif mode == 'retry':
        await ctx.send(Tools.click_retry())
    else:
        await ctx.send(f"**__Available Modes__**\n> `{prefix}class join` **-** to Join a Class\n> `{prefix}class leave` **-** to leave the current Class\n> `{prefix}class retry` **-** to click Retry Button in MSTeams")    
@client.command('status', aliases=['state', 'info', 'classes'])
@commands.is_owner()
async def status_bot(ctx):
    data = auto_login.get_status()
    list = Tools.get_class_list()
    try:
        desc_class = "**__Below are the Classess Scheduled for Today__**\n"
        for x, y in enumerate(list):
            desc_class += f"**{x+1})** {list[y]}\n"
        desc_class += ""
    except:
        desc_class = f"**ERROR : Cannot get Class Informations**\n> First use `{prefix}calendar` to get Class Info"
    desc = f"""
**__Online Class INFO__**
**Auto Login Status :** {data['running']}
**Auto Quit Status  :** {auto_quit.get_status()['running']}
**Entered UserID    :** {data['username']}
**Entered Password  :** {data['password']}
**Clicked Submit    :** {data['submit']}
**Current Session   :** {data['class']}\n{desc_class}"""
    await ctx.send(desc)
@client.command('screenshot', aliases=['screen','photo','ss'])
@commands.is_owner()
async def screenshot_bot(ctx):
    await ctx.send("Taking ScreenShot...")
    data = base64.b64decode(scrape.driver.get_screenshot_as_base64())
    await ctx.send(file=discord.File(BytesIO(data), "ScreenShotOfTheClass.png"))

class Startup():
    def __init__(self):
        os.system('cls')
        print(f"""{Fore.CYAN}{Style.BRIGHT}  Yuvaraja  {Style.RESET_ALL}""")

class WebDriver(threading.Thread):
    def run(self):
        self.running = False
        self.options = ChromeOptions()
        self.options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_experimental_option("prefs", { \
            "profile.default_content_setting_values.media_stream_mic": 2, 
            "profile.default_content_setting_values.media_stream_camera": 2})
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(options=self.options, executable_path=os.environ.get("CHROMEDRIVER_PATH"))
        self.movements = ActionChains(self.driver)
        self.driver.get('https://teams.microsoft.com/')
        while True:
            if self.running == True:
                try:
                    self.driver.quit()
                    self.driver = webdriver.Chrome(options=self.options)
                    self.driver.get('https://teams.microsoft.com/')    
                    self.running = False
                except: pass
    def initate(self):
        self.running = True
        return "Reloading the Browser"
    def discard(self):
        self.running = False
        return "Stopping Reloading the Browser"
    def refresh(self):
        self.driver.refresh()
        return "Refreshed the Current Browser"
class HandleCommands(threading.Thread):
    def run(self):
        print(f"{Fore.CYAN}{Style.BRIGHT}Started Auto-Login...{Style.RESET_ALL}")
        while True:
            try:
                inp=input(f'{Fore.CYAN}{Style.BRIGHT}> {Style.RESET_ALL}')
                if inp=="cookies":
                    Tools.collect_cookies()
                elif inp=="loginstart":
                    print(auto_login.initate())
                elif inp=="loginstop":
                    print(auto_login.discard())
                elif inp=="loginstatus":
                    print(auto_login.get_status())
                elif inp=="calendar":
                    print(Tools.click_calendar())
                elif inp=="retry":
                    print(Tools.click_retry())
                elif inp=="refresh":
                    print(scrape.refresh())
                elif inp=="reload":
                    try:
                        print(scrape.initate())
                    except:
                        print("ERROR : Cant Reload the Broswer")
                elif inp=="classlist":
                    list = Tools.get_class_list()
                    print(f"{Fore.CYAN}{Style.BRIGHT}Below are the Classess Scheduled for Today{Style.RESET_ALL}")
                    for x, y in enumerate(list):
                        print(f"{Fore.CYAN}{Style.BRIGHT}{x+1}){Style.RESET_ALL} {list[y]}")
                elif inp=="joinclass":
                    list = Tools.get_class_list()
                    ids = []
                    print(f"{Fore.CYAN}{Style.BRIGHT}Below are the Classess Scheduled for Today{Style.RESET_ALL}")
                    for x, y in enumerate(list):
                        ids.append(y)
                        print(f"{Fore.CYAN}{Style.BRIGHT}{x+1}){Style.RESET_ALL} {list[y]}")
                    id = int(input('Choose the class to Join : '))
                    print(auto_login.join_class([ids[id-1], list[ids[id-1]]]))
                elif inp=="quit":
                    print(auto_quit.initate())
            except KeyboardInterrupt: break
            except EOFError: break
            except: 
                print(traceback.format_exc())
class Tools:
    def get_source():
        try:
            elem = scrape.driver.find_element(By.XPATH, "//*")
            source_code = elem.get_attribute("outerHTML")
            return source_code
        except:
            return "Error Occured"
    def get_class_list():
        try:
            source = Tools.get_source()
            if source == "Error Occured":
                raise ValueError
            months = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
            day = time.localtime().tm_mday
            mon = months[time.localtime().tm_mon]
            ex = BeautifulSoup(source, 'html.parser')
            exe= ex.find_all("div", class_='node_modules--msteams-bridges-components-calendar-grid-dist-es-src-renderers-calendar-multi-day-renderer-calendar-multi-day-renderer__eventCard--3NBeS')
            total_classes = {}
            len_total_classes = 1
            for x in exe:
                temp=BeautifulSoup(str(x), 'html.parser')
                text = [tag['aria-label'] for tag in temp.select('div[aria-label]')]
                text=re.sub('\n+', ' ', text[0])
                text=re.sub(' +', ' ', text)
                if f"{mon} {day}" in text:
                    ids = [tag['id'] for tag in temp.select('div[id]')]
                    len_total_classes+=1
                    total_classes[ids[0]] = str(text).replace(', Press Shift+F10 for more options', '')
            auto_login.class_list = total_classes
            return total_classes
        except:
            return "Error Occured"
    def disable_mic_cam():
        try:
            source = Tools.get_source()
            if source == "Error Occured":
                raise ValueError
            microphone = scrape.driver.find_element(By.XPATH, '//*[@id="preJoinAudioButton"]/div/button')
            video = scrape.driver.find_element(By.XPATH, '//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button')
            source = Tools.get_source()
            temp=BeautifulSoup(source, 'html.parser')
            main = [tag['title'] for tag in temp.select('span[title]')]
            for x in main:
                if x == 'Mute microphone':
                    microphone.click()
                if x == 'Turn camera off':
                    video.click()
        except:
            return "Error Occured"
    def click_calendar():
        try:
            scrape.driver.find_element(By.XPATH,'//*[@id="app-bar-ef56c0de-36fc-4ef8-b417-3d82ba9d073c"]').click()
            return "Successfully Clicked"
        except:
            return "Error Occured"
    def collect_cookies():
        cookie=scrape.driver.get_cookies
        with open('creds.txt','w') as f:
            f.write(str(cookie))
    def click_retry():
        try:
            scrape.driver.find_element(By.XPATH,'//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/div[2]/div[2]/div/div/calling-retry-screen/div/form/div/button[1]').click()
            return "Successfully Clicked"
        except:
            return "Error Occured"
            

class AutoLogin(threading.Thread):
    def run(self):
        self.running = True
        self.class_list = None
        self.status = {'running':self.running,'username':None, 'password':None, 'submit':None, 'class':None}
        while True:
            if self.running:
                while True:
                    try:
                        scrape.driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(os.environ.get("EMAIL"))
                        scrape.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                        self.status['username'] = 'success'
                        break
                    except:
                        self.status['username'] = 'failed'
                time.sleep(2.5)
                while True:
                    try:
                        scrape.driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(os.environ.get("PASSWORD"))
                        scrape.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                        self.status['password'] = 'success'
                        break
                    except:
                        self.status['password'] = 'failed'
                time.sleep(2.5)
                while True:
                    try:
                        scrape.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                        self.status['submit'] = 'success'
                        self.status['running'] = False
                        self.running = False
                        break
                    except:
                        self.status['submit'] = 'failed'
            time.sleep(1)
    def initate(self):
        self.running = True
        self.status['running'] = True
        return "Started Auto-Login..."
    def discard(self):
        self.running = False
        self.status['running'] = False
        return "Stopping Auto-Login"
    def get_status(self):
        return self.status
    def join_class(self, data):
        try:
            id = data[0]
            self.status['class'] = data[1]
            scrape.driver.find_element(By.XPATH, f'//*[@id="{id}"]').click()
            time.sleep(1)
            for x in range(4,20):
                try:
                    scrape.driver.find_element(By.XPATH, f'/html/body/div[{x}]/div/div/div/div[3]/div/div/div[1]/div[2]/div[3]/button[1]/span').click()
                except:
                    pass
            time.sleep(0.8)
            for x in range(1,10):
                try:
                    scrape.driver.find_element(By.XPATH, f'//*[@id="ngdialog{x}"]/div[2]/div/div/div/div[1]/div/div/div[2]/div/button').click()
                except: pass
            time.sleep(1)
            Tools.disable_mic_cam()
            time.sleep(1)
            scrape.driver.find_element(By.XPATH, '//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[1]/div/div/button').click()
            return f"Successfully Joined [{data[1]}]"
        except:
            return "Error Occured"

class AutoQuit(threading.Thread):
    def run(self):
        self.running = False
        self.class_list = None
        self.status = {'running':self.running}
        while True:
            if self.running:
                while True:
                    try:
                        try:
                            window = scrape.driver.find_element(By.XPATH, '//*[@id="page-content-wrapper"]/div[1]/div/calling-screen/div/div[2]/div[2]').click()
                            scrape.movements.move_to_element(window)
                            scrape.movements.perform()
                        except: pass
                        time.sleep(1)
                        scrape.driver.find_element(By.XPATH, '//*[@id="hangup-button"]').click()
                        auto_login.status['class'] = None
                        self.running = False
                        break
                    except: pass
            time.sleep(1)
    def initate(self):
        self.running = True
        self.status['running'] = True
        return f"Quitting [{auto_login.status['class']}] Class"
    def discard(self):
        self.running = False
        self.status['running'] = False
        return "Stopping AutoQuit"
    def get_status(self):
        return self.status

class WebServer(threading.Thread):
    def run(self):
        app = Flask(__name__)
        auth = HTTPBasicAuth()
        @app.route('/')
        def login():
            return "<h1>HI, I am Yuvaraja, Passionate Backend Developer :)</h1>"
        @auth.verify_password
        def verify_password(email, password):
            return verifyAuthentication(email, password)
        def verifyAuthentication(email, password):
            knownUsers = {'yuvaraja28': 'yuvaraja'} #credentials for the webserver
            authenticated = False
            if email in knownUsers:
                if knownUsers[email] == password:
                    authenticated = True
            return authenticated
        @app.route('/login/<mode>')
        @auth.login_required
        def login_server(mode):
            if mode == 'start':
                return f"<h3>{auto_login.initate()}</h3>"
            elif mode == 'stop':
                return f"<h3>{auto_login.discard()}</h3>"
            else:
                return f"<h2>Available Modes</h2><h3>[login/start] - to Start Auto-Login Process</h3><h3>[login/stop] - to Stop Auto-Login Process</h3>"
        @app.route('/calendar')
        @auth.login_required
        def calendar_server():
            return f"<h3>{Tools.click_calendar()}</h3>"
        @app.route('/browser')
        def browser_help():
            return f"<h2>Available Modes</h2><h3>[browser/restart] - to Restart the current Browser</h3><h3>[browser/refresh] - to Refresh the current Tab</h3>"
        @app.route('/browser/<mode>')
        @auth.login_required
        def browser_server(mode):
            if mode == 'restart':
                try:        
                    return f"<h3>{scrape.initate()}</h3>"        
                except:
                    return "<h3>ERROR : Cant Restart the Broswer</h3>"
            elif mode == 'refresh':
                return f"<h3>{scrape.refresh()}</h3>"
            else:
                return f"<h2>Available Modes</h2><h3>[browser/restart] - to Restart the current Browser</h3><h3>[browser/refresh] - to Refresh the current Tab</h3>"
        @app.route('/class')
        def class_help():
            return f"<h2>Available Modes</h2><h3>[class/join] - to Join a Class</h3><h3>[class/leave] - to leave the current Class</h3><h3>[class/retry] - to click Retry Button in MSTeams</h3>"    
        @app.route('/class/<mode>')
        @auth.login_required
        def class_server(mode):
            if mode == 'join':
                list = Tools.get_class_list()
                ids = []
                desc = ""
                for x, y in enumerate(list):
                    ids.append(y)
                while True:
                    try:
                        id = request.args.get('no', default = 1, type = int)
                        desc += f"<h3>{auto_login.join_class([ids[id-1], list[ids[id-1]]])}</h3>"
                        return desc
                    except ValueError:
                        desc += "<h3>ERROR : Enter a Valid Number not a String</h3>"
                        return desc
                    except:
                        desc += f"<h3>Error Occured</h3>{traceback.format_exc()}"
                        return desc
            elif mode in ['leave', 'quit']:
                return f"<h3>{auto_quit.initate()}</h3>"
            elif mode == 'retry':
                return f"<h3>{Tools.click_retry()}</h3>"
            else:
                return f"<h2>Available Modes</h2><h3>[class/join] - to Join a Class</h3><h3>[class/leave] - to leave the current Class</h3><h3>[class/retry] - to click Retry Button in MSTeams</h3>"    
        @app.route('/status')
        @auth.login_required
        def status_server():
            data = auto_login.get_status()
            list = Tools.get_class_list()
            try:
                desc_class = "<h3>Below are the Classess Scheduled for Today</h3>"
                for x, y in enumerate(list):
                    desc_class += f"<h3>{x+1}) {list[y]}</h3>"
                desc_class += ""
            except:
                desc_class = f"<h3>ERROR : Cannot get Class Informations</h3><h3>First use [calendar] to get Class Info</h3>"
            desc = f"""
        <h2>Online Class INFO</h2>
        <h3>Auto Login Status : {data['running']}</h3>
        <h3>Auto Quit Status  : {auto_quit.get_status()['running']}</h3>
        <h3>Entered UserID    : {data['username']}</h3>
        <h3>Entered Password  : {data['password']}</h3>
        <h3>Clicked Submit    : {data['submit']}</h3>
        <h3>Current Session   : {data['class']}</h3>{desc_class}"""
            return desc
        @app.route('/screen')
        def screenshot_screen():
            data = scrape.driver.get_screenshot_as_base64()
            return f'<!DOCTYPE html><html><body><img src="data:image/png;base64,{data}" alt="ClassScreenShot" width="500" height="333"></body></html>'
        @auth.error_handler
        def unauthorized():
            return '<h3>Hmm whoare you</h3>'    
        @app.errorhandler(400)
        def bad_request(error):
            return 'Bad request'
        @app.errorhandler(404)
        def not_found(error):
            return '<h3>LOL,you just came to Wrong Neighbourhood</h3>'
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

Startup()
HandleCommands().start()
WebServer().start()
scrape = WebDriver()
scrape.start()
auto_login = AutoLogin()
auto_login.start()
auto_quit = AutoQuit()
auto_quit.start()

client.run(os.environ.get("BOT"))