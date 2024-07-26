import argparse
import os
import shutil
from datetime import datetime
from typing import Optional

from crawler.course_fetch import (
    generate_request_list,
    list_all_levels,
    perform_session_requests,
)
from crawler.persist import save_results_to_db, save_results_to_json
from crawler.session_process import process_all_sessions


def run_course_data_processing(options: Optional[dict] = None):
    course_json_file_path = ".temp/current_course.json"
    sessions_directory = ".temp/sessions/"
    backup_directory = ".temp/backup_sessions/"
    options = options or {}

    if options.get("reset_session_data", True):
        # Check if the sessions directory exists and move it to backup
        if os.path.exists(sessions_directory):
            if not os.path.exists(backup_directory):
                os.makedirs(backup_directory)
            shutil.move(sessions_directory, backup_directory +
                        "sessions_backup_" + datetime.now().strftime("%Y%m%d%H%M%S"))

        # Ensure the sessions directory is recreated
        os.makedirs(sessions_directory, exist_ok=True)

    levels_list = list_all_levels(course_json_file_path)
    request_list = generate_request_list(levels_list)
    perform_session_requests(request_list, sessions_directory)

    all_results = process_all_sessions(sessions_directory)
    return all_results


def run_course_data_processing_on_backup():
    backup_directory = ".temp/backup_sessions/"

    for entry in os.listdir(backup_directory):
        full_path = os.path.join(backup_directory, entry)
        if os.path.isdir(full_path):
            results = process_all_sessions(full_path)
            save_results_to_db(results)
            save_results_to_json(results)


def main():
    parser = argparse.ArgumentParser(
        description="Run the web scraping process.")

    parser.add_argument('--on-backup', action='store_true',
                        help="Run processing on backup data")

    parser.add_argument('--reset', action='store_true',
                        help="Reload session data")

    args = parser.parse_args()

    if args.on_backup:
        run_course_data_processing_on_backup()
    else:
        all_results = run_course_data_processing(
            {"reset_session_data": args.reset})
        save_results_to_db(all_results)
        save_results_to_json(all_results)


if __name__ == "__main__":
    main()
