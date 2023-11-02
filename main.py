import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from linkedinautoapply import LinkedinAutoApply
from indeedautoapply import IndeedAutoApply
from validate_email import validate_email
import logging
import yaml
config_path = 'cgi-bin/linkedinconfig.yaml'
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)
logging.basicConfig(
    filename="jobs.log", encoding="utf-8", level=logging.INFO, filemode="w"
)


logging.info("Starting AutoApply application")


def init_browser():
    browser_options = Options()
    options = [
        "--disable-blink-features",
        "--no-sandbox",
        "--start-maximized",
        "--disable-extensiions",
        "--ignore-certificate-errors",
        "--disable-blink-features=AutomationControlled",
        "--acceptInsecureCerts",
    ]

    for option in options:
        browser_options.add_argument(option)

    browser_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    driver.set_window_position(0, 0)
    driver.maximize_window()

    return driver


def validate_linkedin_yaml():
    with open("cgi-bin/linkedinconfig.yaml", "r") as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)
            raise exc

    mandatory_params = [
        "email",
        "password",
        "disableAntiLock",
        "remote",
        "experienceLevel",
        "jobTypes",
        "date",
        "positions",
        "locations",
        "distance",
        "outputFileDirectory",
        "checkboxes",
        "universityGpa",
        "languages",
        "technology",
        "personalInfo",
        "eeo",
        "uploads",
    ]

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            raise SyntaxError(mandatory_param + " is not inside the yml file!")

    assert validate_email(parameters["email"])
    assert len(str(parameters["password"])) > 0

    assert isinstance(parameters["disableAntiLock"], bool)

    assert isinstance(parameters["remote"], bool)

    assert len(parameters["experienceLevel"]) > 0
    experience_level = parameters.get("experienceLevel", [])
    at_least_one_experience = False
    for key in experience_level.keys():
        if experience_level[key]:
            at_least_one_experience = True
    assert at_least_one_experience

    assert len(parameters["jobTypes"]) > 0
    job_types = parameters.get("jobTypes", [])
    at_least_one_job_type = False
    for key in job_types.keys():
        if job_types[key]:
            at_least_one_job_type = True
    assert at_least_one_job_type

    assert len(parameters["date"]) > 0
    date = parameters.get("date", [])
    at_least_one_date = False
    for key in date.keys():
        if date[key]:
            at_least_one_date = True
    assert at_least_one_date

    approved_distances = {0, 5, 10, 25, 50, 100}
    assert parameters["distance"] in approved_distances

    assert len(parameters["positions"]) > 0
    assert len(parameters["locations"]) > 0

    assert len(parameters["uploads"]) >= 1 and "resume" in parameters["uploads"]

    assert len(parameters["checkboxes"]) > 0

    checkboxes = parameters.get("checkboxes", [])
    assert isinstance(checkboxes["driversLicence"], bool)
    assert isinstance(checkboxes["requireVisa"], bool)
    assert isinstance(checkboxes["legallyAuthorized"], bool)
    assert isinstance(checkboxes["urgentFill"], bool)
    assert isinstance(checkboxes["commute"], bool)
    assert isinstance(checkboxes["backgroundCheck"], bool)
    assert "degreeCompleted" in checkboxes

    assert isinstance(parameters["universityGpa"], (int, float))

    languages = parameters.get("languages", [])
    language_types = {"none", "conversational", "professional", "native or bilingual"}
    for language in languages:
        assert languages[language].lower() in language_types

    technology = parameters.get("technology", [])

    for tech in technology:
        assert isinstance(technology[tech], int)
    assert "default" in technology

    assert len(parameters["personalInfo"])
    personal_info = parameters.get("personalInfo", [])
    for info in personal_info:
        assert personal_info[info] != ""

    assert len(parameters["eeo"])
    eeo = parameters.get("eeo", [])
    for survey_question in eeo:
        assert eeo[survey_question] != ""

    return parameters


def validate_indeed_yaml():
    with open("cgi-bin/indeedconfig.yaml", "r") as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)
            raise exc

    mandatory_params = [
        "email",
        "password",
        "disableAntiLock",
        "remote",
        "experienceLevel",
        "jobTypes",
        "date",
        "positions",
        "locations",
        "distance",
        "outputFileDirectory",
        "checkboxes",
        "universityGpa",
        "languages",
        "technology",
        "personalInfo",
        "eeo",
        "uploads",
    ]

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            raise SyntaxError(mandatory_param + " is not inside the yml file!")

    assert validate_email(parameters["email"])
    assert len(str(parameters["password"])) > 0

    assert isinstance(parameters["disableAntiLock"], bool)

    assert isinstance(parameters["remote"], bool)

    assert len(parameters["experienceLevel"]) > 0
    experience_level = parameters.get("experienceLevel", [])
    at_least_one_experience = False
    for key in experience_level.keys():
        if experience_level[key]:
            at_least_one_experience = True
    assert at_least_one_experience

    assert len(parameters["jobTypes"]) > 0
    job_types = parameters.get("jobTypes", [])
    at_least_one_job_type = False
    for key in job_types.keys():
        if job_types[key]:
            at_least_one_job_type = True
    assert at_least_one_job_type

    assert len(parameters["date"]) > 0
    date = parameters.get("date", [])
    at_least_one_date = False
    for key in date.keys():
        if date[key]:
            at_least_one_date = True
    assert at_least_one_date

    approved_distances = {0, 5, 10, 25, 50, 100}
    assert parameters["distance"] in approved_distances

    assert len(parameters["positions"]) > 0
    assert len(parameters["locations"]) > 0

    assert len(parameters["uploads"]) >= 1 and "resume" in parameters["uploads"]

    assert len(parameters["checkboxes"]) > 0

    checkboxes = parameters.get("checkboxes", [])
    assert isinstance(checkboxes["driversLicence"], bool)
    assert isinstance(checkboxes["requireVisa"], bool)
    assert isinstance(checkboxes["legallyAuthorized"], bool)
    assert isinstance(checkboxes["urgentFill"], bool)
    assert isinstance(checkboxes["commute"], bool)
    assert isinstance(checkboxes["backgroundCheck"], bool)
    assert "degreeCompleted" in checkboxes

    assert isinstance(parameters["universityGpa"], (int, float))

    languages = parameters.get("languages", [])
    language_types = {"none", "conversational", "professional", "native or bilingual"}
    for language in languages:
        assert languages[language].lower() in language_types

    technology = parameters.get("technology", [])

    for tech in technology:
        assert isinstance(technology[tech], int)
    assert "default" in technology

    assert len(parameters["personalInfo"])
    personal_info = parameters.get("personalInfo", [])
    for info in personal_info:
        assert personal_info[info] != ""

    assert len(parameters["eeo"])
    eeo = parameters.get("eeo", [])
    for survey_question in eeo:
        assert eeo[survey_question] != ""

    return parameters


if __name__ == "__main__":
    #job_site = input("What job site do you want to apply on? (LinkedIn or Indeed): ")
    job_site = config.get('job_site', 'LinkedIn')
    try:
        browser = init_browser()
        if job_site.lower() == "linkedin":
            parameters = validate_linkedin_yaml()
            linkedin_auto_apply = LinkedinAutoApply(parameters, browser)
            linkedin_auto_apply.login()
            linkedin_auto_apply.security_check()
            linkedin_auto_apply.apply_to_jobs_in_search()
        elif job_site.lower() == "indeed":
            parameters = validate_indeed_yaml()
            indeed_auto_apply = IndeedAutoApply(parameters, browser)
            indeed_auto_apply.login()
            indeed_auto_apply.apply_to_jobs_in_search()
        else:
            print("Invalid job site")
    except Exception as e:
        logging.error(f"Exiting AutoApply application with error: {e}")

logging.info("Finished")
