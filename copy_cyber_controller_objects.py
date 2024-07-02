import time
import requests
import urllib3
import json
import os
from getpass import getpass
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
current_working_directory = os.path.abspath(os.getcwd()) + os.path.sep
log = current_working_directory + 'copy_cyber_controller_objects.log'
logging.basicConfig(filename=log, filemode='w', format='%(asctime)s - %(message)s',
                    level=logging.INFO)


def login_cyber_controller(ip, user, password):
    headers = {
        'authority': ip,
        'accept': 'application/json; */*',
        "accept-encoding": "gzip, deflate, br",
        'accept-language': 'en-US,en;q=0.9,he;q=0.8',
        'content-type': 'application/json',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/113.0.0.0 Safari/537.36'
    }

    with requests.sessions.Session() as session:
        session.auth = (user, password)
        session.verify = False
        session.headers = headers

    login_data = '{"username":"' + user + '","password":"' + password + '"}'
    login_url = 'https://' + ip + '/mgmt/system/user/login'
    login_response = session.post(login_url, headers=headers, verify=False, data=login_data)
    if login_response.status_code != 200:
        print("Cyber-Controller " + ip + " login status code:", login_response.status_code)
        logging.error("Cyber-Controller " + ip + " login status code: " + str(login_response.status_code))
        logging.info('Finishing the script.')
        exit(1)
    else:
        return session


def get_parent_site_id(parent_site_name, session, dst_cc_ip):
    parent_site_name_url = 'https://' + dst_cc_ip + '/mgmt/system/config/tree/site/byname/' + parent_site_name
    parent_site_name_response = session.get(parent_site_name_url, verify=False)
    data = json.loads(parent_site_name_response.text)
    if "There is no site with name" in parent_site_name_response.text:
        return False
    else:
        parent_site_id = data['ormID']
        return parent_site_id


def get_parent_site_name(device_parent_id, session, ip):
    parent_site_id_url = 'https://' + ip + '/mgmt/system/config/tree/site/byid/' + device_parent_id
    parent_site_id_response = session.get(parent_site_id_url, verify=False)
    data = json.loads(parent_site_id_response.text)
    if "There is no site with name" in parent_site_id_response.text:
        return False
    else:
        parent_site_name = data['name']
        return parent_site_name


def extract_sites_and_devices(data, src_session, src_cc_ip, parent_id=None):
    sites = []
    devices = []

    for item in data["children"]:
        if item["meIdentifier"]["managedElementClass"] == "com.radware.insite.model.device.Device":
            device_parent_id = parent_id if parent_id else data["meIdentifier"]["managedElementID"]

            # parent_site_name = get_parent_site_name(device_parent_id)

            device = {
                "name": item["name"],
                "type": item["type"],
                "managementIp": item["managementIp"],
                "id": item["meIdentifier"]["managedElementID"],
                "parentOrmID": device_parent_id
                # "parent_site_name": parent_site_name
            }
            devices.append(device)
        elif item["meIdentifier"]["managedElementClass"] == "com.radware.insite.model.device.Site":
            site_parent_id = parent_id if parent_id else data["meIdentifier"]["managedElementID"]
            parent_site_name = get_parent_site_name(site_parent_id, src_session, src_cc_ip)

            site = {
                "name": item["name"],
                "id": item["meIdentifier"]["managedElementID"],
                "parent_site_name": parent_site_name,
                "parentOrmID": site_parent_id
            }

            sites.append(site)
            extracted_sites, extracted_devices = extract_sites_and_devices(item, src_session, src_cc_ip,
                                                                           item["meIdentifier"]["managedElementID"])
            sites.extend(extracted_sites)
            devices.extend(extracted_devices)

    return sites, devices


def extract_device_access_data(device_ip, existing_file_data, session, src_cc_ip):
    url = 'https://' + src_cc_ip + '/mgmt/system/config/tree/device/byip/' + device_ip
    response = session.get(url, verify=False)
    data = json.loads(response.text)
    device_access_data = data["deviceSetup"]['deviceAccess']
    del device_access_data['ormID']

    for device in existing_file_data['devices']:
        if device['managementIp'] == device_ip:
            device['deviceAccess'] = device_access_data
            break

    return existing_file_data


def get_site_name_by_id(site_id, json_data):
    # Extracting the name of the site by ID
    site_name = None

    for site in json_data['sites']:
        if site['id'] == site_id:
            site_name = site['name']
            break

    return site_name


def main(src_cc_ip, src_cc_user, src_cc_password, dst_cc_ip, dst_cc_user, dst_cc_password, url_suffix):

    src_session = login_cyber_controller(src_cc_ip, src_cc_user, src_cc_password)

    url = 'https://' + src_cc_ip + url_suffix
    response = src_session.get(url, verify=False)
    data = json.loads(response.text)

    # Extract sites and devices
    extracted_sites, extracted_devices = extract_sites_and_devices(data, src_session, src_cc_ip)

    # Construct the final JSON structure
    final_json = {
        "sites": extracted_sites,
        "devices": extracted_devices
    }

    for device in final_json['devices']:
        device_ip = device['managementIp']
        final_json = extract_device_access_data(device_ip, final_json, src_session, src_cc_ip)

    src_cc_root_site_name = data["name"]

    dst_session = login_cyber_controller(dst_cc_ip, dst_cc_user, dst_cc_password)
    url = 'https://' + dst_cc_ip + url_suffix
    response = dst_session.get(url, verify=False)
    data = json.loads(response.text)

    dst_cc_root_site_name = data["name"]
    dst_cc_root_site_id = data["meIdentifier"]["managedElementID"]

    if dst_cc_root_site_name != src_cc_root_site_name:
        url = 'https://' + dst_cc_ip + '/mgmt/system/config/tree/site'
        payload = {
            "ormID": dst_cc_root_site_id,
            "name": src_cc_root_site_name
        }
        response = dst_session.put(url, json=payload, verify=False)
        if response.status_code != 200:
            print("Failed to change root site name")
            logging.error('Failed to change root site name')
        else:
            print("Root site name has been successfully changed to", src_cc_root_site_name)
            logging.info("Root site name has been successfully changed to " + src_cc_root_site_name)

    for site in final_json["sites"]:
        site_name = site["name"]
        parent_site_name = site["parent_site_name"]

        parent_site_id = get_parent_site_id(parent_site_name, dst_session, dst_cc_ip)
        if not parent_site_id:
            parent_site_id = dst_cc_root_site_id

        # Make POST request
        payload = {
            "parentOrmID": parent_site_id,
            "name": site_name
        }
        url = 'https://' + dst_cc_ip + '/mgmt/system/config/tree/site'

        response = dst_session.post(url, verify=False, json=payload)
        if response.status_code != 200:
            print("Failed to add site: ", site_name)
            error = response.json()
            error_message = error['message']
            logging.error("Failed to add site - " + site_name + ' ' + error_message)
        else:
            print("Added site:", site_name)
            logging.info("Added site: " + site_name)

    for device in final_json["devices"]:
        device_name = device['name']

        src_parent_device_id = device['parentOrmID']
        parent_site_name = get_site_name_by_id(src_parent_device_id, final_json)

        if not parent_site_name:
            parent_orm_id = dst_cc_root_site_id
        else:
            parent_orm_id = get_parent_site_id(parent_site_name, dst_session, dst_cc_ip)

        payload = {
            "name": device['name'],
            "parentOrmID": parent_orm_id,
            "type": device['type'],
            "deviceSetup": {
                "deviceAccess": device['deviceAccess']
            }
        }

        url = 'https://' + dst_cc_ip + '/mgmt/system/config/tree/device'
        response = dst_session.post(url, verify=False, json=payload)
        if response.status_code != 200:
            print("Failed to add device:", device_name)
            error = response.json()
            error_message = error['message']
            logging.error("Failed to add device - " + device_name + ' ' + error_message)
        else:
            print("Added device:", device_name)
            logging.info("Added device: " + device_name)


if __name__ == "__main__":
    logging.info('Starting the script.')
    print("--- Source Cyber-Controller Details ---")
    src_cc_ip = input("Address: ")
    src_cc_user = input("Username: ")
    src_cc_password = getpass("Password: ")

    print("\n--- Destination Cyber-Controller Details ---")
    dst_cc_ip = input("Address: ")
    dst_cc_user = input("Username: ")
    dst_cc_password = getpass("Password: ")

    main(src_cc_ip, src_cc_user, src_cc_password, dst_cc_ip, dst_cc_user, dst_cc_password,
         '/mgmt/system/config/tree/Physical')
    main(src_cc_ip, src_cc_user, src_cc_password, dst_cc_ip, dst_cc_user, dst_cc_password,
         '/mgmt/system/config/tree/Organization')

    logging.info('Finishing the script.')
    print("Done.")
    print("This prompt will be closed in 5 seconds.")
    print("You can see the log file in this directory")
    time.sleep(5)
