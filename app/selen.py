from selenium import webdriver

class Epiphany(webdriver.WebKitGTK):
    def __init__(self):
        options = webdriver.WebKitGTKOptions()
        options.binary_location = 'epiphany'
        options.add_argument('--automation-mode')
        options.add_argument('--display=:19')
        options.set_capability('browserName', 'Epiphany')
        options.set_capability('version', '3.36.4')

        webdriver.WebKitGTK.__init__(self, options=options, desired_capabilities={})

ephy = Epiphany()
ephy.get('http://www.patrzyk.me/foreign-tourists')
print(ephy.page_source)
ephy.quit()