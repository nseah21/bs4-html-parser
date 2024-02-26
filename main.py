from bs4 import BeautifulSoup
from datetime import date, time
from dataclasses import dataclass
import dateutil.parser as dparser
from typing import List

@dataclass
class MaintenanceRow:
    start_date: date
    start_time: time
    end_date: date 
    end_time: time
    affected_services: List[str]

DATE_FORMAT = "%d %b %Y (%a)"
TIME_FORMAT = "%#I.%M%#p"

def get_dates_and_times_from_maintenance_duration(maintenance_duration: str) -> tuple[date, time, date, time]:
    start_date_string, start_time_string, end_date_string, end_time_string = tokenize_maintenance_duration(maintenance_duration)
    start_date = dparser.parse(start_date_string, fuzzy=True).date()
    start_time = dparser.parse(start_time_string, fuzzy=True).time()
    end_date = dparser.parse(end_date_string, fuzzy=True).date()
    end_time = dparser.parse(end_time_string, fuzzy=True).time()
    return start_date, start_time, end_date, end_time
    
def tokenize_maintenance_duration(maintenance_duration: str):
    maintenance_duration = maintenance_duration.replace(".", ":")
    start_datetime, end_datetime = maintenance_duration.split("to")
    start_date, start_time = start_datetime.split(",")
    end_date, end_time = end_datetime.split(",") if end_datetime.find(",") != -1 else (start_date, end_datetime)
    return start_date, start_time, end_date, end_time

def get_list_of_services_under_maintenance(affected_services: str):
    return affected_services.split("/")

def get_maintenance_row(maintenance_duration: str, affected_services: str) -> MaintenanceRow:
    start_date, start_time, end_date, end_time = get_dates_and_times_from_maintenance_duration(maintenance_duration)
    services_under_maintenance = get_list_of_services_under_maintenance(affected_services)
    return MaintenanceRow(
        start_date=start_date,
        start_time=start_time,
        end_date=end_date,
        end_time=end_time,
        affected_services=services_under_maintenance
    )

def get_maintenance_rows_from_html(filename: str) -> List[MaintenanceRow]:
    rows = []
    with open(filename) as fp:
        soup = BeautifulSoup(fp, "html.parser")
        data = soup.find_all("td")
        for i in range(0, len(data), 2):
            maintenance_duration = data[i].get_text()
            affected_services = data[i + 1].get_text()      
            rows.append(get_maintenance_row(maintenance_duration, affected_services))
    return rows

def get_test_data():
    return [MaintenanceRow(
        start_date=date(2035, 9, 11),
        start_time=time(9, 45, 0),
        end_date=date(2077, 12, 25),
        end_time=time(13, 45),
        affected_services=["Pantry arcade machine", "Level 11 pool table", "Old tea hut coffee steamer"]
    )]

def update_html_with_maintenance_rows(filename:str, maintenance_rows: List[MaintenanceRow]):
    with open(filename) as fp:
        soup = BeautifulSoup(fp, "html.parser")

        for tag in soup.select("tr")[1:]:
            tag.extract()

        for row in maintenance_rows:
            table_row = soup.new_tag("tr")
            table_duration_data = soup.new_tag("td")
            table_services_data = soup.new_tag("td")

            start_date = row.start_date.strftime(DATE_FORMAT)
            start_time = row.start_time.strftime(TIME_FORMAT).lower()
            end_date = row.end_date.strftime(DATE_FORMAT)
            end_time = row.end_time.strftime(TIME_FORMAT).lower()
            
            maintenance_duration_string =  f"{start_date}, {start_time} to {end_date + ', ' if end_date != start_date else ''}{end_time}"
            services_affected_string = "/".join(row.affected_services)

            table_duration_data.string = maintenance_duration_string
            table_services_data.string = services_affected_string

            table_row.append(table_duration_data)
            table_row.append(table_services_data)

            soup.html.tbody.append(table_row)

        with open("maintenance.copy.html", "wb") as f_op:
            f_op.write(soup.prettify("utf-8"))

def main():
    get_maintenance_rows_from_html("pages/maintenance.html")
    update_html_with_maintenance_rows("pages/maintenance.copy.html", get_test_data())    

if __name__ == "__main__":
    main()
