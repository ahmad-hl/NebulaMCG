from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# chromedriverpath = webdriver.Chrome('/home/symlab/ahmad/webrtc-node-app/chromedriver')
# driver.implicitly_wait(30)
# driver.maximize_window()
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome( options=options)
driver.implicitly_wait(30)
driver.maximize_window()

# Navigate to the application home page
driver.get("https://localhost:8444")
# get the search textbox
search_field = driver.find_element_by_id("room-input")
search_field.send_keys(200)
search_field = driver.find_element_by_id("connect-button")
search_field.send_keys(Keys.RETURN)

print(driver.current_url)
driver.implicitly_wait(30)
driver.quit()
# driver.close()
