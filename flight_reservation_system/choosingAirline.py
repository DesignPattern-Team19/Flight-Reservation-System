from asiana_airlines import asiana_air
from jeju_airlines import jeju_air
from korean_airlines import korean_air
import pandas as pd

def check_all_flights(departure_date, origin, destination):
    flights = []

    # 아시아나 항공 조회
    flight_ids_asiana, flight_infos_asiana = asiana_air.proxy_server.check_flight_schedule_one_way(departure_date, origin, destination)
    if flight_ids_asiana:
        for i in range(len(flight_ids_asiana)):
            flights.append((flight_ids_asiana[i], flight_infos_asiana[i], "Asiana Airlines"))

    # 제주 항공 조회
    flight_ids_jeju, flight_infos_jeju = jeju_air.proxy_server.query_flight_schedule_one_way(departure_date, origin, destination)
    if flight_ids_jeju:
        for i in range(len(flight_ids_jeju)):
            flights.append((flight_ids_jeju[i], flight_infos_jeju[i], "Jeju Air"))

    # 대한 항공 조회
    flight_ids_korean, flight_infos_korean = korean_air.proxy_server.search_flight_schedule_one_way(departure_date, origin, destination)
    if flight_ids_korean:
        for i in range(len(flight_ids_korean)):
            flights.append((flight_ids_korean[i], flight_infos_korean[i], "Korean Air"))

    return flights

# 항공편 조회 예제
departure_date = "2024-07-01"
origin = "인천(ICN)"
destination = "토론토(YYZ)"

flights = check_all_flights(departure_date, origin, destination)

# 조회된 항공편 출력
if flights:
    for i, flight in enumerate(flights):
        print(f"{i+1}. Flight ID: {flight[0]}, Airline: {flight[2]}")
        df = pd.DataFrame([flight[1]])
        print(df)
else:
    print("해당 조건에 맞는 항공편이 없습니다.")

# 사용자 선택 (예시로 첫 번째 항공편 선택) 예약
if flights:
    selected_flight = flights[0]  # 예시로 첫 번째 항공편 선택
    print(f"선택된 항공편 ID: {selected_flight[0]}, Airline: {selected_flight[2]}")
    passengers_info = [("Billy", "M", "1974-08-17"), ("Watson", "M", "1960-04-19")]

    #  예약 함수
    def book_flight(flight_id, airline, passengers_info):
        if airline == "Asiana Airlines":
            return asiana_air.proxy_server.book_flight(flight_id, None, len(passengers_info), passengers_info, "goodtrip")
        elif airline == "Jeju Air":
            return jeju_air.proxy_server.book_flight(flight_id, None, len(passengers_info), passengers_info, "goodtrip")
        elif airline == "Korean Air":
            return korean_air.proxy_server.book_flight(flight_id, None, len(passengers_info), passengers_info, "goodtrip")

    # 편도 예약
    t_or_f, booking_reference = book_flight(selected_flight[0], selected_flight[2], passengers_info)
    print("예약 성공 여부: ", str(t_or_f))
    print("예약 번호: ", str(booking_reference))

    # 예약 취소 함수
    def cancel_flight(booking_reference, airline):
        if airline == "Asiana Airlines":
            return asiana_air.proxy_server.cancel_flight(booking_reference)
        elif airline == "Jeju Air":
            return jeju_air.proxy_server.cancel_flight(booking_reference)
        elif airline == "Korean Air":
            return korean_air.proxy_server.cancel_flight(booking_reference)

    # 예약 취소
    if booking_reference:
        t_or_f = cancel_flight(booking_reference, selected_flight[2])
        print("예약 취소 여부: ", str(t_or_f))
else:
    print("예약 가능한 항공편이 없습니다.")
