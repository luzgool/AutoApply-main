import time, random, csv, pyautogui, datetime
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from itertools import product
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging


class LinkedinAutoApply:
    def __init__(self, parameters, driver):
        self.browser = driver
        self.email = parameters["email"]
        self.password = parameters["password"]
        self.disable_lock = parameters["disableAntiLock"]
        self.company_blacklist = parameters.get("companyBlacklist", []) or []
        self.title_blacklist = parameters.get("titleBlacklist", []) or []
        self.positions = parameters.get("positions", [])
        self.locations = parameters.get("locations", [])
        self.base_search_url = self.get_base_search_url(parameters)
        self.file_name = "output"
        self.max_number_of_pages = parameters.get("maxNumberOfPages")
        self.skip_promoted = parameters.get("skipPromoted")
        self.max_number_of_applicants = parameters.get("maxNumberOfApplicants")
        self.output_file_directory = parameters["outputFileDirectory"]
        self.resume_dir = parameters["uploads"]["resume"]
        if "coverLetter" in parameters["uploads"]:
            self.cover_letter_dir = parameters["uploads"]["coverLetter"]
        else:
            self.cover_letter_dir = ""
        self.checkboxes = parameters.get("checkboxes", [])
        self.university_gpa = parameters["universityGpa"]
        self.minimum_time_on_page = parameters["minimumTimeOnPage"]
        self.languages = parameters.get("languages", [])
        self.industry = parameters.get("industry", [])
        self.technology = parameters.get("technology", [])
        self.personal_info = parameters.get("personalInfo", [])
        self.eeo = parameters.get("eeo", [])
        self.technology_default = self.technology["default"]

    def login(self):
        try:
            print(f"Entering Login Function {str(self.now())}")
            logging.info(f"Entering Login Function {str(self.now())}")
            self.browser.get("https://www.linkedin.com/login")

            username_field = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(self.email)

            password_field = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_field.send_keys(self.password)

            sign_in_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn__primary--large"))
            )
            sign_in_button.click()

            print(f"Exiting Login Function {str(self.now())}")
            logging.info(f"Exiting Login Function {str(self.now())}")
        except TimeoutException:
            logging.error(f"Timed out logging in {self.now()} ")
            raise TimeoutException("Could not login!")

    def security_check(self):
        print(f"Entering Security Check Function {str(self.now())}")
        logging.info(f"Entering Security Check Function {str(self.now())}")
        current_url = self.browser.current_url
        page_source = self.browser.page_source

        if "/checkpoint/challenge/" in current_url or "security check" in page_source:
            input(
                "Please complete the security check and press enter in this console when it is done."
            )
            time.sleep(random.uniform(5.5, 10.5))
        print(f"Exiting Security Check Function {str(self.now())}")
        logging.info(f"Exiting Security Check Function {str(self.now())}")

    # Main function to start the application process
    def apply_to_jobs_in_search(self):
        print(f"Entering apply to jobs in search function {str(self.now())}")
        logging.info(f"Entering apply to jobs in search function {str(self.now())}")
        # Create random search order and set minimum time
        searches = list(product(self.positions, self.locations))
        random.shuffle(searches)
        page_sleep = 0
        for position in searches:
            location_url = "&location=" + "Remote"
            job_page_number = 0
            print(f"Starting the search for {position[0]} {str(self.now())}")
            logging.info(f"Starting the search for {position[0]} {str(self.now())}")

            # Starts navigating to the job page
            print("Going to first page")
            logging.info("Going to first page")
            self.next_job_page(position, location_url, job_page_number)
            time.sleep(random.uniform(0.1, 1))

            # Check to see if there is more than one page of jobs, if not then continue with next search
            page_state = self.browser.find_elements(
                By.CLASS_NAME, "artdeco-pagination__indicator"
            )
            if len(page_state) > 0:
                job_page_number = int(page_state[0].text)
                if self.max_number_of_pages <= 0:
                    max_number_of_pages = int(page_state[len(page_state) - 1].text)
                else:
                    max_number_of_pages = self.max_number_of_pages
            else:
                continue
            try:
                # Main loop for applying to jobs
                while job_page_number <= max_number_of_pages:
                    minimum_page_time = time.time() + self.minimum_time_on_page
                    page_sleep += 1
                    if job_page_number >= 2:
                        print("Going to page: " + str(job_page_number))
                        logging.info("Going to job page: " + str(job_page_number))
                        self.next_job_page(
                            position, location_url, (job_page_number - 1)
                        )
                        time.sleep(random.uniform(0.1, 1))
                    # Starts applying to jobs on the job page
                    print("Starting the application process for this page...")
                    logging.info("Starting the application process for this page...")
                    self.apply_to_jobs_on_current_page()
                    print("Applying to jobs on this page has been completed!")
                    logging.info("Applying to jobs on this page has been completed!")

                    # Timeouts to help prevent getting banned, getting flagged as a bot, and too many requests errors
                    time_left = minimum_page_time - time.time()
                    self.sleep_backoff(page_sleep, time_left, 100, 200)
                    job_page_number += 1
            except Exception as e:
                logging.error(
                    f"Something went wrong with this search. Moving on to the next one. {str(self.now())} {e} "
                )
                print(
                    "Something went wrong with this search. Moving on to the next one."
                )
                # Timeouts to help prevent getting banned, getting flagged as a bot, and too many requests errors
                time_left = minimum_page_time - time.time()
                self.sleep_backoff(page_sleep, time_left, 100, 200)
                job_page_number += 1

        print(f"Exiting apply to jobs in search Function {str(self.now())}")
        logging.info(f"Exiting apply to jobs in search Function {str(self.now())}")

    # Function to apply to the jobs on the current job page
    def apply_to_jobs_on_current_page(self):
        print(f"Entering apply to jobs on current page function {str(self.now())}")
        logging.info(
            f"Entering apply to jobs on current page function {str(self.now())}"
        )
        # Check if there are jobs on the page
        if self.browser.find_elements(By.CLASS_NAME, "jobs-search-no-results-banner"):
            raise Exception("No matching jobs found")
        # Gets the container that has the the jobs in a list
        job_list = self.browser.find_elements(
            By.CLASS_NAME, "jobs-search-results-list"
        )[0].find_elements(By.CLASS_NAME, "jobs-search-results__list-item")

        # Checks to make sure job list is not empty, and loops through list of jobs
        if len(job_list):
            for job in job_list:
                # Parses the job to get deatils(Job Title, Company, Link to job, and Job Location)
                job_details = self.get_job_details(job)
                if job_details:
                    blacklisted = self.blacklist_check(
                        job_details.get("job_title"), job_details.get("company")
                    )
                    if blacklisted:
                        continue
                else:
                    continue
                over_applicant_limit = self.over_applicant_limit()
                if not over_applicant_limit:
                    try:
                        time.sleep(random.uniform(1, 2))
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
                else:
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

        # Checks to see if there is a easy apply button and stores for later use
        easy_apply_button = self.browser.find_elements(
            By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"
        )
        if not easy_apply_button:
            raise NoSuchElementException
        logging.info(f"Filling out job application.... {str(self.now())}")
        print(f"Filling out job application.... {str(self.now())}")
        easy_apply_button[0].click()
        # Loop for moving through the application process pages

        self.loop_application_pages(job_details)

    # --------------------------------------------------------------Helper Functions ----------------------------------------------------------------------
    def loop_application_pages(self, job_details):
        retries = 3
        while (
            "review your application" not in self.check_application_status_by_header()
        ):
            while retries > 0:
                try:
                    # Getting status of application via header and button
                    app_status_header = self.check_application_status_by_header()
                    app_status_button = self.check_application_status_by_button()

                    # Contact info is always first page as of 6/22/2023
                    if "contact info" in app_status_header:
                        logging.info(f"Filling in contact info {str(self.now())}")
                        print(f"Filling in contact info {str(self.now())}")
                        self.contact_info()
                        app_status_button.click()
                        time.sleep(random.uniform(1, 2))

                    # Checking if resume, work experiance, or education page and skipping it
                    if (
                        "resume" in self.check_application_status_by_header()
                        or "currículum" in self.check_application_status_by_header()
                        or "work experience"
                        in self.check_application_status_by_header()
                        or "education" in self.check_application_status_by_header()
                        or "screening" in self.check_application_status_by_header()
                    ):
                        logging.info(f"Bypassing auto filled page {str(self.now())}")
                        print(f"Bypassing Bypassing auto filled page {str(self.now())}")
                        self.check_application_status_by_button().click()
                        time.sleep(random.uniform(1, 2))
                        continue

                    # Answer application questions
                    if "additional" in self.check_application_status_by_header():
                        logging.info(
                            f"Answering additional questions {str(self.now())}"
                        )
                        print(f"Answering additional questions {str(self.now())}")
                        self.additional_questions()
                        logging.info(
                            f"Answered application questions {str(self.now())}"
                        )
                        self.check_application_status_by_button().click()
                        time.sleep(random.uniform(3.0, 5.0))

                    if (
                        "voluntary self identification"
                        in self.check_application_status_by_header()
                    ):
                        logging.info(f"Filling in EEO info {str(self.now())}")
                        print(f"Filling in EEO info {str(self.now())}")
                        self.eeo()
                        self.check_application_status_by_button().click()
                        time.sleep(random.uniform(2.5, 5.5))

                    if (
                        "work authorization"
                        in self.check_application_status_by_header()
                    ):
                        logging.info(f"Filling in work auth info {str(self.now())}")
                        print(f"Filling in work auth info {str(self.now())}")
                        self.work_auth()
                        self.check_application_status_by_button().click()
                        time.sleep(random.uniform(2.5, 5.5))

                    if "privacy policy" in self.check_application_status_by_header():
                        question = self.browser.find_element(
                            By.CLASS_NAME,
                            "jobs-easy-apply-form-section__grouping",
                        )
                        logging.info(f"Filling in privacy info {str(self.now())}")
                        print(f"Filling in privacy info {str(self.now())}")
                        checkbox = question.find_element(By.TAG_NAME, "input")
                        self.browser.execute_script("arguments[0].click()", checkbox)
                        self.check_application_status_by_button().click()
                        time.sleep(random.uniform(2.5, 5.5))

                    if "home address" in self.check_application_status_by_header():
                        logging.info(f"Filling in address info {str(self.now())}")
                        print(f"Filling in address info {str(self.now())}")
                        self.home_address()
                        self.check_application_status_by_button().click()
                        time.sleep(random.uniform(2.5, 5.5))

                    # Checking to see if the button is the submit application button
                    if (
                        "review your application"
                        in self.check_application_status_by_header()
                    ):
                        try:
                            self.unfollow()
                            self.check_application_status_by_button().click()
                            time.sleep(random.uniform(2.5, 4.0))
                        except Exception as e:
                            logging.error(
                                f"Error submitting application: {e} {str(self.now())}"
                            )
                            print(f"Error submitting application {str(self.now())}")

                    # Checking to see if the application is done and closing the confirmation pop up
                    if "done" in self.check_application_status_by_button().text.lower():
                        logging.info(f"Application successful {str(self.now())}")
                        print(f"Application successful {str(self.now())}")
                        self.close_confirmation()
                        return

                    if (
                        "please enter a valid" in self.browser.page_source.lower()
                        or "file is required" in self.browser.page_source.lower()
                    ):
                        retries -= 1
                        print(f"Retrying application, attempts left: {retries}")

                    retries -= 1
                    print(f"Retrying application, attempts left: {retries}")
                except Exception as e:
                    logging.info(f"Failed to apply to job {e} {str(self.now())}")
                    print(f"Failed to apply to job {str(self.now())}")
                    retries -= 1
                    break

            if retries <= 0:
                self.close_confirmation()
                self.browser.find_element(
                    By.XPATH, "//span[text()='Discard']/.."
                ).click()
                time.sleep(random.uniform(3, 5))
                self.log_application(job_details, True)
                raise NoSuchElementException()

    def home_address(self):
        print("Entering Home Address Function")
        try:
            groups = self.browser.find_elements(
                By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"
            )
            if len(groups) > 0:
                for group in groups:
                    lb = group.find_element(By.TAG_NAME, "label").text.lower()
                    input_field = group.find_element(By.TAG_NAME, "input")
                    if "street address line 1" in lb:
                        self.enter_text(
                            input_field, self.personal_info["Street address"]
                        )
                    elif "city" in lb:
                        self.enter_text(input_field, self.personal_info["City"])
                        time.sleep(3)
                        input_field.send_keys(Keys.DOWN)
                        input_field.send_keys(Keys.RETURN)
                    elif "zip" in lb or "postal" in lb:
                        self.enter_text(input_field, self.personal_info["Zip"])
                    elif "state" in lb or "province" in lb:
                        self.enter_text(input_field, self.personal_info["State"])
                    else:
                        logging.info(f"Could not find address fields {str(self.now())}")
                        print(f"Could not find address fields {str(self.now())}")

        except Exception as e:
            logging.error(f"Error filling in address {e} {str(self.now())}")
            print(f"Error filling in address {str(self.now())}")
        print("Exiting Home Address Function")

    def get_answer(self, question):
        print("Entering Get Answer Function")
        if self.checkboxes[question]:
            return "yes"
        else:
            return "no"

    def additional_questions(self):
        logging.info(f"Entering additional questions {str(self.now())}")
        print(f"Entering additional questions{str(self.now())}")
        questions = self.browser.find_elements(
            By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"
        )
        radio_questions = [
            "Have you completed the following level of education",
            "sponsorship",
            "Do you have the following license or certification",
            "Are you willing to undergo a background check",
            "Will you now or in the future require sponsorship",
            "legally authorized",
            "drug test",
            "remote",
        ]
        if len(questions) > 0:
            for question in questions:
                # TODO check questions to see what type of answer is needed(Dropdown, Radio, Text)
                if question.find_elements(By.TAG_NAME, "select"):
                    self.dropdown_question_check(question)
                elif question.text in radio_questions:
                    self.radio_question_check(question)
                elif (
                    "How many" in question.text or "experience" in question.text.lower()
                ):
                    try:
                        self.years_of_experiance(question)
                    except NoSuchElementException as e:
                        pass
                elif (
                    "salary" in question.text
                    or "pay" in question.text
                    or "compensation" in question.text
                ):
                    self.enter_text(
                        question.find_element(
                            By.CLASS_NAME, "artdeco-text-input--input"
                        ),
                        "100000",
                    )
                # Some questions have overlap on wheter or not they are dropdown or radio
                else:
                    try:
                        self.radio_question_check(question)
                        self.dropdown_question_check(question)
                        self.enter_text(
                            question.find_element(
                                By.CLASS_NAME, "artdeco-text-input--input"
                            ),
                            "1",
                        )
                    except Exception as e:
                        logging.error(
                            f"Could not answer questions on additnal question page {e} {self.now()}"
                        )
                        print(
                            f"Could not answer questions on additnal question page {self.now()}"
                        )
                        continue
        print("Exiting Additional Questions Function")

    def unfollow(self):
        print("Entering Unfollow Function")
        try:
            unfollow = self.browser.find_element(
                By.XPATH,
                "//label[contains(.,'to stay up to date with their page.')]",
            )
            unfollow.click()
            print("Exiting Unfollow Function")
        except Exception:
            logging.error(
                f"Could not find unfollow button: Exiting Unfollow Function {self.now()}"
            )
            print(
                f"Could not find unfollow button: Exiting Unfollow Function {self.now()}"
            )
            return

    def contact_info(self):
        question_groups = self.browser.find_elements(
            By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"
        )
        if len(question_groups) > 0:
            for questions in question_groups:
                question_text = questions.text.lower()
                if "First name" in question_text:
                    first_name_field = questions.find_element(
                        By.CLASS_NAME, "fb-single-line-text__input"
                    )
                    self.enter_text(first_name_field, self.personal_info["First Name"])
                elif "Last name" in question_text:
                    last_name_field = questions.find_element(
                        By.CLASS_NAME, "fb-single-line-text__input"
                    )
                    self.enter_text(last_name_field, self.personal_info["Last Name"])
                elif "mobile" in question_text or "teléfono móvil" in question_text:
                    try:
                        phone_number_field = questions.find_element(
                            By.TAG_NAME, "input"
                        )
                        self.enter_text(
                            phone_number_field,
                            self.personal_info["Mobile Phone Number"],
                        )
                    except Exception as e:
                        logging.error(
                            f"Could not input phone number. {e} {str(self.now())}"
                        )
                        print(f"Could not input phone number. {str(self.now())}")

    def close_confirmation(self):
        try:
            self.browser.find_element(
                By.XPATH,
                "//button[contains(@class, 'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]",
            ).click()
            print("Closed the applied confirmation window")
        except Exception as e:
            logging.error(
                f"Could not close the applied confirmation window  {e} {str(self.now())}"
            )
            print(f"Could not close the applied confirmation window {str(self.now())}")
        time.sleep(random.uniform(3, 5))

    def work_auth(self):
        try:
            questions = self.browser.find_elements(
                By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"
            )
            for question in questions:
                radio_text = question.text.lower()
                radio_options = ""
                radio_options = question.find_elements(By.TAG_NAME, "input")
                for indx, option in enumerate(radio_options):
                    if indx == 0:
                        yes_option = ""
                        yes_option = option
                    else:
                        no_option = ""
                        no_option = option
                        break
                if (
                    "will you now, or in the future, require sponsorship for employment visa status"
                    in radio_text
                ):
                    self.radio_select(no_option)
                    continue
                else:
                    self.radio_select(yes_option)
                    continue
        except Exception as e:
            print(e)

    def radio_question_check(self, question):
        try:
            radio_options = question.find_elements(By.TAG_NAME, "input")
            for indx, option in enumerate(radio_options):
                if indx == 0:
                    yes_option = option
                else:
                    no_option = option
                    break
            radio_text = question.text.lower()

            yes_options = [
                "driver's licence",
                "driver's license",
                "urgent",
                "background check",
                "level of education",
                "Do you have the following license or certification",
                "drug test",
                "remote",
            ]

            if radio_text in yes_options:
                self.radio_select(yes_option)
            elif "commuting" in radio_text:
                self.radio_select(no_option)
            else:
                self.radio_select(yes_option)
        except Exception as e:
            logging.error(f"Could not find radio button {e} {self.now()}")

    def radio_select(self, option):
        self.browser.execute_script("arguments[0].click();", option)

    def eeo(self):
        # TODO need to add logic to check for question type and fill in logic for extra questions
        try:
            questions = self.browser.find_elements(
                By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"
            )
            for question in questions:
                question_text = question.text.lower()
                # GENDER TEST TO SEE IF TEXT CONTAINS WHAT IS NEEDED
                if "Male" in question_text:
                    radio_options = question.find_elements(By.TAG_NAME, "input")
                    for indx, option in enumerate(radio_options):
                        if indx == 0:
                            male = option
                        elif indx == 1:
                            female = option
                            break
                        else:
                            decline_to_answer = option
                        self.radio_select(male)
                        print(female, decline_to_answer)
        except Exception as e:
            logging.error(f"Could not fill out EEO {e} {self.now()}")

    def years_of_experiance(self, question):
        no_of_years = self.technology_default
        for technology in self.technology:
            if technology.lower() in question.text.lower():
                no_of_years = self.technology[technology]
        self.enter_text(
            question.find_element(By.CLASS_NAME, "artdeco-text-input--input"),
            no_of_years,
        )

    def enter_text(self, element, text):
        element.clear()
        element.send_keys(text)

    def dropdown_question_check(self, questions):
        try:
            question = questions.find_element(
                By.CLASS_NAME, "jobs-easy-apply-form-element"
            )
            dropdown_field = question.find_element(By.TAG_NAME, "select")
            select_dropdown = Select(dropdown_field)

            if "What is your level of proficiency in English" in question.text:
                select_dropdown.select_by_visible_text("Native or bilingual")
            else:
                select_dropdown.select_by_visible_text("Yes")
        except NoSuchElementException as e:
            logging.error(
                f"Error in drop down question check, option other than Yes or No {e} {self.now()}"
            )

    def scroll_slow(
        self, scrollable_element, start=0, end=3600, step=100, reverse=False
    ):
        if reverse:
            start, end = end, start
            step = -step

        for i in range(start, end, step):
            self.browser.execute_script(
                "arguments[0].scrollTo(0, {})".format(i), scrollable_element
            )
            time.sleep(random.uniform(1.0, 2.6))

    def avoid_lock(self):
        if self.disable_lock:
            return

        pyautogui.keyDown("ctrl")
        pyautogui.press("esc")
        pyautogui.keyUp("ctrl")
        time.sleep(1.0)
        pyautogui.press("esc")

    def get_base_search_url(self, parameters):
        remote_url = ""

        if parameters["remote"]:
            remote_url = "f_CF=f_WRA"

        level = 1
        experience_level = parameters.get("experienceLevel", [])
        experience_url = "f_E="
        for key in experience_level.keys():
            if experience_level[key]:
                experience_url += "%2C" + str(level)
            level += 1

        distance_url = "?distance=" + str(parameters["distance"])

        job_types_url = "f_JT="
        job_types = parameters.get("experienceLevel", [])
        for key in job_types:
            if job_types[key]:
                job_types_url += "%2C" + key[0].upper()

        date_url = ""
        dates = {
            "all time": "",
            "month": "&f_TPR=r2592000",
            "week": "&f_TPR=r604800",
            "24 hours": "&f_TPR=r86400",
        }
        date_table = parameters.get("date", [])
        for key in date_table.keys():
            if date_table[key]:
                date_url = dates[key]
                break

        easy_apply_url = "&f_LF=f_AL"

        extra_search_terms = [distance_url, remote_url, job_types_url, experience_url]
        extra_search_terms_str = (
            "&".join(term for term in extra_search_terms if len(term) > 0)
            + easy_apply_url
            + date_url
        )

        return extra_search_terms_str

    def next_job_page(self, position, location, job_page):
        print("Entering Next Job Page Function")
        time.sleep(random.uniform(0.1, 2))
        try:
            self.browser.get(
                f"https://www.linkedin.com/jobs/search/{self.base_search_url}&keywords=+{position[0]}{location}&start={str(job_page * 25)}&sortBy=DD"
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
                time.sleep(1)
                self.next_job_page(position, location, job_page)
        except Exception as e:
            pass

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

    def get_job_details(self, job):
        self.browser.execute_script("arguments[0].scrollIntoView(true);", job)
        job.click()
        time.sleep(random.uniform(1.0, 2.6))
        job_info = {}
        try:
            # Check status of job before parsing for details
            job_status = job.find_element(
                By.CLASS_NAME, "job-card-container__footer-item"
            ).text
            if self.skip_promoted and "Promoted" in job_status:
                print("Promoted job, skipping...")
                return False
            if "Applied" in job_status:
                print("Already applied, skipping...")
                return False
            # Parsing the Job for title, company, location, link, and if its a promoted job
            # Job Title
            job_title = job.find_element(By.CLASS_NAME, "job-card-list__title").text
            # Job Link
            link = (
                job.find_element(By.CLASS_NAME, "job-card-list__title")
                .get_attribute("href")
                .split("?")[0]
            )
            # Company Name
            company = job.find_element(
                By.CLASS_NAME, "job-card-container__primary-description"
            ).text
            # Job Location
            job_location = job.find_element(
                By.CLASS_NAME, "job-card-container__metadata-item"
            ).text
            job_info = {
                "job_title": job_title,
                "company": company,
                "job_location": job_location,
                "link": link,
            }
        except Exception as e:
            logging.error(f"Error parsing job info {job_info} {e} ")
        return job_info

    def check_application_status_by_header(self):
        return self.browser.find_element(By.TAG_NAME, "h3").text.lower()

    def check_application_status_by_button(self):
        return self.browser.find_element(By.CLASS_NAME, "artdeco-button--primary")

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

    def over_applicant_limit(self):
        # Checks the number of applicants to the job and if it is less than specified amount then it will apply to the job
        try:
            try:
                number_of_applicants_string = self.browser.find_element(
                    By.XPATH, "//span[contains(text(),'applicants')]"
                ).text.split(" ")
            except Exception as e:
                pass
            try:
                number_of_applicants_string = self.browser.find_element(
                    By.CLASS_NAME, "jobs-unified-top-card__applicant-count"
                ).text.split(" ")
            except Exception as e:
                pass

            index_of_applicants = number_of_applicants_string.index("applicants") - 1
            number_of_applicants = int(number_of_applicants_string[index_of_applicants])
            if number_of_applicants < self.max_number_of_applicants:
                print(f"{number_of_applicants} applicants, applying to the job")
                return False
            else:
                print(
                    f"{number_of_applicants} is greater than the max number of applicants specified {self.max_number_of_applicants}, skipping..."
                )
                return True
        except Exception as e:
            # If cant find the number of applicants then it will just apply to the job
            logging.info(f"Couldn't get number of applicants {e} ")
            return False

    def log_application(self, job_details, failed_application):
        if failed_application:
            self.file_name = "app_failed"
            print(
                "Failed to apply to job! Please submit a bug report with this link: "
                + job_details.get("link")
            )
            print("Writing to the failed csv file...")
            try:
                self.write_to_file(
                    self.file_name,
                    job_details.get("company"),
                    job_details.get("job_title"),
                    job_details.get("link"),
                    job_details.get("location"),
                )
            except Exception as e:
                logging.error(f"Error writing to failed csv file {e} ")
        else:
            self.file_name = "app_success"
            self.write_to_file(
                self.file_name,
                job_details.get("company"),
                job_details.get("job_title"),
                job_details.get("link"),
                job_details.get("location"),
            )

    def write_to_file(self, app_outcome, company, job_title, link, location):
        to_write = [company, job_title, link, location, str(self.now())]
        try:
            with open(f"{app_outcome}.csv", "a", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(to_write)
        except Exception as e:
            logging.error(f"Error writing to csv file {e} ")

    def now(self):
        return datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")


logging.info("Finished")