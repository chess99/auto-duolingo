import json
import os
import time

from crawler.session_fetch import fetch_session


# fmt: off
def print_course_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        currentCourse = data.get('currentCourse', {})
        pathSectioned = currentCourse.get('pathSectioned', [])
        print(f"Path sections: {len(pathSectioned)}\n")

        total_sessions = 0  # Initialize total sessions counter

        for section in pathSectioned:
            print(f"Section {section['index']}: {section['debugName']}")
            print(f"  Units: {len(section['units'])}")

            for unit in section['units']:
                print(f"    Unit {unit['unitIndex']}: {unit['teachingObjective']}")
                print(f"      Levels: {len(unit['levels'])}")

                for level in unit['levels']:
                    print(f"        Level {level['absoluteNodeIndex']}: {level['debugName']}")
                    print(f"          Total Sessions: {level['totalSessions']}")
                    print(f"          Path Level Client Data: {level['pathLevelClientData']}\n")
                    total_sessions += level['totalSessions']  # Add to total sessions

        print(f"Total sessions for the full course: {total_sessions}")  # Print the total sessions
# fmt: on


def list_all_levels(course_json_file_path):
    with open(course_json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        currentCourse = data.get('currentCourse', {})
        pathSectioned = currentCourse.get('pathSectioned', [])

        levels_list = []

        for section in pathSectioned:
            for unit in section['units']:
                for level in unit['levels']:
                    level_info = {
                        'sectionIndex': section['index'],
                        'sectionName': section['debugName'],
                        'unitIndex': unit['unitIndex'],
                        'unitTeachingObjective': unit['teachingObjective'],
                        'absoluteNodeIndex': level['absoluteNodeIndex'],
                        'debugName': level['debugName'],
                        'pathLevelClientData': level['pathLevelClientData'],
                        'totalSessions': level['totalSessions'],
                    }
                    levels_list.append(level_info)

        return levels_list


def generate_request_list(levels_list):
    request_list = []
    for level in levels_list:
        if 'crownLevelIndex' not in level['pathLevelClientData'] or not level['pathLevelClientData']['crownLevelIndex']:
            print(
                f"Missing 'crownLevelIndex' for level {level['absoluteNodeIndex']}, skip.")
            continue

        totalSessions = level['totalSessions']
        for sessionIndex in range(totalSessions):
            params = {
                'absoluteNodeIndex': level['absoluteNodeIndex'],
                'levelSessionIndex': sessionIndex,
                'type': 'LEVEL_REVIEW' if sessionIndex == totalSessions - 1 else 'LESSON',
                'levelIndex': level['pathLevelClientData']['crownLevelIndex'],
            }

            if 'skillId' in level['pathLevelClientData']:
                params['skillId'] = level['pathLevelClientData']['skillId']
            elif 'skillIds' in level['pathLevelClientData']:
                params['skillIds'] = level['pathLevelClientData']['skillIds']
            else:
                print(
                    f"Skipping level due to missing skillId/skillIds: {level}")
                continue

            request_list.append(params)
    return request_list


def perform_session_requests(request_list, sessions_directory=".temp/sessions/"):
    total_requests = len(request_list)
    print(f"Total requests: {total_requests}")

    current_request_index = 0
    fetched_requests_count = 0  # Counter for fetched requests
    for params in request_list:
        current_request_index += 1
        file_path = f"{sessions_directory}/{params['absoluteNodeIndex']}_{params['levelSessionIndex']}.json"

        # Check if the file already exists
        if os.path.exists(file_path):
            print(f"File already exists. Skipping: {file_path}")
            continue  # Skip to the next iteration

        print(f"Fetching ({current_request_index}/{total_requests}): {params}")

        try:
            # Assuming fetch_session is a function that makes the actual request
            response = fetch_session(params)

            os.makedirs(sessions_directory, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            fetched_requests_count += 1  # Increment only on successful fetch
        except Exception as e:
            print(f"Error fetching session for params {params}: {e}")
            continue  # Skip to the next iteration

        # Calculate long break based on fetched requests
        if fetched_requests_count % 20 == 0:
            print("Taking a long break...")
            time.sleep(60)  # Long break after every 20 successful fetches

        time.sleep(1)  # Short delay between requests


if __name__ == "__main__":
    course_json_file_path = ".temp/current_course.json"
    levels_list = list_all_levels(course_json_file_path)
    request_list = generate_request_list(levels_list)
    perform_session_requests(request_list)
