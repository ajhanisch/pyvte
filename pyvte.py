#!/usr/bin/env python3

import os
import sys
import time
import logging
import getpass
import argparse
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Setup:
    '''
    VARIABLES
    '''
    version = '0.3'
    program = os.path.basename(__file__)
    repository = 'https://github.com/ajhanisch/pyVTE'
    wiki = 'https://github.com/ajhanisch/pyVTE/wikis/home'
    date = time.strftime('%Y-%m-%d_%H-%M-%S')
    user = getpass.getuser()

    '''
    CREATE ARGUMENT PARSER
    '''
    parser = argparse.ArgumentParser(description='Program to automatically process courses/classes from FedVTE within specificied role.')

    '''
    REQUIRED ARGUMENTS
    '''
    process = parser.add_argument_group('Required', 'Ensure to use all of these parameters to run successfully.')
    process.add_argument(
    '--driver',
    type=str,
    help='Full path to [browser].exe file. Example: C:\\[users]\\[user]\\Desktop\\chromedriver\\chromedriver.exe.'
    )
    process.add_argument(
    '--url',
    type=str,
    help='URL to open within FedVTE. Example: https://fedvte.usalearning.gov/launcher.php?group=1'
    )
    process.add_argument(
    '--username',
    type=str,
    help='Username used to log into FedVTE.'
    )
    process.add_argument(
    '--password',
    type=str,
    help='Password used to log into FedVTE.'
    )
    process.add_argument(
    '--role',
    choices=['Technical Support Specialist', 'Data Administrator', 'Knowledge Management', 'Network Services', 'System Administrator', 'Systems Analysis'],
    help='Role name within the menu of the URL example. Currently you must choose one of these roles.'
    )
    '''
    OPTIONAL ARGUMENTS
    '''
    parser.add_argument(
    '--verbose',
    choices=[ 'debug', 'info', 'warning', 'error', 'critical' ],
    default='info',
    help='Enable specific program verbosity. Default is info. Set to debug for complete script processing in logs and screen. Set to warning or critical for minimal script processing in logs and screen.'
    )
    parser.add_argument(
    '--headless',
    action='store_true',
    help='Disable browser from opening, all actions happen in the background.'
    )

    '''
    VERSION
    '''
    parser.add_argument(
    '--version',
    action='version',
    version='[{}] - Version [{}]. Check [{}] for the most up to date information.'.format(program, version, repository)
    )

    args = parser.parse_args()

    '''
    DIRECTORIES
    '''
    dir_working = os.getcwd()
    dir_working_log = os.path.join(dir_working, 'LOGS', date)

    '''
    FILES
    '''
    file_log = os.path.join(dir_working_log, '{}_{}.log'.format(date, program))

    '''
    DICTIONARIES
    '''
    dict_directories = {
    'dir_working_log' : dir_working_log
    }

class pyVTE:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _login(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--log-level=3")

        if self.headless == True:
            self.chrome_options.add_argument("--headless")
        elif self.headless == False:
            self.chrome_options.add_argument("--window-size=1920x1080")
        try:
            self.driver = webdriver.Chrome(chrome_options=self.chrome_options, executable_path=self.driver_browser) # Using Chrome to access web
            self.driver.get(self.url) # Open the website
        except:
            logging.error('[!] Unable to open [{}]. Most likely due to incorrect URL. Ensure your URL is correct.'.format(self.url))
            sys.exit()
        self.id_box = self.driver.find_element_by_name('add') # Select the id box
        self.id_box.send_keys(self.username) # Send id information
        self.pass_box = self.driver.find_element_by_name('pin') # Find password box
        self.pass_box.send_keys(self.password) # Send password
        self.login_button = self.driver.find_element_by_name('submit') # Find login button
        self.login_button.click() # Click login
        try:
            self.my_courses = self.driver.find_element_by_class_name('mycourses_up') # Select MyCourses
            self.my_courses.click() # Click my_courses
        except:
            logging.error('[!] Unable to select MyCourses. Most likely due to incorrect username/password. Ensure your username/password are correct.')
            sys.exit()
        try:
            self.work_role = self.driver.find_element_by_xpath("//select[@id='workrole']/option[text()='{}']".format(self.role)).click() # Select Workrole
            return self.driver
        except:
            logging.error('[!] Unable to find courses for work role [{}]. Ensure your work role is spelled correctly and/or exists.'.format(self.role))
            sys.exit()

    def _find_courses(self):
        # self.start_classes = driver.find_elements_by_xpath('//*[@name="begin"]')
        self.start_classes = self.driver.find_elements_by_xpath('//*[@name="resume"]')
        self.list_classes = []
        for s in self.start_classes:
            self.title = s.get_attribute('title')
            if self.title not in self.list_classes:
                self.list_classes.append(self.title)
        return self.list_classes

    def _process_courses_classes(self):
        self.count_list_courses = len(self.list_courses)
        if self.count_list_courses > 0:
            logging.info('[*] Looks like we are automatically processing [{}] courses for you. Starting now.'.format(self.count_list_courses))
            self.dict_courses_classes = {} # dictionary to hold each course and all classes for each course
            self.window_main = self.driver.window_handles[0]

            for self.course in self.list_courses:
                logging.info('[-] Finding course [{}].'.format(self.course))
                self.find_class = self.driver.find_element_by_xpath('//*[@title="{}"]'.format(self.course))
                if self.find_class:
                    logging.info('[+] Found course [{}].'.format(self.course))
                    self.dict_courses_classes[self.course] = []
                    self.click_button = self.find_class.click() # Click on resume/begin login_button first page
                    try:
                        self.driver.find_element_by_name('begin').click() # Click on begin second page. Course has not yet started.
                    except:
                        self.driver.find_element_by_name('resume').click() # Click on resume second page. Course was already started.
                    logging.info('[-] Looking for classes within course [{}]'.format(self.course))
                    self.count_looped = 1
                    self.dejavu = True
                    while(self.dejavu):
                        try:
                            self.class_links = [ x for x in self.driver.find_elements_by_xpath("//a[@href]") if 'launcher.php' in x.get_attribute('href') ]
                            self.count_class_links = len(self.class_links)
                            while self.count_class_links >= self.count_looped:
                                if self.count_class_links == self.count_looped:
                                    if self.role == 'Technical Support Specialist':
                                        self.driver.get('https://fedvte.usalearning.gov/mycourses_sub.php?group=1&submenu=operate_and_maintain&showsub=1|0|0|0|0|0')
                                    elif self.role == 'Data Administrator':
                                        #self.driver.get('https://fedvte.usalearning.gov/mycourses_sub.php?group=1&submenu=operate_and_maintain&showsub=0|1|0|0|0|0')
                                        logging.error('[!] Role [{}] does not currently have any courses. Try again later.'.format(self.role))
                                        sys.exit()
                                    elif self.role == 'Knowledge Management':
                                        self.driver.get('https://fedvte.usalearning.gov/mycourses_sub.php?group=1&submenu=operate_and_maintain&showsub=0|0|1|0|0|0')
                                    elif self.role == 'Network Services':
                                        self.driver.get('https://fedvte.usalearning.gov/mycourses_sub.php?group=1&submenu=operate_and_maintain&showsub=0|0|0|1|0|0')
                                    elif self.role == 'System Administrator':
                                        self.driver.get("https://fedvte.usalearning.gov/mycourses_sub.php?group=1&submenu=operate_and_maintain&showsub=0|0|0|0|1|0")
                                    elif self.role == 'Systems Analysis':
                                        self.driver.get('https://fedvte.usalearning.gov/mycourses_sub.php?group=1&submenu=operate_and_maintain&showsub=0|0|0|0|0|1')
                                    else:
                                        logging.error('[!] Role [{}] does not exist. Try again with a real role.'.format(self.role))
                                        sys.exit()
                                    sleep(3)
                                    self.dejavu = False
                                    break
                                else:
                                    for c in self.class_links[1:]:
                                        self.course_title = c.get_attribute('text')
                                        if self.course_title not in self.dict_courses_classes[self.course]:
                                            self.count_looped += 1
                                            logging.info('[!] Found class [{}].'.format(self.course_title))
                                            self.dict_courses_classes[self.course].append(self.course_title)
                                            self.course_class = self.driver.find_element_by_link_text('{}'.format(self.course_title)) # open class video window
                                            self.course_class.click()
                                            sleep(3)
                                            self.window_after = self.driver.window_handles[1] # switch focus to opened window
                                            self.driver.switch_to_window(self.window_after)
                                            sleep(0.5)
                                            self.driver.close()
                                            sleep(0.5)
                                            self.driver.switch_to_window(self.window_main)
                                            logging.info('[+] Finished class [{}]! [{}/{}] processed.'.format(self.course_title, self.count_looped, self.count_class_links))
                                    # End for c in self.class_links[1:]
                        except:
                            continue
                else:
                    logging.error('[!] Error finding class [{}]!'.format(self.course))
                # End if self.find_class:
            # End for course in self.list_courses
        else:
            logging.error('[!] list_courses contains [{}] courses. We need at least one to process. Exiting.'.format(self.count_list_courses))
            sys.exit()
        # End if self.count_list_courses > 0:
        logging.info('[*] Finished processing [{}] courses for you. See you next time!'.format(self.count_list_courses))
        sys.exit()

        return self.dict_courses_classes

def main():
    '''
    Main function. Everything starts here.
    '''
    setup = Setup()
    args = setup.args
    '''
    Create required directories from setup.
    '''
    for key, value in setup.dict_directories.items():
        if not os.path.exists(value):
            os.makedirs(value)

    '''
    Setup logging.
    '''
    dict_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    }
    level_name = args.verbose
    level = dict_levels.get(level_name)
    format = '[%(asctime)s] - [%(levelname)s] - %(message)s'
    handlers = [logging.FileHandler(setup.file_log), logging.StreamHandler()]
    logging.basicConfig(
    level = level,
    format = format,
    handlers = handlers
    )
    '''
    Present what arguments and parameters are being used. Useful for developer and user of script to easily start troubleshooting by having as much info in logs as possible.
    '''
    logging.debug('Hello [{}]! You are running [{}] with the following arguments: '.format(setup.user, setup.program))
    for a in args.__dict__:
        logging.debug(str(a) + ' : ' + str(args.__dict__[a]))

        '''
        Argument handling.
        '''
        if args.headless:
            headless = True
        else:
            headless = False

        if args.driver and args.url and args.username and args.password and args.role:
            '''
            LOG INTO URL
            '''
            dict_data = {
                'driver_browser' : args.driver,
                'url' : args.url,
                'username' : args.username,
                'password' : args.password,
                'role' : args.role,
                'headless' : headless
            }
            driver = pyVTE(**dict_data)._login()

            '''
            FIND COURSES
            '''
            dict_data = {
                'driver' : driver
            }
            list_courses = pyVTE(**dict_data)._find_courses()

            '''
            FIND CLASSES FOR ALL COURSES AND COMPLETE THEM
            '''
            dict_data = {
                'driver' : driver,
                'list_courses' : list_courses,
                'role' : args.role
            }
            list_courses_classes = pyVTE(**dict_data)._process_courses_classes()
        else:
            logging.error('Make sure to have all required parameters and arguments and try again.')
            sys.exit()

'''
Entry point of script.
'''
if __name__ == '__main__':
	main()
