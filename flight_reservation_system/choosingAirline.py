from abc import ABC, abstractmethod
from asiana_airlines import asiana_air
from jeju_airlines import jeju_air
from korean_airlines import korean_air
import pandas as pd

# 추상 클래스 정의
class FlightSearch(ABC):

    @abstractmethod
    def check_flights(self, departure_date, origin, destination, return_date=None):
        pass

    def book_flight(self, flight_id, airline, passengers_info):
        if airline == "Asiana Airlines":
            return asiana_air.proxy_server.book_flight(flight_id, None, len(passengers_info), passengers_info, "goodtrip")
        elif airline == "Jeju Air":
            return jeju_air.proxy_server.book_flight(flight_id, None, len(passengers_info), passengers_info, "goodtrip")
        elif airline == "Korean Air":
            return korean_air.proxy_server.book_flight(flight_id, None, len(passengers_info), passengers_info, "goodtrip")

    def cancel_flight(self, booking_reference, airline):
        if airline == "Asiana Airlines":
            return asiana_air.proxy_server.cancel_flight(booking_reference)
        elif airline == "Jeju Air":
            return jeju_air.proxy_server.cancel_flight(booking_reference)
        elif airline == "Korean Air":
            return korean_air.proxy_server.cancel_flight(booking_reference)

# 편도 항공편 조회 클래스
class OneWayFlightSearch(FlightSearch):

    def check_flights(self, departure_date, origin, destination, return_date=None):
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

# 왕복 항공편 조회 클래스
class RoundTripFlightSearch(FlightSearch):

    def check_flights(self, departure_date, origin, destination, return_date=None):
        if return_date is None:
            raise ValueError("Return date is required for round trip flights")

        depart_flights = OneWayFlightSearch().check_flights(departure_date, origin, destination)
        return_flights = OneWayFlightSearch().check_flights(return_date, destination, origin)

        round_trip_combinations = []
        for depart_flight in depart_flights:
            for return_flight in return_flights:
                round_trip_combinations.append((depart_flight, return_flight))

        return round_trip_combinations

# 팩토리 클래스
class FlightSearchFactory:

    @staticmethod
    def get_flight_search(flight_type):
        if flight_type == "oneway":
            return OneWayFlightSearch()
        elif flight_type == "roundtrip":
            return RoundTripFlightSearch()
        else:
            raise ValueError("Invalid flight type")

# 사용 예시

# 편도 항공편 조회 예제
flight_search = FlightSearchFactory.get_flight_search("oneway")
flights = flight_search.check_flights("2024-07-01", "인천(ICN)", "토론토(YYZ)")

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

    t_or_f, booking_reference = flight_search.book_flight(selected_flight[0], selected_flight[2], passengers_info)
    print("예약 성공 여부: ", str(t_or_f))
    print("예약 번호: ", str(booking_reference))

    # 예약 취소
    if booking_reference:
        t_or_f = flight_search.cancel_flight(booking_reference, selected_flight[2])
        print("예약 취소 여부: ", str(t_or_f))
else:
    print("예약 가능한 항공편이 없습니다.")

# 왕복 항공편 조회 예제
flight_search = FlightSearchFactory.get_flight_search("roundtrip")
round_trip_combinations = flight_search.check_flights("2024-07-04", "인천(ICN)", "로마(FCO)", "2024-07-09")

# 조회된 왕복 항공편 출력
if round_trip_combinations:
    for i, (depart_flight, return_flight) in enumerate(round_trip_combinations):
        print(f"왕복 조합 {i+1}:")
        print(f"출발 - Flight ID: {depart_flight[0]}, Airline: {depart_flight[2]}")
        print(pd.DataFrame([depart_flight[1]]))
        print(f"돌아오는 항공편 - Flight ID: {return_flight[0]}, Airline: {return_flight[2]}")
        print(pd.DataFrame([return_flight[1]]))
        print("----------------------------------------------------------------------------------------------------------------------")
else:
    print("해당 조건에 맞는 왕복 항공편이 없습니다.")

# 사용자 선택 (예시로 첫 번째 왕복 항공편 선택) 예약
if round_trip_combinations:
    selected_depart_flight = round_trip_combinations[0][0]  # 예시로 첫 번째 출발 항공편 선택
    selected_return_flight = round_trip_combinations[0][1]  # 예시로 첫 번째 돌아오는 항공편 선택
    print(f"선택된 출발 항공편 ID: {selected_depart_flight[0]}, Airline: {selected_depart_flight[2]}")
    print(f"선택된 돌아오는 항공편 ID: {selected_return_flight[0]}, Airline: {selected_return_flight[2]}")
    passengers_info = [("Billy", "M", "1974-08-17"), ("Watson", "M", "1960-04-19")]

    # 출발 항공편 예약
    t_or_f_depart, booking_reference_depart = flight_search.book_flight(selected_depart_flight[0], selected_depart_flight[2], passengers_info)
    print("출발 항공편 예약 성공 여부: ", str(t_or_f_depart))
    print("출발 항공편 예약 번호: ", str(booking_reference_depart))

    # 돌아오는 항공편 예약
    t_or_f_return, booking_reference_return = flight_search.book_flight(selected_return_flight[0], selected_return_flight[2], passengers_info)
    print("돌아오는 항공편 예약 성공 여부: ", str(t_or_f_return))
    print("돌아오는 항공편 예약 번호: ", str(booking_reference_return))

    # 예약 취소 (예시로 출발 항공편만 취소)
    if booking_reference_depart:
        t_or_f_cancel_depart = flight_search.cancel_flight(booking_reference_depart, selected_depart_flight[2])
        print("출발 항공편 예약 취소 여부: ", str(t_or_f_cancel_depart))

    # 예약 취소 (예시로 돌아오는 항공편만 취소)
    if booking_reference_return:
        t_or_f_cancel_return = flight_search.cancel_flight(booking_reference_return, selected_return_flight[2])
        print("돌아오는 항공편 예약 취소 여부: ", str(t_or_f_cancel_return))
else:
    print("예약 가능한 왕복 항공편이 없습니다.")
