import time, random, csv, pyautogui, datetime, math
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait as wait
from itertools import product
import logging
import sys


class IndeedAutoApply:
    def __init__(self, parameters, driver):
        self.browser = driver
        self.email = parameters["email"]
        self.password = parameters["password"]
        self.disable_lock = parameters["disableAntiLock"]
        self.company_blacklist = parameters.get("companyBlacklist", []) or []
        self.title_blacklist = parameters.get("titleBlacklist", []) or []
        self.positions = parameters.get("positions", [])
        self.locations = parameters.get("locations", [])
        self.personal_details = parameters.get("personalInfo", {})
        self.desired_pay = parameters["desiredPay"]
        self.base_search_url = self.get_base_search_url(parameters)
        self.file_name = "output"
        self.skip_opened_jobs = parameters["skipOpenedJobs"]
        self.max_number_of_pages = parameters.get("maxNumberOfPages")
        self.max_number_of_applicants = parameters.get("maxNumberOfApplicants")
        self.output_file_directory = parameters["outputFileDirectory"]
        self.technology = parameters.get("technology", [])
        self.technology_default = self.technology["default"]

    def login(self):
        try:
            print(f"Entering Indeed Login Function {str(self.now())}")
            logging.info(f"Entering Indeed Login Function {str(self.now())}")
            self.browser.get("https://secure.indeed.com/")
            while "settings/account" not in self.browser.current_url:
                submit_xpath = "//button[@type='submit']"
                time.sleep(random.uniform(3, 5))
                try:
                    # Email Input
                    self.browser.find_element(By.ID, "ifl-InputFormField-3").send_keys(
                        self.email
                    )
                    self.browser.find_element(By.XPATH, submit_xpath).click()
                    if self.captcha_check():
                        self.browser.find_element(By.XPATH, submit_xpath).click()

                    # Password fallback
                    time.sleep(random.uniform(1, 3))
                    self.browser.find_element(
                        By.XPATH, "//a[text()='Log in with a password instead']"
                    ).click()

                    # Password Input
                    self.browser.find_element(By.NAME, "__password").send_keys(
                        self.password
                    )
                    self.browser.find_element(By.XPATH, submit_xpath).click()
                    if self.captcha_check():
                        self.browser.find_element(By.NAME, "__password").send_keys(
                            self.password
                        )
                        self.browser.find_element(By.XPATH, submit_xpath).click()
                    if self.two_factor_auth():
                        self.browser.find_element(By.XPATH, submit_xpath).click()
                except Exception as e:
                    continue
                time.sleep(random.uniform(1, 7))
            print(f"Exiting Indeed Login Function {str(self.now())}")
            logging.info(f"Exiting Indeed Login Function {str(self.now())}")
        except TimeoutException:
            logging.error(f"Timed out logging in {self.now()} ")
            raise TimeoutException("Could not login!")

    def two_factor_auth(self):
        print(f"Entering Two Factor Auth Function {str(self.now())}")
        logging.info(f"Entering Two Factor Auth Function {str(self.now())}")
        time.sleep(random.uniform(1, 3))
        current_url = self.browser.current_url
        page_source = self.browser.page_source
        if "twofactorauth" in current_url or "2-Step Verification" in page_source:
            input(
                "Please complete Two Factor Auth and press enter in this console when it is done."
            )
            self.too_many_requests()
            return True
        print(f"Exiting Two Factor Auth Function {str(self.now())}")
        logging.info(f"Exiting Two Factor Auth Function {str(self.now())}")
        return False

    def captcha_check(self):
        print(f"Entering Captcha Check Function {str(self.now())}")
        logging.info(f"Entering Captcha Check Function {str(self.now())}")
        time.sleep(random.uniform(1.2, 1.5))
        captcha = False
        try:
            captcha = self.browser.find_element(
                By.XPATH, "//iframe[contains(@src,'captcha')]"
            )
        except NoSuchElementException:
            pass
        if captcha:
            input(
                "Please complete Captcha and press enter in this console when it is done."
            )
            time.sleep(random.uniform(1.2, 1.5))
            return True
        print(f"Exiting Captcha Check Function {str(self.now())}")
        logging.info(f"Exiting Captcha Check Function{str(self.now())}")
        return False

    def too_many_requests(self):
        page_source = self.browser.page_source
        if "429: Too Many Requests" in page_source:
            logging.error(f"Too many requests, waiting{self.now()}")
            time.sleep(random.uniform(60, 120))

    # Main function to start the application process
    def apply_to_jobs_in_search(self):
        print(f"Entering apply to jobs in search function {str(self.now())}")
        logging.info(f"Entering apply to jobs in search function {str(self.now())}")
        # Create random search order and set minimum time
        searches = list(product(self.positions, self.locations))
        random.shuffle(searches)
        page_sleep = 0
        minimum_time = 60
        for position in searches:
            job_page_number = 0
            print(f"Starting the search for {position[0]} {str(self.now())}")
            logging.info(f"Starting the search for {position[0]} {str(self.now())}")

            # Starts navigating to the job page
            print("Going to first page")
            logging.info("Going to first page")
            self.next_job_page(position, job_page_number)
            time.sleep(random.uniform(1.5, 3.5))

            # Checking number of jobs in search
            job_count = int(
                (
                    self.browser.find_element(
                        By.CLASS_NAME, "jobsearch-JobCountAndSortPane-jobCount"
                    ).text.split(" ")[0]
                ).replace(",", "")
            )
            if job_count:
                number_of_pages = math.floor(job_count / 15)
                if self.max_number_of_pages <= 0:
                    max_number_of_pages = number_of_pages
                else:
                    max_number_of_pages = self.max_number_of_pages
            elif not job_count:
                continue
            else:
                continue
            try:
                # Main loop for applying to jobs
                while job_page_number <= max_number_of_pages:
                    minimum_page_time = time.time() + minimum_time
                    page_sleep += 1
                    if job_page_number >= 1:
                        print("Going to page: " + str(job_page_number + 1))
                        logging.info("Going to job page: " + str(job_page_number + 1))
                        self.next_job_page(position, job_page_number)
                        time.sleep(random.uniform(1.5, 3.5))
                    # Starts applying to jobs on the job page
                    print("Starting the application process for this page...")
                    logging.info("Starting the application process for this page...")
                    self.apply_to_jobs_on_current_page()
                    print("Applying to jobs on this page has been completed!")
                    logging.info("Applying to jobs on this page has been completed!")

                    # Timeouts to help prevent getting banned, getting flagged as a bot, and too many requests errors
                    time_left = minimum_page_time - time.time()
                    self.sleep_backoff(page_sleep, time_left, 100, 300)
                    job_page_number += 1
            except Exception as e:
                logging.error(
                    f"Something went wrong with this search. Moving on to the next one. {str(self.now())} {e} "
                )
                # Timeouts to help prevent getting banned, getting flagged as a bot, and too many requests errors
                time_left = minimum_page_time - time.time()
                self.sleep_backoff(page_sleep, time_left, 100, 300)
                job_page_number += 1

        print(f"Exiting apply to jobs in search Function {str(self.now())}")
        logging.info(f"Exiting apply to jobs in search Function {str(self.now())}")

    def apply_to_jobs_on_current_page(self):
        print(f"Entering apply to jobs on current page function {str(self.now())}")
        logging.info(
            f"Entering apply to jobs on current page function {str(self.now())}"
        )
        # Gets the container that has the the jobs in a list
        job_list = self.browser.find_elements(
            By.XPATH, "//*[@id='mosaic-provider-jobcards']/ul/li"
        )
        # Checks to make sure job list is not empty, and loops through list of jobs
        if len(job_list):
            for job in job_list:
                if (
                    job.find_elements(By.CLASS_NAME, "mosaic-afterFifteenthJobResult")
                    or job.find_elements(By.CLASS_NAME, "mosaic-afterTenthJobResult")
                    or job.find_elements(By.CLASS_NAME, "mosaic-afterFifthJobResult")
                ):
                    continue
                # Parses the job to get deatils(Job Title, Company, Link to job, and Job Location)
                try:
                    self.popup_handler()
                    job_details = self.get_job_details(job)
                except Exception as e:
                    logging.error(f"Error getting job details: {e}")
                    continue
                if job_details:
                    blacklisted = self.blacklist_check(
                        job_details.get("job_title"), job_details.get("company")
                    )
                    if blacklisted:
                        continue
                else:
                    continue
                try:
                    time.sleep(random.uniform(3, 5))
                    try:
                        # Fills out the application of the currently selected job
                        self.fill_out_application(job_details)
                        print("Done applying to the job!")
                        logging.info("Done applying to the job!")
                    except Exception as e:
                        logging.error(f"Error applying for job: {e}")
                        continue
                    # logging to the successful app csv file
                    self.log_application(job_details, False)
                    continue
                except Exception as e:
                    # logging to the Unsuccessful app csv file
                    self.log_application(job_details, True)
                    logging.error(f"Could not apply to job {e}")
                    print("Could not apply to the job!")
                    continue
            print(f"Exiting apply to jobs on current page function {str(self.now())}")
            logging.info(
                f"Exiting apply to jobs on current page function {str(self.now())}"
            )
        else:
            print("No more jobs on this page")
            logging.info("No more jobs on this page")

    def fill_out_application(self, job_details):
        print(f"Entering Fill Out Application Function {str(self.now())}")
        logging.info(f"Entering Fill Out Application Function {str(self.now())}")
        original_window_handle = self.browser.current_window_handle
        self.browser.find_elements(By.ID, "indeedApplyButton")[0].click()
        self.popup_handler()
        # Loop for moving through the application process pages
        try:
            self.loop_application_pages(job_details, original_window_handle)
        except Exception as e:
            raise e

    def loop_application_pages(self, job_details, original_window_handle):
        wait(self.browser, timeout=10).until(EC.number_of_windows_to_be(2))
        print("Swapping to application window")
        logging.info("Swapping to application window")
        time.sleep(random.uniform(3.5, 5.5))
        for window_handle in self.browser.window_handles:
            if window_handle != original_window_handle:
                self.browser.switch_to.window(window_handle)
                break
        retries = 3
        while retries > 0:
            try:
                if (
                    "be a valid" in self.browser.page_source.lower()
                    or "required" in self.browser.page_source.lower()
                    or "choose the correct" in self.browser.page_source.lower()
                ):
                    retries -= 1
                    print(f"Retrying application, attempts left: {retries}")

                if "resume" in self.check_application_status_by_header():
                    logging.info(f"{str(self.now())}")
                    print(f" {str(self.now())}")
                    time.sleep(random.uniform(0.8, 2.2))
                    self.browser.find_element(
                        By.ID, "ia-IndeedResumeSelect-headerButton"
                    ).click()
                    self.check_application_status_by_button().click()
                    time.sleep(random.uniform(2, 2.5))
                    continue

                # Checking if Highlight a Job or qualifications and skipping it
                if (
                    "highlight a job that" in self.check_application_status_by_header()
                    or "qualifications" in self.check_application_status_by_header()
                    or "relevant work" in self.check_application_status_by_header()
                    or "may have more success"
                    in self.check_application_status_by_header()
                    or "employer requests a cover letter"
                    in self.check_application_status_by_header()
                ):
                    logging.info(f"Bypassing auto filled page {str(self.now())}")
                    print(f"Bypassing Bypassing auto filled page {str(self.now())}")
                    self.check_application_status_by_button().click()
                    time.sleep(random.uniform(2.5, 3.4))
                    continue

                # Answer questions from the employer
                if "questions" in self.check_application_status_by_header():
                    logging.info(f"Answering additional questions {str(self.now())}")
                    print(f"Answering additional questions {str(self.now())}")
                    try:
                        self.additional_questions()
                    except Exception as e:
                        logging.error(f"Error answering questions: {e}")
                        retries -= 1
                        continue
                    logging.info(f"Answered application questions {str(self.now())}")
                    self.check_application_status_by_button().click()
                    time.sleep(random.uniform(3.0, 5.0))
                    continue

                # Checking to see if the button is the submit application button
                if (
                    "review your application"
                    in self.check_application_status_by_header()
                ):
                    try:
                        time.sleep(random.uniform(1.5, 2.0))
                        self.browser.execute_script(
                            "arguments[0].scrollIntoView(true);",
                            self.check_application_status_by_button(),
                        )
                        time.sleep(random.uniform(1.5, 2.0))
                        self.check_application_status_by_button().click()
                        time.sleep(random.uniform(1.5, 2.0))
                    except Exception as e:
                        logging.error(
                            f"Error submitting application: {e} {str(self.now())}"
                        )
                        print(f"Error submitting application {str(self.now())}")
                # Checking to see if the application is done and closing the confirmation pop up
                if (
                    "application has been submitted"
                    in self.check_application_status_by_header().lower()
                    or "one more step"
                    in self.check_application_status_by_header().lower()
                ):
                    logging.info(f"Application successful {str(self.now())}")
                    print(f"Application successful {str(self.now())}")
                    self.browser.close()
                    self.browser.switch_to.window(original_window_handle)
                    return
                retries -= 1
                print(f"Retrying application, attempts left: {retries}")
            except Exception as e:
                logging.info(f"Failed to apply to job {e} {str(self.now())}")
                print(f"Failed to apply to job {str(self.now())}")
                self.browser.close()
                self.browser.switch_to.window(original_window_handle)
                raise e

        if retries <= 0:
            self.browser.close()
            self.browser.switch_to.window(original_window_handle)
            time.sleep(random.uniform(3, 5))
            self.log_application(job_details, True)
            raise NoSuchElementException("No more retries left")

    # --------------------------------- Helper Functions --------------------------------- #

    def additional_questions(self):
        logging.info(f"Entering additional questions {str(self.now())}")
        print(f"Entering additional questions {str(self.now())}")
        questions = self.browser.find_elements(By.CLASS_NAME, "ia-Questions-item")
        if questions:
            for question in questions:
                try:
                    self.browser.execute_script(
                        "arguments[0].scrollIntoView(true);", question
                    )
                    if (
                        "dates and times" in question.text.lower()
                        or "optional" in question.text.lower()
                    ):
                        continue
                    if question.find_elements(By.TAG_NAME, "select"):
                        self.select_question(question)
                    if question.find_elements(By.TAG_NAME, "fieldset"):
                        self.fieldset_question(question)
                    if "how many" in question.text.lower() and question.find_elements(
                        By.XPATH, ".//input[@type='number']"
                    ):
                        self.years_of_experiance(question)
                    if question.find_elements(
                        By.TAG_NAME, "textarea"
                    ) or question.find_elements(By.XPATH, ".//input[@type='text']"):
                        self.text_question(question)
                    if question.find_elements(By.XPATH, ".//input[@type='date']"):
                        question.find_element(
                            By.XPATH, ".//input[@type='date']"
                        ).send_keys(datetime.datetime.now().strftime("%m/%d/%Y"))

                except Exception as e:
                    logging.error(f"Error in quesitons {e} | {str(self.now())}")
                    raise e
            print("Exiting Additional Questions Function")
        else:
            return False

    def popup_handler(self):
        try:
            self.browser.find_elements(By.CLASS_NAME, "icl-CloseButton")[0].click()
            time.sleep(random.uniform(1, 1.5))
            return True
        except Exception as e:
            return False

    def select_question(self, question):
        question_text = question.find_element(By.TAG_NAME, "label").text.lower()
        select_options = Select(question.find_element(By.TAG_NAME, "select"))
        try:
            match question_text:
                case question_text if "professional experience" in question_text:
                    select_options.select_by_value("3")
                case question_text if "highest level" in question_text:
                    select_options.select_by_visible_text("bachelor degree")
                case question_text if "visa or citizenship status" in question_text:
                    select_options.select_by_value("8076111")
                case question_text if "salary range" in question_text:
                    for option in select_options.options:
                        if "100,000" in option.text:
                            select_options.select_by_visible_text(option.text)
                case question_text if "country" in question_text:
                    select_options.select_by_value(
                        # self.personal_details.get("Phone Country Code")
                        "US"
                    )
                    time.sleep(random.uniform(1.0, 2.0))
                    state_question = question.find_elements(By.TAG_NAME, "select")
                    select_options = Select(state_question[1])
                    select_options.select_by_visible_text(
                        self.personal_details.get("State")
                    )
                case _:
                    self.log_question(question_text, "select", select_options.options)
                    select_options.select_by_index(1)
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(
                f"Error in select quesitons {e} | {exception_type} | {line_number} | {str(self.now())}"
            )
            raise e

    def fieldset_question(self, question):
        try:
            options = question.find_elements(By.TAG_NAME, "label")
            if question.find_elements(By.CLASS_NAME, "ia-MultiselectQuestion"):
                question_text = question.find_element(By.TAG_NAME, "label").text.lower()
                # Poping first item because it is the question text in a multi select question
                options.pop(0)
            else:
                question_text = question.find_element(
                    By.TAG_NAME, "legend"
                ).text.lower()
            match question_text:
                case question_text if "sponsorship" in question_text or "company before" in question_text or "refer you" in question_text or "security clearance" in question_text or "veteran" in question_text or "you previously worked for" in question_text or "non-compete" in question_text:
                    options[1].click()
                case question_text if "ethnic origin" in question_text or "choose one of the options below" in question_text:
                    options[2].click()
                case question_text if "highest level of education" in question_text:
                    options[3].click()
                case question_text if "authorized to work" in question_text or "eligible to work" in question_text or "gender" in question_text or "consent" in question_text or "W2" in question_text or "experience" or "at least" in question_text:
                    options[0].click()
                case question_text if "want to add a response" in question_text:
                    options[1].click()
                case _:
                    self.log_question(question_text, "fieldset", options)
                    options[0].click()
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(
                f"Error in fieldset quesiton {e} | {exception_type} | {line_number} | {str(self.now())}"
            )
            raise e

    def text_question(self, question):
        try:
            question_text = question.find_element(By.TAG_NAME, "label").text.lower()
            if question.find_elements(By.TAG_NAME, "textarea"):
                match question_text:
                    case question_text if "salary" in question_text or "pay" in question_text or "rate" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "textarea"),
                            self.desired_pay,
                        )
                    case question_text if "address" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "textarea"),
                            self.personal_details["Street Address"],
                        )
                    case question_text if "you ever worked" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "textarea"), "No"
                        )
                    case _:
                        self.log_question(question_text, "textarea", "text")
                        self.update_value(
                            question.find_element(By.TAG_NAME, "textarea"), "Yes"
                        )
            else:
                match question_text:
                    case question_text if "address" in question_text or "street" in question_text or "location" in question_text or "currently live" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            self.personal_details["Street Address"],
                        )
                    case question_text if "city" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            self.personal_details.get("City"),
                        )
                    case question_text if "state" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            self.personal_details.get("State"),
                        )
                    case question_text if "zip" in question_text or "postal" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            self.personal_details.get("Zip"),
                        )
                    case question_text if "linkedin" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            self.personal_details.get("LinkedIn"),
                        )
                    case question_text if "phone" in question_text or "number" in question_text or "cell" in question_text or "mobile" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            self.personal_details.get("Mobile Phone Number"),
                        )
                    case question_text if "salary" in question_text or "pay" in question_text or "rate" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            self.desired_pay,
                        )
                    case question_text if "name" in question_text or "signature" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"),
                            (
                                self.personal_details.get("First Name")
                                + self.personal_details.get("Last Name")
                            ),
                        )
                    case question_text if "hear about" in question_text:
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"), "Indeed"
                        )
                    case _:
                        self.log_question(question_text, "text input", "text")
                        self.update_value(
                            question.find_element(By.TAG_NAME, "input"), "1"
                        )
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error(
                f"Error in text quesiton {e} | {exception_type} | {line_number} | {str(self.now())}"
            )
            raise e

    def get_base_search_url(self, parameters):
        remote_url = ""
        if parameters["remote"]:
            remote_url = f"l=Remote&sc=0kf%3Aattr%28DSQF7%29%3B"

        # TODO need to update this for how indeed does experience level
        # %29explvl%28ENTRY_LEVEL%29%3B
        # %29explvl%28SENIOR_LEVEL%29%3B
        # %29explvl%28MID_LEVEL%29%3B
        # level = 1
        # experience_level = parameters.get("experienceLevel", [])
        # experience_url = "f_E="
        # for key in experience_level.keys():
        #     if experience_level[key]:
        #         experience_url += "%2C" + str(level)
        #     level += 1

        # distance_url = "?distance=" + str(parameters["distance"])

        # job_types_url = "f_JT="
        # job_types = parameters.get("experienceLevel", [])
        # for key in job_types:
        #     if job_types[key]:
        #         job_types_url += "%2C" + key[0].upper()

        date_url = ""
        dates = {
            "2 weeks": "fromage=14",
            "week": "fromage=7",
            "3 days": "fromage=3",
            "24 hours": "fromage=1",
            "lastvisit": "fromage=last",
        }
        date_table = parameters.get("date", [])
        for key in date_table.keys():
            if date_table[key]:
                date_url = dates[key]
                break
        # TODO need to update to work
        sort_url = "sort=date"

        # https://www.indeed.com/jobs?q=software+engineer&l=Remote&sc=0kf%3Aattr%28DSQF7%29%3B&sort=date&fromage=1
        extra_search_terms_str = f"{remote_url}&{sort_url}&{date_url}"
        # extra_search_terms_str = (
        #     "&".join(term for term in extra_search_terms if len(term) > 0)
        #     + date_url
        # )

        return extra_search_terms_str

    def blacklist_check(self, job_title, company):
        for blacklisted_job_title in self.title_blacklist:
            if blacklisted_job_title in job_title.lower():
                print("Job contains blacklisted phrase in title!")
                return True

        for blacklisted_company in self.company_blacklist:
            if company.lower().split(" ")[0] in blacklisted_company.lower():
                print("Company is blacklisted!")
                return True
        return False

    def next_job_page(self, position, job_page):
        print("Entering Next Job Page Function")
        time.sleep(random.uniform(3.0, 5.6))
        try:
            position = position[0].replace(" ", "+")
            if job_page == 0:
                self.browser.get(
                    f"https://www.indeed.com/jobs?q={position}&{self.base_search_url}"
                )
            else:
                self.browser.get(
                    f"https://www.indeed.com/jobs?q={position}&{self.base_search_url}&start={str(job_page * 10)}"
                )
            self.avoid_lock()
            print("Exiting Next Job Page Function")
        except Exception as e:
            logging.error(f"Error getting to next page: {e} ")

        try:
            error_code = self.browser.find_element(By.CLASS_NAME, "error-code")
            if "429" in error_code.text:
                logging.info(f"429 Error Code: Sleeping for 60 seconds {self.now()}")
                print(f"429 Error Code: Sleeping for 60 seconds {self.now()}")
                time.sleep(60)
                self.next_job_page(position, job_page)
        except Exception as e:
            pass

    def get_job_details(self, job):
        self.browser.execute_script("arguments[0].scrollIntoView(true);", job)
        job.click()
        time.sleep(random.uniform(1.0, 2.6))
        if self.popup_handler():
            job.click()
            if self.popup_handler():
                # Occasionally there is a popup that will continue to show up
                # regardless of how many times you click the close button
                # This is a failsafe to prevent the program from getting stuck
                print("Popup loop detected, exiting")
                return False
        # Checks to see if there is a easy apply button and stores for later use
        if not len(self.browser.find_elements(By.ID, "indeedApplyButton")):
            print("Not and easy apply job, skipping")
            raise NoSuchElementException("No easy apply button found")
        time.sleep(random.uniform(1.0, 2.6))
        job_info = {}
        try:
            # Checking to see if applied for job recently
            if len(job.find_elements(By.CLASS_NAME, "applied-snippet")):
                print("Already applied, skipping")
                return False
            # Check to see if job has been opened before
            if self.skip_opened_jobs:
                if len(job.find_elements(By.CLASS_NAME, "myJobsState")):
                    print("Job has been opened before, skipping")
                    return False
            # Parsing the Job for title, company, location, link, and if its a promoted job
            # Job Title
            job_title = job.find_element(By.CLASS_NAME, "jobTitle").text
            # Job Link
            link = job.find_element(
                By.XPATH, "//a[contains(@class,'JobTitle')]"
            ).get_attribute("href")
            # Company Name
            company = job.find_element(By.CLASS_NAME, "companyName").text
            # Job Location
            job_location = job.find_element(By.CLASS_NAME, "companyLocation").text
            job_info = {
                "job_title": job_title,
                "company": company,
                "job_location": job_location,
                "link": link,
            }
        except Exception as e:
            logging.error(f"Error parsing job info {job_info} {e} ")
        return job_info

    def avoid_lock(self):
        if self.disable_lock:
            return

        pyautogui.keyDown("ctrl")
        pyautogui.press("esc")
        pyautogui.keyUp("ctrl")
        time.sleep(1.0)
        pyautogui.press("esc")

    def years_of_experiance(self, question):
        no_of_years = self.technology_default
        for technology in self.technology:
            if technology.lower() in question.text.lower():
                no_of_years = self.technology[technology]
        self.update_value(
            question.find_element(By.XPATH, ".//input[@type='number']"), no_of_years
        )

    def update_value(self, element, text):
        element.send_keys(Keys.BACKSPACE * 10)
        element.send_keys(text)

    def sleep_backoff(self, page_sleep, time_left, min, max):
        if time_left > 0:
            print("Sleeping for " + str(time_left) + " seconds.")
            time.sleep(time_left)
            return True
        if page_sleep % 5 == 0:
            sleep_time = random.randint(min, max)
            print("Sleeping for " + str(sleep_time / 60) + " minutes.")
            time.sleep(sleep_time)
        return False

    def log_application(self, job_details, failed_application):
        to_write = [
            job_details.get("company"),
            job_details.get("job_title"),
            job_details.get("link"),
            job_details.get("location"),
            str(self.now()),
        ]
        if failed_application:
            try:
                print(f"Failed to apply to job, please apply via link: {to_write[2]}")
                with open(f"app_failed.csv", "a", encoding="UTF8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(to_write)
            except Exception as e:
                logging.error(f"Error writing to failed csv file {e} ")
        else:
            try:
                with open(f"app_success.csv", "a", encoding="UTF8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(to_write)
            except Exception as e:
                logging.error(f"Error writing to success csv file {e} ")

    def log_question(self, question_text, question_type, options):
        print(
            f"Question not programmed for yet. Please submit a bug report with this question: {question_text}"
        )
        print("Writing to the unanswered csv file...")
        try:
            to_write = [question_text, question_type, str(self.now())]
            if options != "text":
                option_text_list = []
                for option in options:
                    option_text_list.append(option.text)
                to_write.insert(2, option_text_list)
            with open(f"question_log.csv", "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(to_write)
        except Exception as e:
            logging.error(f"Error writing to the unanswered csv file {e} ")

    def check_application_status_by_header(self):
        return self.browser.find_element(By.TAG_NAME, "h1").text.lower()

    def check_application_status_by_button(self):
        return self.browser.find_element(By.CLASS_NAME, "ia-continueButton")

    def now(self):
        return datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
